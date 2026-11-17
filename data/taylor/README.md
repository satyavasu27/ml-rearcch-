# Taylor et al. emergency-department urine dataset

`S1File.csv` is the unmodified **S1 File.csv** accompanying:

> Taylor RA, Moore CL, Cheung K-H, Brandt C. Predicting urinary tract
> infections in the emergency department with machine learning. PLOS ONE
> 13(3): e0194085 (2018). https://doi.org/10.1371/journal.pone.0194085

The authors describe this as a retrospective dataset of real adult
emergency-department visits, not a synthetic dataset. The CSV contains
80,387 records and 220 columns; `UCX_abnormal` is `yes` in 18,284 and `no`
in 62,103 records. The dataset is de-identified, and the study notes that
individual patients may have multiple visits. Avoid patient overlap when
splitting data, and review feature timing to prevent outcome leakage.

- Publisher dataset and direct download: https://plos.figshare.com/articles/dataset/Predicting_urinary_tract_infections_in_the_emergency_department_with_machine_learning/5959417
- Publisher metadata, including file size and checksum: https://api.figshare.com/v2/articles/5959417
- Downloaded via GitHub mirror because the publisher's download host was not
  reachable from this environment: https://github.com/seanxuxx/UTI-ED-Prediction/blob/87ffcdd30c23cbcaebb1b0c0e80eaf68260bfefa/data/S1File.csv
- The file's MD5 matches the checksum listed by the publisher. File size is
  85,690,524 bytes. The file is shared under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit the
  original authors and source when reusing it.

```text
MD5     0e51d504f41b15944a02a8fd5dd81a17
SHA256  72c054b8fee2bf12a35ac1e649cf6d675ca6abb4db884c3991428666d754ef14
```
