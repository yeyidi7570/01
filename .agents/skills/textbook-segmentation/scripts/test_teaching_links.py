"""Regression tests for Teaching Link direction and task scope."""

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
        validate_content(self.read_lesson(3))
        validate_content(self.read_lesson(12))

    def test_archived_same_module_links_require_compatibility_option(self):
        data = self.read_lesson(81)
        with self.assertRaisesRegex(ValueError, 'uses_as_material must cross Module or Subtask boundaries'):
            validate_content(data)
        validate_content(data, allow_legacy_material_links=True)

    def test_swapped_note_and_task_are_rejected(self):
        for number, suffix in [(3, ':link-compare-m02'), (12, ':link-m02-use-unit-note')]:
            data = self.read_lesson(number)
            link = next(link for link in data['lesson']['teaching_links'] if link['id'].endswith(suffix))
            link['from_id'], link['to_id'] = link['to_id'], link['from_id']
            data['lesson']['teaching_links'] = [link]
            with self.subTest(relationship=link['relationship']), self.assertRaisesRegex(
                ValueError, 'invalid teaching link direction'
            ):
                validate_content(data)

    def test_material_within_same_task_scope_is_rejected_at_any_depth(self):
        data = self.read_lesson(12)
        link = data['lesson']['teaching_links'][0]
        prefix = data['lesson']['id']
        scenarios = (
            ('m01', 'm01:formula-1'),
            ('m01:formula-1', 'm01'),
            ('m02', 'm02:part-a'),
            ('m02:part-a', 'm02'),
            ('m03', 'm03:area-chart'),
            ('m03:prompt', 'm03:countries-left'),
        )
        for origin, target in scenarios:
            with self.subTest(origin=origin, target=target), self.assertRaisesRegex(
                ValueError, 'uses_as_material must cross Module or Subtask boundaries'
            ):
                link.update(from_id=f'{prefix}:{origin}', to_id=f'{prefix}:{target}')
                validate_content(data)

    def test_material_can_cross_subtasks_of_one_module(self):
        data = self.read_lesson(84)
        link = data['lesson']['teaching_links'][0]
        link['relationship'] = 'uses_as_material'
        prefix = f'{data["lesson"]["id"]}:m03'
        graph = f'{prefix}:sub-Ә:route-graph'
        link['to_id'] = graph
        for origin in ('sub-Б', 'sub-Б:prompt'):
            with self.subTest(origin=origin):
                link['from_id'] = f'{prefix}:{origin}'
                validate_content(data)
        for origin in ('sub-Ә', 'sub-Ә:prompt'):
            with self.subTest(origin=origin), self.assertRaisesRegex(
                ValueError, 'uses_as_material must cross Module or Subtask boundaries'
            ):
                link['from_id'] = f'{prefix}:{origin}'
                validate_content(data)

    def test_material_outside_module_is_permitted(self):
        data = self.read_lesson(12)
        link = data['lesson']['teaching_links'][0]
        prefix = data['lesson']['id']
        link['from_id'] = f'{prefix}:m02:part-a'
        for target in ('m01', 'm03:area-chart', 'note-unit-equivalences', 'note-unit-equivalences:area-1', 'cover-words'):
            with self.subTest(target=target):
                link['to_id'] = f'{prefix}:{target}'
                validate_content(data)

    def test_support_from_note_content_to_module_content_is_permitted(self):
        data = self.read_lesson(12)
        prefix = data['lesson']['id']
        link = data['lesson']['teaching_links'][0]
        link.update(relationship='supports', from_id=f'{prefix}:note-unit-equivalences:area-1',
                    to_id=f'{prefix}:m02:part-a')
        validate_content(data)

    def test_page_and_self_references_are_rejected(self):
        for target in ('page', 'self'):
            data = self.read_lesson(12)
            link = data['lesson']['teaching_links'][0]
            link['to_id'] = data['pages'][0]['id'] if target == 'page' else link['from_id']
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'invalid teaching link'):
                validate_content(data)
