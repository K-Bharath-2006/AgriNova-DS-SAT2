# AgriNova Farm Analytics — Detailed Line-by-Line Code Explanation

**Project:** Understand Yield. Discover Influences. Support Better Farming.  
**Domain:** Agricultural Data Science, Machine Learning Pipeline & Excel Automation  
**Author:** Antigravity Senior Data Science Team  

This document explains every component, function, logic block, and line of code across all production Python scripts built from scratch in the `AgriNova/src/` directory.

---

## Table of Contents
1. [src/generate_raw_data.py — Benchmark Data Synthesis](#1-srcgenerate_raw_datapy)
2. [src/data_validation.py — Structural Audit & Schema Inspection](#2-srcdata_validationpy)
3. [src/data_cleaning.py — Cleaning, Deduplication & Relational Merge](#3-srcdata_cleaningpy)
4. [src/feature_engineering.py — Feature Construction, PCA & Leak-Free ML](#4-srcfeature_engineeringpy)
5. [src/generate_visualizations.py — Publication-Grade Visualization Engine](#5-srcgenerate_visualizationspy)
6. [src/build_notebook.py & validate_notebook_execution.py — Notebook Engine](#6-notebook-compilation--validation-scripts)
7. [src/generate_excel_workbook.py — 10-Sheet Excel Workbook Builder](#7-srcgenerate_excel_workbookpy)
8. [src/validate_excel_workbook.py — Automated Excel Quality Assurance](#8-srcvalidate_excel_workbookpy)

---

## 1. `src/generate_raw_data.py`

This script generates the 5 realistic relational CSV files with domain-accurate agronomic response functions and injected real-world anomalies.

### Header & Imports (Lines 1–25)
```python
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
```
- `os`: Provides operating system operations, such as creating target directories (`os.makedirs`).
- `random`, `numpy`: Used for pseudo-random number generation, array mathematics, and probability sampling.
- `pandas`: Builds and serializes structured tabular DataFrames into CSV files.
- `datetime`, `timedelta`: Generates and manipulates calendar dates for sowing, daily weather, and harvest.

### Function Definition & Reproducibility Setup (Lines 26–31)
```python
def generate_benchmark_data(output_dir="data/raw", seed=42):
    np.random.seed(seed)
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
```
- `seed=42`: Sets fixed seeds for both NumPy and Python's random generators, guaranteeing that generated numbers, distributions, and anomalies are identical across any run.
- `os.makedirs(output_dir, exist_ok=True)`: Ensures `data/raw` exists before writing files.

### 1. Generating `fields.csv` (Lines 32–72)
```python
    n_fields = 250
    field_ids = [f"F_{i:03d}" for i in range(1, n_fields + 1)]
    regions = ["North Valley", "Eastern Highlands", "Central Plains", "Southern Basin", "Western Coast"]
```
- Creates 250 unique alphanumeric field IDs (`F_001` through `F_250`).
- Defines the 5 commercial agricultural regions.

```python
    field_regions = np.random.choice(regions, size=n_fields, p=[0.25, 0.20, 0.30, 0.15, 0.10])
    field_areas = np.round(np.random.uniform(5.0, 120.0, size=n_fields), 1)
```
- Assigns fields to regions using fixed proportions (e.g., Central Plains = 30%, North Valley = 25%).
- Generates field areas uniformly between 5.0 and 120.0 hectares, rounded to 1 decimal place.

```python
    canonical_crops = ["Maize", "Wheat", "Soybean", "Barley"]
    assigned_crops = np.random.choice(canonical_crops, size=n_fields, p=[0.35, 0.30, 0.25, 0.10])
```
- Assigns one of four canonical commercial crops per field based on regional market share.

```python
    noisy_crops = []
    for c in assigned_crops:
        rand_val = np.random.rand()
        if rand_val < 0.08:
            noisy_crops.append(c.lower())        # e.g., "maize"
        elif rand_val < 0.15:
            noisy_crops.append(c.upper())        # e.g., "MAIZE"
        elif rand_val < 0.22:
            noisy_crops.append(f" {c} ")         # e.g., " Maize "
        elif rand_val < 0.30 and c == "Maize":
            noisy_crops.append("Corn")           # Regional synonym
        elif rand_val < 0.35 and c == "Soybean":
            noisy_crops.append("Soy")            # Regional synonym
        elif rand_val < 0.38 and c == "Wheat":
            noisy_crops.append(" wheat")
        else:
            noisy_crops.append(c)
```
- **Anomaly Injection:** Iterates through assigned crops and introduces noise: lowercase, uppercase, irregular leading/trailing whitespace, and regional synonyms (`Corn -> Maize`, `Soy -> Soybean`). This establishes the 19 raw string variations audited in Phase 2.

```python
    df_fields = pd.DataFrame({
        "field_id": field_ids,
        "region": field_regions,
        "area_hectares": field_areas,
        "crop": noisy_crops
    })
```
- Assembles the clean/noisy fields data structure into a DataFrame.

---

### 2. Generating `practices.csv` (Lines 74–145)
```python
    seasons = [2021, 2022, 2023, 2024]
    irrigation_options = ["Drip", "Sprinkler", "Flood", "Rainfed"]
    fertilizer_options = ["Synthetic NPK", "Organic Compost", "Biofertilizer", "Minimal/None"]
```
- Defines 4 consecutive growing seasons and realistic management practices.

```python
    for f_idx, fid in enumerate(field_ids):
        can_crop = assigned_crops[f_idx]
        region = field_regions[f_idx]
        for season in seasons:
            if can_crop in ["Maize", "Soybean"]:
                base_month = 4 if region in ["Southern Basin", "Central Plains"] else 5
                day = np.random.randint(1, 28)
                sow_date = datetime(season, base_month, day)
            elif can_crop in ["Wheat", "Barley"]:
                base_month = 10 if region in ["North Valley", "Eastern Highlands"] else 3
                day = np.random.randint(1, 28)
                sow_date = datetime(season if base_month == 3 else season - 1, base_month, day)
```
- Assigns crop- and region-appropriate sowing dates: summer crops (Maize, Soy) plant in April–May; winter cereals (Wheat, Barley) plant in autumn (October) or early spring (March).

```python
            if region in ["Southern Basin", "Western Coast"]:
                irr_p = [0.4, 0.3, 0.2, 0.1]
            elif region == "Central Plains":
                irr_p = [0.25, 0.35, 0.25, 0.15]
            else:
                irr_p = [0.15, 0.25, 0.15, 0.45]
            irrigation = np.random.choice(irrigation_options, p=irr_p)
            fertilizer = np.random.choice(fertilizer_options, p=[0.50, 0.25, 0.15, 0.10])
```
- Conditions irrigation probabilities on regional climate (arid Southern Basin relies more on drip/sprinkler; Highlands use more rainfed cultivation).

```python
    # Inject duplicate field-season records in practices (exact and conflicting)
    dup_indices = np.random.choice(len(df_practices), size=25, replace=False)
    dup_rows = []
    for idx in dup_indices:
        row = df_practices.iloc[idx].copy()
        if np.random.rand() < 0.5:
            row["irrigation_type"] = "Sprinkler" if row["irrigation_type"] != "Sprinkler" else "Drip"
        dup_rows.append(row)
    df_practices = pd.concat([df_practices, pd.DataFrame(dup_rows)], ignore_index=True)
```
- **Anomaly Injection:** Selects 25 random records and duplicates them: half as exact duplicates, and half with conflicting operational updates (simulating contradictory field logs).

---

### 3. Generating `soil.csv` (Lines 147–215)
```python
        if region == "North Valley":
            base_ph, base_n, base_p, base_k = 6.8, 140, 35, 180
        elif region == "Eastern Highlands":
            base_ph, base_n, base_p, base_k = 5.5, 95, 20, 120  # Acidic, lower fertility
        elif region == "Central Plains":
            base_ph, base_n, base_p, base_k = 7.2, 160, 42, 210  # Optimal fertile loam
```
- Establishes regional chemical baselines: Eastern Highlands are naturally acidic (pH ~5.5); Central Plains are neutral-alkaline loam (pH ~7.2).

```python
        for season in seasons:
            if np.random.rand() < 0.12:
                continue # Missing soil test record entirely
```
- **Anomaly Injection:** Injects a 12% probability that a field was not tested by the laboratory in a given season, creating real-world missingness.

```python
            if np.random.rand() < 0.05:
                moisture = np.nan
            if np.random.rand() < 0.04:
                p_ppm = np.nan
```
- Injects partial laboratory assay dropouts (missing moisture or phosphorus readings within tested records).

---

### 4. Generating `weather.csv` (Lines 217–305)
```python
    regional_weather_profiles = {
        "North Valley": {"temp_mean": 18.5, "temp_amp": 9.0, "rain_prob": 0.28, "rain_mean": 9.5, "hum": 68},
        "Eastern Highlands": {"temp_mean": 14.0, "temp_amp": 7.5, "rain_prob": 0.40, "rain_mean": 13.0, "hum": 78},
        ...
    }
```
- Calibrates 365 daily weather cycles per region across 4 seasons (7,300 daily rows).
- Embeds year-level macro climate shocks: 2022 wet year (+25% rain); 2023 regional drought year (-25% rain, +1.2°C heat).

```python
    temp_cycle = np.sin((day_of_year - 105) * 2 * np.pi / 365)
    t_mean = prof["temp_mean"] + prof["temp_amp"] * temp_cycle + year_temp_shift + np.random.normal(0, 2.0)
```
- Models annual temperature cycles using a sinusoidal curve peaking in summer (day 195) and dipping in winter.

```python
    is_rain = np.random.rand() < (prof["rain_prob"] * year_rain_mult)
    rainfall = np.random.gamma(shape=1.8, scale=prof["rain_mean"] / 1.8) if is_rain else 0.0
```
- Rainfall uses a zero-inflated Gamma distribution, creating genuine zero-rain days ($0.0\text{ mm}$) and realistic skewed rainfall events on wet days.

```python
    if np.random.rand() < 0.035:
        t_mean_val, rainfall_val, hum_val = np.nan, np.nan, np.nan
```
- **Anomaly Injection:** 3.5% probability of automated station sensor outages, introducing NaNs that must be distinguished from genuine dry days.

---

### 5. Generating `harvest.csv` & Agronomic Yield Formula (Lines 307–415)
```python
    crop_potential = {"Maize": 7800, "Wheat": 5200, "Soybean": 3600, "Barley": 4400}
    irr_mult = {"Drip": 1.22, "Sprinkler": 1.15, "Flood": 1.06, "Rainfed": 0.88}[irr]
    fert_mult = {"Synthetic NPK": 1.20, "Organic Compost": 1.12, "Biofertilizer": 1.08, "Minimal/None": 0.85}[fert]
```
- Sets physiological genetic ceilings and management efficiency multipliers.

```python
    ph_mult = np.exp(-0.5 * ((s_ph - 6.6) / 1.4)**2) # Gaussian pH curve
    rain_mult = np.clip(1.0 - 0.0000015 * (rain - 650)**2, 0.65, 1.15) # Quadratic rain response
    temp_penalty = 1.0 - max(0, (temp - 23.0) * 0.04) # Thermal heat penalty
```
- Implements non-linear biological response functions:
  - `ph_mult`: Yield drops when soil pH deviates from 6.6.
  - `rain_mult`: Quadratic curve peaking at 650 mm; water stress below 500 mm, waterlogging above 850 mm.
  - `temp_penalty`: Linear yield loss for each degree above 23°C.

```python
    sim_yield = base_pot * field_quality_factor * irr_mult * fert_mult * ph_mult * rain_mult * temp_penalty
```
- Synthesizes the ground-truth agronomic harvest yield.

```python
    # Anomaly Injection: Extreme typographical and sensor errors
    err_indices = np.random.choice(len(df_harvest), size=12, replace=False)
    for i, idx in enumerate(err_indices):
        if i % 3 == 0:
            df_harvest.at[idx, "yield_kg_per_ha"] *= 10.0 # 65,000+ kg/ha decimal typo
        elif i % 3 == 1:
            df_harvest.at[idx, "yield_kg_per_ha"] = -abs(df_harvest.at[idx, "yield_kg_per_ha"]) # Negative yield
        else:
            df_harvest.at[idx, "yield_kg_per_ha"] = 85000.0 # Sensor key error
```
- Injects 12 severe yield outliers: decimal shift typos (10x), impossible negative yields, and sensor overflow entries.

---

## 2. `src/data_validation.py`

This module performs the structural audit across all 5 raw files before cleaning.

### Structural Loop & Metric Computation (Lines 20–85)
```python
    for name, filename in files.items():
        filepath = raw_path / filename
        df = pd.read_csv(filepath)
        n_rows, n_cols = df.shape
        missing_counts = df.isnull().sum()
        missing_pcts = (missing_counts / n_rows * 100).round(2)
        n_exact_dups = df.duplicated().sum()
```
- Reads each raw CSV and extracts core shape dimensions (`n_rows`, `n_cols`).
- Computes column-level missing values and percentages.
- Counts exact duplicate rows using `df.duplicated().sum()`.

```python
        candidate_keys = ["field_id", "season"]
        avail_keys = [k for k in candidate_keys if k in df.columns]
        key_dups = df.duplicated(subset=avail_keys).sum() if avail_keys else 0
```
- Tests candidate composite keys (`field_id, season`) to detect conflicting records before attempting relational joins.

### Domain-Specific Integrity Checks (Lines 87–125)
```python
    # 1. fields.csv: crop names inspection
    crop_counts = dfs["fields"]["crop"].value_counts().to_dict()
```
- Tallies unique crop strings to quantify taxonomy fragmentation (identifying 19 noisy variants).

```python
    # 2. harvest.csv: yield distribution & negative / extreme values
    yield_col = dfs["harvest"]["yield_kg_per_ha"]
    neg_yields = (yield_col < 0).sum()
    extreme_high_yields = (yield_col > 15000).sum()
```
- Flags impossible negative values (`yield < 0`) and entries exceeding biological plausibility (`yield > 15,000 kg/ha`).

```python
    # 4. weather.csv: rainfall zero vs missing
    zero_rain = (w_df["rainfall_mm"] == 0).sum()
    nan_rain = w_df["rainfall_mm"].isnull().sum()
```
- Separates valid zero-rainfall dry days (5,057 days) from sensor outages (262 NaNs).

### Report Generation (Lines 126–160)
- Builds a consolidated summary DataFrame, serializes audit metrics to `outputs/reports/data_validation_summary.json`, and writes `data_quality_audit_table.md`.

---

## 3. `src/data_cleaning.py`

This module cleans each table, tracks actions in an audit log, and merges the datasets at the **field-season grain**.

### Audit Logging Function (Lines 22–35)
```python
    cleaning_log = []
    def log_action(issue, affected_entity, action_taken, rationale, count_affected):
        cleaning_log.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "issue_detected": issue,
            "affected_entity": affected_entity,
            "action_taken": action_taken,
            "rationale": rationale,
            "count_affected": count_affected
        })
```
- Records a structured entry for every transformation: the issue detected, affected column/table, action taken, agronomic justification, and number of records modified.

### 1. Cleaning Fields (Lines 37–58)
```python
    df_fields["crop_raw"] = df_fields["crop"]
    df_fields["crop_clean"] = df_fields["crop"].astype(str).str.strip().str.title()
    synonym_map = {"Corn": "Maize", "Soy": "Soybean"}
    df_fields["crop_clean"] = df_fields["crop_clean"].replace(synonym_map)
    df_fields["crop"] = df_fields["crop_clean"]
```
- Preserves `crop_raw` for traceability.
- Trims whitespace with `.str.strip()` and capitalizes with `.str.title()`.
- Maps verified synonyms (`Corn -> Maize`, `Soy -> Soybean`), consolidating the taxonomy into 4 canonical crops.

### 2. Cleaning Practices (Lines 60–92)
```python
    df_practices = df_practices.drop_duplicates()
    df_practices = df_practices.drop_duplicates(subset=["field_id", "season"], keep="last")
    df_practices["sowing_date"] = pd.to_datetime(df_practices["sowing_date"])
```
- Removes 11 exact duplicate rows.
- Resolves conflicting duplicate keys by retaining the latest logged operational entry (`keep="last"`).
- Converts sowing dates to `pd.to_datetime`.

### 3. Cleaning Soil (Lines 94–140)
```python
    df_soil = df_soil.drop_duplicates().drop_duplicates(subset=["field_id", "season"], keep="first")
    df_soil["missing_soil_moisture"] = df_soil["soil_moisture_pct"].isnull().astype(int)
    df_soil["missing_phosphorus"] = df_soil["phosphorus_ppm"].isnull().astype(int)
    df_soil["soil_tested"] = 1
```
- Deduplicates soil records.
- Creates binary missingness indicators before imputation to retain the signal that an assay was missing.
- Sets `soil_tested = 1` for records with physical laboratory test data.

```python
    soil_with_region = df_soil.merge(df_fields[["field_id", "region"]], on="field_id", how="left")
    for col in ["soil_moisture_pct", "phosphorus_ppm"]:
        df_soil[col] = soil_with_region.groupby("region")[col].transform(lambda grp: grp.fillna(grp.median()))
```
- Imputes missing moisture and phosphorus values within tested records using regional medians.

### 4. Cleaning & Aggregating Weather (Lines 142–185)
```python
    df_weather["temperature_mean_c"] = df_weather.groupby("region")["temperature_mean_c"].transform(
        lambda s: s.interpolate(method="linear").bfill().ffill()
    )
```
- Linearly interpolates continuous temperature and humidity along regional time series.

```python
    df_weather["rainfall_missing_flag"] = df_weather["rainfall_mm"].isnull().astype(int)
    df_weather["rainfall_mm"] = df_weather["rainfall_mm"].fillna(0.0)
```
- Distinguishes sensor dropouts from genuine zero rainfall by creating a flag before filling NaNs with 0.0 mm.

```python
    df_weather_seasonal = df_weather.groupby(["region", "season"]).agg(
        seasonal_rainfall_mm=("rainfall_mm", "sum"),
        mean_temperature_c=("temperature_mean_c", "mean"),
        min_temperature_c=("temperature_min_c", "min"),
        max_temperature_c=("temperature_max_c", "max"),
        temperature_range_c=("temperature_mean_c", lambda s: s.max() - s.min()),
        mean_humidity_pct=("humidity_pct", "mean"),
        rainy_days_count=("rainfall_mm", lambda s: (s > 1.0).sum()),
        weather_sensor_missing_days=("rainfall_missing_flag", "sum")
    ).reset_index().round(2)
```
- Aggregates daily meteorological records into growing-season summaries per `(region, season)`.

### 5. Cleaning Harvest (Lines 187–225)
```python
    df_harvest = df_harvest.drop_duplicates().drop_duplicates(subset=["field_id", "season"], keep="first")
    invalid_mask = (df_harvest["yield_kg_per_ha"] <= 0) | (df_harvest["yield_kg_per_ha"] > 15000)
    df_harvest = df_harvest[~invalid_mask].copy()
```
- Deduplicates harvest records.
- Filters out corrupted entries: negative values and 10x typos ($>15,000\text{ kg/ha}$). Valid yield records: 988.

### 6. Relational Merge & Row Count Audit (Lines 227–285)
```python
    merged = df_harvest.copy()
    row_count_track = [("0_harvest_base", len(merged))]
    
    merged = merged.merge(df_fields[["field_id", "region", "area_hectares", "crop"]], on="field_id", how="left")
    merged = merged.merge(df_practices[["field_id", "season", "irrigation_type", "fertilizer_type", "sowing_date"]], 
                          on=["field_id", "season"], how="left")
    merged = merged.merge(df_weather_seasonal, on=["region", "season"], how="left")
    merged = merged.merge(df_soil[soil_cols], on=["field_id", "season"], how="left")
```
- Uses cleaned harvest records as the analytical base spine.
- Executes sequential left joins with fields (1:1), practices (1:1), weather (N:1), and soil (1:1).

```python
    merged["soil_tested"] = merged["soil_tested"].fillna(0).astype(int)
    for scol in ["soil_ph", "soil_moisture_pct", "nitrogen_ppm", "phosphorus_ppm", "potassium_ppm"]:
        merged[scol] = merged.groupby("region")[scol].transform(lambda grp: grp.fillna(grp.median()))
```
- Untested fields receive `soil_tested = 0` and are imputed with regional medians, preserving harvest rows while retaining the missingness signal.

```python
    assert row_count_track[0][1] == row_count_track[-1][1], "CRITICAL ERROR: Merge changed row count!"
```
- Validates row count constancy: exactly 988 records from start to finish (zero Cartesian expansion).
- Exports `agrinova_cleaned.csv` and `cleaning_log.md`.

---

## 4. `src/feature_engineering.py`

This module engineers agronomic covariates, evaluates PCA, and fits a predictive machine learning model with field-grouped validation.

### Feature Engineering Function (Lines 25–65)
```python
def engineer_features(df):
    df["sowing_date"] = pd.to_datetime(df["sowing_date"])
    df["sowing_month"] = df["sowing_date"].dt.month
    df["sowing_day_of_year"] = df["sowing_date"].dt.dayofyear
```
- Extracts calendar month and day-of-year from sowing dates.

```python
    def categorize_sowing_window(month):
        if month in [3, 4]: return "Early Spring"
        elif month in [5, 6]: return "Late Spring"
        elif month in [9, 10]: return "Autumn"
        elif month in [11, 12]: return "Winter"
        else: return "Summer"
    df["sowing_period"] = df["sowing_month"].apply(categorize_sowing_window)
```
- Groups planting dates into agronomic sowing windows.

```python
    df["rain_per_rainy_day"] = (df["seasonal_rainfall_mm"] / (df["rainy_days_count"] + 1e-5)).round(2)
    df["heat_stress_index"] = df["mean_temperature_c"].apply(lambda t: max(0.0, t - 22.0)).round(2)
```
- `rain_per_rainy_day`: Measures precipitation intensity (heavy downpours vs. steady rain).
- `heat_stress_index`: Computes thermal degree-days above the 22°C vegetative threshold.

```python
    optimal_crop_ph = {"Maize": 6.5, "Wheat": 6.4, "Soybean": 6.5, "Barley": 6.8}
    df["optimal_ph"] = df["crop"].map(optimal_crop_ph).fillna(6.5)
    df["crop_ph_deviation"] = (df["soil_ph"] - df["optimal_ph"]).abs().round(2)
```
- Computes physiological soil pH stress: the absolute distance between actual soil pH and the crop species' documented optimal pH.

```python
    df["soil_n_p_ratio"] = (df["nitrogen_ppm"] / (df["phosphorus_ppm"] + 1e-5)).round(2)
    df["soil_npk_total"] = (df["nitrogen_ppm"] + df["phosphorus_ppm"] + df["potassium_ppm"]).round(1)
```
- Stoichiometric nutrient ratio and macronutrient sum.

```python
    field_stats = df.groupby("field_id")["yield_kg_per_ha"].agg(
        field_mean_yield="mean", field_std_yield="std", season_count="count"
    ).reset_index()
    field_stats["field_yield_cv"] = (field_stats["field_std_yield"] / (field_stats["field_mean_yield"] + 1e-5) * 100).round(2)
```
- Computes each field's multi-season Coefficient of Variation (CV = SD / Mean * 100) to quantify historical production stability.

### PCA Evaluation (Lines 67–110)
```python
def run_pca_analysis(df_feat, out_path):
    env_vars = ["seasonal_rainfall_mm", "mean_temperature_c", "temperature_range_c", 
                "mean_humidity_pct", "soil_ph", "soil_moisture_pct", 
                "nitrogen_ppm", "phosphorus_ppm", "potassium_ppm"]
    X_scaled = StandardScaler().fit_transform(df_feat[env_vars].dropna())
    pca = PCA().fit(X_scaled)
```
- Standardizes continuous environmental covariates to zero mean and unit variance.
- Fits PCA to assess dimensionality reduction trade-offs: PC1–PC3 explain 75.7% of variance, but raw engineered features are retained for primary modeling because they preserve agronomic interpretability.
- Exports `pca_analysis.json`, `pca_loadings.csv`, and `pca_report.md`.

### Leakage-Free Predictive Modeling (Lines 112–215)
```python
    # STRICT EXCLUSIONS to prevent target leakage:
    # 'quality_grade': determined after harvest
    # 'harvest_date': post-harvest event
    # 'field_mean_yield', 'field_std_yield', 'field_yield_cv': contains target in historical calculation
    # 'field_id', 'season': identifiers
```
- Documents and enforces strict feature screening to eliminate target leakage.

```python
    df_encoded = pd.get_dummies(df_feat[feature_cols_num + feature_cols_cat], drop_first=True, dtype=float)
    X = df_encoded.copy()
    y = df_feat["yield_kg_per_ha"].values
    groups = df_feat["field_id"].values
```
- One-hot encodes nominal categoricals (`crop`, `region`, `irrigation_type`, `fertilizer_type`, `sowing_period`).

```python
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
```
- **Field-Grouped Split:** Partitions data at the field level (200 training fields, 50 test fields). Guarantees that fields in the test set never appeared in the training set across any season, preventing cross-season leakage.

```python
    model = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_split=5, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
```
- Trains an ensemble of 300 decision trees with depth regularization.

```python
    perm_res = permutation_importance(model, X_test, y_test, n_repeats=15, random_state=42)
    mi_scores = mutual_info_regression(X_train, y_train, random_state=42)
```
- Computes permutation feature importance on held-out test data (unbiased by feature cardinality) and mutual information on training data.
- Exports model metrics to `model_metrics.json` ($R^2 = 0.8721$, $\text{RMSE} = 732.82\text{ kg/ha}$) and rankings to `selected_features.md`.

---

## 5. `src/generate_visualizations.py`

This module creates the 8 publication-grade charts saved in `outputs/charts/`.

### Aesthetics Configuration (Lines 22–32)
```python
    sns.set_theme(style="whitegrid", font="sans-serif")
    palette = sns.color_palette("deep")
```
- Enforces clean styling: whitegrid background, sans-serif typography, and consistent color palettes.

### Chart Implementations (Lines 34–290)
1. **Regional Comparison (`regional_yield_comparison.png`):**
   - Left subplot: Boxplot of yield by region, sorted by median, with red marker for mean and sample counts annotated.
   - Right subplot: Stacked bar chart showing crop composition percentages across regions.
2. **Rainfall Response (`rainfall_versus_yield.png`):**
   - Left subplot: Scatterplot with a quadratic regression fit (`order=2`) illustrating diminishing returns above 750 mm.
   - Right subplot: Rainfall scatter stratified by irrigation method, showing how irrigation buffers dry conditions.
3. **Soil Analysis (`soil_correlation_heatmap.png`):**
   - Left subplot: Masked lower-triangle correlation heatmap among soil and environmental variables.
   - Right subplot: Scatterplot of soil pH vs. yield with an optimal band overlay (pH 6.2–7.0).
4. **Irrigation & Fertilizer (`irrigation_fertilizer_practices.png`):**
   - Left subplot: Boxplots of yield across Drip, Sprinkler, Flood, and Rainfed practices.
   - Right subplot: Bar chart of fertilizer practices stratified by crop species with 95% confidence intervals.
5. **Sowing Windows (`sowing_period_analysis.png`):**
   - Left subplot: Yield distributions across sowing periods faceted by crop.
   - Right subplot: Planting calendar day-of-year vs. yield with a May 1 pivot line.
6. **Field Stability (`field_yield_stability.png`):**
   - Left subplot: Distribution of field Coefficient of Variation (CV %) with median and 90th-percentile lines.
   - Right subplot: Multi-season yield trajectories (2021–2024) comparing the 4 most volatile fields against the 4 most stable fields.
7. **Feature Importance (`feature_importance_ranking.png`):**
   - Horizontal bar chart of the top 10 predictors ranked by test permutation importance.
8. **Quality Grades (`quality_grade_yield_analysis.png`):**
   - Boxplot validating the expected post-harvest relationship between yield and Quality Grades A, B, C, and D.

---

## 6. Notebook Compilation & Validation Scripts

### `src/build_notebook.py`
- Uses Python's `nbformat` library to construct `notebooks/agrinova_eda.ipynb` programmatically.
- Organizes content into 11 alternating Markdown narrative and code cells:
  - Header & mission statement.
  - Scientific library imports and environment initialization.
  - Data loading with flexible path discovery (`Path("../data/raw")` vs. `Path("data/raw")`).
  - Structural audit table generation.
  - Cleaning pipeline and relational merge execution.
  - Analyses A through F (Regional, Rainfall, Soil, Irrigation, Sowing, Field Stability).
  - Feature engineering and PCA evaluation.
  - Model fitting, test evaluation, and permutation importance.
  - Answers to the six primary business questions.
- Serializes the notebook structure to valid `.ipynb` JSON format.

### `src/validate_notebook_execution.py`
- Uses `matplotlib.use("Agg")` and stubs `plt.show = lambda: None` to ensure headless execution without blocking GUI windows.
- Iterates through every code cell in `agrinova_eda.ipynb`, executes the code within a shared `global_scope`, and confirms that all cells execute from beginning to end without syntax, import, or runtime errors.

---

## 7. `src/generate_excel_workbook.py`

This script builds the 10-sheet Microsoft Excel workbook `AgriNova_Round3_Excel_Analysis.xlsx`.

### Setup & Palette Configuration (Lines 25–125)
- Uses `openpyxl` to construct worksheets, tables, formulas, styles, and native charts.
- Configures a professional palette:
  - `primary_header_fill`: Deep Forest Green (`#1E4620`), white bold text.
  - `secondary_header_fill`: Medium Forest Green (`#2E7D32`), white bold text.
  - `accent_fill`: Light Sage (`#E8F5E9`), green bold text.
  - `kpi_fill`: Soft Mint (`#F1F8E9`), green border (`#A5D6A7`).
  - `zebra_fill`: Alternate row tint (`#F9FBF9`).
  - `total_fill`: Summary total row tint (`#DCEDC8`), double-bottom accounting border.

### Sheet 2: Cleaned Data (Lines 130–185)
- Writes all 988 records and 29 columns.
- Applies number formats: dates (`yyyy-mm-dd`), yield ($t/ha$ as `0.00`, $kg/ha$ as `#,##0.0`), pH (`0.00`), rainfall (`#,##0.0`).
- Freezes row 1 (`ws.freeze_panes = "A2"`).
- Wraps the data range `A1:AC989` in an official Excel Table named **`AgriData`** with style `TableStyleMedium9`.
- Adds a 3-color conditional formatting gradient on `yield_t_per_ha` (Column D).

### Sheet 3: Statistical Analysis (Lines 190–280)
- Writes the Yield Descriptive Statistics Table using native uppercase Excel formulas:
  - Count: `=COUNT('Cleaned Data'!$D$2:$D$989)`
  - Missing: `=COUNTBLANK('Cleaned Data'!$D$2:$D$989)`
  - Mean: `=AVERAGE('Cleaned Data'!$D$2:$D$989)`
  - Median: `=MEDIAN('Cleaned Data'!$D$2:$D$989)`
  - Min/Max: `=MIN(...)` / `=MAX(...)`
  - Range: `=MAX(...) - MIN(...)`
  - Std Dev: `=STDEV.S('Cleaned Data'!$D$2:$D$989)`
  - Variance: `=VAR.S('Cleaned Data'!$D$2:$D$989)`
  - Quartiles: `=QUARTILE.INC('Cleaned Data'!$D$2:$D$989, 1)` and `=QUARTILE.INC(..., 3)`
  - IQR: `=Q3 - Q1`
  - CV: `=STDEV.S / AVERAGE` (formatted as `0.00%`)
- Writes the Environmental Correlation Table with `=CORREL(...)` formulas linking each covariate to `yield_t_per_ha`.

### Sheets 4–8: Analytical Domain Worksheets (Lines 285–560)
- **Sheet 4 (Region):** Regional summary table with `=COUNTIF(...)` and `=AVERAGEIF(...)` formulas; horizontal `BarChart` of average yield by region; regional crop breakdown table.
- **Sheet 5 (Rainfall):** Bivariate regression metrics (`SLOPE`, `INTERCEPT`, `RSQ`, `CORREL`); non-linear rainfall intervals table ($<500\text{ mm}$, $500–750\text{ mm}$, $750–900\text{ mm}$, $\ge 900\text{ mm}$); clustered column chart.
- **Sheet 6 (Soil):** Soil pH categories table (Acidic, Near-Neutral, Alkaline); macronutrient summary table (N, P, K); clustered column chart.
- **Sheet 7 (Irrigation):** Water regime summary table (Drip, Sprinkler, Flood, Rainfed) with `=COUNTIF` and `=AVERAGEIF`; cross-tabulation of irrigation by region; clustered column chart.
- **Sheet 8 (Sowing):** Sowing period summary table (Early Spring, Late Spring, Autumn, Winter) and calendar quarters table (Q1–Q4); clustered column chart.

### Sheet 9: Yield Variability (Lines 565–640)
- Filters fields meeting the $\ge 3$ seasons screening rule.
- Populates the Top 10 Most Unstable Fields table (sorted by CV descending) and the Top 10 Most Resilient Fields table (lowest CV).
- Embeds a horizontal `BarChart` comparing field CV values.

### Sheet 10: Pivot Analysis (Lines 645–735)
- Builds 6 multi-dimensional analytical matrices:
  - Model 1: Crop $\times$ Region Matrix (two-way cross-tabulation).
  - Model 2: Crop $\times$ Irrigation Matrix.
  - Model 3: Multi-Season Yield Trajectory (2021–2024 annual trend).
- Embeds a Clustered Column Chart for Crop by Region and a Line Chart for the annual yield trend.
- Documents instructions for activating dynamic desktop Excel slicers.

### Sheet 1: Executive Summary (Dashboard) (Lines 740–835)
- Dashboard title banner.
- **6 Merged KPI Cards:**
  - Card 1: `=COUNT('Cleaned Data'!$A$2:$A$989)` (Total observations: 988)
  - Card 2: `=COUNTA('Yield by Region'!$A$6:$A$10)` (Regions: 5)
  - Card 3: `4` (Crops)
  - Card 4: `='Statistical Analysis'!$B$8` (Average yield: 4.92 t/ha)
  - Card 5: `='Statistical Analysis'!$B$9` (Median yield: 4.49 t/ha)
  - Card 6: `='Statistical Analysis'!$B$13` (Std dev: 2.22 t/ha)
- Core Business Questions table with formula-linked findings.
- Embeds 4 executive charts positioned in a clean 2x2 layout.

### Layout & Recalculation Settings (Lines 840–875)
- Auto-fits column widths across all 10 sheets with character-length padding.
- Sets `wb.calculation.calcMode = "auto"` and `wb.calculation.fullCalcOnLoad = True` to force Excel to recalculate all formulas upon opening.
- Saves the workbook to `AgriNova_Round3_Excel_Analysis.xlsx` (with a copy in `AgriNova/`).

---

## 8. `src/validate_excel_workbook.py`

This module provides automated quality assurance for the generated `.xlsx` workbook.

### Validation Checks (Lines 15–95)
```python
    expected_sheets = [
        "Executive Summary", "Cleaned Data", "Statistical Analysis", "Yield by Region",
        "Rainfall Analysis", "Soil Analysis", "Irrigation Analysis", "Sowing Period Analysis",
        "Yield Variability", "Pivot Analysis"
    ]
    assert actual_sheets == expected_sheets
```
- **Check 1:** Verifies that all 10 sheets exist in the exact required sequence.

```python
    assert ws_data.max_row == 989 and ws_data.max_column == 29
    assert "AgriData" in ws_data.tables
    assert ws_data.tables["AgriData"].ref == "A1:AC989"
```
- **Check 2:** Verifies that Sheet 2 contains 989 rows (1 header + 988 data rows), 29 columns, and that table `AgriData` spans range `A1:AC989`.

```python
    assert "COUNT" in str(ws_stats["B6"].value)
    assert "AVERAGE" in str(ws_stats["B8"].value)
    assert "CORREL" in str(ws_stats["C22"].value)
```
- **Check 3:** Confirms formula integrity: Count uses `COUNT`, Mean uses `AVERAGE`, and Correlation uses `CORREL`.

```python
    assert total_charts >= 8
```
- **Check 4:** Audits charts across all worksheets, verifying that at least 8 native charts exist (finds 12 total).

```python
    assert "COUNT" in str(ws_exec["B5"].value)
    assert "Yield by Region" in str(ws_exec["C10"].value)
```
- **Check 5:** Verifies that Dashboard KPI Card 1 links dynamically via formula and that Question 1 links to the regional analysis sheet.
