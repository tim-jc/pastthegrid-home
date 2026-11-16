import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import image_assets as images
import bike_library
import build
from image_fixture import jpeg


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.library = self.root / 'library'
        self.source = jpeg(self.library / 'photos/standert/standert.jpg')
        self.path = self.root / 'assets.json'
        self.config = json.loads((build.ROOT / 'config/assets.json').read_text())
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.config))

    def test_manifest_rejections(self):
        original = self.config['standert-hero']['source']
        for value in ('/tmp/source.jpg', '../source.jpg', 'photos/../../source.jpg',
                      'photos/*.jpg', 'photos/a?.jpg', 'C:\\image.jpg', 'photos/a.gif'):
            with self.subTest(path=value):
                self.config['standert-hero']['source'] = value
                self.save()
                with self.assertRaises(ValueError):
                    images.manifest(self.path)
        self.config['standert-hero']['source'] = original
        self.config['unapproved'] = dict(self.config['standert-hero'])
        self.save()
        with self.assertRaises(ValueError):
            images.manifest(self.path)
        del self.config['unapproved']
        self.config['standert-hero']['output'] = 'extra.webp'
        self.save()
        with self.assertRaises(ValueError):
            images.manifest(self.path)

    def test_missing_symlink_and_wrong_format(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing approved'):
            images.prepare(self.library, self.path)
        outside = jpeg(self.root / 'outside.jpg')
        self.source.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            images.prepare(self.library, self.path)
        self.source.unlink()
        self.source.write_bytes(b'GIF89a')
        with self.assertRaisesRegex(ValueError, 'not a JPEG'):
            images.prepare(self.library, self.path)

    def test_fresh_metadata_free_reproducible_encoding(self):
        before = self.source.read_bytes()
        self.assertIn(b'Exif\0\0', before)
        self.assertIn(b'xmpmeta', before)
        self.assertIn(b'synthetic-private-comment', before)
        item, data, dimensions = images.prepare(self.library, self.path)
        self.assertEqual(dimensions, (40, 20))
        self.assertEqual(images.validate(data), dimensions)
        self.assertNotEqual(before, data)
        for marker in (b'EXIF', b'XMP ', b'ICCP', b'Exif', b'synthetic-private', b'http://'):
            self.assertNotIn(marker, data)
        self.assertEqual(before, self.source.read_bytes())
        self.assertEqual(data, images.prepare(self.library, self.path)[1])
        # Actual encoded output rejects even unknown metadata and trailing bytes.
        for kind in (b'EXIF', b'XMP ', b'ICCP', b'JUNK', b'ANIM'):
            dirty = data + kind + struct.pack('<I', 4) + b'test'
            dirty = dirty[:4] + struct.pack('<I', len(dirty)-8) + dirty[8:]
            with self.assertRaisesRegex(ValueError, 'metadata'):
                images.validate(dirty)
        with self.assertRaises(ValueError):
            images.validate(data + b'comment')

    def test_orientation_and_resize(self):
        jpeg(self.source, width=100, height=40, orientation=6)
        self.assertEqual(images.orientation(self.source.read_bytes()), 6)
        _, encoded, dimensions = images.prepare(self.library, self.path)
        self.assertEqual(dimensions, (40, 100))
        path = self.root / 'result.webp'
        decoded = self.root / 'result.ppm'
        path.write_bytes(encoded)
        images.run(['dwebp', '-quiet', str(path), '-ppm', '-o', str(decoded)])
        width, height, pixels = images.ppm(decoded.read_bytes())
        # Original bottom-left (red, dark green) becomes top-left after 90 CW.
        r, g, b = pixels[(5*width+5)*3:(5*width+5)*3+3]
        self.assertGreater(r, 150)
        self.assertLess(g, 80)
        jpeg(self.source, width=1800, height=900)
        _, data, dimensions = images.prepare(self.library, self.path)
        self.assertEqual(dimensions, (1600, 800))

    def test_all_orientation_pixel_mappings(self):
        pixels = bytes(v for i in range(1, 7) for v in (i, i, i))
        expected = {1:[1,2,3,4,5,6], 2:[2,1,4,3,6,5], 3:[6,5,4,3,2,1],
                    4:[5,6,3,4,1,2], 5:[1,3,5,2,4,6], 6:[5,3,1,6,4,2],
                    7:[6,4,2,5,3,1], 8:[2,4,6,1,3,5]}
        for orientation, values in expected.items():
            width, height, data = images.orient(2, 3, pixels, orientation)
            self.assertEqual(list(data[::3]), values)
            self.assertEqual((width,height), (3,2) if orientation >= 5 else (2,3))

    def test_approved_markdown_link_maps_to_displayed_figure(self):
        body, toc, warnings = bike_library.markdown(
            '# Standert Kreissäge RS\n\n![Unapproved](../../photos/standert/other.jpg)')
        self.assertNotIn('<img', body)
        self.assertTrue(warnings)
        # Owner-applied canonical link remains text in generic parser; only the
        # configured Standert renderer maps the exact approved reference.
        record = self.library / bike_library.BIKE
        record.parent.mkdir(parents=True)
        record.write_text('# Standert Kreissäge RS\n\n![Bike](../../photos/standert/standert.jpg)')
        log = self.library / bike_library.LOG
        log.parent.mkdir(parents=True)
        log.write_text('work_date,bike,work_done,notes\n')
        hero = images.prepare(self.library, self.path)
        page, warnings, _, _ = bike_library.render(self.library, (build.ROOT / 'src/index.html').read_text(), hero)
        self.assertIn('href="#standert-photograph"', page)
        self.assertIn('id="standert-photograph"', page)
        self.assertNotIn('image not included', page)
        self.assertIn('width="40" height="20"', page)
        self.assertIn('../../../assets/bikes/standert/hero.webp', page)


if __name__ == '__main__':
    unittest.main()
