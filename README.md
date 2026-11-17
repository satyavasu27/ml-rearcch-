# Urinalysis machine-learning research

This repository contains an original urinalysis CSV, three research papers,
and the published FlowUTI clinical urine datasets. See
[`data/flowuti/README.md`](data/flowuti/README.md) for FlowUTI provenance and
format details.

## Exploratory experiments

[`results/REPORT.md`](results/REPORT.md) describes and compares three
paper-inspired models on the original dataset and on each FlowUTI cohort. The
implementations are adaptations, **not exact reproductions** of the papers, and
are not intended for clinical use.

To reproduce the results (Python 3.11):

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiments/run_experiments.py
```

The script writes `results/metrics.csv` and `results/splits.json`. See the report
for methodology, limitations, and interpretation.
