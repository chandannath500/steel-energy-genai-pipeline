# Data Sources & Attribution

## Primary Dataset

**Steel Industry Energy Consumption** — UCI Machine Learning Repository, Dataset 851.

Source: https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption

DOI: https://doi.org/10.24432/C52G8C

License: **CC BY 4.0**

The UCI dataset contains **35,040 instances** of steel-industry energy observations and related electrical/operational variables.

### Citation

V E, S., Shin, C., & Cho, Y. (2021). *Steel Industry Energy Consumption*. UCI Machine Learning Repository. https://doi.org/10.24432/C52G8C

## Dataset Handling

The raw CSV is intentionally excluded from the Git repository. `src/download_data.py` retrieves the dataset from UCI and saves it locally under `data/raw/`.

## Repository Code License

The project code is provided under the MIT License. The dataset remains subject to its original CC BY 4.0 terms; see the UCI source for the authoritative dataset license and attribution requirements.
