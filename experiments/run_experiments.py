#!/usr/bin/env python3
"""Run fixed, paper-inspired models on three non-comparable data cohorts."""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
SEED = 42


def load_datasets(root=ROOT):
    original = pd.read_csv(root / 'urinalysis_tests.csv')
    if 'Unnamed: 0' not in original or 'Diagnosis' not in original:
        raise ValueError('Expected an index and Diagnosis column in the original dataset')
    # The source index is not a predictive feature.
    original = original.drop(columns=['Unnamed: 0'])
    elderly = pd.read_csv(root / 'data/flowuti/Elderly.csv', index_col=0)
    neonates = pd.read_csv(root / 'data/flowuti/Neonates.csv', sep=';')
    return [('Original urinalysis', original, 'Diagnosis'),
            ('FlowUTI elderly', elderly, 'Culture'),
            ('FlowUTI neonates', neonates, 'Culture')]


def features_and_labels(frame, target):
    labels = frame[target].astype(str).str.strip().str.upper()
    if set(labels) != {'POSITIVE', 'NEGATIVE'}:
        raise ValueError(f'Unexpected labels in {target}: {sorted(set(labels))}')
    x = frame.drop(columns=[target]).copy()
    if x.empty or x.columns.duplicated().any():
        raise ValueError('Expected nonempty, uniquely named features')
    return x, labels.eq('POSITIVE').astype(int)


def split_indices(x, y):
    # Keep exact duplicate feature vectors together even if their labels differ.
    # This does not establish patient independence: patient identifiers are absent.
    groups = pd.factorize(pd.MultiIndex.from_frame(x.fillna('__MISSING__')), sort=False)[0]
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    # Select the fold with prevalence closest to the full cohort; no model
    # predictions or test performance are used in choosing the holdout.
    folds = list(splitter.split(x, y, groups))
    train, test = min(folds, key=lambda pair: abs(y.iloc[pair[1]].mean() - y.mean()))
    assert not set(groups[train]).intersection(groups[test])
    if len(np.unique(y.iloc[train])) != 2 or len(np.unique(y.iloc[test])) != 2:
        raise ValueError('Both classes must be represented in each split')
    return train, test


def normalize_missing(frame):
    return frame.fillna(np.nan)


def make_preprocessor(x):
    num = x.select_dtypes(include=[np.number]).columns.tolist()
    cat = [c for c in x.columns if c not in num]
    return ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median')),
                              ('scale', StandardScaler())]), num),
        ('categorical', Pipeline([('normalize_missing', FunctionTransformer(normalize_missing)),
                                  ('impute', SimpleImputer(strategy='most_frequent')),
                                  ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat),
    ], sparse_threshold=0)


def make_models():
    # These are fixed choices, not the papers' published tuned configurations.
    return {
        'All-negative baseline': DummyClassifier(strategy='constant', constant=0),
        'Dedeene-inspired MLP': MLPClassifier(hidden_layer_sizes=(32, 16), alpha=0.001,
                                              max_iter=1000, random_state=SEED),
        'Farashi-inspired voting': VotingClassifier(estimators=[
            ('xgb', XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                                  n_jobs=1, random_state=SEED, eval_metric='logloss')),
            ('tree', DecisionTreeClassifier(max_depth=5, random_state=SEED)),
            ('lgbm', LGBMClassifier(n_estimators=100, max_depth=5, learning_rate=0.1,
                                    n_jobs=1, random_state=SEED, verbosity=-1)),
        ], voting='soft', n_jobs=1),
        'Favresse-inspired CatBoost': CatBoostClassifier(iterations=500, depth=6,
                                                           learning_rate=0.05, verbose=False,
                                                           random_seed=SEED, thread_count=1,
                                                           allow_writing_files=False),
    }


def evaluate(y, probabilities):
    prediction = (probabilities >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {'accuracy': accuracy_score(y, prediction),
            'roc_auc': roc_auc_score(y, probabilities),
            'average_precision': average_precision_score(y, probabilities),
            'precision': precision_score(y, prediction, zero_division=0),
            'recall': recall_score(y, prediction, zero_division=0),
            'specificity': tn / (tn + fp),
            'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)}


def run():
    output = ROOT / 'results'
    output.mkdir(exist_ok=True)
    records, splits = [], []
    for name, frame, target in load_datasets():
        x, y = features_and_labels(frame, target)
        train, test = split_indices(x, y)
        print(f'{name}: train={len(train)} test={len(test)}, positives={int(y.iloc[test].sum())}', flush=True)
        splits.append({'dataset': name, 'rows': len(frame), 'features': list(x.columns),
                       'train_rows': len(train), 'train_positive': int(y.iloc[train].sum()),
                       'test_rows': len(test), 'test_positive': int(y.iloc[test].sum())})
        for model_name, estimator in make_models().items():
            model = Pipeline([('preprocess', make_preprocessor(x)), ('model', estimator)])
            # No preprocessing is fitted on the test partition.
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                model.fit(x.iloc[train], y.iloc[train])
                probabilities = model.predict_proba(x.iloc[test])[:, 1]
            for warning in caught:
                print(f'  {model_name} warning: {warning.message}', flush=True)
            row = {'dataset': name, 'model': model_name,
                   **evaluate(y.iloc[test], probabilities)}
            records.append(row)
            print(f"  {model_name}: AUC={row['roc_auc']:.3f} AP={row['average_precision']:.3f} "
                  f"recall={row['recall']:.3f} FN={row['fn']}", flush=True)
    pd.DataFrame(records).to_csv(output / 'metrics.csv', index=False, float_format='%.6f')
    (output / 'splits.json').write_text(json.dumps(splits, indent=2) + '\n')


if __name__ == '__main__':
    run()
