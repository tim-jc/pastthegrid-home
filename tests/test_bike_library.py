"""Synthetic source fixtures; no dependency on the private live checkout."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bike_library as bike
import build
from image_fixture import jpeg
from test_build import Page

MARKDOWN = '''# Standert Kreissäge RS

## Summary

| Item | Value |
|------|------:|
| Frame | Alloy & carbon |

# Drivetrain

## Groupset

- **Model:** Test <script>alert(1)</script>
- *Note* and `code`
- [ ] Check bearings

### Notes

- Two-line manufacturer note
  with continuation.

[See groupset](#groupset)
[Guide](https://example.org/guide?a=1&b=2)
[Invoice](../../documents/invoice.pdf)
[Unsafe](javascript:alert)
'''
CSV = '''work_date,bike,work_done,notes
2026-01-01,standert,Old work,Original note
2026-03-01,standert,Recent work,
2026-02-01,bokeh,Other bike,
,standert,Undated work,"not completed, retain wording"
'''


class BikeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.library = self.root / 'library'
        for name, value in ((bike.BIKE, MARKDOWN), (bike.LOG, CSV)):
            path = self.library / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        for name in bike.registry():
            if name != str(bike.BIKE):
                path = self.library / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# Fixture ' + path.stem + '\n\n## Summary\n\n| Item | Specification |\n|---|---|\n| Status | > TODO |\n')
        jpeg(self.library / 'photos/standert/standert.jpg')
        self.home = self.root / 'home'
        shutil.copytree(build.ROOT / 'config', self.home / 'config')
        shutil.copytree(build.ROOT / 'src', self.home / 'src')

    def test_loading_structure_and_escaping(self):
        body, toc, warnings, completed, planned = bike.load(self.library)
        self.assertIn('<h2 id="drivetrain">', body)
        self.assertIn('<h3 id="groupset">', body)
        self.assertIn('<th scope="col">Item</th>', body)
        self.assertIn('Alloy &amp; carbon', body)
        self.assertIn('&lt;script&gt;', body)
        self.assertNotIn('<script>', body)
        self.assertIn('<strong>Model:</strong>', body)
        self.assertIn('<em>Note</em>', body)
        self.assertIn('with continuation.', body)
        self.assertIn('Unchecked:', body)
        self.assertIn('href="#groupset"', body)
        self.assertIn('href="https://example.org/guide?a=1&amp;b=2"', body)
        self.assertNotIn('href="../../documents', body)
        self.assertNotIn('href="javascript:', body)
        self.assertEqual(len(warnings), 2)
        self.assertEqual([r['work_date'] for r in completed], ['2026-03-01', '2026-01-01'])
        self.assertEqual(len(planned), 1)
        self.assertEqual(planned[0]['notes'], 'not completed, retain wording')

    def test_source_errors(self):
        with self.assertRaisesRegex(ValueError, 'existing directory'):
            bike.load(self.root / 'missing')
        (self.library / bike.BIKE).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            bike.load(self.library)

    def test_dates_names_and_schema(self):
        for bad in ('2026-02-30', '01/03/2026', ' ', '2026-1-01'):
            with self.subTest(date=bad):
                (self.library / bike.LOG).write_text(CSV.replace('2026-01-01', bad))
                with self.assertRaisesRegex(ValueError, 'Invalid maintenance date'):
                    bike.load(self.library)
        (self.library / bike.LOG).write_text(CSV.replace(',standert,', ',Standert,', 1))
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            bike.load(self.library)
        (self.library / bike.LOG).write_text(CSV.replace('work_date', 'date'))
        with self.assertRaisesRegex(ValueError, 'schema'):
            bike.load(self.library)
        (self.library / bike.LOG).write_text(CSV + '2026-01-01,standert\n')
        with self.assertRaisesRegex(ValueError, 'Malformed'):
            bike.load(self.library)

    def test_unsupported_markdown_and_local_paths(self):
        for block in ('> > nested quote', '```\ncode\n```', '1. numbered', '###### Deep heading', '- [broken link]', '| A | B |\n|---|---|\n| only one |'):
            with self.subTest(block=block), self.assertRaises(ValueError):
                bike.markdown('# Standert Kreissäge RS\n\n' + block)
        with self.assertRaisesRegex(ValueError, 'filesystem path'):
            bike.markdown('# Standert Kreissäge RS\n\n/Users/person/private.txt')

    def test_empty_states(self):
        self.assertIn('No completed maintenance', bike.maintenance([], True))
        self.assertIn('No planned or undated work', bike.maintenance([], False))

    def test_build_modes_and_reference_graph(self):
        # Binary files in the external source must never cross the build boundary.
        (self.library / 'private.pdf').write_bytes(b'%PDF-private')
        (self.library / 'photo.jpg').write_bytes(b'private')
        before = {p.relative_to(self.library): p.read_bytes() for p in self.library.rglob('*') if p.is_file()}
        output = build.build(self.home, self.library)
        self.assertTrue((output / bike.PAGE).is_file())
        self.assertIn('bikes/', (output / 'index.html').read_text())
        self.assertIn('standert/kreissage_rs/index.html', (output / 'bikes/index.html').read_text())
        snapshot = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        self.assertEqual(set(map(str, snapshot)), set(build.FILES) | {str(Path(p).with_suffix('') / 'index.html') for p in bike.registry()} | {'bikes/index.html', 'assets/bikes/standert/hero.webp'})
        for name, data in snapshot.items():
            if name.suffix == '.webp':
                continue
            text = data.decode()
            self.assertNotIn(str(self.library), text)
            self.assertNotIn('BIKE_LIBRARY_ROOT', text)
            self.assertNotIn('file:', text)
            if name.suffix == '.html':
                page = Page()
                page.feed(text)
                self.assertEqual(len(page.ids - {None}), text.count(' id="'))
                for ref in page.refs:
                    url = urlsplit(ref)
                    if url.scheme:
                        self.assertEqual(url.hostname, 'example.org')
                    elif url.fragment:
                        self.assertIn(url.fragment, page.ids)
                    else:
                        self.assertTrue(((output / name).parent / url.path).exists(), ref)
        build.build(self.home, self.library)
        self.assertEqual(snapshot, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})
        self.assertEqual(before, {p.relative_to(self.library): p.read_bytes() for p in self.library.rglob('*') if p.is_file()})
        build.build(self.home)
        self.assertFalse((output / bike.PAGE).exists())
        self.assertIn('Forthcoming', (output / 'index.html').read_text())
        with self.assertRaises(ValueError):
            build.build(self.home, '')

    def test_command_environment_contract(self):
        # Run a copied entry point so subprocess output remains in the fixture.
        shutil.copytree(build.ROOT / 'scripts', self.home / 'scripts')
        env = dict(os.environ, BIKE_LIBRARY_ROOT=str(self.library))
        result = subprocess.run([sys.executable, 'scripts/build.py'], cwd=self.home, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / 'dist' / bike.PAGE).exists())
        env.pop('BIKE_LIBRARY_ROOT')
        result = subprocess.run([sys.executable, 'scripts/build.py'], cwd=self.home, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / 'dist' / bike.PAGE).exists())


if __name__ == '__main__':
    unittest.main()
