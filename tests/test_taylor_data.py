import csv
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TaylorDatasetTests(unittest.TestCase):
    def test_file_matches_publisher_and_has_expected_rows(self):
        path = ROOT / 'data/taylor/S1File.csv'
        digest = hashlib.md5()  # Check against Figshare's published checksum.
        with path.open('rb') as source:
            for block in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(block)
        self.assertEqual(digest.hexdigest(), '0e51d504f41b15944a02a8fd5dd81a17')
        with path.open(newline='', encoding='utf-8-sig') as source:
            reader = csv.DictReader(source)
            counts = {'yes': 0, 'no': 0}
            for row in reader:
                counts[row['UCX_abnormal']] += 1
        self.assertEqual(counts, {'yes': 18284, 'no': 62103})
        self.assertEqual(len(reader.fieldnames), 220)


if __name__ == '__main__':
    unittest.main()
