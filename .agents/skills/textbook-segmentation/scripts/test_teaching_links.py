"""Regression tests for Teaching Link endpoints in archived lessons."""

import json
import unittest
from pathlib import Path

from lesson import validate_content


class TeachingLinkDirectionTests(unittest.TestCase):
    def read_lesson(self, number):
        root = Path(__file__).resolve().parents[4]
        return json.loads(next(
            (root / 'structured_textbooks').glob(
                f'数学2023*/01_segmentation/lesson_{number:03}/content.json'
            )
        ).read_bytes())

    def test_archived_relationships(self):
        for number in (3, 12):
            with self.subTest(lesson=number):
                validate_content(self.read_lesson(number))

    def test_swapped_note_and_task_are_rejected(self):
        for number, suffix in [(3, ':link-compare-m02'), (12, ':link-m02-use-unit-note')]:
            data = self.read_lesson(number)
            link = next(link for link in data['lesson']['teaching_links'] if link['id'].endswith(suffix))
            link['from_id'], link['to_id'] = link['to_id'], link['from_id']
            with self.subTest(relationship=link['relationship']), self.assertRaisesRegex(
                ValueError, 'invalid teaching link direction'
            ):
                validate_content(data)

    def test_page_and_self_references_are_rejected(self):
        for target in ('page', 'self'):
            data = self.read_lesson(12)
            link = data['lesson']['teaching_links'][0]
            link['to_id'] = data['pages'][0]['id'] if target == 'page' else link['from_id']
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'invalid teaching link'):
                validate_content(data)
