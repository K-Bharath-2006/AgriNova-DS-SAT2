# AgriNova Farm Analytics: End-to-End Data Science Project

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Clean](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://pep8.org/)

**Project Title:** Understand Yield. Discover Influences. Support Better Farming.  
**Organization:** AgriNova Farm Analytics  
**Competition Category:** Round 2 Data Science Competition  
**Analytical Grain:** 1 observation per field per growing season `(field_id, season)`  

The complete codebase, processed data, visualizations, and Jupyter notebook are located in the [`AgriNova/`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova) directory.

---

## 1. Quick Navigation
- **Jupyter Notebook:** [`AgriNova/notebooks/agrinova_eda.ipynb`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/notebooks/agrinova_eda.ipynb)
- **Executive Scientific Report:** [`AgriNova/outputs/reports/agrinova_findings.md`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/outputs/reports/agrinova_findings.md)
- **Cleaned Dataset:** [`AgriNova/data/processed/agrinova_cleaned.csv`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/data/processed/agrinova_cleaned.csv)
- **Visualizations (8 Charts):** [`AgriNova/outputs/charts/`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/outputs/charts)
- **Feature Analysis & Metrics:** [`AgriNova/outputs/feature_analysis/`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/outputs/feature_analysis)
- **Cleaning Audit Log:** [`AgriNova/outputs/reports/cleaning_log.md`](file:///c:/Black-Drive/My%20Life/Sem-5/Data%20Science/SAT-2/AgriNova/outputs/reports/cleaning_log.md)

---

## 2. Six Primary Business Questions — Summary Table

| Question | Calculated Result | Key Agronomic Insight |
|:---|:---|:---|
| **1. Regional yield differences** | **Central Plains** (mean 5,725 kg/ha) & **North Valley** (5,625 kg/ha) lead; **Eastern Highlands** (3,292 kg/ha) lowest. | Favorable soil pH (6.8–7.2) and high nitrogen in Central Plains vs severe soil acidity (pH ~5.5) in Eastern Highlands. |
| **2. Rainfall and yield** | Quadratic water response curve; optimal yield between **600 mm and 750 mm**. | Beyond 850 mm, yield plateaus/declines from waterlogging. Drier fields suffer sharp yield loss unless irrigated. |
| **3. Soil factors and yield** | **Crop pH deviation (`|soil_ph - optimal_ph|`)** is the top soil driver (Permutation Importance = **0.2583**). | Soil acidity (<5.8 pH) restricts nutrient uptake. Liming acidic fields offers the highest return on investment. |
| **4. Irrigation practices** | **Drip** median = 5,510 kg/ha; **Rainfed** median = 3,820 kg/ha (-30.7% deficit). | Drip maintains root zone hydration with minimal evaporative loss, eliminating drought shocks. |
| **5. Sowing period** | **Early Spring (March–April)** optimizes Maize/Soybean yield; Late Spring causes 6–12% yield loss. | Early sowing maximizes degree days before reproductive-phase summer heat stress. |
| **6. Yield stability** | Fields with **CV > 18.5%** are concentrated in Eastern Highlands and Southern Basin. | Complete rainfed dependence on drought-prone soils causes extreme inter-annual yield swings. |

---

## 3. Execution

```bash
# Run modular pipeline
python AgriNova/src/generate_raw_data.py
python AgriNova/src/data_validation.py
python AgriNova/src/data_cleaning.py
python AgriNova/src/feature_engineering.py
python AgriNova/src/generate_visualizations.py
python AgriNova/src/validate_notebook_execution.py

# Launch Jupyter notebook
jupyter notebook AgriNova/notebooks/agrinova_eda.ipynb
```
