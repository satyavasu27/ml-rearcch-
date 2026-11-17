import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from run_selected import TAYLOR_FEATURES, TRANG_FEATURES, load_data, split_data


class SelectedExperimentsTest(unittest.TestCase):
    def test_feature_allowlists_exclude_outcomes_and_identifiers(self):
        self.assertFalse({'PATID', 'ID', 'UCX_abnormal', 'UTI_diag', 'abx'} & set(TAYLOR_FEATURES))
        self.assertFalse({'URCULBAC', 'URCUL_pos_yn'} & set(TRANG_FEATURES))

    def test_group_split_keeps_visits_of_same_patient_together(self):
        groups = pd.Series(np.repeat(np.arange(100), 3))
        x = pd.DataFrame({'x': np.arange(300)})
        y = pd.Series(np.tile([0, 1, 0], 100))
        train, test = split_data(x, y, groups)
        self.assertFalse(set(groups.iloc[train]) & set(groups.iloc[test]))
        self.assertEqual(len(train) + len(test), len(y))
        np.testing.assert_array_equal(train, split_data(x, y, groups)[0])

    def test_missing_file_is_clear(self):
        with self.assertRaisesRegex(FileNotFoundError, 'missing'):
            load_data('trang', '/does/not/exist.csv')

    def test_taylor_labels_and_patient_groups(self):
        x, y, groups, _ = load_data('taylor')
        self.assertEqual(len(y), 80387)
        self.assertEqual(int(y.sum()), 18284)
        self.assertEqual(groups.nunique(), 55365)
        self.assertEqual(list(x.columns), TAYLOR_FEATURES)


if __name__ == '__main__':
    unittest.main()
