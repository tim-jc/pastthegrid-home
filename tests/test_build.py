"""Checks for the output boundary and the complete offline reference graph."""
import hashlib
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'scripts/build.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
EXPECTED = {'index.html', 'assets/css/home.css', 'assets/identity/identity.css',
            'assets/identity/symbol.svg', 'assets/identity/favicon.svg'}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.tags = [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        self.ids.add(attrs.get('id'))
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])
        if tag == 'link':
            assert attrs.get('rel') in ('stylesheet', 'icon')


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'src', self.root / 'src')

    def test_build_allowlist_and_determinism(self):
        (self.root / 'src/unselected.txt').write_text('not publishable')
        output = module.build(self.root)
        (output / 'stale.txt').write_text('remove on rebuild')
        module.build(self.root)
        actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
        self.assertEqual(actual, EXPECTED)
        before = {name: (output / name).read_bytes() for name in EXPECTED}
        module.build(self.root)
        self.assertEqual(before, {name: (output / name).read_bytes() for name in EXPECTED})

    def test_missing_asset_preserves_previous_build(self):
        output = module.build(self.root)
        (self.root / 'src/assets/identity/symbol.svg').unlink()
        with self.assertRaisesRegex(FileNotFoundError, 'Missing required source asset'):
            module.build(self.root)
        self.assertTrue((output / 'index.html').is_file())

    def test_symlink_rejected(self):
        path = self.root / 'src/index.html'
        path.unlink()
        path.symlink_to(ROOT / 'src/index.html')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            module.build(self.root)

    def test_offline_references(self):
        output = module.build(self.root)
        page = Page()
        page.feed((output / 'index.html').read_text())
        self.assertNotIn('script', page.tags)
        self.assertNotIn('iframe', page.tags)
        for ref in page.refs:
            url = urlsplit(ref)
            self.assertFalse(url.scheme or url.netloc or ref.startswith('/'), ref)
            if url.fragment:
                self.assertIn(url.fragment, page.ids)
            if url.path:
                self.assertTrue((output / url.path).exists(), ref)
        for name in EXPECTED:
            text = (output / name).read_text()
            if name.endswith('.css'):
                self.assertNotRegex(text, r'@import|url\s*\(')
            if name.endswith('.svg'):
                svg = ET.fromstring(text)
                for element in svg.iter():
                    self.assertNotIn(element.tag.split('}')[-1], ('script', 'image', 'foreignObject'))
                    self.assertFalse(any(k.endswith('href') for k in element.attrib))

    def test_identity_checksums_documented(self):
        provenance = (ROOT / 'docs/asset-provenance.md').read_text()
        for path in (ROOT / 'src/assets/identity').iterdir():
            self.assertIn(hashlib.sha256(path.read_bytes()).hexdigest(), provenance)

    def test_output_and_secrets_ignored(self):
        for name in ('dist/index.html', '.env', '.env.local'):
            result = subprocess.run(['git', 'check-ignore', '--quiet', name], cwd=ROOT)
            self.assertEqual(result.returncode, 0, name)
        tracked = subprocess.check_output(['git', 'ls-files', 'dist'], cwd=ROOT, text=True)
        self.assertEqual(tracked, '')


if __name__ == '__main__':
    unittest.main()
