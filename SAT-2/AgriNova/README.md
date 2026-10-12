# AgriNova Farm Analytics: End-to-End Data Science Project

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Clean](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://pep8.org/)

**Project Title:** Understand Yield. Discover Influences. Support Better Farming.  
**Organization:** AgriNova Farm Analytics  
**Competition Category:** Round 2 Data Science Competition  
**Analytical Grain:** 1 observation per field per growing season `(field_id, season)`  

---

## 1. Project Overview & Business Mission

AgriNova works with commercial and cooperative farming enterprises across multiple agricultural regions. The primary business question driving this study is:

> **Which environmental and farming factors are associated with differences in crop yield?**

To answer this, we integrate five relational data layers (`fields.csv`, `soil.csv`, `weather.csv`, `practices.csv`, and `harvest.csv`), resolve severe real-world data flaws (conflicting duplicates, sensor dropouts, extreme typographical errors, and inconsistent taxonomy), and construct a leakage-free predictive modeling pipeline evaluated on strictly held-out unseen farms.

---

## 2. Repository Structure

```text
AgriNova/
├── data/
│   ├── raw/                           <- Raw multi-table relational CSV files
│   │   ├── fields.csv                 <- 250 fields (acreage, region, crop)
│   │   ├── soil.csv                   <- Soil chemistry (pH, moisture, N, P, K)
│   │   ├── weather.csv                <- 7,300 daily agro-meteorological records
│   │   ├── practices.csv              <- Management logs (irrigation, fertilizer, sowing)
│   │   └── harvest.csv                <- Harvest outcomes (yield kg/ha, quality grade)
│   └── processed/
│       └── agrinova_cleaned.csv       <- Integrated clean analytical dataset (988 rows)
├── notebooks/
│   └── agrinova_eda.ipynb             <- Fully executable Jupyter Notebook (Phases 1-8)
├── outputs/
│   ├── charts/                        <- 8 publication-quality agronomic charts
│   │   ├── regional_yield_comparison.png
│   │   ├── rainfall_versus_yield.png
│   │   ├── soil_correlation_heatmap.png
│   │   ├── irrigation_fertilizer_practices.png
│   │   ├── sowing_period_analysis.png
│   │   ├── field_yield_stability.png
│   │   ├── feature_importance_ranking.png
│   │   └── quality_grade_yield_analysis.png
│   ├── reports/                       <- Audit logs and executive reports
│   │   ├── agrinova_findings.md       <- Full executive report with 6 business answers
│   │   ├── cleaning_log.md            <- Step-by-step cleaning audit log
│   │   ├── data_quality_audit_table.md<- Structural audit summary table
│   │   └── data_validation_summary.json
│   └── feature_analysis/              <- Feature selection and ML results
│       ├── feature_dictionary.md      <- Full feature dictionary with formulas
│       ├── feature_importance_summary.csv
│       ├── model_metrics.json         <- Held-out test set performance
│       ├── selected_features.md       <- Ranked predictor analysis
│       ├── pca_report.md              <- PCA variance and loadings analysis
│       └── agrinova_features_enriched.csv
├── src/
│   ├── generate_raw_data.py           <- Realistic benchmark data generator (seed=42)
│   ├── data_validation.py             <- Phase 2 structural audit module
│   ├── data_cleaning.py               <- Phase 3 & 4 cleaning and relational merge
│   ├── feature_engineering.py         <- Phase 5 & 6 feature engineering and modeling
│   ├── generate_visualizations.py     <- Publication-quality chart generator
│   ├── build_notebook.py              <- Programmatic notebook builder
│   └── validate_notebook_execution.py <- Headless notebook validator
├── requirements.txt                   <- Environment dependencies
└── README.md                          <- Main project documentation
```

---

## 3. Dataset Provenance & Known Quality Issues

The dataset is a realistic agronomic benchmark built according to USDA and FAO-56 crop yield response functions. It models 250 commercial fields evaluated across four growing seasons (2021–2024), explicitly injecting five real-world data quality challenges:

1. **Inconsistent Crop Names:** 19 raw string variations due to irregular whitespace (` Maize `), mixed casing (`wheat`, `WHEAT`), and regional synonyms (`Corn`, `Soy`).
2. **Duplicate Records:** Exact duplicate rows and conflicting key updates in `practices.csv`, `soil.csv`, and `harvest.csv`.
3. **Severe Yield Outliers:** Physically impossible negative yields (-8,676 kg/ha) and 10x typographical errors (>15,000 kg/ha).
4. **Missing Soil Tests:** 12% of fields lacked seasonal soil assays; missing moisture and phosphorus readings within tested records.
5. **Weather Gaps:** 262 sensor outage dropouts (NaN) distinguished from 5,057 genuine zero-rainfall days.

---

## 4. Installation & Environment Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.11.0)
- Pip

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/K-Bharath-2006/Data_Science_SAT.git
cd Data_Science_SAT/AgriNova

# Install dependencies
pip install -r requirements.txt
```

### Dependencies
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `scipy>=1.10.0`
- `matplotlib>=3.7.0`
- `seaborn>=0.12.0`
- `scikit-learn>=1.2.0`
- `nbformat>=5.9.0`
- `tabulate>=0.9.0`

---

## 5. Execution Instructions

The entire project is built to execute reproducibly via command-line scripts or via Jupyter Notebook:

### Run Full Modular Pipeline via CLI:
```bash
# Step 1: Generate benchmark raw relational data (if starting from scratch)
python src/generate_raw_data.py

# Step 2: Run Phase 2 structural data validation audit
python src/data_validation.py

# Step 3: Run Phase 3 & 4 cleaning and relational merge
python src/data_cleaning.py

# Step 4: Run Phase 5 & 6 feature engineering and model evaluation
python src/feature_engineering.py

# Step 5: Generate all 8 publication-grade charts
python src/generate_visualizations.py

# Step 6: Validate notebook headless execution
python src/validate_notebook_execution.py
```

### Run via Jupyter Notebook:
Open and execute:
```bash
jupyter notebook notebooks/agrinova_eda.ipynb
```
*(The notebook executes from cell 1 to cell 11 without any manual adjustments).*

---

## 6. Answers to the Six Primary Business Questions

| Business Question | Key Calculated Finding | Agronomic Mechanism / Confounder |
|:---|:---|:---|
| **1. Which regions have higher yield?** | **Central Plains** (mean 5,725 kg/ha) and **North Valley** (mean 5,625 kg/ha) outperform **Eastern Highlands** (mean 3,292 kg/ha). | Central Plains possesses optimal soil pH (6.8–7.2) and fertile nitrogen; Eastern Highlands suffer from chronic soil acidity (pH ~5.5). |
| **2. How does rainfall relate to yield?** | Non-linear quadratic saturation curve. Optimal yield occurs between **600 mm and 750 mm**. Above 850 mm, yields plateau. | Extreme moisture causes waterlogging and root hypoxia. Linear Pearson correlation (-0.288) is confounded by region/acidity (Simpson's Paradox). |
| **3. Which soil factors vary with yield?** | **Soil pH distance from crop optimum (`crop_ph_deviation`)** is the top soil driver (Permutation Importance = **0.2583**). | Acidic soils (<5.8 pH) cause aluminum toxicity and phosphorus fixation, reducing yields by up to 40%. |
| **4. How do irrigation practices differ?** | **Drip** delivers highest median yield (5,510 kg/ha), while **Rainfed** has lowest median (3,820 kg/ha) and highest downside risk. | Drip provides continuous root zone moisture without evaporative losses; Rainfed fields suffer during seasonal droughts. |
| **5. Does sowing period matter?** | **Early Spring (March–April)** optimizes Maize and Soybean yield; Late Spring causes 6–12% yield loss from flowering heat stress. | Winter crops (Wheat, Barley) require autumn/winter planting for proper vernalization. |
| **6. Which fields show unstable yield?** | Fields with **CV > 18.5%** (e.g., F_042 at 28.4% CV) are concentrated in Eastern Highlands and Southern Basin. | Complete reliance on rainfed agriculture and low soil moisture capacity (<16%) drives multi-season volatility. |

---

## 7. Predictive Modeling & Leakage Prevention

- **Model:** Random Forest Regressor (300 estimators, max depth 12).
- **Leakage Prevention:** Post-harvest variables (`quality_grade`, `harvest_date`) strictly excluded.
- **Grouped Splitting:** Evaluated using `GroupShuffleSplit` on `field_id` (200 training fields, 50 strictly unseen test fields).
- **Held-Out Test Set Performance:**
  - **R² Score:** `0.8721`
  - **RMSE:** `732.82 kg/ha`
  - **MAE:** `578.99 kg/ha`

---

## 8. Limitations & Methodology

1. **Prediction vs Causation:** Machine learning feature importance demonstrates predictive utility rather than counterfactual causation.
2. **Soil Testing Coverage:** 12% of fields lacked annual laboratory assays, requiring regional median imputation.
3. **Synthetic Grounding:** The benchmark dataset was generated from USDA/FAO physiological models to guarantee 100% reproducible evaluation for competition judging.
