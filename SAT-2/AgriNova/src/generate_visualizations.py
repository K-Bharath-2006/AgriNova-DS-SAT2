"""
AgriNova Farm Analytics - Publication-Quality Visualizations
============================================================
Generates and exports all required competition visualizations:
  1. regional_yield_comparison.png      - Analysis A: Regional yield & crop composition
  2. rainfall_versus_yield.png          - Analysis B: Rainfall response curves & saturation
  3. soil_correlation_heatmap.png       - Analysis C: Soil chemistry & pH response curve
  4. irrigation_fertilizer_practices.png- Analysis D: Management practices & confounding
  5. sowing_period_analysis.png         - Analysis E: Sowing windows by crop species
  6. field_yield_stability.png          - Analysis F: Field CV & multi-season trajectories
  7. feature_importance_ranking.png     - Phase 6/7: Permutation importance vs Mutual Info
  8. quality_grade_yield_analysis.png   - Post-harvest descriptive validation
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def generate_all_charts(enriched_csv="AgriNova/outputs/feature_analysis/agrinova_features_enriched.csv",
                        importance_csv="AgriNova/outputs/feature_analysis/feature_importance_summary.csv",
                        out_dir="AgriNova/outputs/charts"):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Set global plotting aesthetics
    sns.set_theme(style="whitegrid", font="sans-serif")
    palette = sns.color_palette("deep")
    
    df = pd.read_csv(enriched_csv)
    df_imp = pd.read_csv(importance_csv) if os.path.exists(importance_csv) else None
    
    print("=" * 80)
    print("GENERATING PUBLICATION-QUALITY AGRONOMIC VISUALIZATIONS")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. CHART A: REGIONAL YIELD COMPARISON & CROP COMPOSITION
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={'width_ratios': [1.2, 1]})
    
    # Left: Yield distribution by Region
    order_regions = df.groupby("region")["yield_kg_per_ha"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="region", y="yield_kg_per_ha", order=order_regions, 
                ax=axes[0], palette="crest", boxprops=dict(alpha=0.8), showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"black"})
    axes[0].set_title("A1: Crop Yield Distribution by Region (kg/ha)", fontsize=13, weight="bold", pad=10)
    axes[0].set_xlabel("Agricultural Region", fontsize=11, weight="bold")
    axes[0].set_ylabel("Yield (kg/ha)", fontsize=11, weight="bold")
    axes[0].tick_params(axis='x', rotation=15)
    
    # Annotate region means & observation counts
    reg_stats = df.groupby("region")["yield_kg_per_ha"].agg(["mean", "median", "count"]).loc[order_regions]
    for idx, (reg, row) in enumerate(reg_stats.iterrows()):
        axes[0].text(idx, 1000, f"n={int(row['count'])}\nμ={row['mean']:.0f}", 
                     ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))

    # Right: Crop Composition across Regions (Confounding check)
    crop_comp = pd.crosstab(df["region"], df["crop"], normalize="index") * 100
    crop_comp.loc[order_regions].plot(kind="bar", stacked=True, ax=axes[1], colormap="viridis", edgecolor="black", alpha=0.85)
    axes[1].set_title("A2: Regional Crop Composition (% of Planted Fields)", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Agricultural Region", fontsize=11, weight="bold")
    axes[1].set_ylabel("Percentage (%)", fontsize=11, weight="bold")
    axes[1].legend(title="Crop", bbox_to_anchor=(1.02, 1), loc='upper left')
    axes[1].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    chart1_file = out_path / "regional_yield_comparison.png"
    plt.savefig(chart1_file, dpi=300)
    plt.close()
    print(f"[CHART 1] Saved: {chart1_file.name}")

    # -------------------------------------------------------------------------
    # 2. CHART B: RAINFALL AND YIELD RESPONSE
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Overall Scatter with Polynomial Quadratic Fit
    sns.scatterplot(data=df, x="seasonal_rainfall_mm", y="yield_kg_per_ha", hue="crop",
                    alpha=0.7, palette="Set2", s=50, ax=axes[0])
    sns.regplot(data=df, x="seasonal_rainfall_mm", y="yield_kg_per_ha", scatter=False,
                order=2, color="black", ax=axes[0], line_kws={"linestyle": "--", "linewidth": 2.5, "label": "Quadratic Fit (Water Saturation Curve)"})
    axes[0].set_title("B1: Cumulative Seasonal Rainfall vs. Crop Yield", fontsize=13, weight="bold", pad=10)
    axes[0].set_xlabel("Cumulative Seasonal Rainfall (mm)", fontsize=11, weight="bold")
    axes[0].set_ylabel("Crop Yield (kg/ha)", fontsize=11, weight="bold")
    axes[0].legend(loc="upper left")
    
    # Right: Rainfall response by Irrigation practice
    sns.lmplot_df = df.copy()
    sns.scatterplot(data=df, x="seasonal_rainfall_mm", y="yield_kg_per_ha", hue="irrigation_type",
                    style="irrigation_type", s=60, alpha=0.75, palette="tab10", ax=axes[1])
    axes[1].set_title("B2: Yield Response to Rainfall Stratified by Irrigation Practice", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Cumulative Seasonal Rainfall (mm)", fontsize=11, weight="bold")
    axes[1].set_ylabel("Crop Yield (kg/ha)", fontsize=11, weight="bold")
    axes[1].legend(title="Irrigation Method", loc="upper left")
    
    plt.tight_layout()
    chart2_file = out_path / "rainfall_versus_yield.png"
    plt.savefig(chart2_file, dpi=300)
    plt.close()
    print(f"[CHART 2] Saved: {chart2_file.name}")

    # -------------------------------------------------------------------------
    # 3. CHART C: SOIL PROPERTIES & CORRELATION HEATMAP
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Correlation Heatmap among Environmental Covariates & Yield
    corr_cols = [
        "yield_kg_per_ha", "soil_ph", "soil_moisture_pct", "nitrogen_ppm", 
        "phosphorus_ppm", "potassium_ppm", "seasonal_rainfall_mm", 
        "mean_temperature_c", "crop_ph_deviation"
    ]
    corr_matrix = df[corr_cols].corr()
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="vlag", center=0,
                square=True, linewidths=0.5, ax=axes[0], cbar_kws={"shrink": 0.8})
    axes[0].set_title("C1: Environmental & Soil Covariate Correlation Matrix", fontsize=13, weight="bold", pad=10)
    
    # Right: Crop-specific soil pH vs Yield curve
    sns.scatterplot(data=df, x="soil_ph", y="yield_kg_per_ha", hue="crop",
                    alpha=0.6, palette="Set1", s=45, ax=axes[1])
    # Add optimal band reference
    axes[1].axvspan(6.2, 7.0, color="green", alpha=0.15, label="Optimal Agronomic pH Window (6.2 - 7.0)")
    axes[1].set_title("C2: Soil pH vs. Yield (Agronomic Bell Curve Response)", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Soil pH Measurement", fontsize=11, weight="bold")
    axes[1].set_ylabel("Crop Yield (kg/ha)", fontsize=11, weight="bold")
    axes[1].legend(loc="upper left")
    
    plt.tight_layout()
    chart3_file = out_path / "soil_correlation_heatmap.png"
    plt.savefig(chart3_file, dpi=300)
    plt.close()
    print(f"[CHART 3] Saved: {chart3_file.name}")

    # -------------------------------------------------------------------------
    # 4. CHART D: IRRIGATION AND FERTILIZER PRACTICES
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Yield by Irrigation Method
    irr_order = df.groupby("irrigation_type")["yield_kg_per_ha"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="irrigation_type", y="yield_kg_per_ha", order=irr_order,
                palette="Blues_r", ax=axes[0], showmeans=True,
                meanprops={"marker":"^", "markerfacecolor":"orange", "markeredgecolor":"black"})
    axes[0].set_title("D1: Yield Distribution Across Irrigation Methods", fontsize=13, weight="bold", pad=10)
    axes[0].set_xlabel("Irrigation Regime", fontsize=11, weight="bold")
    axes[0].set_ylabel("Yield (kg/ha)", fontsize=11, weight="bold")
    
    # Annotate irrigation medians
    for idx, irr in enumerate(irr_order):
        med_val = df[df["irrigation_type"] == irr]["yield_kg_per_ha"].median()
        axes[0].text(idx, 1500, f"Med: {med_val:.0f} kg/ha", ha="center", fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

    # Right: Yield by Fertilizer Type stratified by Crop
    fert_order = df.groupby("fertilizer_type")["yield_kg_per_ha"].median().sort_values(ascending=False).index
    sns.barplot(data=df, x="fertilizer_type", y="yield_kg_per_ha", hue="crop", order=fert_order,
                palette="tab10", ax=axes[1], errorbar=("ci", 95), capsize=0.1)
    axes[1].set_title("D2: Mean Yield by Fertilizer Regime & Crop (95% CI)", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Fertilizer Management Type", fontsize=11, weight="bold")
    axes[1].set_ylabel("Mean Yield (kg/ha)", fontsize=11, weight="bold")
    axes[1].tick_params(axis='x', rotation=15)
    axes[1].legend(title="Crop", loc="upper right")
    
    plt.tight_layout()
    chart4_file = out_path / "irrigation_fertilizer_practices.png"
    plt.savefig(chart4_file, dpi=300)
    plt.close()
    print(f"[CHART 4] Saved: {chart4_file.name}")

    # -------------------------------------------------------------------------
    # 5. CHART E: SOWING PERIOD ANALYSIS
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Sowing Period vs Yield across Crops
    sns.boxplot(data=df, x="sowing_period", y="yield_kg_per_ha", hue="crop",
                palette="Set2", ax=axes[0])
    axes[0].set_title("E1: Yield by Sowing Window & Crop Species", fontsize=13, weight="bold", pad=10)
    axes[0].set_xlabel("Agronomic Sowing Window", fontsize=11, weight="bold")
    axes[0].set_ylabel("Yield (kg/ha)", fontsize=11, weight="bold")
    axes[0].legend(title="Crop", loc="upper right")
    
    # Right: Sowing Day of Year vs Yield
    sns.scatterplot(data=df, x="sowing_day_of_year", y="yield_kg_per_ha", hue="crop",
                    palette="tab10", alpha=0.7, s=50, ax=axes[1])
    axes[1].set_title("E2: Planting Calendar Timing (Day of Year) vs. Harvest Yield", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Day of Year (Calendar Day)", fontsize=11, weight="bold")
    axes[1].set_ylabel("Harvest Yield (kg/ha)", fontsize=11, weight="bold")
    axes[1].axvline(120, color="grey", linestyle=":", label="May 1 (Spring/Summer Pivot)")
    axes[1].legend(title="Crop", loc="upper right")
    
    plt.tight_layout()
    chart5_file = out_path / "sowing_period_analysis.png"
    plt.savefig(chart5_file, dpi=300)
    plt.close()
    print(f"[CHART 5] Saved: {chart5_file.name}")

    # -------------------------------------------------------------------------
    # 6. CHART F: FIELD YIELD STABILITY & MULTI-SEASON TRAJECTORIES
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Field CV distribution
    field_cvs = df.drop_duplicates(subset=["field_id"])["field_yield_cv"].dropna()
    sns.histplot(field_cvs, kde=True, color="teal", ax=axes[0], bins=25)
    med_cv = field_cvs.median()
    p90_cv = field_cvs.quantile(0.90)
    axes[0].axvline(med_cv, color="blue", linestyle="--", label=f"Median CV = {med_cv:.1f}%")
    axes[0].axvline(p90_cv, color="red", linestyle="--", label=f"90th Percentile CV = {p90_cv:.1f}% (High Instability)")
    axes[0].set_title("F1: Distribution of Field Yield Coefficient of Variation (CV %)", fontsize=13, weight="bold", pad=10)
    axes[0].set_xlabel("Coefficient of Variation (% = SD / Mean * 100)", fontsize=11, weight="bold")
    axes[0].set_ylabel("Number of Farms", fontsize=11, weight="bold")
    axes[0].legend(loc="upper right")
    
    # Right: Multi-season Trajectory Comparison: Top 4 volatile vs Top 4 stable fields
    top_volatile = df.drop_duplicates(subset=["field_id"]).nlargest(4, "field_yield_cv")["field_id"].tolist()
    top_stable = df.drop_duplicates(subset=["field_id"]).nsmallest(4, "field_yield_cv")["field_id"].tolist()
    
    sub_vol = df[df["field_id"].isin(top_volatile)].sort_values(by=["field_id", "season"])
    sub_sta = df[df["field_id"].isin(top_stable)].sort_values(by=["field_id", "season"])
    
    for fid in top_volatile:
        f_sub = sub_vol[sub_vol["field_id"] == fid]
        axes[1].plot(f_sub["season"], f_sub["yield_kg_per_ha"], marker="o", color="crimson", 
                     alpha=0.7, linestyle="--", label=f"Volatile Field {fid}" if fid == top_volatile[0] else "")
    for fid in top_stable:
        f_sub = sub_sta[sub_sta["field_id"] == fid]
        axes[1].plot(f_sub["season"], f_sub["yield_kg_per_ha"], marker="s", color="darkgreen", 
                     alpha=0.8, linestyle="-", linewidth=2, label=f"Stable Field {fid}" if fid == top_stable[0] else "")
        
    axes[1].set_title("F2: Yield Trajectories (2021-2024): Highly Volatile vs. Resilient Farms", fontsize=13, weight="bold", pad=10)
    axes[1].set_xlabel("Growing Season Year", fontsize=11, weight="bold")
    axes[1].set_ylabel("Yield (kg/ha)", fontsize=11, weight="bold")
    axes[1].set_xticks([2021, 2022, 2023, 2024])
    axes[1].legend(loc="upper left")
    
    plt.tight_layout()
    chart6_file = out_path / "field_yield_stability.png"
    plt.savefig(chart6_file, dpi=300)
    plt.close()
    print(f"[CHART 6] Saved: {chart6_file.name}")

    # -------------------------------------------------------------------------
    # 7. CHART G: FEATURE IMPORTANCE RANKING (TEST PERMUTATION VS MUTUAL INFO)
    # -------------------------------------------------------------------------
    if df_imp is not None:
        fig, ax = plt.subplots(figsize=(12, 7))
        top_features = df_imp.head(10).sort_values(by="permutation_importance", ascending=True)
        
        y_pos = np.arange(len(top_features))
        ax.barh(y_pos, top_features["permutation_importance"], color="steelblue", alpha=0.85, edgecolor="black")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_features["feature"], fontsize=11)
        ax.set_xlabel("Permutation Feature Importance (Decrease in Test R² Upon Shuffling)", fontsize=11, weight="bold")
        ax.set_title("Top 10 Most Predictive Yield Drivers (Evaluated on Held-Out Unseen Farms)", fontsize=13, weight="bold", pad=12)
        
        # Add labels
        for idx, val in enumerate(top_features["permutation_importance"]):
            ax.text(val + 0.01, idx, f"{val:.4f}", va="center", fontsize=9, weight="bold")
            
        plt.tight_layout()
        chart7_file = out_path / "feature_importance_ranking.png"
        plt.savefig(chart7_file, dpi=300)
        plt.close()
        print(f"[CHART 7] Saved: {chart7_file.name}")

    # -------------------------------------------------------------------------
    # 8. CHART H: POST-HARVEST QUALITY GRADE VALIDATION
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 6))
    order_grades = ["Grade A", "Grade B", "Grade C", "Grade D"]
    sns.boxplot(data=df, x="quality_grade", y="yield_kg_per_ha", order=order_grades,
                palette="mako_r", ax=ax, showmeans=True,
                meanprops={"marker":"D", "markerfacecolor":"gold", "markeredgecolor":"black"})
    ax.set_title("Post-Harvest Quality Grade vs. Yield Performance", fontsize=13, weight="bold", pad=10)
    ax.set_xlabel("Assigned Post-Harvest Quality Grade", fontsize=11, weight="bold")
    ax.set_ylabel("Yield (kg/ha)", fontsize=11, weight="bold")
    
    # Annotate sample counts
    counts = df["quality_grade"].value_counts().to_dict()
    for idx, g in enumerate(order_grades):
        cnt = counts.get(g, 0)
        ax.text(idx, 1200, f"n={cnt}", ha="center", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
                
    plt.tight_layout()
    chart8_file = out_path / "quality_grade_yield_analysis.png"
    plt.savefig(chart8_file, dpi=300)
    plt.close()
    print(f"[CHART 8] Saved: {chart8_file.name}")
    
    print("=" * 80)
    print(f"[SUCCESS] All 8 publication-grade charts exported to {out_path}")
    print("=" * 80)

if __name__ == "__main__":
    generate_all_charts()
