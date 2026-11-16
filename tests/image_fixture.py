"""Generate synthetic JPEG pixels and explicit EXIF/GPS/thumbnail/XMP/comment data."""
from pathlib import Path
import struct
import subprocess


def jpeg(path, width=40, height=20, orientation=1):
    # Four colour quadrants allow orientation to be checked from decoded pixels.
    pixels = b''.join(bytes((230 if x < width//2 else 15, 230 if y < height//2 else 15, 25))
                      for y in range(height) for x in range(width))
    ppm = f'P6\n{width} {height}\n255\n'.encode() + pixels
    encoded = subprocess.run(['cjpeg', '-quality', '95'], input=ppm, capture_output=True, check=True).stdout
    # IFD0 orientation and GPS pointer, GPS IFD, IFD1 thumbnail pointer/length.
    gps_offset, thumbnail_ifd, thumbnail_bytes, latitude, longitude = 38, 92, 122, 126, 150
    tiff = (b'II' + struct.pack('<HIH', 42, 8, 2)
            + struct.pack('<HHIH', 0x112, 3, 1, orientation) + b'\0\0'
            + struct.pack('<HHII', 0x8825, 4, 1, gps_offset) + struct.pack('<I', thumbnail_ifd)
            + struct.pack('<H', 4)
            + struct.pack('<HHI4s', 1, 2, 2, b'N\0\0\0')
            + struct.pack('<HHII', 2, 5, 3, latitude)
            + struct.pack('<HHI4s', 3, 2, 2, b'E\0\0\0')
            + struct.pack('<HHII', 4, 5, 3, longitude) + b'\0'*4
            + struct.pack('<H', 2) + struct.pack('<HHII', 0x201, 4, 1, thumbnail_bytes)
            + struct.pack('<HHII', 0x202, 4, 1, 4) + b'\0'*4 + b'\xff\xd8\xff\xd9'
            + struct.pack('<IIIIII', 1, 1, 2, 1, 3, 1)
            + struct.pack('<IIIIII', 4, 1, 5, 1, 6, 1))
    def segment(marker, data):
        return b'\xff' + bytes([marker]) + struct.pack('>H', len(data)+2) + data
    metadata = segment(0xe1, b'Exif\0\0' + tiff)
    metadata += segment(0xe1, b'http://ns.adobe.com/xap/1.0/\0<x:xmpmeta>synthetic-private</x:xmpmeta>')
    metadata += segment(0xfe, b'synthetic-private-comment')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded[:2] + metadata + encoded[2:])
    return path
