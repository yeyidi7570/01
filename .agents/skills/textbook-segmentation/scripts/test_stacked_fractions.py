"""Regression checks for structured fractions in a continuous problem."""

import json
from pathlib import Path
import unittest

from lesson import validate_content


class StackedFractionTests(unittest.TestCase):
    def read_lesson(self):
        root = Path(__file__).resolve().parents[4]
        book = root / 'structured_textbooks' / '数学2023_哈语学生_哈语教材（4-3）_АЛМАТЫКІТАП'
        return json.loads((book / '01_segmentation/lesson_083/content.json').read_bytes())

    def test_problem_preserves_fraction_order(self):
        data = self.read_lesson()
        ids, _ = validate_content(data)
        passage = ids[data['lesson']['id'] + ':m10:problem']
        fractions = [ids[oid]['fraction'] for oid in passage['content_order'] if 'fraction' in ids[oid]]
        self.assertEqual(
            [(f['numerator'], f['denominator'], f['notation']) for f in fractions],
            [(1, denominator, 'stacked') for denominator in (7, 6, 5, 4, 3, 2)],
        )

    def test_invalid_fraction_values_are_rejected(self):
        for denominator in (0, -1, True, '7'):
            with self.subTest(denominator=denominator):
                data = self.read_lesson()
                ids, _ = validate_content(data)
                ids[data['lesson']['id'] + ':m10:problem:fraction-1-7']['fraction']['denominator'] = denominator
                with self.assertRaisesRegex(ValueError, 'invalid stacked fraction'):
                    validate_content(data)
