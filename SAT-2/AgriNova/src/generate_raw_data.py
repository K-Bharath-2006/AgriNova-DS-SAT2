"""
AgriNova Farm Analytics - Synthetic Benchmark Dataset Generator
================================================================
Generates 5 realistic agricultural relational CSV files for competition evaluation:
  1. fields.csv    - Field characteristics (field_id, region, area_ha, crop)
  2. soil.csv      - Soil chemistry & physics (field_id, season, soil_ph, soil_moisture_pct, nitrogen_ppm, phosphorus_ppm, potassium_ppm)
  3. weather.csv   - Daily agro-meteorological records (record_id, field_id, region, date, season, rainfall_mm, temp_mean_c, temp_min_c, temp_max_c, humidity_pct)
  4. practices.csv - Field management practices (field_id, season, irrigation_type, fertilizer_type, sowing_date)
  5. harvest.csv   - Yield and harvest outcome (field_id, season, harvest_date, yield_kg_per_ha, quality_grade)

Contains realistic agronomic responses (soil pH curve, moisture curve, heat effects, fertilizer impacts)
and explicitly injects the 5 documented real-world data quality challenges:
  - Missing soil tests
  - Duplicate field-season records
  - Inconsistent crop names and casing
  - Extreme yield outliers (entry errors vs valid extremes)
  - Weather observation dropouts (missing sensor days vs genuine zero rainfall)

PROVENANCE:
  - Data Type: Synthetic Benchmark for Round 2 Competition
  - Reference Models: FAO Crop Water Productivity & USDA Yield Response Models
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_benchmark_data(output_dir="data/raw", seed=42):
    np.random.seed(seed)
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    # -------------------------------------------------------------
    # 1. FIELDS.CSV
    # -------------------------------------------------------------
    n_fields = 250
    field_ids = [f"F_{i:03d}" for i in range(1, n_fields + 1)]
    regions = ["North Valley", "Eastern Highlands", "Central Plains", "Southern Basin", "Western Coast"]
    
    # Assign field properties
    field_regions = np.random.choice(regions, size=n_fields, p=[0.25, 0.20, 0.30, 0.15, 0.10])
    field_areas = np.round(np.random.uniform(5.0, 120.0, size=n_fields), 1)
    
    # Base crops
    canonical_crops = ["Maize", "Wheat", "Soybean", "Barley"]
    assigned_crops = np.random.choice(canonical_crops, size=n_fields, p=[0.35, 0.30, 0.25, 0.10])
    
    # Inconsistent crop naming injection (inconsistent casing, whitespace, synonyms)
    noisy_crops = []
    for c in assigned_crops:
        rand_val = np.random.rand()
        if rand_val < 0.08:
            noisy_crops.append(c.lower())  # "maize", "wheat"
        elif rand_val < 0.15:
            noisy_crops.append(c.upper())  # "MAIZE", "SOYBEAN"
        elif rand_val < 0.22:
            noisy_crops.append(f" {c} ")   # leading/trailing whitespace
        elif rand_val < 0.30 and c == "Maize":
            noisy_crops.append("Corn")     # Synonym
        elif rand_val < 0.35 and c == "Soybean":
            noisy_crops.append("Soy")      # Synonym
        elif rand_val < 0.38 and c == "Wheat":
            noisy_crops.append(" wheat")
        else:
            noisy_crops.append(c)
            
    df_fields = pd.DataFrame({
        "field_id": field_ids,
        "region": field_regions,
        "area_hectares": field_areas,
        "crop": noisy_crops
    })
    
    # -------------------------------------------------------------
    # 2. SEASONS & MANAGEMENT (PRACTICES.CSV)
    # -------------------------------------------------------------
    seasons = [2021, 2022, 2023, 2024]
    irrigation_options = ["Drip", "Sprinkler", "Flood", "Rainfed"]
    fertilizer_options = ["Synthetic NPK", "Organic Compost", "Biofertilizer", "Minimal/None"]
    
    practice_rows = []
    sowing_lookup = {}
    
    for f_idx, fid in enumerate(field_ids):
        can_crop = assigned_crops[f_idx]
        region = field_regions[f_idx]
        
        for season in seasons:
            # Regional and crop-based sowing dates
            if can_crop in ["Maize", "Soybean"]:
                # Spring / Early Summer sowing
                base_month = 4 if region in ["Southern Basin", "Central Plains"] else 5
                day = np.random.randint(1, 28)
                sow_date = datetime(season, base_month, day)
            elif can_crop in ["Wheat", "Barley"]:
                # Winter / Early Spring sowing
                base_month = 10 if region in ["North Valley", "Eastern Highlands"] else 3
                day = np.random.randint(1, 28)
                sow_date = datetime(season if base_month == 3 else season - 1, base_month, day)
                
            sowing_lookup[(fid, season)] = sow_date
            
            # Irrigation practice by region
            if region in ["Southern Basin", "Western Coast"]:
                irr_p = [0.4, 0.3, 0.2, 0.1]
            elif region == "Central Plains":
                irr_p = [0.25, 0.35, 0.25, 0.15]
            else:
                irr_p = [0.15, 0.25, 0.15, 0.45]
            irrigation = np.random.choice(irrigation_options, p=irr_p)
            
            fertilizer = np.random.choice(fertilizer_options, p=[0.50, 0.25, 0.15, 0.10])
            
            practice_rows.append({
                "field_id": fid,
                "season": season,
                "irrigation_type": irrigation,
                "fertilizer_type": fertilizer,
                "sowing_date": sow_date.strftime("%Y-%m-%d")
            })
            
    df_practices = pd.DataFrame(practice_rows)
    
    # Inject duplicate field-season records in practices (exact and conflicting)
    dup_indices = np.random.choice(len(df_practices), size=25, replace=False)
    dup_rows = []
    for idx in dup_indices:
        row = df_practices.iloc[idx].copy()
        if np.random.rand() < 0.5:
            # Conflicting duplicate (e.g. updated irrigation or typo in date)
            row["irrigation_type"] = "Sprinkler" if row["irrigation_type"] != "Sprinkler" else "Drip"
        dup_rows.append(row)
    df_practices = pd.concat([df_practices, pd.DataFrame(dup_rows)], ignore_index=True)
    df_practices = df_practices.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    # -------------------------------------------------------------
    # 3. SOIL.CSV
    # -------------------------------------------------------------
    soil_rows = []
    for f_idx, fid in enumerate(field_ids):
        region = field_regions[f_idx]
        # Regional baseline soil chemistry
        if region == "North Valley":
            base_ph, base_n, base_p, base_k = 6.8, 140, 35, 180
        elif region == "Eastern Highlands":
            base_ph, base_n, base_p, base_k = 5.5, 95, 20, 120  # More acidic, lower nutrients
        elif region == "Central Plains":
            base_ph, base_n, base_p, base_k = 7.2, 160, 42, 210  # Optimal loam
        elif region == "Southern Basin":
            base_ph, base_n, base_p, base_k = 7.8, 120, 28, 150  # Alkaline, drier
        else: # Western Coast
            base_ph, base_n, base_p, base_k = 6.4, 130, 30, 160
            
        for season in seasons:
            # Not every field is tested every season (missing soil test anomaly)
            if np.random.rand() < 0.12:
                continue # Missing test record entirely
                
            ph = np.clip(np.random.normal(base_ph, 0.45), 4.5, 8.8)
            moisture = np.clip(np.random.normal(24.0, 6.5), 8.0, 48.0)
            n_ppm = max(10.0, np.random.normal(base_n, 25.0))
            p_ppm = max(5.0, np.random.normal(base_p, 9.0))
            k_ppm = max(20.0, np.random.normal(base_k, 35.0))
            
            # Partial missingness (e.g. missing moisture or phosphorus reading)
            if np.random.rand() < 0.05:
                moisture = np.nan
            if np.random.rand() < 0.04:
                p_ppm = np.nan
                
            soil_rows.append({
                "field_id": fid,
                "season": season,
                "soil_ph": np.round(ph, 2),
                "soil_moisture_pct": np.round(moisture, 1) if not np.isnan(moisture) else np.nan,
                "nitrogen_ppm": np.round(n_ppm, 1),
                "phosphorus_ppm": np.round(p_ppm, 1) if not np.isnan(p_ppm) else np.nan,
                "potassium_ppm": np.round(k_ppm, 1)
            })
            
    df_soil = pd.DataFrame(soil_rows)
    # Inject a few duplicate soil records
    soil_dup_idx = np.random.choice(len(df_soil), size=12, replace=False)
    df_soil = pd.concat([df_soil, df_soil.iloc[soil_dup_idx]], ignore_index=True)
    df_soil = df_soil.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    # -------------------------------------------------------------
    # 4. WEATHER.CSV (Daily observations per region/season)
    # -------------------------------------------------------------
    # To represent realistic weather, we generate daily weather records for each region and season
    # with sensor dropouts (missing weather observations) and genuine 0 rain days.
    weather_rows = []
    record_counter = 1
    
    regional_weather_profiles = {
        "North Valley": {"temp_mean": 18.5, "temp_amp": 9.0, "rain_prob": 0.28, "rain_mean": 9.5, "hum": 68},
        "Eastern Highlands": {"temp_mean": 14.0, "temp_amp": 7.5, "rain_prob": 0.40, "rain_mean": 13.0, "hum": 78},
        "Central Plains": {"temp_mean": 21.0, "temp_amp": 10.5, "rain_prob": 0.24, "rain_mean": 8.0, "hum": 62},
        "Southern Basin": {"temp_mean": 24.5, "temp_amp": 11.0, "rain_prob": 0.16, "rain_mean": 6.5, "hum": 50},
        "Western Coast": {"temp_mean": 19.0, "temp_amp": 5.5, "rain_prob": 0.32, "rain_mean": 11.0, "hum": 75}
    }
    
    # To keep file size optimized while demonstrating rich time-series daily aggregation,
    # we record daily regional weather across all 365 days for each season (2021-2024),
    # and provide field mapping.
    for reg, prof in regional_weather_profiles.items():
        for season in seasons:
            start_date = datetime(season, 1, 1)
            # Weather anomaly per year
            year_rain_mult = 1.25 if season == 2022 else (0.75 if season == 2023 else 1.0) # 2022 wet year, 2023 drought year
            year_temp_shift = 1.2 if season == 2023 else (-0.5 if season == 2022 else 0.0)
            
            for day_idx in range(365):
                cur_date = start_date + timedelta(days=day_idx)
                # Seasonal sinusoidal curve
                day_of_year = day_idx + 1
                temp_cycle = np.sin((day_of_year - 105) * 2 * np.pi / 365)
                
                t_mean = prof["temp_mean"] + prof["temp_amp"] * temp_cycle + year_temp_shift + np.random.normal(0, 2.0)
                t_min = t_mean - np.random.uniform(3.5, 7.5)
                t_max = t_mean + np.random.uniform(4.0, 8.5)
                
                # Rainfall: Zero-inflated gamma distribution
                is_rain = np.random.rand() < (prof["rain_prob"] * year_rain_mult)
                if is_rain:
                    rainfall = np.random.gamma(shape=1.8, scale=prof["rain_mean"] / 1.8)
                else:
                    rainfall = 0.0 # Genuine zero rainfall
                    
                hum = np.clip(prof["hum"] + (15.0 if is_rain else -5.0) + np.random.normal(0, 6.0), 20.0, 99.0)
                
                # INJECT DATA QUALITY ISSUE: Missing weather observation (sensor failure)
                # 3.5% probability of sensor dropout / NaN values
                if np.random.rand() < 0.035:
                    # Sensor down: missing temp and humidity or rainfall
                    t_mean_val = np.nan
                    rainfall_val = np.nan
                    hum_val = np.nan
                else:
                    t_mean_val = np.round(t_mean, 1)
                    rainfall_val = np.round(rainfall, 1)
                    hum_val = np.round(hum, 1)
                    
                weather_rows.append({
                    "weather_record_id": f"W_{record_counter:06d}",
                    "region": reg,
                    "date": cur_date.strftime("%Y-%m-%d"),
                    "season": season,
                    "rainfall_mm": rainfall_val,
                    "temperature_mean_c": t_mean_val,
                    "temperature_min_c": np.round(t_min, 1) if not np.isnan(t_mean_val) else np.nan,
                    "temperature_max_c": np.round(t_max, 1) if not np.isnan(t_mean_val) else np.nan,
                    "humidity_pct": hum_val
                })
                record_counter += 1
                
    df_weather = pd.DataFrame(weather_rows)
    
    # -------------------------------------------------------------
    # 5. HARVEST.CSV & AGRONOMIC YIELD FORMULA
    # -------------------------------------------------------------
    # Compute aggregate growing conditions per field-season to simulate realistic agronomic yield
    harvest_rows = []
    
    # Regional aggregate weather lookup for the growing season (approx day 100 to 280)
    # to drive realistic yields
    seasonal_weather_summary = {}
    for reg in regions:
        for s in seasons:
            w_sub = df_weather[(df_weather["region"] == reg) & (df_weather["season"] == s)]
            valid_rain = w_sub["rainfall_mm"].fillna(0)
            valid_temp = w_sub["temperature_mean_c"].dropna()
            seasonal_weather_summary[(reg, s)] = {
                "tot_rain": valid_rain.sum(),
                "mean_temp": valid_temp.mean() if len(valid_temp) > 0 else 20.0
            }
            
    # Base yield potentials by crop (kg/ha)
    crop_potential = {
        "Maize": 7800,
        "Wheat": 5200,
        "Soybean": 3600,
        "Barley": 4400
    }
    
    # Clean practices lookup for deterministic generation
    practices_clean = df_practices.drop_duplicates(subset=["field_id", "season"]).set_index(["field_id", "season"])
    soil_clean = df_soil.dropna(subset=["soil_ph"]).drop_duplicates(subset=["field_id", "season"]).set_index(["field_id", "season"])
    
    for f_idx, fid in enumerate(field_ids):
        can_crop = assigned_crops[f_idx]
        region = field_regions[f_idx]
        base_pot = crop_potential[can_crop]
        
        # Inherent field quality factor (fixed per field across seasons to model yield stability!)
        field_quality_factor = np.random.normal(1.0, 0.08)
        
        for season in seasons:
            w_summary = seasonal_weather_summary.get((region, season), {"tot_rain": 600, "mean_temp": 20})
            rain = w_summary["tot_rain"]
            temp = w_summary["mean_temp"]
            
            # Practice factors
            if (fid, season) in practices_clean.index:
                p_row = practices_clean.loc[(fid, season)]
                irr = p_row["irrigation_type"]
                fert = p_row["fertilizer_type"]
            else:
                irr = "Rainfed"
                fert = "Minimal/None"
                
            # Irrigation multiplier
            irr_mult = {"Drip": 1.22, "Sprinkler": 1.15, "Flood": 1.06, "Rainfed": 0.88}[irr]
            # Fertilizer multiplier
            fert_mult = {"Synthetic NPK": 1.20, "Organic Compost": 1.12, "Biofertilizer": 1.08, "Minimal/None": 0.85}[fert]
            
            # Soil pH multiplier (bell curve centered at optimal pH ~ 6.5)
            if (fid, season) in soil_clean.index:
                s_ph = soil_clean.loc[(fid, season)]["soil_ph"]
                ph_mult = np.exp(-0.5 * ((s_ph - 6.6) / 1.4)**2)
            else:
                ph_mult = 0.95
                
            # Rainfall quadratic response (water deficit or waterlogging)
            rain_mult = np.clip(1.0 - 0.0000015 * (rain - 650)**2, 0.65, 1.15)
            
            # Temperature response (heat stress penalty)
            temp_penalty = 1.0 - max(0, (temp - 23.0) * 0.04)
            
            # Simulated realistic yield
            sim_yield = base_pot * field_quality_factor * irr_mult * fert_mult * ph_mult * rain_mult * temp_penalty
            sim_yield += np.random.normal(0, base_pot * 0.05) # natural stochastic variance
            sim_yield = max(400.0, sim_yield)
            
            # Quality grade correlation with yield
            if sim_yield > base_pot * 1.15:
                grade = "Grade A"
            elif sim_yield > base_pot * 0.95:
                grade = "Grade B"
            elif sim_yield > base_pot * 0.75:
                grade = "Grade C"
            else:
                grade = "Grade D"
                
            # Harvest date (~120 to 150 days after sowing)
            sow_d = sowing_lookup.get((fid, season), datetime(season, 4, 15))
            harv_d = sow_d + timedelta(days=np.random.randint(115, 155))
            
            harvest_rows.append({
                "field_id": fid,
                "season": season,
                "harvest_date": harv_d.strftime("%Y-%m-%d"),
                "yield_kg_per_ha": np.round(sim_yield, 1),
                "quality_grade": grade
            })
            
    df_harvest = pd.DataFrame(harvest_rows)
    
    # INJECT DATA QUALITY PROBLEMS INTO HARVEST:
    # 1. Extreme Outliers: typographical / data entry errors (e.g. 10x factor or negative)
    # Valid high yields also exist naturally in the distribution
    err_indices = np.random.choice(len(df_harvest), size=12, replace=False)
    for i, idx in enumerate(err_indices):
        if i % 3 == 0:
            df_harvest.at[idx, "yield_kg_per_ha"] = df_harvest.at[idx, "yield_kg_per_ha"] * 10.0 # 65,000+ kg/ha typo
        elif i % 3 == 1:
            df_harvest.at[idx, "yield_kg_per_ha"] = -abs(df_harvest.at[idx, "yield_kg_per_ha"]) # Negative impossible yield
        else:
            df_harvest.at[idx, "yield_kg_per_ha"] = 85000.0 # extreme sensor key error
            
    # 2. Duplicate harvest records
    harv_dup_idx = np.random.choice(len(df_harvest), size=15, replace=False)
    df_harvest = pd.concat([df_harvest, df_harvest.iloc[harv_dup_idx]], ignore_index=True)
    df_harvest = df_harvest.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    # -------------------------------------------------------------
    # SAVE RAW CSVS
    # -------------------------------------------------------------
    df_fields.to_csv(os.path.join(output_dir, "fields.csv"), index=False)
    df_soil.to_csv(os.path.join(output_dir, "soil.csv"), index=False)
    df_weather.to_csv(os.path.join(output_dir, "weather.csv"), index=False)
    df_practices.to_csv(os.path.join(output_dir, "practices.csv"), index=False)
    df_harvest.to_csv(os.path.join(output_dir, "harvest.csv"), index=False)
    
    print(f"[SUCCESS] Synthetic benchmark dataset generated in '{output_dir}':")
    print(f"  - fields.csv:    {len(df_fields)} rows")
    print(f"  - soil.csv:      {len(df_soil)} rows")
    print(f"  - weather.csv:   {len(df_weather)} rows")
    print(f"  - practices.csv: {len(df_practices)} rows")
    print(f"  - harvest.csv:   {len(df_harvest)} rows")

if __name__ == "__main__":
    generate_benchmark_data(output_dir="AgriNova/data/raw", seed=42)
