#!/usr/bin/env python3
"""Exploratory paper-inspired classifiers on the selected clinical datasets."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import Pipeline

from run_experiments import SEED, evaluate, make_models, make_preprocessor

ROOT = Path(__file__).resolve().parents[1]
TAYLOR = ROOT / 'data/taylor/S1File.csv'
TRANG = ROOT / 'data/trang/pone.0323664.s003.csv'
TAYLOR_FEATURES = ['age', 'gender', 'ua_bacteria', 'ua_bili', 'ua_blood',
                   'ua_clarity', 'ua_color', 'ua_epi', 'ua_glucose',
                   'ua_ketones', 'ua_leuk', 'ua_nitrite', 'ua_ph',
                   'ua_protein', 'ua_rbc', 'ua_spec_grav', 'ua_urobili', 'ua_wbc']
# Prespecified urinalysis/dipstick and flow cytometry variables. Avoid culture
# organism (URCULBAC), source/year, unknown flags and any target-derived fields.
TRANG_FEATURES = ['Female', 'UGLU', 'UKET', 'UBIL', 'UPROT', 'UNIT', 'UPH',
                  'UBLD', 'USG', 'ULEU', 'AHC', 'BC', 'BCK', 'CTT', 'DTTrong',
                  'ETBL', 'FTBCV', 'FTBKV', 'GTBBMCT', 'GTBBMOT', 'GVT', 'HTBN']


def load_data(name, path=None):
    path = Path(path) if path else {'taylor': TAYLOR, 'trang': TRANG}[name]
    if not path.is_file():
        raise FileNotFoundError(f'{name} dataset missing: {path}. Download/upload the original file before running.')
    frame = pd.read_csv(path, low_memory=False)
    columns = TAYLOR_FEATURES if name == 'taylor' else TRANG_FEATURES
    target = 'UCX_abnormal' if name == 'taylor' else 'URCUL_pos_yn'
    required = columns + [target] + (['PATID'] if name == 'taylor' else [])
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f'{name} is missing columns: {missing}')
    if len(frame) < 2000:
        raise ValueError(f'{name} contains fewer than 2,000 records')
    if name == 'taylor':
        labels = frame[target].astype(str).str.lower().str.strip()
        if set(labels) != {'yes', 'no'} or frame.PATID.isna().any():
            raise ValueError('Invalid Taylor label or missing patient ID')
        y = labels.eq('yes').astype(int)
        groups = frame.PATID
    else:
        labels = pd.to_numeric(frame[target], errors='coerce')
        if labels.isna().any() or set(labels.unique()) != {0, 1}:
            raise ValueError('Invalid Trang culture label')
        y = labels.astype(int)
        groups = None
    x = frame[columns].copy()
    if name == 'trang':
        # These measurements are numeric codes or values; blank and MS are missing.
        x = x.apply(pd.to_numeric, errors='coerce')
    return x, y, groups, path


def split_data(x, y, groups):
    if groups is not None:
        train, test = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED).split(x, y, groups))
        assert not set(groups.iloc[train]) & set(groups.iloc[test])
    else:
        train, test = train_test_split(np.arange(len(y)), test_size=0.2,
                                       random_state=SEED, stratify=y)
    if y.iloc[train].nunique() != 2 or y.iloc[test].nunique() != 2:
        raise ValueError('Both splits must include both classes')
    return train, test


def run_one(name):
    x, y, groups, path = load_data(name)
    train, test = split_data(x, y, groups)
    models = make_models()
    # Set finite computational budget and deterministic single-worker models.
    models['Dedeene-inspired MLP'].set_params(max_iter=80)
    records, model_warnings = [], {}
    for label, estimator in models.items():
        model = Pipeline([('preprocess', make_preprocessor(x)), ('model', estimator)])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            model.fit(x.iloc[train], y.iloc[train])
            probabilities = model.predict_proba(x.iloc[test])[:, 1]
        row = {'dataset': name, 'model': label, **evaluate(y.iloc[test], probabilities)}
        records.append(row)
        print(f"{name} {label}: AUC={row['roc_auc']:.3f} recall={row['recall']:.3f} FN={row['fn']}", flush=True)
        model_warnings[label] = [str(warning.message) for warning in caught]
        for warning in caught:
            print(f'  warning: {warning.message}', file=sys.stderr, flush=True)
    info = {'dataset': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'features': list(x.columns), 'seed': SEED, 'rows': len(y),
            'train_rows': len(train), 'test_rows': len(test),
            'train_positive': int(y.iloc[train].sum()), 'test_positive': int(y.iloc[test].sum()),
            'warnings': model_warnings,
            'split': 'patient-group shuffle' if groups is not None else 'stratified record split (patient IDs unavailable)',
            'train_index_sha256': hashlib.sha256(np.asarray(train, dtype='<i8').tobytes()).hexdigest(),
            'test_index_sha256': hashlib.sha256(np.asarray(test, dtype='<i8').tobytes()).hexdigest()}
    out = ROOT / 'results/selected'
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(out / f'{name}_metrics.csv', index=False, float_format='%.6f')
    (out / f'{name}_split.json').write_text(json.dumps(info, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', choices=['taylor', 'trang', 'all'], default='all')
    args = parser.parse_args()
    names = ['taylor', 'trang'] if args.dataset == 'all' else [args.dataset]
    # Fail before running anything when either requested dataset is absent.
    for name in names:
        if not {'taylor': TAYLOR, 'trang': TRANG}[name].is_file():
            parser.error(f'{name} file is missing; see README for upload instructions')
    for name in names:
        run_one(name)


if __name__ == '__main__':
    main()
