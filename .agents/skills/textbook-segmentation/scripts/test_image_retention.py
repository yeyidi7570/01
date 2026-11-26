"""Check the image retention decisions for part 3, lesson 081."""

from pathlib import Path
import unittest

from lesson import read_package, validate_content


class ImageRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[4]
        book = root / 'structured_textbooks' / '数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП'
        review = book / '02_segmentation_review/lesson_081'
        _, cls.data, _, cls.assets, cls.history, _, _ = read_package(review / 'revision_3')
        _, cls.previous, _, cls.previous_assets, _, _, _ = read_package(review / 'revision_2')
        cls.ids, _ = validate_content(cls.data)
        cls.previous_ids, _ = validate_content(cls.previous)
        cls.prefix = cls.data['lesson']['id'] + ':'

    def object(self, suffix):
        return self.ids[self.prefix + suffix]

    def test_keep_task_inputs_and_instructional_diagrams(self):
        images = {key.removeprefix(self.prefix) for key, obj in self.ids.items()
                  if obj.get('type') == 'informative_image'}
        self.assertEqual(images, {
            'm01:orchard',
            'm04:weather-chart',
            'recall:price',
            'recall:materials',
            'recall:mass',
            'recall:distance',
            'recall:area',
            'recall:work',
        })
        pairs = self.object('m01:orchard')['structured_description']['relations']
        self.assertEqual(
            [(self.ids[pair['word_id']]['text_kk'], self.ids[pair['formula_id']]['text_kk']) for pair in pairs],
            [('жемісі', '9 100 · 30'), ('жеріне', '2 500 · 30'), ('қарай', '2 000 · 50')],
        )
        weather = self.object('m04:weather-chart')
        self.assertEqual(weather, self.previous_ids[weather['id']])

    def test_exclude_redundant_artwork_and_keep_full_scans(self):
        for suffix in ('m05:milk-chart', 'orientation:avatar-caption'):
            with self.subTest(suffix=suffix):
                oid = self.prefix + suffix
                self.assertNotIn(oid, self.ids)
                self.assertNotIn(oid + ':crop', self.assets)
                self.assertFalse(any(s['object_id'] == oid for s in self.data['ocr_suggestions']))

        crop = self.object('m01:orchard')['crop_asset_id']
        old_box = self.previous['crop_assets'][crop]['bbox']
        new_box = self.data['crop_assets'][crop]['bbox']
        self.assertGreater(new_box[1], old_box[1])
        for pair in self.object('m01:orchard')['elements']:
            left, top, right, bottom = pair['page_refs'][0]['bbox']
            self.assertTrue(new_box[0] <= left < right <= new_box[2])
            self.assertTrue(new_box[1] <= top < bottom <= new_box[3])

        self.assertEqual(self.data['pages'], self.previous['pages'])
        self.assertEqual(self.data['source'], self.previous['source'])
        for page in self.data['pages']:
            scan = page['scan_asset_id']
            self.assertEqual(self.assets[scan], self.previous_assets[scan])

    def test_retain_task_and_review_history(self):
        for suffix in ('m05:prompt', 'm05:problem', 'closing:prompt'):
            obj = self.object(suffix)
            self.assertEqual(obj, self.previous_ids[obj['id']])
        self.assertEqual(self.data['lesson']['teaching_links'], self.previous['lesson']['teaching_links'])

        revision = self.data['review_revision']
        self.assertEqual(len(self.history['records']), 121)
        ancestor = revision['ancestors'][self.history['data_version']]
        for suffix in ('m01:orchard', 'm05:milk-chart', 'orientation:avatar-caption'):
            oid = self.prefix + suffix
            self.assertNotIn(oid, ancestor['equivalent_object_ids'])
            self.assertTrue(any(r['object_id'] == oid for r in self.history['records']))
        self.assertIn(self.prefix + 'm04:weather-chart', ancestor['equivalent_object_ids'])
