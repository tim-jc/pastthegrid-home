"""Multi-bike edge cases use isolated fixtures, not the live private checkout."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bike_library as bikes
import build
import test_bike_library


class MultiBikeTests(unittest.TestCase):
    setUp = test_bike_library.BikeTests.setUp

    def test_discovery_and_index(self):
        found = bikes.discover(self.library)
        self.assertEqual(len(found), 8)
        self.assertEqual(len({str(bike['page']) for bike in found}), 8)
        self.assertEqual(next(b for b in found if b['source'] == bikes.BIKE)['title'], 'Standert Kreissäge RS')
        page = bikes.index((self.home / 'src/index.html').read_text(), found)
        for bike in found:
            self.assertIn(str(bike['page']).removeprefix('bikes/'), page)
        self.assertNotIn(str(self.library), page)
        # Supporting documents are deliberately outside the registry.
        support = self.library / 'bikes/standert/repaint/build-sheet.md'
        support.parent.mkdir()
        support.write_text('# Project\n\n1. Unsupported project text')
        self.assertEqual(len(bikes.discover(self.library)), 8)

    def test_different_structures_and_no_maintenance(self):
        path = self.library / 'bikes/nukeproof/cub_scout_14.md'
        path.write_text('# Child bike\n\n## Summary\n\n| Item | Value |\n|---|---|\n| Size | 14 inch |\n\n# Wheels\n\n## Wheelset\n\n### Rims\n\n#### Rim model\n\n> Technical note with **emphasis**.\n\n[Maker](https://example.org)\n[Diagram](../../photos/private.png)\n')
        template = (self.home / 'src/index.html').read_text()
        page, warnings, complete, planned = bikes.render(self.library, template, bike=path.relative_to(self.library))
        self.assertIn('<title>Child bike — Past the Grid Home</title>', page)
        self.assertIn('<h5 id="rim-model">Rim model</h5>', page)
        self.assertIn('<blockquote><p>Technical note with <strong>emphasis</strong>.', page)
        self.assertIn('No completed maintenance recorded.', page)
        self.assertIn('No planned or undated work recorded.', page)
        self.assertIn('href="../../">← Bike Library', page)
        self.assertEqual((complete, planned), (0,0))
        self.assertNotIn('hero.webp', page)
        self.assertNotIn('href="../../photos', page)

    def test_verified_maintenance_associations(self):
        log = self.library / bikes.LOG
        log.write_text('work_date,bike,work_done,notes\n2026-01-01,burls,Other completed,Keep note\n,standert,Planned standert,Unfinished\n2026-03-01,standert,New,\n2026-02-01,standert,Older,\n,big bro,Planned brother,\n')
        rows = bikes.maintenance_rows(self.library)
        _, _, _, completed, planned = bikes.load(self.library, rows=rows)
        self.assertEqual([row['work_done'] for row in completed], ['New','Older'])
        self.assertEqual([row['work_done'] for row in planned], ['Planned standert'])
        _, _, _, completed, planned = bikes.load(self.library, bike=Path('bikes/burls/burls_v2.md'), rows=rows)
        self.assertEqual(completed[0]['notes'], 'Keep note')
        self.assertEqual(planned, [])
        for key in ('unknown', 'Standert', ' big bro '):
            log.write_text('work_date,bike,work_done,notes\n,' + key + ',Work,\n')
            with self.assertRaisesRegex(ValueError, 'unmapped'):
                bikes.maintenance_rows(self.library)
        # Invalid dates on another bike must fail the whole build too.
        log.write_text('work_date,bike,work_done,notes\ninvalid,bokeh,Work,\n')
        with self.assertRaisesRegex(ValueError, 'Invalid maintenance date'):
            bikes.load(self.library)

    def test_registry_paths_and_mapping_collisions(self):
        path = self.root / 'mapping.json'
        for mapping in ({'../escape.md':None}, {'/absolute.md':None},
                        {'bikes/a/one.md':'same', 'bikes/b/two.md':'same'}, {}):
            path.write_text(json.dumps(mapping))
            with self.assertRaises(ValueError):
                bikes.registry(path)

    def test_source_escape_missing_and_failure_preserves_output(self):
        output = build.build(self.home, self.library)
        before = (output / bikes.PAGE).read_bytes()
        path = self.library / 'bikes/mason/bokeh.md'
        original = path.read_text()
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            build.build(self.home, self.library)
        self.assertEqual(before, (output / bikes.PAGE).read_bytes())
        outside = self.root / 'outside.md'
        outside.write_text(original)
        path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'within configured root'):
            bikes.discover(self.library)

    def test_anchor_uniqueness_and_unsupported_blocks(self):
        body, _, _ = bikes.markdown('# Test\n\n# Wheels\n\n## Rims\n\n## Rims\n\n## Completed maintenance\n')
        self.assertIn('id="rims-1"', body)
        self.assertIn('id="completed-maintenance-1"', body)
        for value in ('```code', '> > nested quote', '1. ordered', '###### Too deep'):
            with self.assertRaises(ValueError):
                bikes.markdown('# Test\n\n' + value)


if __name__ == '__main__':
    unittest.main()
