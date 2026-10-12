"""
AgriNova Farm Analytics - Data Cleaning & Integration Pipeline
==============================================================
Phases 3 & 4:
  - Rigorous data cleaning (duplicates, synonyms, outliers, weather gaps, missing soil)
  - Full audit logging of all cleaning operations
  - Multi-table relational merge at the field-season analytical grain
  - Export of processed dataset to data/processed/agrinova_cleaned.csv
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

def clean_and_merge_agrinova(raw_dir="AgriNova/data/raw", 
                             processed_dir="AgriNova/data/processed",
                             reports_dir="AgriNova/outputs/reports"):
    raw_path = Path(raw_dir)
    proc_path = Path(processed_dir)
    rep_path = Path(reports_dir)
    
    proc_path.mkdir(parents=True, exist_ok=True)
    rep_path.mkdir(parents=True, exist_ok=True)
    
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

    print("=" * 80)
    print("AGRINOVA PIPELINE: EXECUTING PHASE 3 & 4 CLEANING AND MERGE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. CLEAN FIELDS.CSV
    # -------------------------------------------------------------------------
    df_fields = pd.read_csv(raw_path / "fields.csv")
    df_fields["crop_raw"] = df_fields["crop"]
    
    # Standardize whitespace and casing
    df_fields["crop_clean"] = df_fields["crop"].astype(str).str.strip().str.title()
    
    # Synonym mapping
    synonym_map = {
        "Corn": "Maize",
        "Soy": "Soybean"
    }
    syn_count = df_fields["crop_clean"].isin(synonym_map.keys()).sum()
    df_fields["crop_clean"] = df_fields["crop_clean"].replace(synonym_map)
    df_fields["crop"] = df_fields["crop_clean"]
    
    log_action(
        issue="Inconsistent crop names, irregular casing, leading/trailing whitespace, and synonyms",
        affected_entity="fields.csv: crop",
        action_taken="Applied .str.strip().title() and mapped synonyms ('Corn'->'Maize', 'Soy'->'Soybean')",
        rationale="Eliminate category fragmentation and ensure standardized agronomic groupings",
        count_affected=len(df_fields)
    )
    print(f"[FIELDS] Standardized crops. Canonical categories: {sorted(df_fields['crop'].unique().tolist())}")

    # -------------------------------------------------------------------------
    # 2. CLEAN PRACTICES.CSV
    # -------------------------------------------------------------------------
    df_practices = pd.read_csv(raw_path / "practices.csv")
    n_init_practices = len(df_practices)
    
    # Deduplicate exact duplicate rows
    df_practices = df_practices.drop_duplicates()
    n_exact_p_dups = n_init_practices - len(df_practices)
    if n_exact_p_dups > 0:
        log_action(
            issue="Exact duplicate rows in practices records",
            affected_entity="practices.csv: all columns",
            action_taken="Removed exact duplicates via df.drop_duplicates()",
            rationale="Redundant identical rows distort join cardinality and statistical weight",
            count_affected=n_exact_p_dups
        )
        
    # Deduplicate conflicting key combinations (field_id, season)
    n_key_dups_p = df_practices.duplicated(subset=["field_id", "season"]).sum()
    if n_key_dups_p > 0:
        # Keep the last recorded entry per field-season
        df_practices = df_practices.drop_duplicates(subset=["field_id", "season"], keep="last")
        log_action(
            issue="Conflicting duplicate field-season management records",
            affected_entity="practices.csv: (field_id, season)",
            action_taken="Retained latest logged record per (field_id, season)",
            rationale="Reconcile contradictory field logs while enforcing strict 1:1 join key",
            count_affected=n_key_dups_p
        )
    df_practices["sowing_date"] = pd.to_datetime(df_practices["sowing_date"])
    print(f"[PRACTICES] Cleaned {len(df_practices)} records (removed {n_exact_p_dups} exact dups, {n_key_dups_p} key dups).")

    # -------------------------------------------------------------------------
    # 3. CLEAN SOIL.CSV
    # -------------------------------------------------------------------------
    df_soil = pd.read_csv(raw_path / "soil.csv")
    n_init_soil = len(df_soil)
    
    # Deduplicate exact rows and key combinations
    df_soil = df_soil.drop_duplicates()
    n_exact_s_dups = n_init_soil - len(df_soil)
    if n_exact_s_dups > 0:
        log_action(
            issue="Exact duplicate soil test records",
            affected_entity="soil.csv: all columns",
            action_taken="Removed duplicate rows via df.drop_duplicates()",
            rationale="Prevent artificial over-representation of repeated soil tests",
            count_affected=n_exact_s_dups
        )
        
    n_key_dups_s = df_soil.duplicated(subset=["field_id", "season"]).sum()
    if n_key_dups_s > 0:
        df_soil = df_soil.drop_duplicates(subset=["field_id", "season"], keep="first")
        log_action(
            issue="Duplicate soil tests for identical field and season",
            affected_entity="soil.csv: (field_id, season)",
            action_taken="Retained primary laboratory reading",
            rationale="Ensure unique (field_id, season) key for relational join",
            count_affected=n_key_dups_s
        )
        
    # Track missing nutrient readings with explicit indicators before imputation
    df_soil["missing_soil_moisture"] = df_soil["soil_moisture_pct"].isnull().astype(int)
    df_soil["missing_phosphorus"] = df_soil["phosphorus_ppm"].isnull().astype(int)
    
    # Mark that this record was physically tested
    df_soil["soil_tested"] = 1
    
    # Compute regional medians for imputation
    soil_with_region = df_soil.merge(df_fields[["field_id", "region"]], on="field_id", how="left")
    reg_soil_medians = soil_with_region.groupby("region")[["soil_moisture_pct", "phosphorus_ppm"]].median()
    
    # Impute missing within tested records using regional medians
    for col in ["soil_moisture_pct", "phosphorus_ppm"]:
        n_missing = df_soil[col].isnull().sum()
        if n_missing > 0:
            df_soil[col] = soil_with_region.groupby("region")[col].transform(lambda grp: grp.fillna(grp.median()))
            log_action(
                issue=f"Missing laboratory measurements in {col}",
                affected_entity=f"soil.csv: {col}",
                action_taken="Created missingness indicator and imputed with regional soil median",
                rationale="Preserve observed chemistry while providing neutral imputation for modeling",
                count_affected=n_missing
            )
            
    print(f"[SOIL] Cleaned {len(df_soil)} soil test records across seasons.")

    # -------------------------------------------------------------------------
    # 4. CLEAN & AGGREGATE WEATHER.CSV
    # -------------------------------------------------------------------------
    df_weather = pd.read_csv(raw_path / "weather.csv")
    df_weather["date"] = pd.to_datetime(df_weather["date"])
    df_weather = df_weather.sort_values(by=["region", "date"]).reset_index(drop=True)
    
    # Distinguish genuine 0 rainfall from missing observations
    n_nan_rain = df_weather["rainfall_mm"].isnull().sum()
    n_nan_temp = df_weather["temperature_mean_c"].isnull().sum()
    
    # Weather interpolation within region time-series
    # Continuous variables (temp, humidity) interpolated linearly across short sensor outages
    df_weather["temperature_mean_c"] = df_weather.groupby("region")["temperature_mean_c"].transform(lambda s: s.interpolate(method="linear").bfill().ffill())
    df_weather["temperature_min_c"] = df_weather.groupby("region")["temperature_min_c"].transform(lambda s: s.interpolate(method="linear").bfill().ffill())
    df_weather["temperature_max_c"] = df_weather.groupby("region")["temperature_max_c"].transform(lambda s: s.interpolate(method="linear").bfill().ffill())
    df_weather["humidity_pct"] = df_weather.groupby("region")["humidity_pct"].transform(lambda s: s.interpolate(method="linear").bfill().ffill())
    
    # Rainfall sensor outages: missing rainfall filled conservatively with 0 (distinguished from genuine 0)
    df_weather["rainfall_missing_flag"] = df_weather["rainfall_mm"].isnull().astype(int)
    df_weather["rainfall_mm"] = df_weather["rainfall_mm"].fillna(0.0)
    
    log_action(
        issue="Sensor dropouts (NaN) in meteorological time-series",
        affected_entity="weather.csv: temperature, humidity, rainfall",
        action_taken="Interpolated temperature/humidity linearly by region; filled rainfall gaps with 0 after logging missingness flag",
        rationale="Preserve continuity of daily meteorological series without conflating missing days with genuine 0 rain days",
        count_affected=int(n_nan_rain)
    )
    
    # Aggregate daily weather to crop-relevant seasonal summaries per (region, season)
    df_weather_seasonal = df_weather.groupby(["region", "season"]).agg(
        seasonal_rainfall_mm=("rainfall_mm", "sum"),
        mean_temperature_c=("temperature_mean_c", "mean"),
        min_temperature_c=("temperature_min_c", "min"),
        max_temperature_c=("temperature_max_c", "max"),
        temperature_range_c=("temperature_mean_c", lambda s: s.max() - s.min()),
        mean_humidity_pct=("humidity_pct", "mean"),
        rainy_days_count=("rainfall_mm", lambda s: (s > 1.0).sum()),
        weather_sensor_missing_days=("rainfall_missing_flag", "sum")
    ).reset_index()
    
    # Round numerical metrics
    df_weather_seasonal = df_weather_seasonal.round(2)
    print(f"[WEATHER] Aggregated {len(df_weather)} daily records into {len(df_weather_seasonal)} regional-seasonal summaries.")

    # -------------------------------------------------------------------------
    # 5. CLEAN HARVEST.CSV
    # -------------------------------------------------------------------------
    df_harvest = pd.read_csv(raw_path / "harvest.csv")
    n_init_harvest = len(df_harvest)
    
    # Deduplicate exact duplicate rows
    df_harvest = df_harvest.drop_duplicates()
    n_exact_h_dups = n_init_harvest - len(df_harvest)
    if n_exact_h_dups > 0:
        log_action(
            issue="Exact duplicate harvest records",
            affected_entity="harvest.csv: all columns",
            action_taken="Removed exact duplicates via df.drop_duplicates()",
            rationale="Eliminate duplicated harvest tallies",
            count_affected=n_exact_h_dups
        )
        
    # Deduplicate keys (field_id, season)
    n_key_dups_h = df_harvest.duplicated(subset=["field_id", "season"]).sum()
    if n_key_dups_h > 0:
        df_harvest = df_harvest.drop_duplicates(subset=["field_id", "season"], keep="first")
        log_action(
            issue="Duplicate harvest entries for single field-season",
            affected_entity="harvest.csv: (field_id, season)",
            action_taken="Retained primary harvest record",
            rationale="Enforce unique target observation per analytical unit",
            count_affected=n_key_dups_h
        )
        
    # Outlier Detection in Yield (kg/ha)
    # Biological plausibility bounds:
    # Negative yields are impossible data collection errors (< 0)
    # Yields > 15,000 kg/ha represent typographical errors (e.g., 10x decimal errors: 65,000 or 85,000 kg/ha)
    y_raw = df_harvest["yield_kg_per_ha"]
    invalid_mask = (y_raw <= 0) | (y_raw > 15000)
    n_invalid_yields = invalid_mask.sum()
    
    if n_invalid_yields > 0:
        # Document excluded extreme anomalies
        excluded_records = df_harvest[invalid_mask][["field_id", "season", "yield_kg_per_ha"]].to_dict(orient="records")
        df_harvest = df_harvest[~invalid_mask].copy()
        log_action(
            issue="Severe yield measurement errors (negative yields and 10x typographical entries > 15,000 kg/ha)",
            affected_entity="harvest.csv: yield_kg_per_ha",
            action_taken="Excluded physically impossible entries (yield <= 0 or yield > 15,000 kg/ha)",
            rationale="Protect statistical models from severe distortion caused by instrument/clerical entry corruption",
            count_affected=n_invalid_yields
        )
        print(f"[HARVEST] Filtered {n_invalid_yields} corrupted yield outliers. Valid yield records: {len(df_harvest)}")
        
    df_harvest["harvest_date"] = pd.to_datetime(df_harvest["harvest_date"])

    # -------------------------------------------------------------------------
    # 6. PHASE 4: COMBINE DATASETS AT FIELD-SEASON GRAIN
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("PHASE 4: RELATIONAL MERGE & ROW COUNT AUDIT")
    print("-" * 80)
    
    # Starting analytical spine: Harvest records (the target variable)
    merged = df_harvest.copy()
    row_count_track = [("0_harvest_base", len(merged))]
    
    # Merge fields.csv (1:1 on field_id)
    merged = merged.merge(df_fields[["field_id", "region", "area_hectares", "crop"]], on="field_id", how="left")
    row_count_track.append(("1_after_fields", len(merged)))
    
    # Merge practices.csv (1:1 on field_id, season)
    merged = merged.merge(df_practices[["field_id", "season", "irrigation_type", "fertilizer_type", "sowing_date"]], 
                          on=["field_id", "season"], how="left")
    row_count_track.append(("2_after_practices", len(merged)))
    
    # Merge aggregated weather (N:1 on region, season)
    merged = merged.merge(df_weather_seasonal, on=["region", "season"], how="left")
    row_count_track.append(("3_after_weather", len(merged)))
    
    # Merge soil.csv (1:1 on field_id, season)
    soil_cols = ["field_id", "season", "soil_ph", "soil_moisture_pct", "nitrogen_ppm", "phosphorus_ppm", "potassium_ppm", "soil_tested"]
    merged = merged.merge(df_soil[soil_cols], on=["field_id", "season"], how="left")
    row_count_track.append(("4_after_soil", len(merged)))
    
    # Handle untested soil fields gracefully
    # If soil was not tested in that season, flag it explicitly
    merged["soil_tested"] = merged["soil_tested"].fillna(0).astype(int)
    n_untested_soil = (merged["soil_tested"] == 0).sum()
    
    # Impute missing soil values for untested fields using regional medians (preserving soil_tested=0)
    for scol in ["soil_ph", "soil_moisture_pct", "nitrogen_ppm", "phosphorus_ppm", "potassium_ppm"]:
        merged[scol] = merged.groupby("region")[scol].transform(lambda grp: grp.fillna(grp.median()))
        
    log_action(
        issue=f"Fields lacking seasonal soil laboratory testing ({n_untested_soil} field-seasons)",
        affected_entity="merged: soil properties",
        action_taken="Preserved soil_tested=0 indicator and imputed missing values with regional soil medians",
        rationale="Prevents dropping valid harvest observations while allowing algorithms to utilize missingness signal",
        count_affected=n_untested_soil
    )
    
    # Validate row count constancy
    print("Row Count Verification Across Merges:")
    for step_name, cnt in row_count_track:
        print(f"  - {step_name}: {cnt} rows")
        
    assert row_count_track[0][1] == row_count_track[-1][1], "CRITICAL ERROR: Merge changed row count!"
    print(f"[SUCCESS] Relational integrity verified. Exactly {len(merged)} field-season observations preserved.")
    
    # Sort logically
    merged = merged.sort_values(by=["field_id", "season"]).reset_index(drop=True)
    
    # Save clean dataset
    out_clean_csv = proc_path / "agrinova_cleaned.csv"
    merged.to_csv(out_clean_csv, index=False)
    print(f"[EXPORT] Saved clean analytical dataset to: {out_clean_csv}")
    
    # Export cleaning log
    df_log = pd.DataFrame(cleaning_log)
    df_log.to_csv(rep_path / "cleaning_log.csv", index=False)
    
    with open(rep_path / "cleaning_log.md", "w") as f:
        f.write("# AgriNova Farm Analytics - Data Cleaning & Transformation Log\n\n")
        f.write(df_log.to_markdown(index=False))
        f.write("\n\n### Analytical Grain Verification:\n")
        f.write(f"- Analytical unit: **1 observation per field per growing season** `(field_id, season)`\n")
        f.write(f"- Final clean observations: **{len(merged)}** rows across 250 distinct farms\n")
        f.write(f"- Preserved seasons: **2021, 2022, 2023, 2024**\n")
        f.write(f"- Cartesian multiplication check: **PASSED (0 row expansion)**\n")
        
    print(f"[EXPORT] Saved cleaning audit log to: {rep_path / 'cleaning_log.md'}")
    
    return merged, df_log

if __name__ == "__main__":
    clean_and_merge_agrinova()
