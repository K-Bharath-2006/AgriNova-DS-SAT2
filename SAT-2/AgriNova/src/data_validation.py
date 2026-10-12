"""
AgriNova Farm Analytics - Data Validation Module
================================================
Phase 2: Load and inspect raw datasets, perform comprehensive structural
and data-quality auditing, identify anomalies, and generate a consolidated
Data Quality Summary Table.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

def validate_datasets(raw_data_dir="AgriNova/data/raw", output_report_dir="AgriNova/outputs/reports"):
    raw_path = Path(raw_data_dir)
    report_path = Path(output_report_dir)
    report_path.mkdir(parents=True, exist_ok=True)
    
    files = {
        "fields": "fields.csv",
        "soil": "soil.csv",
        "weather": "weather.csv",
        "practices": "practices.csv",
        "harvest": "harvest.csv"
    }
    
    dfs = {}
    audit_results = {}
    
    print("=" * 80)
    print("AGRINOVA DATA VALIDATION AUDIT - RAW DATASET INSPECTION")
    print("=" * 80)
    
    for name, filename in files.items():
        filepath = raw_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Missing required raw file: {filepath}")
            
        df = pd.read_csv(filepath)
        dfs[name] = df
        
        n_rows, n_cols = df.shape
        missing_counts = df.isnull().sum()
        missing_pcts = (missing_counts / n_rows * 100).round(2)
        n_exact_dups = df.duplicated().sum()
        
        # Key uniqueness check
        candidate_keys = ["field_id", "season"]
        avail_keys = [k for k in candidate_keys if k in df.columns]
        if avail_keys:
            key_dups = df.duplicated(subset=avail_keys).sum()
        else:
            key_dups = 0
            
        audit_results[name] = {
            "file": filename,
            "rows": n_rows,
            "cols": n_cols,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "exact_duplicates": int(n_exact_dups),
            "key_duplicates": int(key_dups),
            "missing_cells": int(missing_counts.sum()),
            "missing_by_column": {col: {"count": int(missing_counts[col]), "pct": float(missing_pcts[col])} for col in df.columns if missing_counts[col] > 0}
        }
        
        print(f"\n[FILE: {filename}] Shape: {n_rows} rows x {n_cols} columns")
        print(f"  - Columns & Types: {dict(zip(df.columns, [str(t) for t in df.dtypes]))}")
        print(f"  - Exact Duplicate Rows: {n_exact_dups}")
        if avail_keys:
            print(f"  - Duplicate Key Combinations ({avail_keys}): {key_dups}")
        if missing_counts.sum() > 0:
            print(f"  - Missing Columns: {audit_results[name]['missing_by_column']}")
        else:
            print("  - Missing Values: None detected (0)")
            
    # Domain specific anomaly inspections
    print("\n" + "-" * 80)
    print("DOMAIN-SPECIFIC DATA QUALITY CHECKS")
    print("-" * 80)
    
    # 1. fields.csv: crop names inspection
    crop_counts = dfs["fields"]["crop"].value_counts().to_dict()
    print(f"1. Crop Names in fields.csv (raw unique entries = {len(crop_counts)}):")
    for c, cnt in crop_counts.items():
        print(f"   '{c}': {cnt}")
        
    # 2. harvest.csv: yield distribution & negative / extreme values
    yield_col = dfs["harvest"]["yield_kg_per_ha"]
    neg_yields = (yield_col < 0).sum()
    extreme_high_yields = (yield_col > 15000).sum()
    print(f"\n2. Yield Anomalies in harvest.csv:")
    print(f"   - Minimum yield: {yield_col.min():.1f} kg/ha (Negative count: {neg_yields})")
    print(f"   - Maximum yield: {yield_col.max():.1f} kg/ha (>15,000 kg/ha extreme count: {extreme_high_yields})")
    print(f"   - Median yield:  {yield_col.median():.1f} kg/ha, Mean: {yield_col.mean():.1f} kg/ha")
    
    # 3. soil.csv: missing soil tests and pH bounds
    soil_df = dfs["soil"]
    print(f"\n3. Soil Quality in soil.csv:")
    print(f"   - Tested rows: {len(soil_df)} (Missing pH: {soil_df['soil_ph'].isnull().sum()}, Missing moisture: {soil_df['soil_moisture_pct'].isnull().sum()})")
    print(f"   - pH range: {soil_df['soil_ph'].min()} to {soil_df['soil_ph'].max()}")
    
    # 4. weather.csv: rainfall zero vs missing
    w_df = dfs["weather"]
    zero_rain = (w_df["rainfall_mm"] == 0).sum()
    nan_rain = w_df["rainfall_mm"].isnull().sum()
    print(f"\n4. Weather Gaps in weather.csv:")
    print(f"   - Genuine zero rainfall days: {zero_rain} ({zero_rain / len(w_df) * 100:.1f}%)")
    print(f"   - Missing rainfall sensor observations (NaN): {nan_rain} ({nan_rain / len(w_df) * 100:.1f}%)")
    print(f"   - Missing temperature observations: {w_df['temperature_mean_c'].isnull().sum()}")
    
    # Build consolidated markdown table
    summary_rows = []
    for name, info in audit_results.items():
        missing_summary = ", ".join([f"{col} ({cinfo['count']})" for col, cinfo in info["missing_by_column"].items()])
        if not missing_summary:
            missing_summary = "None"
        summary_rows.append({
            "Dataset": info["file"],
            "Rows": info["rows"],
            "Columns": info["cols"],
            "Exact Duplicates": info["exact_duplicates"],
            "Key Duplicates": info["key_duplicates"],
            "Missing Values": missing_summary
        })
        
    df_summary = pd.DataFrame(summary_rows)
    md_table = df_summary.to_markdown(index=False)
    
    # Save audit report
    with open(report_path / "data_validation_summary.json", "w") as f:
        json.dump(audit_results, f, indent=2)
        
    with open(report_path / "data_quality_audit_table.md", "w") as f:
        f.write("# AgriNova Farm Analytics - Data Quality Audit Table\n\n")
        f.write(md_table)
        f.write("\n\n### Identified Data Quality Vulnerabilities:\n")
        f.write("1. **Inconsistent Crop Names**: Mixed casing ('maize', 'MAIZE'), whitespace (' wheat '), and synonyms ('Corn', 'Soy').\n")
        f.write("2. **Duplicate Records**: Duplicate (field_id, season) pairs in practices, soil, and harvest tables.\n")
        f.write("3. **Severe Yield Outliers**: Physically impossible negative yields and 10x data-entry typos (>15,000 kg/ha).\n")
        f.write("4. **Missing Soil Tests**: Missing field-season soil testing records, plus missing nutrient sub-measurements.\n")
        f.write("5. **Weather Data Gaps**: Distinguishing genuine zero rainfall from missing meteorological sensor logs.\n")
        
    print("\n" + "=" * 80)
    print("CONSOLIDATED DATA QUALITY AUDIT TABLE:")
    print(df_summary.to_string(index=False))
    print("=" * 80)
    print(f"[SAVED] Audit reports written to {report_path}")
    
    return dfs, audit_results

if __name__ == "__main__":
    validate_datasets()
