# Urinalysis machine-learning research

## Selected datasets

1. **Taylor et al.**: The 80,387-record emergency-department dataset is in
   [`data/taylor/S1File.csv`](data/taylor/S1File.csv). See
   [`data/taylor/README.md`](data/taylor/README.md) for its provenance,
   license, checksum and important caveats.
2. **Second dataset pending**: [Trang et al. (2025)](https://doi.org/10.1371/journal.pone.0323664) provide a real, open clinical dataset with urinalysis, flow cytometry and urine culture results. Their discovery cohort contains 2,617 patients, exceeding the minimum of 2,000, and the [original CSV](https://pmc.ncbi.nlm.nih.gov/articles/instance/12077719/bin/pone.0323664.s003.csv) is publicly downloadable. It has not yet been added or independently counted here because this workspace cannot download from the publisher's host. The study's age- and sex-matched, symptomatic adult outpatient cohort differs from Taylor and from the original papers' populations. Culture positivity is not interchangeable with clinical UTI. `URCULBAC` is a culture-derived field and must not be used as a pre-culture predictor. The article and supporting information are published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The original Dedeene dataset is available on request, not via public download; see its [data-availability statement](https://www.sciencedirect.com/science/article/pii/S0009898124021065).

The formerly included original urinalysis and FlowUTI CSV files were removed
from the current checkout as requested. Their history remains in Git history.
The three PDFs in `papers/` are research papers, not datasets.

## Earlier exploratory experiments

[`results/REPORT.md`](results/REPORT.md) and `results/metrics.csv` are
historical results for the removed datasets. `experiments/run_experiments.py`
was written for those old datasets and **cannot currently run** from this
checkout; it does not train on Taylor or Dedeene. The historical results are
not results for the selected datasets. They are exploratory paper-inspired
adaptations, not clinical tools or exact reproductions.
