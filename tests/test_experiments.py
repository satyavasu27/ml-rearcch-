import unittest
import numpy as np
import pandas as pd

from experiments.run_experiments import (ROOT, evaluate, features_and_labels,
                                         load_datasets, make_preprocessor, split_indices)


class ExperimentTests(unittest.TestCase):
    def test_load_and_targets(self):
        datasets = load_datasets()
        self.assertEqual([len(frame) for _, frame, _ in datasets], [1436, 1174, 204])
        self.assertEqual([int(features_and_labels(frame, target)[1].sum())
                          for _, frame, target in datasets], [81, 496, 57])
        for _, frame, target in datasets:
            x, y = features_and_labels(frame, target)
            self.assertNotIn(target, x.columns)
            self.assertNotIn('Unnamed: 0', x.columns)
            self.assertEqual(set(y), {0, 1})

    def test_no_duplicate_feature_vector_crosses_split(self):
        for _, frame, target in load_datasets():
            x, y = features_and_labels(frame, target)
            train, test = split_indices(x, y)
            train_rows = set(map(tuple, x.iloc[train].fillna('__MISSING__').to_numpy()))
            test_rows = set(map(tuple, x.iloc[test].fillna('__MISSING__').to_numpy()))
            self.assertFalse(train_rows & test_rows)
            self.assertEqual(len(train) + len(test), len(x))
            self.assertEqual(set(y.iloc[train]), {0, 1})
            self.assertEqual(set(y.iloc[test]), {0, 1})
            np.testing.assert_array_equal(split_indices(x, y)[1], test)

    def test_unseen_categories_and_missing_are_supported(self):
        x = pd.DataFrame({'numeric': [1., np.nan, 3.], 'category': ['a', 'b', None]})
        preprocess = make_preprocessor(x)
        preprocess.fit(x)
        transformed = preprocess.transform(pd.DataFrame({'numeric': [np.nan], 'category': ['unseen']}))
        self.assertTrue(np.isfinite(transformed).all())

    def test_metrics_and_threshold(self):
        result = evaluate(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.6, 0.4, 0.8]))
        self.assertEqual((result['tn'], result['fp'], result['fn'], result['tp']), (1, 1, 1, 1))
        self.assertEqual(result['recall'], 0.5)
        self.assertEqual(result['specificity'], 0.5)

    def test_reject_unexpected_labels(self):
        with self.assertRaises(ValueError):
            features_and_labels(pd.DataFrame({'x': [1, 2], 'label': ['negative', 'maybe']}), 'label')


if __name__ == '__main__':
    unittest.main()
