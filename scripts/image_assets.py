"""Explicit JPEG -> pixel transform -> metadata-free WebP. No discovery."""
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import tempfile
import zlib

MAX_DIMENSION = 1600
QUALITY = '82'
OUTPUT = 'assets/bikes/standert/hero.webp'


def run(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Native tools can print metadata and local paths; never echo their output.
        raise ValueError('Image tool failed: ' + Path(args[0]).name)
    return result.stdout


def relative_path(value):
    if not isinstance(value, str) or not value or '\\' in value or re.search(r'[*?\[\]:]', value):
        raise ValueError('Manifest requires an exact relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('..', '.', '') for part in value.split('/')):
        raise ValueError('Unsafe manifest path')
    return path


def manifest(path):
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict) or set(data) != {'standert-hero'}:
        raise ValueError('Only the approved standert-hero asset is supported')
    item = data['standert-hero']
    required = {'source', 'output', 'type', 'use', 'alt', 'caption'}
    if not isinstance(item, dict) or set(item) != required:
        raise ValueError('Invalid image manifest fields')
    for key in ('source', 'output'):
        relative_path(item[key])
    if item['output'] != OUTPUT or item['use'] != 'standert-hero' or item['type'] != 'image/jpeg':
        raise ValueError('Unsupported asset output, use or format')
    if Path(item['source']).suffix.lower() not in ('.jpg', '.jpeg'):
        raise ValueError('Only JPEG sources are supported in this slice')
    if not isinstance(item['alt'], str) or not item['alt'].strip() or not isinstance(item['caption'], str):
        raise ValueError('Descriptive alt text is required')
    return item


def orientation(data):
    """Read only JPEG IFD0 orientation; do not expose EXIF values or thumbnails."""
    if not data.startswith(b'\xff\xd8'):
        raise ValueError('Approved image is not a JPEG')
    offset, result = 2, 1
    while offset < len(data):
        if data[offset] != 255:
            raise ValueError('Malformed JPEG marker')
        while offset < len(data) and data[offset] == 255:
            offset += 1
        if offset >= len(data):
            raise ValueError('Truncated JPEG')
        marker = data[offset]
        offset += 1
        if marker in (0xda, 0xd9):
            break
        if offset + 2 > len(data):
            raise ValueError('Truncated JPEG segment')
        size = int.from_bytes(data[offset:offset+2], 'big')
        if size < 2 or offset + size > len(data):
            raise ValueError('Invalid JPEG segment')
        payload = data[offset+2:offset+size]
        offset += size
        if marker != 0xe1 or not payload.startswith(b'Exif\0\0'):
            continue
        tiff = payload[6:]
        try:
            order = {b'II': '<', b'MM': '>'}[tiff[:2]]
            read = lambda fmt, pos: struct.unpack_from(order + fmt, tiff, pos)[0]
            if read('H', 2) != 42:
                raise ValueError('Invalid EXIF header')
            start = read('I', 4)
            for i in range(read('H', start)):
                pos = start + 2 + 12 * i
                if read('H', pos) == 0x112:
                    if read('H', pos+2) != 3 or read('I', pos+4) != 1:
                        raise ValueError('Invalid orientation field')
                    result = read('H', pos+8)
                    if result not in range(1, 9):
                        raise ValueError('Unsupported image orientation')
        except (KeyError, struct.error, IndexError):
            raise ValueError('Malformed image orientation metadata') from None
    return result


def validate(data):
    """Inspect actual encoded container: only one opaque VP8 pixel chunk allowed.

    This rejects EXIF, XMP, ICC, comments, thumbnails, animation and unknown chunks,
    including appended data. Fresh cwebp opaque lossy output needs only VP8.
    """
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        raise ValueError('Invalid generated WebP')
    if int.from_bytes(data[4:8], 'little') + 8 != len(data):
        raise ValueError('Unexpected trailing or truncated image data')
    size = int.from_bytes(data[16:20], 'little')
    if data[12:16] != b'VP8 ' or 20 + size + size % 2 != len(data):
        raise ValueError('Generated image contains metadata or unapproved chunks')
    pixels = data[20:20+size]
    if pixels[3:6] != b'\x9d\x01\x2a':
        raise ValueError('Invalid VP8 frame')
    width = int.from_bytes(pixels[6:8], 'little') & 0x3fff
    height = int.from_bytes(pixels[8:10], 'little') & 0x3fff
    if not (0 < width <= MAX_DIMENSION and 0 < height <= MAX_DIMENSION):
        raise ValueError('Generated dimensions exceed limits')
    return width, height


def ppm(data):
    # dwebp emits a simple P6 header without comments.
    match = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n', data)
    if not match:
        raise ValueError('Unsupported decoded pixel buffer')
    width, height = map(int, match.groups())
    pixels = data[match.end():]
    if width * height > 40_000_000 or len(pixels) != width * height * 3:
        raise ValueError('Invalid or oversized decoded image')
    return width, height, pixels


def orient(width, height, pixels, value):
    if value == 1:
        return width, height, pixels
    ow, oh = (height, width) if value >= 5 else (width, height)
    output = bytearray(ow * oh * 3)
    for y in range(oh):
        for x in range(ow):
            sx, sy = {
                2: (width-1-x, y), 3: (width-1-x, height-1-y),
                4: (x, height-1-y), 5: (y, x), 6: (y, height-1-x),
                7: (width-1-y, height-1-x), 8: (width-1-y, x),
            }[value]
            start, target = (sy*width+sx)*3, (y*ow+x)*3
            output[target:target+3] = pixels[start:start+3]
    return ow, oh, bytes(output)


def png(width, height, pixels):
    # Fresh RGB PNG consisting only of structural and pixel chunks.
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind+payload))
    rows = b''.join(b'\0' + pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def prepare(root, manifest_path):
    item = manifest(manifest_path)
    root = Path(root).expanduser().resolve()
    source = root / item['source']
    if not source.resolve().is_relative_to(root):
        raise ValueError('Approved image escapes Bike Library root')
    if not source.is_file():
        raise ValueError('Missing approved Standert photograph')
    for tool in ('cwebp', 'dwebp'):
        if not shutil.which(tool):
            raise ValueError('Image build requires libwebp cwebp and dwebp')
    original = source.read_bytes()
    rotation = orientation(original)
    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        snapshot = temporary / 'source.jpg'
        snapshot.write_bytes(original)
        intermediate, decoded = temporary / 'decoded.webp', temporary / 'pixels.ppm'
        # Lossless intermediate preserves decoded JPEG pixels; no original binary
        # data or metadata enters the fresh RGB buffer.
        run(['cwebp', '-quiet', '-lossless', '-metadata', 'none', str(snapshot), '-o', str(intermediate)])
        run(['dwebp', '-quiet', str(intermediate), '-ppm', '-o', str(decoded)])
        width, height, pixels = orient(*ppm(decoded.read_bytes()), rotation)
        image, webp = temporary / 'pixels.png', temporary / 'hero.webp'
        image.write_bytes(png(width, height, pixels))
        if max(width, height) > MAX_DIMENSION:
            resize = ['-resize', str(MAX_DIMENSION if width >= height else 0), str(MAX_DIMENSION if height > width else 0)]
        else:
            resize = []
        run(['cwebp', '-quiet', '-q', QUALITY, '-m', '6', '-metadata', 'none', *resize, str(image), '-o', str(webp)])
        encoded = webp.read_bytes()
        dimensions = validate(encoded)
        if encoded == original:
            raise ValueError('Image was not freshly encoded')
        if abs(dimensions[0] / dimensions[1] - width / height) > 2 / dimensions[1]:
            raise ValueError('Generated image aspect ratio changed')
        run(['dwebp', '-quiet', str(webp), '-ppm', '-o', str(decoded)])
        if ppm(decoded.read_bytes())[:2] != dimensions:
            raise ValueError('Decoded output dimensions disagree')
    return item, encoded, dimensions
