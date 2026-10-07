"""Photographer datasets remain editable, unambiguous and confined to images."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from photo_credits import PhotoCreditError, credit_for_image, load_photo_credits


class PhotoCreditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'assets/docs').mkdir(parents=True)
        (self.root / 'assets/images/lab').mkdir(parents=True)
        (self.root / 'assets/images/team').mkdir()
        (self.root / 'assets/images/lab/chip.webp').write_bytes(b'image')
        (self.root / 'assets/images/team/person.jpg').write_bytes(b'image')
        self.records = [
            {'id': 'lab', 'label': 'Laboratory photographs', 'photographer': 'Alex Example',
             'url': 'https://example.org/alex', 'paths': ['assets/images/lab/chip.webp']},
            {'id': 'team', 'label': 'Team portraits', 'photographer': 'Sam Example',
             'url': '', 'paths': ['assets/images/team']},
        ]

    def load(self, records=None):
        source = self.root / 'assets/docs/photo-credits.json'
        source.write_text(json.dumps({'datasets': self.records if records is None else records}), encoding='utf-8')
        return load_photo_credits(self.root)

    def test_file_matching_returns_editable_dataset(self):
        datasets = self.load()
        credit = credit_for_image('assets/images/lab/chip.webp', datasets)
        self.assertEqual(credit['photographer'], 'Alex Example')
        self.assertEqual(credit['url'], 'https://example.org/alex')
        self.records[0]['photographer'] = 'Another Photographer'
        self.assertEqual(credit_for_image('assets/images/lab/chip.webp', self.load())['photographer'], 'Another Photographer')

    def test_directory_inherits_for_new_and_nested_portraits(self):
        datasets = self.load()
        (self.root / 'assets/images/team/new.jpg').write_bytes(b'new image')
        for image in ('person.jpg', 'new.jpg', 'future/portrait.jpg'):
            self.assertEqual(credit_for_image('assets/images/team/' + image, datasets)['id'], 'team')
        self.assertIsNone(credit_for_image('assets/images/team-other/person.jpg', datasets))
        self.assertIsNone(credit_for_image('assets/images/team', datasets))
        self.assertIsNone(credit_for_image('assets/images/lab/chip.webp/another.jpg', datasets))

    def test_unknown_author_and_external_images_have_no_credit(self):
        self.records[0]['photographer'] = '   '
        self.records[0]['url'] = ''
        datasets = self.load()
        for image in ('assets/images/lab/chip.webp', 'assets/images/lab/other.webp',
                      'https://example.org/person.jpg', '//example.org/person.jpg', '//[invalid',
                      'assets/images/team/../../../secret.jpg', ''):
            self.assertIsNone(credit_for_image(image, datasets), image)

    def test_whitespace_is_trimmed_and_empty_datasets_are_allowed(self):
        self.records[0]['photographer'] = '  Alex Example  '
        self.records[0]['url'] = '  https://example.org/alex  '
        self.records[0]['affiliation'] = '  Example Institute  '
        loaded = self.load()
        self.assertEqual(loaded[0]['photographer'], 'Alex Example')
        self.assertEqual(loaded[0]['url'], 'https://example.org/alex')
        self.assertEqual(loaded[0]['affiliation'], 'Example Institute')
        self.records[0]['affiliation'] = ''
        self.assertEqual(self.load()[0]['affiliation'], '')
        self.assertEqual(self.load([]), [])

    def test_invalid_fields_report_the_dataset_location(self):
        examples = [('id', 'Lab Photos'), ('label', ''), ('photographer', None), ('affiliation', None),
                    ('url', False), ('paths', []), ('paths', 'assets/images/lab/chip.webp')]
        for field, invalid in examples:
            with self.subTest(field=field, invalid=invalid):
                records = deepcopy(self.records)
                records[0][field] = invalid
                with self.assertRaisesRegex(PhotoCreditError, rf'photo-credits\.json\.datasets\[0\]\.{field}'):
                    self.load(records)

    def test_duplicate_ids_and_overlapping_mappings_are_rejected(self):
        self.records[1]['id'] = 'lab'
        with self.assertRaisesRegex(PhotoCreditError, 'duplicate dataset ID'):
            self.load()
        self.records[1]['id'] = 'team'
        self.records[1]['paths'] = ['assets/images/lab/chip.webp']
        with self.assertRaisesRegex(PhotoCreditError, 'overlaps dataset "lab"'):
            self.load()
        self.records[1]['paths'] = ['assets/images/lab']
        with self.assertRaisesRegex(PhotoCreditError, 'overlaps dataset "lab"'):
            self.load()
        self.records.reverse()
        with self.assertRaisesRegex(PhotoCreditError, 'overlaps dataset "team"'):
            self.load()

    def test_directory_ancestors_are_ambiguous_even_when_blank(self):
        self.records[0]['photographer'] = ''
        self.records[0]['paths'] = ['assets/images']
        with self.assertRaisesRegex(PhotoCreditError, 'overlaps dataset "lab"'):
            self.load()

    def test_missing_and_unsafe_paths_are_rejected(self):
        cases = [('assets/images/missing.webp', 'does not exist'),
                 ('/assets/images/lab/chip.webp', 'without traversal'),
                 ('assets/images/../docs/photo-credits.json', 'without traversal'),
                 ('assets/docs/photo-credits.json', 'inside assets/images'),
                 ('https://example.org/chip.webp', 'inside assets/images'),
                 ('assets/images/lab/*.webp', 'does not exist')]
        for path, message in cases:
            with self.subTest(path=path):
                records = deepcopy(self.records)
                records[0]['paths'] = [path]
                with self.assertRaisesRegex(PhotoCreditError, message):
                    self.load(records)

    def test_symlinks_cannot_escape_the_image_directory(self):
        outside = self.root / 'outside.jpg'
        outside.write_bytes(b'outside image')
        (self.root / 'assets/images/lab/escape.jpg').symlink_to(outside)
        self.records[0]['paths'] = ['assets/images/lab/escape.jpg']
        with self.assertRaisesRegex(PhotoCreditError, 'symlink escapes assets/images'):
            self.load()
        self.records[0]['paths'] = ['assets/images/lab']
        with self.assertRaisesRegex(PhotoCreditError, 'symlink escapes assets/images'):
            self.load()

    def test_optional_links_require_safe_https_urls(self):
        without_link = deepcopy(self.records)
        without_link[0].pop('url')
        self.assertEqual(self.load(without_link)[0]['url'], '')
        for invalid in ('http://example.org', 'javascript:alert(1)', '//example.org',
                        'https://', 'https://example.org/a b', 'https://user:password@example.org',
                        'https://[invalid', 'https://example.org:invalid-port'):
            with self.subTest(url=invalid):
                records = deepcopy(self.records)
                records[0]['url'] = invalid
                with self.assertRaisesRegex(PhotoCreditError, 'url: use a full HTTPS URL'):
                    self.load(records)

    def test_json_errors_and_missing_files_are_actionable(self):
        source = self.root / 'assets/docs/photo-credits.json'
        source.write_text('{\n  broken json', encoding='utf-8')
        with self.assertRaisesRegex(PhotoCreditError, r'photo-credits\.json:2:'):
            load_photo_credits(self.root)
        source.write_text('{"datasets": {}}', encoding='utf-8')
        with self.assertRaisesRegex(PhotoCreditError, 'datasets: expected an array'):
            load_photo_credits(self.root)
        source.unlink()
        with self.assertRaisesRegex(PhotoCreditError, 'photo-credits.json: cannot read'):
            load_photo_credits(self.root)

    def test_repository_configuration_uses_the_supplied_credits(self):
        datasets = load_photo_credits(Path(__file__).resolve().parents[1])
        self.assertEqual([dataset['id'] for dataset in datasets], ['spirs', 'photonics', 'group', 'team'])
        self.assertEqual([(dataset['photographer'], dataset.get('affiliation', '')) for dataset in datasets[:2]],
                         [('Juan Carlos Ortiz', 'CSIC Andalucía'), ('Sofía Villar', 'IMSE-CNM')])
        self.assertTrue(all(dataset['photographer'] == '' for dataset in datasets[2:]))
        self.assertTrue(all(dataset['url'] == '' for dataset in datasets))


if __name__ == '__main__':
    unittest.main()
