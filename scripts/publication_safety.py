"""Independent publication boundary. Does not import or invoke the application builder."""
import hashlib
from html.parser import HTMLParser
import json
import posixpath
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import subprocess
import tempfile
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
STATIC = {'index.html', 'assets/css/home.css', 'assets/identity/identity.css',
          'assets/identity/symbol.svg', 'assets/identity/favicon.svg'}
CONTROL = {'_headers': ROOT / 'release/headers.txt', '404.html': ROOT / 'release/404.html'}
PHOTO = 'assets/bikes/standert/hero.webp'
TYPES = {'.html': 'text/html', '.css': 'text/css', '.svg': 'image/svg+xml', '.webp': 'image/webp'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + '\n').encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON field')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def safe_path(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Unsafe relative path')
    if PurePosixPath(name).is_absolute() or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError('Unsafe relative path')
    return name


def policy(bikes_data, assets_data):
    bikes, assets = strict_json(bikes_data), strict_json(assets_data)
    if not isinstance(bikes, dict) or not bikes:
        raise ValueError('Missing bike source configuration')
    keys, outputs = set(), set()
    for name, key in bikes.items():
        safe_path(name)
        if not re.fullmatch(r'bikes/[a-z0-9_-]+/[a-z0-9_-]+\.md', name):
            raise ValueError('Invalid registered bike')
        output = name[:-3] + '/index.html'
        if output.casefold() in outputs:
            raise ValueError('Colliding output paths')
        outputs.add(output.casefold())
        if key is not None:
            if not isinstance(key, str) or not key.strip() or key in keys:
                raise ValueError('Invalid maintenance mapping')
            keys.add(key)
    if 'bikes/standert/kreissage_rs.md' not in bikes:
        raise ValueError('Required approved bike absent')
    if not isinstance(assets, dict) or set(assets) != {'standert-hero'}:
        raise ValueError('Unapproved image registry')
    item = assets['standert-hero']
    if not isinstance(item, dict) or set(item) != {'source','output','type','use','alt','caption'}:
        raise ValueError('Invalid approved asset configuration')
    if (item['source'],item['output'],item['type'],item['use']) != (
        'photos/standert/standert.jpg', PHOTO, 'image/jpeg', 'standert-hero'):
        raise ValueError('Asset approval changed; explicit review required')
    if not isinstance(item['alt'], str) or not item['alt'].strip() or not isinstance(item['caption'], str):
        raise ValueError('Invalid image description')
    expected = STATIC | set(CONTROL) | {'bikes/index.html', PHOTO} | outputs
    inputs = set(bikes) | {'workshop/maintenance_log.csv', item['source']}
    return expected, inputs


def inventory(tree):
    tree = Path(tree)
    if tree.is_symlink() or not tree.is_dir():
        raise ValueError('Publication tree must be a real directory')
    result = {}
    for path in tree.rglob('*'):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or (stat.S_ISREG(mode) and path.stat().st_nlink != 1) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError('Symlink or special object in publication')
        if stat.S_ISREG(mode):
            name = path.relative_to(tree).as_posix()
            safe_path(name)
            result[name] = path.read_bytes()
        elif not any(path.iterdir()):
            raise ValueError('Unexpected empty publication directory')
    return result


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.main, self.h1 = set(), [], False, False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script','style','iframe','object','embed','form','base','video','audio','source'}:
            raise ValueError('Unapproved active HTML')
        if any(k.startswith('on') or k in ('style','srcset','srcdoc') for k in attrs):
            raise ValueError('Unapproved HTML attributes')
        if tag == 'meta' and attrs.get('http-equiv','').lower() == 'refresh':
            raise ValueError('Unapproved HTML redirect')
        if tag == 'link' and attrs.get('rel') not in ('stylesheet','icon'):
            raise ValueError('Unapproved resource link')
        if tag == 'img' and attrs.get('src') is None:
            raise ValueError('Image without source')
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                raise ValueError('Duplicate HTML anchor')
            self.ids.add(attrs['id'])
        self.main |= tag == 'main'
        self.h1 |= tag == 'h1'
        for key in ('href','src'):
            if key in attrs:
                self.refs.append((tag, key, attrs[key]))

    handle_startendtag = handle_starttag


def webp(data):
    # Separate from image_assets.validate, inspect actual output bytes and decode.
    if len(data) < 30 or data[:4] != b'RIFF' or data[8:16] != b'WEBPVP8 ':
        raise ValueError('Unapproved image encoding/metadata')
    size = int.from_bytes(data[16:20], 'little')
    if int.from_bytes(data[4:8], 'little')+8 != len(data) or size+20+size%2 != len(data):
        raise ValueError('Image contains metadata, trailing data or extra chunks')
    if data[23:26] != b'\x9d\x01\x2a':
        raise ValueError('Invalid VP8 image')
    width, height = (int.from_bytes(data[i:i+2], 'little') & 0x3fff for i in (26,28))
    if not (0 < width <= 1600 and 0 < height <= 1600):
        raise ValueError('Invalid image dimensions')
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)/'image.webp'; path.write_bytes(data)
        result = subprocess.run(['dwebp','-quiet',str(path),'-ppm','-o',str(Path(temp)/'pixels.ppm')], capture_output=True)
        if result.returncode:
            raise ValueError('Output image cannot be decoded')
        pixels = (Path(temp)/'pixels.ppm').read_bytes()
        match = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n', pixels)
        if not match or tuple(map(int,match.groups())) != (width,height):
            raise ValueError('Output image dimensions disagree')
    return width, height


def validate(tree, bikes_data, assets_data, declared=None):
    expected, _ = policy(bikes_data, assets_data)
    files = inventory(tree)
    if set(files) != expected:
        raise ValueError('Publication inventory does not match approved policy')
    documents, records = {}, []
    leak = re.compile(rb'(?:file://|/(?:Users|home|private|var/folders)/|BIKE_LIBRARY_ROOT|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:CLOUDFLARE_API_TOKEN|CF_ACCESS_CLIENT_SECRET)\s*[=:])')
    for name, data in sorted(files.items()):
        if not data or len(data) > 25*1024*1024:
            raise ValueError('Empty or oversized publication file')
        if name != PHOTO and leak.search(data):
            raise ValueError('Local path or credential signature in publication')
        if name in CONTROL:
            if data != CONTROL[name].read_bytes():
                raise ValueError('Invalid hosting control or error file')
        suffix = PurePosixPath(name).suffix
        media = 'text/plain' if name == '_headers' else TYPES[suffix]
        if suffix == '.html':
            text = data.decode('utf-8')
            if '<!doctype html>' not in text.lower():
                raise ValueError('Required HTML document missing')
            doc = Document();doc.feed(text);doc.close()
            if not doc.main or not doc.h1:
                raise ValueError('Incomplete or placeholder page')
            documents[name] = doc
        elif suffix == '.css':
            if re.search(r'@import|url\s*\(|expression\s*\(', data.decode(), re.I):
                raise ValueError('External or active CSS')
        elif suffix == '.svg':
            svg = ET.fromstring(data)
            if svg.tag != '{http://www.w3.org/2000/svg}svg':
                raise ValueError('Invalid SVG')
            for element in svg.iter():
                if element.tag.split('}')[-1] in {'script','style','image','foreignObject','use','animate','set'} or any(k.lower().startswith('on') or k.endswith('href') for k in element.attrib):
                    raise ValueError('Active SVG')
                if any(re.search(r'url\s*\(',value,re.I) for value in element.attrib.values()):
                    raise ValueError('External SVG resource')
        elif suffix == '.webp':
            webp(data)
        records.append({'path':name,'size':len(data),'media_type':media,'sha256':digest(data)})
    for name, doc in documents.items():
        for tag, key, ref in doc.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                if tag != 'a' or key != 'href' or url.scheme not in ('https','http') or not url.netloc or url.username or url.password:
                    raise ValueError('Unapproved external resource')
                continue
            decoded = unquote(url.path)
            if '\\' in decoded or any(p == '..' for p in decoded.split('/')) and name == 'index.html':
                raise ValueError('Unsafe internal reference')
            target = posixpath.normpath(decoded.lstrip('/') if decoded.startswith('/') else posixpath.join(posixpath.dirname(name), decoded)) if decoded else name
            if target.startswith('../'):
                raise ValueError('Link escapes publication')
            if decoded.endswith('/') or target == '.':
                target = ('' if target == '.' else target.rstrip('/')+'/')+'index.html'
            if target not in files:
                raise ValueError('Broken internal reference')
            if url.fragment and (target not in documents or unquote(url.fragment) not in documents[target].ids):
                raise ValueError('Broken fragment reference')
    # A placeholder cannot satisfy configured Home->library navigation.
    if not any(ref == 'bikes/' for _,_,ref in documents['index.html'].refs):
        raise ValueError('Placeholder homepage is not a release')
    if declared is not None and records != declared:
        raise ValueError('Publication bytes differ from frozen manifest')
    return records
