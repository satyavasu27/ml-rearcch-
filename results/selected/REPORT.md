# Experiments on selected datasets

These are **exploratory paper-inspired adaptations**, not reproductions of the
original papers, their exact features, optimized hyperparameters, validation
procedures, or reported results. They are not clinical decision tools.
Only Taylor has actually been run. Trang has not yet been downloaded, verified
or evaluated; there are **no Trang results** in this directory.

## Methods

The same prespecified available urine tests and demographics are used for each
method within a dataset, not each paper's original feature set. A fixed
all-negative baseline and three classifiers are compared:

- Dedeene-inspired: MLP with hidden layers 32 and 16, alpha 0.001, max 80 iterations.
- Farashi-inspired: equally weighted soft vote of XGBoost, a decision tree and LightGBM.
- Favresse-inspired: CatBoost.

These are algorithm-level adaptations only. They omit the papers' original
feature selection, training procedures, clinical thresholds and, in particular,
Favresse's dipstick reflectance measurements and multiple outcome definitions.
Full settings are in `experiments/run_experiments.py` and
`experiments/run_selected.py`.

Taylor uses 18 prespecified predictors: age, gender, and available urinalysis
variables. Labels are `UCX_abnormal`; urine culture positivity is not the same
as symptomatic clinical UTI. We exclude IDs, diagnoses, disposition, antibiotics,
other culture/outcome-derived fields, and predictors of uncertain timing rather
than use all 220 columns. Urinalysis categories such as `not_reported` are
retained as categories. Numeric fields are median-imputed and standardized;
categorical fields are mode-imputed and one-hot encoded, with preprocessing
fit on training data only. The split is a seed-42 80/20 **patient-group**
shuffle by PATID, so repeat visits by a patient cannot cross train and test. It
is not a temporal or external validation. Other timing issues may still exist.

The Trang loader is preliminary: it uses a prespecified list of the publisher's
reported urine-measurement columns and sex, treats nonnumeric `MS` and blank
values as missing, and excludes the culture organism `URCULBAC` as outcome
leakage. The available preview contains no patient identifier, so the planned
seed-42 stratified record split cannot guarantee patient independence. The
original file, counts, meanings and coding must be checked against the authors'
variable dictionary before treating results as valid. The matched outpatient
cohort and its culture-based case definition differ from Taylor; performance
across datasets is not directly comparable.

For all methods, prediction uses an **untuned 0.5 threshold**. ROC AUC and
average precision (AP) use probabilities; recall, specificity and confusion
counts use that threshold. This is one split, without model selection, threshold
tuning, confidence intervals, calibration, or prospective validation. The MLP
hit its iteration limit without converging; its result may change with training.

## Taylor holdout

64,336 training visits; 16,051 test visits, including 3,625 culture-positive
visits. Full metrics and feature/split details are in `taylor_metrics.csv` and
`taylor_split.json`.

| Method | ROC AUC | AP | Recall | Specificity | False negatives |
|---|---:|---:|---:|---:|---:|
| All-negative baseline | 0.500 | 0.226 | 0.000 | 1.000 | 3,625 |
| Dedeene-inspired MLP | 0.887 | 0.751 | 0.601 | 0.936 | 1,448 |
| Farashi-inspired voting | 0.890 | 0.759 | 0.528 | 0.959 | 1,710 |
| Favresse-inspired CatBoost | 0.895 | 0.772 | 0.562 | 0.956 | 1,588 |

The default threshold misses many culture-positive visits; these results must
not be used for patient care or presented as clinical safety or paper replication.

## Reproduce

Using Python 3.11 with `requirements.txt` installed, run from the repository root:

```sh
python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python experiments/run_selected.py --dataset taylor
```

To run Trang, upload the original discovery-cohort CSV from
https://pmc.ncbi.nlm.nih.gov/articles/instance/12077719/bin/pone.0323664.s003.csv
as `data/trang/pone.0323664.s003.csv`, then verify its provenance, row counts,
variable dictionary, label meaning and patient-independence limitations before
running `python experiments/run_selected.py --dataset trang`. The default
`--dataset all` requires **both** files and stops before training if either is
missing. Outputs are written separately for each dataset under `results/selected/`.
The legacy report and results in `results/` are for different, removed datasets.
