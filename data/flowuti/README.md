# FlowUTI clinical urine datasets

These are the original, unmodified demo datasets accompanying:

> Martín-Gutiérrez G, Martín-Pérez C, Toledo H, Sánchez-Cantalejo E, Lepe JA.
> FlowUTI: An interactive web-application for optimizing the use of flow
> cytometry as a screening tool in urinary tract infections. *PLOS ONE* 17(11):
> e0277340 (2022). https://doi.org/10.1371/journal.pone.0277340

- Original data: https://github.com/GuillermoMG-HUVR/Microbiology-applications/tree/6f90075442658aff40d696bde9ce91b42545b11d/FlowUTI/Demos
- [Elderly.csv](https://github.com/GuillermoMG-HUVR/Microbiology-applications/blob/6f90075442658aff40d696bde9ce91b42545b11d/FlowUTI/Demos/Elderly.csv)
- [Neonates.csv](https://github.com/GuillermoMG-HUVR/Microbiology-applications/blob/6f90075442658aff40d696bde9ce91b42545b11d/FlowUTI/Demos/Neonates.csv)
- The article states that all data are available without restriction. The
  article itself is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/);
  no separate dataset license was found in the linked repository. Please credit
  the authors and original source when using these files.

## Provenance and contents

The authors describe these as samples from real patients, not simulated data;
this is documented in the paper's Methods, although the underlying collection
cannot be independently audited from the CSV files alone. Both contain
flow-cytometry bacteria and leukocyte counts and a positive/negative culture
result. The culture result is **not necessarily equivalent** to the `Diagnosis`
column in this repository's original dataset, whose definition is undocumented.

| File | Cohort and collection | Rows | Culture results |
| --- | --- | ---: | --- |
| Elderly.csv | Patients aged 65 or older with UTI symptoms, primary care at Virgen del Rocío University Hospital, 2021 | 1,174 | 496 positive, 678 negative |
| Neonates.csv | Neonates and infants aged at most 3 months with suspected UTI, emergency department at the same hospital, 2013–2015 | 204 | 57 positive, 147 negative |

The study used different analyzers and culture positivity thresholds for the
two groups: ≥10⁵ CFU/mL for the elderly cohort and ≥10² CFU/mL for the
neonatal cohort. These are selected age groups, not representative of all ages.
Neither dataset contains the full feature set of `urinalysis_tests.csv`: in
particular, it lacks per-record age, gender, and most dipstick and microscopy
fields. The counts are measured by flow cytometry, so they should not be
assumed directly interchangeable with the original CSV's WBC ranges and
categorical bacteria values. Check the paper and measurement units before any
comparison. Do not use these files as clinical decision tools.

## Reading the files

The files are preserved exactly as published, including their different formats:

- `Elderly.csv` is comma-separated. Its header has three named columns but each
  data row has an additional leading, unlabeled row index. Read with the first
  column as an index, e.g. `pandas.read_csv(path, index_col=0)`.
- `Neonates.csv` is semicolon-separated and has no index column, e.g.
  `pandas.read_csv(path, sep=';')`.

SHA-256 checksums of the downloaded files:

```text
dd5a30797191f6efcae47cbb3906624ad81778b75e41278bb98677af733fe8d5  Elderly.csv
e4f6b23869ad2b66957a92588c8f266dba11076d49d6f8e7bd9545f53f626fee  Neonates.csv
```
