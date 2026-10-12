"""
AgriNova Farm Analytics - Round 3 Excel Workbook Generator
==========================================================
Generates a complete, professional, 10-sheet Microsoft Excel workbook:
  'AgriNova_Round3_Excel_Analysis.xlsx'
Using the cleaned agricultural dataset from Round 2 ('agrinova_cleaned.csv').

Includes:
  Sheet 1:  Executive Summary (KPI cards, findings table, 6 executive charts)
  Sheet 2:  Cleaned Data (Structured Excel Table 'AgriData', 988 records, 29 cols)
  Sheet 3:  Statistical Analysis (Formulas: COUNT, AVERAGE, MEDIAN, STDEV.S, CORREL, etc.)
  Sheet 4:  Yield by Region (Regional summary table, crop composition, bar chart)
  Sheet 5:  Rainfall Analysis (SLOPE, INTERCEPT, RSQ, CORREL, rainfall brackets, scatter chart)
  Sheet 6:  Soil Analysis (pH brackets, nutrient correlations, heatmap, soil chart)
  Sheet 7:  Irrigation Analysis (Summary table, cross-tabulation, irrigation chart)
  Sheet 8:  Sowing Period Analysis (Calendar quarters, agronomic windows, column chart)
  Sheet 9:  Yield Variability (Field-level CV %, top 10 volatile vs stable fields, chart)
  Sheet 10: Pivot Analysis (6 multi-dimensional summary grids & comparative charts)
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import BarChart, LineChart, ScatterChart, Reference, Series
from openpyxl.formatting.rule import ColorScaleRule
import pandas as pd
from pathlib import Path
from datetime import datetime

def create_agrinova_excel_workbook(csv_path="AgriNova/data/processed/agrinova_cleaned.csv",
                                   output_path="AgriNova_Round3_Excel_Analysis.xlsx"):
    print("=" * 80)
    print("AGRINOVA ROUND 3: GENERATING EXCEL WORKBOOK")
    print(f"Source Data: {csv_path}")
    print(f"Target File: {output_path}")
    print("=" * 80)
    
    # 1. Load Cleaned Dataset
    df = pd.read_csv(csv_path)
    n_rows = len(df)
    print(f"Loaded {n_rows} clean field-season observations.")
    
    # Prepare enriched helper columns
    df["harvest_date"] = pd.to_datetime(df["harvest_date"]).dt.strftime("%Y-%m-%d")
    df["sowing_date"] = pd.to_datetime(df["sowing_date"]).dt.strftime("%Y-%m-%d")
    
    # Yield in tonnes per hectare (t/ha) as primary metric
    df["yield_t_per_ha"] = (df["yield_kg_per_ha"] / 1000.0).round(3)
    
    # Sowing month and agronomic periods
    sow_dt = pd.to_datetime(df["sowing_date"])
    df["sowing_month"] = sow_dt.dt.month
    
    def get_sowing_period(m):
        if m in [3, 4]:
            return "Early Spring"
        elif m in [5, 6]:
            return "Late Spring"
        elif m in [9, 10]:
            return "Autumn"
        elif m in [11, 12]:
            return "Winter"
        else:
            return "Summer"
    df["sowing_period"] = df["sowing_month"].apply(get_sowing_period)
    
    def get_quarter(m):
        if m in [1, 2, 3]:
            return "Q1 (Jan-Mar)"
        elif m in [4, 5, 6]:
            return "Q2 (Apr-Jun)"
        elif m in [7, 8, 9]:
            return "Q3 (Jul-Sep)"
        else:
            return "Q4 (Oct-Dec)"
    df["calendar_quarter"] = df["sowing_month"].apply(get_quarter)
    
    # Soil pH category
    def get_ph_cat(ph):
        if ph < 6.0:
            return "Acidic (<6.0)"
        elif ph <= 7.2:
            return "Near-Neutral (6.0-7.2)"
        else:
            return "Alkaline (>7.2)"
    df["soil_ph_category"] = df["soil_ph"].apply(get_ph_cat)
    
    # Organized column sequence for Sheet 2
    cols_order = [
        "field_id", "season", "harvest_date", "yield_t_per_ha", "yield_kg_per_ha",
        "quality_grade", "region", "area_hectares", "crop", "irrigation_type",
        "fertilizer_type", "sowing_date", "sowing_month", "sowing_period", "calendar_quarter",
        "seasonal_rainfall_mm", "mean_temperature_c", "min_temperature_c", "max_temperature_c",
        "temperature_range_c", "mean_humidity_pct", "rainy_days_count", "soil_ph",
        "soil_ph_category", "soil_moisture_pct", "nitrogen_ppm", "phosphorus_ppm",
        "potassium_ppm", "soil_tested"
    ]
    df_clean = df[cols_order].copy()
    
    # 2. Initialize Workbook & Palette
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    # Professional Styling Palette
    FONT_FAMILY = "Segoe UI"
    
    # Fonts
    title_font = Font(name=FONT_FAMILY, size=16, bold=True, color="1E4620")
    subtitle_font = Font(name=FONT_FAMILY, size=10, italic=True, color="4E6B4E")
    section_font = Font(name=FONT_FAMILY, size=12, bold=True, color="1E4620")
    th_font = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
    th_accent_font = Font(name=FONT_FAMILY, size=10, bold=True, color="1B5E20")
    body_font = Font(name=FONT_FAMILY, size=10, color="1A1A1A")
    body_bold = Font(name=FONT_FAMILY, size=10, bold=True, color="1A1A1A")
    num_bold = Font(name=FONT_FAMILY, size=10, bold=True, color="0D47A1")
    kpi_num_font = Font(name=FONT_FAMILY, size=18, bold=True, color="1B5E20")
    kpi_lbl_font = Font(name=FONT_FAMILY, size=9, bold=True, color="4E6B4E")
    kpi_sub_font = Font(name=FONT_FAMILY, size=8, italic=True, color="757575")
    
    # Fills
    primary_header_fill = PatternFill(start_color="1E4620", end_color="1E4620", fill_type="solid") # Deep Forest Green
    secondary_header_fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid") # Medium Forest Green
    accent_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid") # Light Sage
    kpi_fill = PatternFill(start_color="F1F8E9", end_color="F1F8E9", fill_type="solid") # Soft Mint
    zebra_fill = PatternFill(start_color="F9FBF9", end_color="F9FBF9", fill_type="solid") # Alternate Row
    total_fill = PatternFill(start_color="DCEDC8", end_color="DCEDC8", fill_type="solid")
    
    # Borders
    thin_border_side = Side(border_style="thin", color="D0D7DE")
    thick_bottom_side = Side(border_style="medium", color="1E4620")
    double_bottom_side = Side(border_style="double", color="1E4620")
    
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    th_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thick_bottom_side)
    total_border = Border(top=thin_border_side, bottom=double_bottom_side, left=thin_border_side, right=thin_border_side)
    kpi_border = Border(left=Side(style="medium", color="A5D6A7"), right=Side(style="thin", color="C8E6C9"),
                        top=Side(style="thin", color="C8E6C9"), bottom=Side(style="medium", color="A5D6A7"))

    # Alignments
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")
    align_wrap_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Helper function to style ranges
    def style_table_header(ws, row, start_col, end_col, fill=primary_header_fill, font=th_font):
        for col in range(start_col, end_col + 1):
            cell = ws.cell(row=row, column=col)
            cell.fill = fill
            cell.font = font
            cell.alignment = align_center
            cell.border = th_border

    # =========================================================================
    # SHEET 2: CLEANED DATA (Create first so formulas can reference it)
    # =========================================================================
    print("Building Sheet 2: Cleaned Data...")
    ws_data = wb.create_sheet(title="Cleaned Data")
    ws_data.views.sheetView[0].showGridLines = True
    ws_data.freeze_panes = "A2"
    
    # Write Headers
    headers = list(df_clean.columns)
    ws_data.append(headers)
    style_table_header(ws_data, row=1, start_col=1, end_col=len(headers), fill=primary_header_fill, font=th_font)
    
    # Write Data Rows
    for r_idx, row in df_clean.iterrows():
        ws_data.append(list(row))
        curr_row = r_idx + 2
        for c_idx in range(1, len(headers) + 1):
            cell = ws_data.cell(row=curr_row, column=c_idx)
            cell.font = body_font
            cell.border = cell_border
            col_name = headers[c_idx - 1]
            
            # Format types
            if "date" in col_name:
                cell.number_format = "yyyy-mm-dd"
                cell.alignment = align_center
            elif col_name in ["yield_t_per_ha"]:
                cell.number_format = "0.00"
                cell.alignment = align_right
            elif col_name in ["yield_kg_per_ha", "seasonal_rainfall_mm", "nitrogen_ppm", "phosphorus_ppm", "potassium_ppm", "area_hectares"]:
                cell.number_format = "#,##0.0"
                cell.alignment = align_right
            elif col_name in ["soil_ph"]:
                cell.number_format = "0.00"
                cell.alignment = align_right
            elif col_name in ["mean_humidity_pct", "soil_moisture_pct"]:
                cell.number_format = "0.0"
                cell.alignment = align_right
            elif col_name in ["season", "rainy_days_count", "soil_tested", "sowing_month"]:
                cell.number_format = "0"
                cell.alignment = align_center
            elif col_name in ["field_id", "quality_grade", "crop", "region", "irrigation_type", "sowing_period", "calendar_quarter"]:
                cell.alignment = align_left
                
            # Zebra stripe
            if curr_row % 2 == 1:
                cell.fill = zebra_fill
                
    # Add structured table
    data_tab_ref = f"A1:{get_column_letter(len(headers))}{n_rows + 1}"
    tab = Table(displayName="AgriData", ref=data_tab_ref)
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                                        showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    ws_data.add_table(tab)
    
    # Conditional formatting on yield_t_per_ha (Column D)
    color_scale = ColorScaleRule(start_type='min', start_color='F8696B', # Soft red
                                 mid_type='percentile', mid_value=50, mid_color='FFEB84', # Soft yellow
                                 end_type='max', end_color='63BE7B') # Soft green
    ws_data.conditional_formatting.add(f"D2:D{n_rows + 1}", color_scale)

    # =========================================================================
    # SHEET 3: STATISTICAL ANALYSIS
    # =========================================================================
    print("Building Sheet 3: Statistical Analysis...")
    ws_stats = wb.create_sheet(title="Statistical Analysis")
    ws_stats.views.sheetView[0].showGridLines = True
    
    # Title Block
    ws_stats["A1"] = "AgriNova Farm Analytics — Descriptive Statistics & Environmental Correlations"
    ws_stats["A1"].font = title_font
    ws_stats["A2"] = "Evaluated across 988 field-season observations (2021-2024) | Compatible with Excel structured & standard references"
    ws_stats["A2"].font = subtitle_font
    
    # Section 1: Yield Descriptive Statistics
    ws_stats["A4"] = "1. CROP YIELD DESCRIPTIVE STATISTICS"
    ws_stats["A4"].font = section_font
    
    stats_headers = ["Statistical Metric", "Yield (t/ha)", "Yield (kg/ha)", "Excel Formula Syntax", "Interpretation & Domain Relevance"]
    for c_idx, h in enumerate(stats_headers, 1):
        ws_stats.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_stats, row=5, start_col=1, end_col=5)
    
    # Descriptive stat items: (Metric name, formula_t_ha, formula_kg_ha, formula_syntax_text, interpretation)
    yield_stats_def = [
        ("Observation Count (N)", "=COUNT('Cleaned Data'!$D$2:$D$989)", "=COUNT('Cleaned Data'!$E$2:$E$989)", "COUNT(AgriData[yield_t_per_ha])", "Total valid field-season harvest records"),
        ("Missing Observations", "=COUNTBLANK('Cleaned Data'!$D$2:$D$989)", "=COUNTBLANK('Cleaned Data'!$E$2:$E$989)", "COUNTBLANK(AgriData[yield_t_per_ha])", "Missing harvest values (zero missing cells in cleaned data)"),
        ("Arithmetic Mean (μ)", "=AVERAGE('Cleaned Data'!$D$2:$D$989)", "=AVERAGE('Cleaned Data'!$E$2:$E$989)", "AVERAGE(AgriData[yield_t_per_ha])", "Central production tendency across all crops and regions"),
        ("Median (50th Percentile)", "=MEDIAN('Cleaned Data'!$D$2:$D$989)", "=MEDIAN('Cleaned Data'!$E$2:$E$989)", "MEDIAN(AgriData[yield_t_per_ha])", "Robust central location resistant to distribution skewness"),
        ("Minimum Observed Yield", "=MIN('Cleaned Data'!$D$2:$D$989)", "=MIN('Cleaned Data'!$E$2:$E$989)", "MIN(AgriData[yield_t_per_ha])", "Lowest harvest (severe drought/soil acidity stress)"),
        ("Maximum Observed Yield", "=MAX('Cleaned Data'!$D$2:$D$989)", "=MAX('Cleaned Data'!$E$2:$E$989)", "MAX(AgriData[yield_t_per_ha])", "Peak potential under optimal drip irrigation & fertile loam"),
        ("Yield Range (Max - Min)", "=MAX('Cleaned Data'!$D$2:$D$989)-MIN('Cleaned Data'!$D$2:$D$989)", "=MAX('Cleaned Data'!$E$2:$E$989)-MIN('Cleaned Data'!$E$2:$E$989)", "MAX(AgriData[yield]) - MIN(AgriData[yield])", "Total spread between lowest and highest field outputs"),
        ("Sample Standard Deviation (s)", "=STDEV('Cleaned Data'!$D$2:$D$989)", "=STDEV('Cleaned Data'!$E$2:$E$989)", "STDEV(AgriData[yield_t_per_ha])", "Dispersion around the mean across diverse crop species"),
        ("Sample Variance (s²)", "=VAR('Cleaned Data'!$D$2:$D$989)", "=VAR('Cleaned Data'!$E$2:$E$989)", "VAR(AgriData[yield_t_per_ha])", "Variance of harvest yields across field-seasons"),
        ("First Quartile (Q1 / 25%)", "=QUARTILE('Cleaned Data'!$D$2:$D$989, 1)", "=QUARTILE('Cleaned Data'!$E$2:$E$989, 1)", "QUARTILE(AgriData[yield_t_per_ha], 1)", "Lower quartile threshold; 25% of fields yield below this"),
        ("Third Quartile (Q3 / 75%)", "=QUARTILE('Cleaned Data'!$D$2:$D$989, 3)", "=QUARTILE('Cleaned Data'!$E$2:$E$989, 3)", "QUARTILE(AgriData[yield_t_per_ha], 3)", "Upper quartile threshold; 75% of fields yield below this"),
        ("Interquartile Range (IQR)", "=B16-B15", "=C16-C15", "Q3 - Q1 (Interquartile Range)", "Middle 50% spread; robust measure of statistical dispersion"),
        ("Coefficient of Variation (CV)", "=B13/B8", "=C13/C8", "STDEV(AgriData[yield]) / AVERAGE(AgriData[yield])", "Relative variability (percentage spread normalized by mean)")
    ]
    
    start_r = 6
    for idx, (m_name, f_t, f_kg, f_syn, interp) in enumerate(yield_stats_def):
        r = start_r + idx
        ws_stats.cell(row=r, column=1, value=m_name).font = body_bold
        c2 = ws_stats.cell(row=r, column=2, value=f_t)
        c3 = ws_stats.cell(row=r, column=3, value=f_kg)
        ws_stats.cell(row=r, column=4, value=f_syn).font = Font(name=FONT_FAMILY, size=9, color="0D47A1")
        ws_stats.cell(row=r, column=5, value=interp).font = body_font
        
        # Formatting
        c2.font = num_bold
        c3.font = num_bold
        if "Count" in m_name:
            c2.number_format = "#,##0"
            c3.number_format = "#,##0"
        elif "Coefficient" in m_name:
            c2.number_format = "0.00%"
            c3.number_format = "0.00%"
        else:
            c2.number_format = "0.00"
            c3.number_format = "#,##0.0"
            
        for c in range(1, 6):
            ws_stats.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_stats.cell(row=r, column=c).fill = zebra_fill
                
    # Section 2: Environmental Pearson Correlation Matrix
    corr_start_r = 21
    ws_stats.cell(row=corr_start_r - 1, column=1, value="2. ENVIRONMENTAL & EDAPHIC CORRELATIONS WITH YIELD (PEARSON r)").font = section_font
    
    corr_headers = ["Environmental Covariate", "Source Column", "Pearson r with Yield", "Excel Formula Syntax", "Observed Nature of Relationship & Confounding Caution"]
    for c_idx, h in enumerate(corr_headers, 1):
        ws_stats.cell(row=corr_start_r, column=c_idx, value=h)
    style_table_header(ws_stats, row=corr_start_r, start_col=1, end_col=5)
    
    correlations_def = [
        ("Seasonal Rainfall (mm)", "seasonal_rainfall_mm (Col P)", "=CORREL('Cleaned Data'!$P$2:$P$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[rain], AgriData[yield])", "Negative linear r (-0.29) is confounded by region: wettest Highlands have acidic soils; rainfall itself exhibits non-linear saturation curve."),
        ("Mean Temperature (°C)", "mean_temperature_c (Col Q)", "=CORREL('Cleaned Data'!$Q$2:$Q$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[temp_mean], AgriData[yield])", "Moderate negative correlation; excessive heat stress above 22°C impairs summer cereal grain-filling."),
        ("Diurnal Temperature Range (°C)", "temperature_range_c (Col T)", "=CORREL('Cleaned Data'!$T$2:$T$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[temp_range], AgriData[yield])", "Wide daily thermal fluctuations correlate with continental interior heat stress."),
        ("Mean Relative Humidity (%)", "mean_humidity_pct (Col U)", "=CORREL('Cleaned Data'!$U$2:$U$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[humidity], AgriData[yield])", "High humidity co-occurs with overcast Highlands and disease pressure."),
        ("Soil pH (Acidity/Alkalinity)", "soil_ph (Col W)", "=CORREL('Cleaned Data'!$W$2:$W$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[soil_ph], AgriData[yield])", "Positive linear trend: near-neutral soils (6.5-7.2) allow maximum nutrient uptake; acidic soils (<5.8) cause severe yield decline."),
        ("Soil Moisture Content (%)", "soil_moisture_pct (Col Y)", "=CORREL('Cleaned Data'!$Y$2:$Y$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[soil_moist], AgriData[yield])", "Positive association; volumetric moisture buffers root zone during vegetative growth."),
        ("Available Nitrogen (ppm)", "nitrogen_ppm (Col Z)", "=CORREL('Cleaned Data'!$Z$2:$Z$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[nitrogen], AgriData[yield])", "Positive macronutrient association; essential building block for chlorophyll and protein synthesis."),
        ("Available Phosphorus (ppm)", "phosphorus_ppm (Col AA)", "=CORREL('Cleaned Data'!$AA$2:$AA$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[phosphorus], AgriData[yield])", "Positive association; critical for root proliferation and early vigor; restricted in acidic soils."),
        ("Available Potassium (ppm)", "potassium_ppm (Col AB)", "=CORREL('Cleaned Data'!$AB$2:$AB$989, 'Cleaned Data'!$D$2:$D$989)", "CORREL(AgriData[potassium], AgriData[yield])", "Positive association; enhances drought tolerance and enzyme activation.")
    ]
    
    for idx, (var_name, src_col, f_corr, f_syn, interp) in enumerate(correlations_def):
        r = corr_start_r + 1 + idx
        ws_stats.cell(row=r, column=1, value=var_name).font = body_bold
        ws_stats.cell(row=r, column=2, value=src_col).font = Font(name=FONT_FAMILY, size=9, color="555555")
        c3 = ws_stats.cell(row=r, column=3, value=f_corr)
        c3.font = num_bold
        c3.number_format = "+0.0000;-0.0000;0.0000"
        c3.alignment = align_right
        ws_stats.cell(row=r, column=4, value=f_syn).font = Font(name=FONT_FAMILY, size=9, color="0D47A1")
        ws_stats.cell(row=r, column=5, value=interp).font = body_font
        
        for c in range(1, 6):
            ws_stats.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_stats.cell(row=r, column=c).fill = zebra_fill
                
    # Add methodological caveat box
    ws_stats.cell(row=32, column=1, value="CRITICAL METHODOLOGICAL CAVEAT ON CORRELATION VS CAUSATION:").font = Font(name=FONT_FAMILY, size=9, bold=True, color="B71C1C")
    ws_stats.cell(row=33, column=1, value="Pearson correlation measures bivariate linear association across observational data. In agricultural ecosystems, relationships are frequently non-linear (e.g. water saturation, pH bell-curves) and confounded by regional soil differences. High correlation does NOT establish counterfactual causation without controlled agronomic split-plot trials.").font = Font(name=FONT_FAMILY, size=9, italic=True, color="555555")

    # =========================================================================
    # SHEET 4: YIELD BY REGION
    # =========================================================================
    print("Building Sheet 4: Yield by Region...")
    ws_reg = wb.create_sheet(title="Yield by Region")
    ws_reg.views.sheetView[0].showGridLines = True
    
    ws_reg["A1"] = "AgriNova Farm Analytics — Regional Yield Performance & Agronomic Disparities"
    ws_reg["A1"].font = title_font
    ws_reg["A2"] = "Summary of harvest yield across 5 agro-climatic regions | Evaluates sample size, variance, and crop confounding"
    ws_reg["A2"].font = subtitle_font
    
    ws_reg["A4"] = "1. REGIONAL YIELD SUMMARY TABLE"
    ws_reg["A4"].font = section_font
    
    reg_headers = ["Region Name", "Observation Count (N)", "Average Yield (t/ha)", "Median Yield (t/ha)", "Min Yield (t/ha)", "Max Yield (t/ha)", "Std Dev (t/ha)", "CV (%)", "Performance Rating"]
    for c_idx, h in enumerate(reg_headers, 1):
        ws_reg.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_reg, row=5, start_col=1, end_col=len(reg_headers))
    
    regions_list = [
        ("Central Plains", "High Output (Loam & Drip)"),
        ("North Valley", "High Output (Fertile Silt)"),
        ("Western Coast", "Moderate Output (Maritime)"),
        ("Southern Basin", "Below Average (Heat & Arid)"),
        ("Eastern Highlands", "Lowest Output (Acidic Soils)")
    ]
    
    # Regional summary table formulas
    for idx, (reg, rating) in enumerate(regions_list):
        r = 6 + idx
        ws_reg.cell(row=r, column=1, value=reg).font = body_bold
        
        # Observations: COUNTIF
        c2 = ws_reg.cell(row=r, column=2, value=f"=COUNTIF('Cleaned Data'!$G$2:$G$989, A{r})")
        c2.number_format = "#,##0"
        c2.alignment = align_right
        
        # Average: AVERAGEIF
        c3 = ws_reg.cell(row=r, column=3, value=f"=AVERAGEIF('Cleaned Data'!$G$2:$G$989, A{r}, 'Cleaned Data'!$D$2:$D$989)")
        c3.number_format = "0.00"
        c3.font = num_bold
        c3.alignment = align_right
        
        # Exact pre-calculated metrics for regional median, min, max, std dev to guarantee compatibility
        reg_sub = df[df["region"] == reg]["yield_t_per_ha"]
        
        c4 = ws_reg.cell(row=r, column=4, value=float(reg_sub.median()))
        c4.number_format = "0.00"
        c4.alignment = align_right
        
        c5 = ws_reg.cell(row=r, column=5, value=float(reg_sub.min()))
        c5.number_format = "0.00"
        c5.alignment = align_right
        
        c6 = ws_reg.cell(row=r, column=6, value=float(reg_sub.max()))
        c6.number_format = "0.00"
        c6.alignment = align_right
        
        c7 = ws_reg.cell(row=r, column=7, value=float(reg_sub.std()))
        c7.number_format = "0.00"
        c7.alignment = align_right
        
        c8 = ws_reg.cell(row=r, column=8, value=f"=G{r}/C{r}")
        c8.number_format = "0.00%"
        c8.alignment = align_right
        
        ws_reg.cell(row=r, column=9, value=rating).font = body_font
        
        for c in range(1, 10):
            ws_reg.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_reg.cell(row=r, column=c).fill = zebra_fill
                
    # Total row
    tot_r = 11
    ws_reg.cell(row=tot_r, column=1, value="Total / Benchmark Average").font = Font(name=FONT_FAMILY, size=10, bold=True, color="1E4620")
    ws_reg.cell(row=tot_r, column=2, value="=SUM(B6:B10)").number_format = "#,##0"
    ws_reg.cell(row=tot_r, column=3, value="=AVERAGE('Cleaned Data'!$D$2:$D$989)").number_format = "0.00"
    ws_reg.cell(row=tot_r, column=4, value="=MEDIAN('Cleaned Data'!$D$2:$D$989)").number_format = "0.00"
    ws_reg.cell(row=tot_r, column=5, value="=MIN('Cleaned Data'!$D$2:$D$989)").number_format = "0.00"
    ws_reg.cell(row=tot_r, column=6, value="=MAX('Cleaned Data'!$D$2:$D$989)").number_format = "0.00"
    ws_reg.cell(row=tot_r, column=7, value="=STDEV('Cleaned Data'!$D$2:$D$989)").number_format = "0.00"
    ws_reg.cell(row=tot_r, column=8, value="=G11/C11").number_format = "0.00%"
    ws_reg.cell(row=tot_r, column=9, value="Aggregated Portfolio").font = body_bold
    for c in range(1, 10):
        ws_reg.cell(row=tot_r, column=c).fill = total_fill
        ws_reg.cell(row=tot_r, column=c).border = total_border
        
    # Chart: Horizontal Bar Chart of Average Yield by Region
    chart_reg = BarChart()
    chart_reg.type = "bar" # horizontal
    chart_reg.style = 10
    chart_reg.title = "Average Crop Yield by Agricultural Region (t/ha)"
    chart_reg.x_axis.title = "Yield (t/ha)"
    chart_reg.y_axis.title = "Region"
    chart_reg.legend = None
    chart_reg.width = 16
    chart_reg.height = 10
    
    data_ref = Reference(ws_reg, min_col=3, min_row=5, max_row=10)
    cats_ref = Reference(ws_reg, min_col=1, min_row=6, max_row=10)
    chart_reg.add_data(data_ref, titles_from_data=True)
    chart_reg.set_categories(cats_ref)
    ws_reg.add_chart(chart_reg, "A14")
    
    # Regional Crop Breakdown Table
    ws_reg["I14"] = "2. REGIONAL CROP COMPOSITION BREAKDOWN (CONFOUNDING CHECK)"
    ws_reg["I14"].font = section_font
    
    comp_headers = ["Region", "Maize", "Wheat", "Soybean", "Barley", "Total Fields", "Dominant Crop Species"]
    for c_idx, h in enumerate(comp_headers, 9):
        ws_reg.cell(row=15, column=c_idx, value=h)
    style_table_header(ws_reg, row=15, start_col=9, end_col=15, fill=secondary_header_fill)
    
    for idx, (reg, _) in enumerate(regions_list):
        r = 16 + idx
        ws_reg.cell(row=r, column=9, value=reg).font = body_bold
        sub_r = df[df["region"] == reg]
        m_cnt = int((sub_r["crop"] == "Maize").sum())
        w_cnt = int((sub_r["crop"] == "Wheat").sum())
        s_cnt = int((sub_r["crop"] == "Soybean").sum())
        b_cnt = int((sub_r["crop"] == "Barley").sum())
        tot_c = len(sub_r)
        dom = sub_r["crop"].mode()[0]
        
        ws_reg.cell(row=r, column=10, value=m_cnt).number_format = "#,##0"
        ws_reg.cell(row=r, column=11, value=w_cnt).number_format = "#,##0"
        ws_reg.cell(row=r, column=12, value=s_cnt).number_format = "#,##0"
        ws_reg.cell(row=r, column=13, value=b_cnt).number_format = "#,##0"
        ws_reg.cell(row=r, column=14, value=tot_c).number_format = "#,##0"
        ws_reg.cell(row=r, column=15, value=dom).font = body_bold
        
        for c in range(9, 16):
            ws_reg.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_reg.cell(row=r, column=c).fill = zebra_fill

    # =========================================================================
    # SHEET 5: RAINFALL ANALYSIS
    # =========================================================================
    print("Building Sheet 5: Rainfall Analysis...")
    ws_rain = wb.create_sheet(title="Rainfall Analysis")
    ws_rain.views.sheetView[0].showGridLines = True
    
    ws_rain["A1"] = "AgriNova Farm Analytics — Rainfall vs. Crop Yield Dynamics"
    ws_rain["A1"].font = title_font
    ws_rain["A2"] = "Investigating precipitation response curves, regression parameters, and diminishing return saturation"
    ws_rain["A2"].font = subtitle_font
    
    # Section 1: Summary Statistics & Regression Parameters
    ws_rain["A4"] = "1. BIVARIATE LINEAR REGRESSION & CORRELATION METRICS"
    ws_rain["A4"].font = section_font
    
    rain_reg_headers = ["Statistical Parameter", "Excel Formula Syntax", "Calculated Metric Value", "Unit / Format", "Agronomic Interpretation"]
    for c_idx, h in enumerate(rain_reg_headers, 1):
        ws_rain.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_rain, row=5, start_col=1, end_col=5)
    
    reg_rows = [
        ("Pearson Correlation Coefficient (r)", "=CORREL('Cleaned Data'!$P$2:$P$989, 'Cleaned Data'!$D$2:$D$989)", "-0.2886", "Dimensionless [-1, +1]", "Linear inverse association confounded by Highlands soil acidity"),
        ("Linear Regression Slope (m)", "=SLOPE('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)", "-0.0034", "t/ha per mm rain", "Marginal linear change across pooled macro-regions"),
        ("Regression Intercept (b)", "=INTERCEPT('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)", "7.1512", "t/ha", "Theoretical intercept baseline"),
        ("Coefficient of Determination (R²)", "=RSQ('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)", "0.0833", "R² [0, 1]", "Linear model explains only 8.3% of variance due to non-linearity"),
        ("Mean Seasonal Rainfall", "=AVERAGE('Cleaned Data'!$P$2:$P$989)", "656.4", "mm", "Macro-portfolio average seasonal precipitation"),
        ("Rainfall Standard Deviation", "=STDEV('Cleaned Data'!$P$2:$P$989)", "190.2", "mm", "Climatic variability between drought years (2023) and wet years (2022)")
    ]
    
    for idx, (p_name, f_syn, val, unit, interp) in enumerate(reg_rows):
        r = 6 + idx
        ws_rain.cell(row=r, column=1, value=p_name).font = body_bold
        ws_rain.cell(row=r, column=2, value=f_syn).font = Font(name=FONT_FAMILY, size=9, color="0D47A1")
        c3 = ws_rain.cell(row=r, column=3, value=float(val) if "-" in val or "." in val else val)
        c3.font = num_bold
        c3.number_format = "0.0000" if "Correlation" in p_name or "Slope" in p_name or "R²" in p_name else "0.0"
        c3.alignment = align_right
        ws_rain.cell(row=r, column=4, value=unit).font = body_font
        ws_rain.cell(row=r, column=5, value=interp).font = body_font
        for c in range(1, 6):
            ws_rain.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_rain.cell(row=r, column=c).fill = zebra_fill

    # Section 2: Non-Linear Rainfall Brackets Table
    ws_rain["A14"] = "2. NON-LINEAR RAINFALL RESPONSE BRACKETS (AGRONOMIC SATURATION ANALYSIS)"
    ws_rain["A14"].font = section_font
    
    brack_headers = ["Rainfall Interval", "Climatic Regime", "Field Count", "Average Yield (t/ha)", "Median Yield (t/ha)", "Agronomic Water Status"]
    for c_idx, h in enumerate(brack_headers, 1):
        ws_rain.cell(row=15, column=c_idx, value=h)
    style_table_header(ws_rain, row=15, start_col=1, end_col=6, fill=secondary_header_fill)
    
    # Pre-calculated bracket metrics
    b1 = df[df["seasonal_rainfall_mm"] < 500]
    b2 = df[(df["seasonal_rainfall_mm"] >= 500) & (df["seasonal_rainfall_mm"] < 750)]
    b3 = df[(df["seasonal_rainfall_mm"] >= 750) & (df["seasonal_rainfall_mm"] < 900)]
    b4 = df[df["seasonal_rainfall_mm"] >= 900]
    
    brackets_data = [
        ("< 500 mm", "Moisture Deficit / Drought Risk", len(b1), float(b1["yield_t_per_ha"].mean()), float(b1["yield_t_per_ha"].median()), "High vulnerability in rainfed fields; requires drip/sprinkler supplementation"),
        ("500 - 750 mm", "Agronomic Optimum Window", len(b2), float(b2["yield_t_per_ha"].mean()), float(b2["yield_t_per_ha"].median()), "Optimal physiological water availability; peak crop productivity observed"),
        ("750 - 900 mm", "Abundant Moisture", len(b3), float(b3["yield_t_per_ha"].mean()), float(b3["yield_t_per_ha"].median()), "Diminishing marginal returns; adequate moisture but disease risk increases"),
        ("≥ 900 mm", "Moisture Saturation / Excess", len(b4), float(b4["yield_t_per_ha"].mean()), float(b4["yield_t_per_ha"].median()), "Coincides with Highlands acidic soils; waterlogging and root hypoxia risks")
    ]
    
    for idx, (b_name, regime, cnt, mean_y, med_y, interp) in enumerate(brackets_data):
        r = 16 + idx
        ws_rain.cell(row=r, column=1, value=b_name).font = body_bold
        ws_rain.cell(row=r, column=2, value=regime).font = body_font
        ws_rain.cell(row=r, column=3, value=cnt).number_format = "#,##0"
        c4 = ws_rain.cell(row=r, column=4, value=mean_y)
        c4.number_format = "0.00"
        c4.font = num_bold
        c5 = ws_rain.cell(row=r, column=5, value=med_y)
        c5.number_format = "0.00"
        ws_rain.cell(row=r, column=6, value=interp).font = body_font
        for c in range(1, 7):
            ws_rain.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_rain.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Column Chart of Yield across Rainfall Intervals
    chart_rain_brack = BarChart()
    chart_rain_brack.type = "col"
    chart_rain_brack.style = 11
    chart_rain_brack.title = "Crop Yield Across Rainfall Intervals (t/ha)"
    chart_rain_brack.y_axis.title = "Average Yield (t/ha)"
    chart_rain_brack.x_axis.title = "Precipitation Bracket"
    chart_rain_brack.legend = None
    chart_rain_brack.width = 16
    chart_rain_brack.height = 10
    
    d_ref = Reference(ws_rain, min_col=4, min_row=15, max_row=19)
    c_ref = Reference(ws_rain, min_col=1, min_row=16, max_row=19)
    chart_rain_brack.add_data(d_ref, titles_from_data=True)
    chart_rain_brack.set_categories(c_ref)
    ws_rain.add_chart(chart_rain_brack, "A22")

    # =========================================================================
    # SHEET 6: SOIL ANALYSIS
    # =========================================================================
    print("Building Sheet 6: Soil Analysis...")
    ws_soil = wb.create_sheet(title="Soil Analysis")
    ws_soil.views.sheetView[0].showGridLines = True
    
    ws_soil["A1"] = "AgriNova Farm Analytics — Soil Chemistry & Nutrient Impact Analysis"
    ws_soil["A1"].font = title_font
    ws_soil["A2"] = "Evaluating soil pH categories, macronutrient levels (N-P-K), and moisture bioavailability"
    ws_soil["A2"].font = subtitle_font
    
    # Section 1: Soil pH Categorization Table
    ws_soil["A4"] = "1. SOIL pH CLASSIFICATION & YIELD RESPONSE"
    ws_soil["A4"].font = section_font
    
    ph_headers = ["Soil pH Category", "pH Range Boundary", "Observations (N)", "Average Yield (t/ha)", "Median Yield (t/ha)", "Std Dev (t/ha)", "Agronomic Chemistry Mechanism"]
    for c_idx, h in enumerate(ph_headers, 1):
        ws_soil.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_soil, row=5, start_col=1, end_col=len(ph_headers))
    
    ph_b1 = df[df["soil_ph"] < 6.0]
    ph_b2 = df[(df["soil_ph"] >= 6.0) & (df["soil_ph"] <= 7.2)]
    ph_b3 = df[df["soil_ph"] > 7.2]
    
    ph_table_data = [
        ("Acidic Soils", "pH < 6.0", len(ph_b1), float(ph_b1["yield_t_per_ha"].mean()), float(ph_b1["yield_t_per_ha"].median()), float(ph_b1["yield_t_per_ha"].std()), "Severe aluminum/manganese toxicity; binds soluble phosphorus into insoluble compounds; suppresses nodulation."),
        ("Near-Neutral Soils", "6.0 ≤ pH ≤ 7.2", len(ph_b2), float(ph_b2["yield_t_per_ha"].mean()), float(ph_b2["yield_t_per_ha"].median()), float(ph_b2["yield_t_per_ha"].std()), "Optimal agronomic bioavailability window; maximum nitrogen and phosphorus solubility; robust microbial activity."),
        ("Alkaline Soils", "pH > 7.2", len(ph_b3), float(ph_b3["yield_t_per_ha"].mean()), float(ph_b3["yield_t_per_ha"].median()), float(ph_b3["yield_t_per_ha"].std()), "Common in arid Southern Basin; calcium carbonate precipitation reduces iron and zinc micronutrient bioavailability.")
    ]
    
    for idx, (cat_name, ph_rng, cnt, mean_y, med_y, std_y, mech) in enumerate(ph_table_data):
        r = 6 + idx
        ws_soil.cell(row=r, column=1, value=cat_name).font = body_bold
        ws_soil.cell(row=r, column=2, value=ph_rng).font = body_font
        ws_soil.cell(row=r, column=3, value=cnt).number_format = "#,##0"
        c4 = ws_soil.cell(row=r, column=4, value=mean_y)
        c4.number_format = "0.00"
        c4.font = num_bold
        c5 = ws_soil.cell(row=r, column=5, value=med_y)
        c5.number_format = "0.00"
        c6 = ws_soil.cell(row=r, column=6, value=std_y)
        c6.number_format = "0.00"
        ws_soil.cell(row=r, column=7, value=mech).font = body_font
        for c in range(1, 8):
            ws_soil.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_soil.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Soil pH Category Bar Chart
    chart_ph = BarChart()
    chart_ph.type = "col"
    chart_ph.style = 10
    chart_ph.title = "Average Crop Yield by Soil pH Category (t/ha)"
    chart_ph.y_axis.title = "Yield (t/ha)"
    chart_ph.x_axis.title = "Soil pH Class"
    chart_ph.legend = None
    chart_ph.width = 15
    chart_ph.height = 9
    
    d_ref_ph = Reference(ws_soil, min_col=4, min_row=5, max_row=8)
    c_ref_ph = Reference(ws_soil, min_col=1, min_row=6, max_row=8)
    chart_ph.add_data(d_ref_ph, titles_from_data=True)
    chart_ph.set_categories(c_ref_ph)
    ws_soil.add_chart(chart_ph, "A11")

    # Section 2: Soil Nutrient Summary Table
    ws_soil["I11"] = "2. SOIL NUTRIENT CONCENTRATIONS & AGRONOMIC ADEQUACY"
    ws_soil["I11"].font = section_font
    
    nut_headers = ["Soil Nutrient Factor", "Mean (ppm)", "Median (ppm)", "Min (ppm)", "Max (ppm)", "Correlation with Yield (r)", "Agronomic Role"]
    for c_idx, h in enumerate(nut_headers, 9):
        ws_soil.cell(row=12, column=c_idx, value=h)
    style_table_header(ws_soil, row=12, start_col=9, end_col=15, fill=secondary_header_fill)
    
    nut_data = [
        ("Nitrogen (N)", float(df["nitrogen_ppm"].mean()), float(df["nitrogen_ppm"].median()), float(df["nitrogen_ppm"].min()), float(df["nitrogen_ppm"].max()), float(df["nitrogen_ppm"].corr(df["yield_t_per_ha"])), "Primary vegetative protein & chlorophyll driver"),
        ("Phosphorus (P)", float(df["phosphorus_ppm"].mean()), float(df["phosphorus_ppm"].median()), float(df["phosphorus_ppm"].min()), float(df["phosphorus_ppm"].max()), float(df["phosphorus_ppm"].corr(df["yield_t_per_ha"])), "Root energy transfer & seed formation"),
        ("Potassium (K)", float(df["potassium_ppm"].mean()), float(df["potassium_ppm"].median()), float(df["potassium_ppm"].min()), float(df["potassium_ppm"].max()), float(df["potassium_ppm"].corr(df["yield_t_per_ha"])), "Stomatal water regulation & disease defense")
    ]
    
    for idx, (n_name, n_mean, n_med, n_min, n_max, n_corr, a_role) in enumerate(nut_data):
        r = 13 + idx
        ws_soil.cell(row=r, column=9, value=n_name).font = body_bold
        ws_soil.cell(row=r, column=10, value=n_mean).number_format = "#,##0.0"
        ws_soil.cell(row=r, column=11, value=n_med).number_format = "#,##0.0"
        ws_soil.cell(row=r, column=12, value=n_min).number_format = "#,##0.0"
        ws_soil.cell(row=r, column=13, value=n_max).number_format = "#,##0.0"
        c14 = ws_soil.cell(row=r, column=14, value=n_corr)
        c14.font = num_bold
        c14.number_format = "+0.0000"
        ws_soil.cell(row=r, column=15, value=a_role).font = body_font
        for c in range(9, 16):
            ws_soil.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_soil.cell(row=r, column=c).fill = zebra_fill

    # =========================================================================
    # SHEET 7: IRRIGATION ANALYSIS
    # =========================================================================
    print("Building Sheet 7: Irrigation Analysis...")
    ws_irr = wb.create_sheet(title="Irrigation Analysis")
    ws_irr.views.sheetView[0].showGridLines = True
    
    ws_irr["A1"] = "AgriNova Farm Analytics — Irrigation Regime Impact on Crop Yield"
    ws_irr["A1"].font = title_font
    ws_irr["A2"] = "Comparative evaluation of Drip, Sprinkler, Flood, and Rainfed water delivery systems"
    ws_irr["A2"].font = subtitle_font
    
    ws_irr["A4"] = "1. IRRIGATION METHODS SUMMARY TABLE"
    ws_irr["A4"].font = section_font
    
    irr_headers = ["Irrigation Method", "Observations (N)", "Average Yield (t/ha)", "Median Yield (t/ha)", "Std Dev (t/ha)", "CV (%)", "Yield Difference vs Rainfed", "Water Efficiency Rating"]
    for c_idx, h in enumerate(irr_headers, 1):
        ws_irr.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_irr, row=5, start_col=1, end_col=len(irr_headers))
    
    irr_list = [
        ("Drip", "High Precision (+35.7% vs Rainfed)"),
        ("Sprinkler", "Moderate-High (+29.2% vs Rainfed)"),
        ("Flood", "Moderate Efficiency (+21.7% vs Rainfed)"),
        ("Rainfed", "Baseline Control (No Water Infrastructure)")
    ]
    
    rainfed_mean = float(df[df["irrigation_type"] == "Rainfed"]["yield_t_per_ha"].mean())
    
    for idx, (irr_m, eff_rating) in enumerate(irr_list):
        r = 6 + idx
        ws_irr.cell(row=r, column=1, value=irr_m).font = body_bold
        sub_irr = df[df["irrigation_type"] == irr_m]["yield_t_per_ha"]
        
        # Formulas & pre-calculated values
        c2 = ws_irr.cell(row=r, column=2, value=f"=COUNTIF('Cleaned Data'!$J$2:$J$989, A{r})")
        c2.number_format = "#,##0"
        c2.alignment = align_right
        
        c3 = ws_irr.cell(row=r, column=3, value=f"=AVERAGEIF('Cleaned Data'!$J$2:$J$989, A{r}, 'Cleaned Data'!$D$2:$D$989)")
        c3.number_format = "0.00"
        c3.font = num_bold
        c3.alignment = align_right
        
        c4 = ws_irr.cell(row=r, column=4, value=float(sub_irr.median()))
        c4.number_format = "0.00"
        c4.alignment = align_right
        
        c5 = ws_irr.cell(row=r, column=5, value=float(sub_irr.std()))
        c5.number_format = "0.00"
        c5.alignment = align_right
        
        c6 = ws_irr.cell(row=r, column=6, value=f"=E{r}/C{r}")
        c6.number_format = "0.00%"
        c6.alignment = align_right
        
        diff_pct = (float(sub_irr.mean()) - rainfed_mean) / rainfed_mean
        c7 = ws_irr.cell(row=r, column=7, value=diff_pct)
        c7.number_format = "+0.0%;-0.0%;0.0%"
        c7.font = body_bold
        c7.alignment = align_right
        
        ws_irr.cell(row=r, column=8, value=eff_rating).font = body_font
        for c in range(1, 9):
            ws_irr.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_irr.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Column Chart of Yield by Irrigation Method
    chart_irr = BarChart()
    chart_irr.type = "col"
    chart_irr.style = 10
    chart_irr.title = "Average Crop Yield by Irrigation Method (t/ha)"
    chart_irr.y_axis.title = "Yield (t/ha)"
    chart_irr.x_axis.title = "Irrigation System"
    chart_irr.legend = None
    chart_irr.width = 15
    chart_irr.height = 9
    
    d_ref_irr = Reference(ws_irr, min_col=3, min_row=5, max_row=9)
    c_ref_irr = Reference(ws_irr, min_col=1, min_row=6, max_row=9)
    chart_irr.add_data(d_ref_irr, titles_from_data=True)
    chart_irr.set_categories(c_ref_irr)
    ws_irr.add_chart(chart_irr, "A12")

    # Section 2: Regional Irrigation Cross-Tabulation
    ws_irr["I12"] = "2. IRRIGATION METHOD BY AGRO-REGION CROSS-TABULATION"
    ws_irr["I12"].font = section_font
    
    irr_cross_headers = ["Region", "Drip", "Sprinkler", "Flood", "Rainfed", "Total", "% Irrigated"]
    for c_idx, h in enumerate(irr_cross_headers, 9):
        ws_irr.cell(row=13, column=c_idx, value=h)
    style_table_header(ws_irr, row=13, start_col=9, end_col=15, fill=secondary_header_fill)
    
    for idx, (reg, _) in enumerate(regions_list):
        r = 14 + idx
        ws_irr.cell(row=r, column=9, value=reg).font = body_bold
        sub_r = df[df["region"] == reg]
        d_cnt = int((sub_r["irrigation_type"] == "Drip").sum())
        sp_cnt = int((sub_r["irrigation_type"] == "Sprinkler").sum())
        fl_cnt = int((sub_r["irrigation_type"] == "Flood").sum())
        rf_cnt = int((sub_r["irrigation_type"] == "Rainfed").sum())
        tot_cnt = len(sub_r)
        pct_irr = (tot_cnt - rf_cnt) / tot_cnt
        
        ws_irr.cell(row=r, column=10, value=d_cnt).number_format = "#,##0"
        ws_irr.cell(row=r, column=11, value=sp_cnt).number_format = "#,##0"
        ws_irr.cell(row=r, column=12, value=fl_cnt).number_format = "#,##0"
        ws_irr.cell(row=r, column=13, value=rf_cnt).number_format = "#,##0"
        ws_irr.cell(row=r, column=14, value=tot_cnt).number_format = "#,##0"
        c15 = ws_irr.cell(row=r, column=15, value=pct_irr)
        c15.number_format = "0.0%"
        c15.font = body_bold
        for c in range(9, 16):
            ws_irr.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_irr.cell(row=r, column=c).fill = zebra_fill

    # =========================================================================
    # SHEET 8: SOWING PERIOD ANALYSIS
    # =========================================================================
    print("Building Sheet 8: Sowing Period Analysis...")
    ws_sow = wb.create_sheet(title="Sowing Period Analysis")
    ws_sow.views.sheetView[0].showGridLines = True
    
    ws_sow["A1"] = "AgriNova Farm Analytics — Sowing Date & Seasonal Window Analysis"
    ws_sow["A1"].font = title_font
    ws_sow["A2"] = "Evaluating planting window timing, thermal accumulation, and crop-specific agricultural calendars"
    ws_sow["A2"].font = subtitle_font
    
    ws_sow["A4"] = "1. AGRONOMIC SOWING PERIOD SUMMARY TABLE"
    ws_sow["A4"].font = section_font
    
    sow_headers = ["Agronomic Sowing Period", "Calendar Months", "Observations (N)", "Average Yield (t/ha)", "Median Yield (t/ha)", "Std Dev (t/ha)", "Target Crop Agronomy"]
    for c_idx, h in enumerate(sow_headers, 1):
        ws_sow.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_sow, row=5, start_col=1, end_col=len(sow_headers))
    
    sow_periods = [
        ("Early Spring", "March – April", "Optimal planting for summer grains (Maize & Soybean); avoids silking heat waves."),
        ("Late Spring", "May", "Delayed summer planting; increased risk of reproductive heat stress in July/August."),
        ("Autumn", "October", "Optimal planting for winter cereals (Wheat & Barley); allows vernalization.")
    ]
    
    for idx, (p_name, m_range, target_ag) in enumerate(sow_periods):
        r = 6 + idx
        ws_sow.cell(row=r, column=1, value=p_name).font = body_bold
        ws_sow.cell(row=r, column=2, value=m_range).font = body_font
        
        sub_sow = df_clean[df_clean["sowing_period"] == p_name]["yield_t_per_ha"]
        
        c3 = ws_sow.cell(row=r, column=3, value=f"=COUNTIF('Cleaned Data'!$N$2:$N$989, A{r})")
        c3.number_format = "#,##0"
        c3.alignment = align_right
        
        c4 = ws_sow.cell(row=r, column=4, value=f"=AVERAGEIF('Cleaned Data'!$N$2:$N$989, A{r}, 'Cleaned Data'!$D$2:$D$989)")
        c4.number_format = "0.00"
        c4.font = num_bold
        c4.alignment = align_right
        
        c5 = ws_sow.cell(row=r, column=5, value=float(sub_sow.median()))
        c5.number_format = "0.00"
        c5.alignment = align_right
        
        c6 = ws_sow.cell(row=r, column=6, value=float(sub_sow.std()))
        c6.number_format = "0.00"
        c6.alignment = align_right
        
        ws_sow.cell(row=r, column=7, value=target_ag).font = body_font
        for c in range(1, 8):
            ws_sow.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_sow.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Sowing Period Yield Chart
    chart_sow = BarChart()
    chart_sow.type = "col"
    chart_sow.style = 10
    chart_sow.title = "Average Crop Yield by Sowing Period (t/ha)"
    chart_sow.y_axis.title = "Yield (t/ha)"
    chart_sow.x_axis.title = "Agronomic Planting Window"
    chart_sow.legend = None
    chart_sow.width = 15
    chart_sow.height = 9
    
    d_ref_sow = Reference(ws_sow, min_col=4, min_row=5, max_row=8)
    c_ref_sow = Reference(ws_sow, min_col=1, min_row=6, max_row=8)
    chart_sow.add_data(d_ref_sow, titles_from_data=True)
    chart_sow.set_categories(c_ref_sow)
    ws_sow.add_chart(chart_sow, "A12")

    # Section 2: Calendar Quarters Summary Table
    ws_sow["I12"] = "2. CALENDAR QUARTERS SUMMARY TABLE (Q1 - Q4)"
    ws_sow["I12"].font = section_font
    
    q_headers = ["Calendar Quarter", "Field Count", "Average Yield (t/ha)", "Median Yield (t/ha)", "Dominant Crops Planted"]
    for c_idx, h in enumerate(q_headers, 9):
        ws_sow.cell(row=13, column=c_idx, value=h)
    style_table_header(ws_sow, row=13, start_col=9, end_col=13, fill=secondary_header_fill)
    
    q_data = [
        ("Q1 (Jan-Mar)", len(df_clean[df_clean["calendar_quarter"] == "Q1 (Jan-Mar)"]), float(df_clean[df_clean["calendar_quarter"] == "Q1 (Jan-Mar)"]["yield_t_per_ha"].mean()), float(df_clean[df_clean["calendar_quarter"] == "Q1 (Jan-Mar)"]["yield_t_per_ha"].median()), "Early spring cereal establishment"),
        ("Q2 (Apr-Jun)", len(df_clean[df_clean["calendar_quarter"] == "Q2 (Apr-Jun)"]), float(df_clean[df_clean["calendar_quarter"] == "Q2 (Apr-Jun)"]["yield_t_per_ha"].mean()), float(df_clean[df_clean["calendar_quarter"] == "Q2 (Apr-Jun)"]["yield_t_per_ha"].median()), "Primary summer grain sowing (Maize, Soy)"),
        ("Q3 (Jul-Sep)", len(df_clean[df_clean["calendar_quarter"] == "Q3 (Jul-Sep)"]), float(df_clean[df_clean["calendar_quarter"] == "Q3 (Jul-Sep)"]["yield_t_per_ha"].mean()), float(df_clean[df_clean["calendar_quarter"] == "Q3 (Jul-Sep)"]["yield_t_per_ha"].median()), "Early autumn cereal seeding"),
        ("Q4 (Oct-Dec)", len(df_clean[df_clean["calendar_quarter"] == "Q4 (Oct-Dec)"]), float(df_clean[df_clean["calendar_quarter"] == "Q4 (Oct-Dec)"]["yield_t_per_ha"].mean()), float(df_clean[df_clean["calendar_quarter"] == "Q4 (Oct-Dec)"]["yield_t_per_ha"].median()), "Winter wheat & winter barley planting")
    ]
    
    for idx, (q_name, cnt, mean_y, med_y, crops_desc) in enumerate(q_data):
        r = 14 + idx
        ws_sow.cell(row=r, column=9, value=q_name).font = body_bold
        ws_sow.cell(row=r, column=10, value=cnt).number_format = "#,##0"
        c11 = ws_sow.cell(row=r, column=11, value=mean_y)
        c11.number_format = "0.00"
        c11.font = num_bold
        c12 = ws_sow.cell(row=r, column=12, value=med_y)
        c12.number_format = "0.00"
        ws_sow.cell(row=r, column=13, value=crops_desc).font = body_font
        for c in range(9, 14):
            ws_sow.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_sow.cell(row=r, column=c).fill = zebra_fill

    # =========================================================================
    # SHEET 9: YIELD VARIABILITY
    # =========================================================================
    print("Building Sheet 9: Yield Variability...")
    ws_var = wb.create_sheet(title="Yield Variability")
    ws_var.views.sheetView[0].showGridLines = True
    
    ws_var["A1"] = "AgriNova Farm Analytics — Multi-Season Field Yield Stability & Volatility Analysis"
    ws_var["A1"].font = title_font
    ws_var["A2"] = "Screening threshold: Fields with ≥3 observed seasons | Quantifying temporal stability via Coefficient of Variation (CV %)"
    ws_var["A2"].font = subtitle_font
    
    # Calculate Field Stability across 4 seasons
    field_grp = df.groupby("field_id").agg(
        region=("region", "first"),
        crop=("crop", "first"),
        irrigation=("irrigation_type", "first"),
        seasons_count=("season", "count"),
        mean_yield_t=("yield_t_per_ha", "mean"),
        std_yield_t=("yield_t_per_ha", "std"),
        min_yield_t=("yield_t_per_ha", "min"),
        max_yield_t=("yield_t_per_ha", "max")
    ).reset_index()
    
    field_grp["range_t"] = field_grp["max_yield_t"] - field_grp["min_yield_t"]
    field_grp["cv_pct"] = (field_grp["std_yield_t"] / field_grp["mean_yield_t"] * 100.0).round(2)
    
    # Filter for fields with at least 3 seasons (Screening rule)
    field_eligible = field_grp[field_grp["seasons_count"] >= 3].sort_values(by="cv_pct", ascending=False).reset_index(drop=True)
    
    # Section 1: Top 10 Most Volatile Fields
    ws_var["A4"] = "1. TOP 10 MOST UNSTABLE FIELDS (HIGHEST YIELD COEFFICIENT OF VARIATION)"
    ws_var["A4"].font = section_font
    
    var_headers = ["Field ID", "Region", "Crop", "Irrigation Regime", "Observed Seasons", "Mean Yield (t/ha)", "Std Dev (t/ha)", "Min (t/ha)", "Max (t/ha)", "Range (t/ha)", "CV (%)", "Volatility Risk Level"]
    for c_idx, h in enumerate(var_headers, 1):
        ws_var.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_var, row=5, start_col=1, end_col=len(var_headers), fill=primary_header_fill)
    
    top_volatile = field_eligible.head(10)
    for idx, row in top_volatile.iterrows():
        r = 6 + idx
        ws_var.cell(row=r, column=1, value=row["field_id"]).font = body_bold
        ws_var.cell(row=r, column=2, value=row["region"]).font = body_font
        ws_var.cell(row=r, column=3, value=row["crop"]).font = body_font
        ws_var.cell(row=r, column=4, value=row["irrigation"]).font = body_font
        ws_var.cell(row=r, column=5, value=int(row["seasons_count"])).number_format = "0"
        ws_var.cell(row=r, column=6, value=float(row["mean_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=7, value=float(row["std_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=8, value=float(row["min_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=9, value=float(row["max_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=10, value=float(row["range_t"])).number_format = "0.00"
        c11 = ws_var.cell(row=r, column=11, value=float(row["cv_pct"]) / 100.0)
        c11.number_format = "0.00%"
        c11.font = Font(name=FONT_FAMILY, size=10, bold=True, color="B71C1C")
        c11.alignment = align_right
        ws_var.cell(row=r, column=12, value="HIGH VOLATILITY (Drought Sensitive)").font = body_bold
        for c in range(1, 13):
            ws_var.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_var.cell(row=r, column=c).fill = zebra_fill
                
    # Section 2: Top 10 Most Resilient Fields
    ws_var["A18"] = "2. TOP 10 MOST STABLE & RESILIENT FIELDS (LOWEST COEFFICIENT OF VARIATION)"
    ws_var["A18"].font = section_font
    
    for c_idx, h in enumerate(var_headers, 1):
        ws_var.cell(row=19, column=c_idx, value=h)
    style_table_header(ws_var, row=19, start_col=1, end_col=len(var_headers), fill=secondary_header_fill)
    
    top_stable = field_eligible.tail(10).sort_values(by="cv_pct", ascending=True)
    for idx, row in top_stable.reset_index(drop=True).iterrows():
        r = 20 + idx
        ws_var.cell(row=r, column=1, value=row["field_id"]).font = body_bold
        ws_var.cell(row=r, column=2, value=row["region"]).font = body_font
        ws_var.cell(row=r, column=3, value=row["crop"]).font = body_font
        ws_var.cell(row=r, column=4, value=row["irrigation"]).font = body_font
        ws_var.cell(row=r, column=5, value=int(row["seasons_count"])).number_format = "0"
        ws_var.cell(row=r, column=6, value=float(row["mean_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=7, value=float(row["std_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=8, value=float(row["min_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=9, value=float(row["max_yield_t"])).number_format = "0.00"
        ws_var.cell(row=r, column=10, value=float(row["range_t"])).number_format = "0.00"
        c11 = ws_var.cell(row=r, column=11, value=float(row["cv_pct"]) / 100.0)
        c11.number_format = "0.00%"
        c11.font = Font(name=FONT_FAMILY, size=10, bold=True, color="1B5E20")
        c11.alignment = align_right
        ws_var.cell(row=r, column=12, value="HIGH RESILIENCE (Stable Loam & Drip)").font = body_bold
        for c in range(1, 13):
            ws_var.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_var.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Top 5 Volatile vs Top 5 Resilient Bar Chart
    chart_var = BarChart()
    chart_var.type = "bar"
    chart_var.style = 10
    chart_var.title = "Yield Instability (CV %) of Top Unstable Fields"
    chart_var.x_axis.title = "Coefficient of Variation (%)"
    chart_var.y_axis.title = "Field ID"
    chart_var.legend = None
    chart_var.width = 16
    chart_var.height = 10
    
    d_ref_var = Reference(ws_var, min_col=11, min_row=5, max_row=15)
    c_ref_var = Reference(ws_var, min_col=1, min_row=6, max_row=15)
    chart_var.add_data(d_ref_var, titles_from_data=True)
    chart_var.set_categories(c_ref_var)
    ws_var.add_chart(chart_var, "A32")

    # =========================================================================
    # SHEET 10: PIVOT ANALYSIS (6 Multi-Dimensional Analytical Grids)
    # =========================================================================
    print("Building Sheet 10: Pivot Analysis...")
    ws_piv = wb.create_sheet(title="Pivot Analysis")
    ws_piv.views.sheetView[0].showGridLines = True
    
    ws_piv["A1"] = "AgriNova Farm Analytics — Multi-Dimensional Pivot & Cross-Tabulation Models"
    ws_piv["A1"].font = title_font
    ws_piv["A2"] = "Summary models capturing multi-way interactions across crops, regions, seasons, and irrigation practices"
    ws_piv["A2"].font = subtitle_font
    
    # Pivot 1: Yield by Crop and Region Matrix (Two-way Pivot)
    ws_piv["A4"] = "MODEL 1: AVERAGE YIELD BY CROP & REGION MATRIX (t/ha)"
    ws_piv["A4"].font = section_font
    
    piv1_headers = ["Agricultural Region", "Barley", "Maize", "Soybean", "Wheat", "Regional Average (t/ha)"]
    for c_idx, h in enumerate(piv1_headers, 1):
        ws_piv.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_piv, row=5, start_col=1, end_col=6)
    
    piv1_matrix = df.pivot_table(index="region", columns="crop", values="yield_t_per_ha", aggfunc="mean").round(2)
    # Order regions
    for idx, (reg, _) in enumerate(regions_list):
        r = 6 + idx
        ws_piv.cell(row=r, column=1, value=reg).font = body_bold
        ws_piv.cell(row=r, column=2, value=float(piv1_matrix.loc[reg, "Barley"])).number_format = "0.00"
        ws_piv.cell(row=r, column=3, value=float(piv1_matrix.loc[reg, "Maize"])).number_format = "0.00"
        ws_piv.cell(row=r, column=4, value=float(piv1_matrix.loc[reg, "Soybean"])).number_format = "0.00"
        ws_piv.cell(row=r, column=5, value=float(piv1_matrix.loc[reg, "Wheat"])).number_format = "0.00"
        reg_avg = float(df[df["region"] == reg]["yield_t_per_ha"].mean())
        c6 = ws_piv.cell(row=r, column=6, value=reg_avg)
        c6.number_format = "0.00"
        c6.font = num_bold
        for c in range(1, 7):
            ws_piv.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_piv.cell(row=r, column=c).fill = zebra_fill
                
    # Total row for Pivot 1
    ws_piv.cell(row=11, column=1, value="Crop Portfolio Average").font = Font(name=FONT_FAMILY, size=10, bold=True, color="1E4620")
    ws_piv.cell(row=11, column=2, value=float(df[df["crop"] == "Barley"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=11, column=3, value=float(df[df["crop"] == "Maize"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=11, column=4, value=float(df[df["crop"] == "Soybean"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=11, column=5, value=float(df[df["crop"] == "Wheat"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=11, column=6, value=float(df["yield_t_per_ha"].mean())).number_format = "0.00"
    for c in range(1, 7):
        ws_piv.cell(row=11, column=c).fill = total_fill
        ws_piv.cell(row=11, column=c).border = total_border
        
    # Chart: Clustered Column Chart for Crop by Region
    chart_crop_reg = BarChart()
    chart_crop_reg.type = "col"
    chart_crop_reg.style = 10
    chart_crop_reg.title = "Average Yield by Crop Species Across Regions (t/ha)"
    chart_crop_reg.y_axis.title = "Yield (t/ha)"
    chart_crop_reg.x_axis.title = "Agro-Region"
    chart_crop_reg.width = 16
    chart_crop_reg.height = 10
    
    d_ref_cr = Reference(ws_piv, min_col=2, min_row=5, max_col=5, max_row=10)
    c_ref_cr = Reference(ws_piv, min_col=1, min_row=6, max_row=10)
    chart_crop_reg.add_data(d_ref_cr, titles_from_data=True)
    chart_crop_reg.set_categories(c_ref_cr)
    ws_piv.add_chart(chart_crop_reg, "A14")
    
    # Pivot 2: Yield by Crop and Irrigation Method Matrix
    ws_piv["H4"] = "MODEL 2: AVERAGE YIELD BY CROP & IRRIGATION METHOD (t/ha)"
    ws_piv["H4"].font = section_font
    
    piv2_headers = ["Irrigation Method", "Barley", "Maize", "Soybean", "Wheat", "Irrigation Average"]
    for c_idx, h in enumerate(piv2_headers, 8):
        ws_piv.cell(row=5, column=c_idx, value=h)
    style_table_header(ws_piv, row=5, start_col=8, end_col=13, fill=secondary_header_fill)
    
    piv2_matrix = df.pivot_table(index="irrigation_type", columns="crop", values="yield_t_per_ha", aggfunc="mean").round(2)
    for idx, (irr_m, _) in enumerate(irr_list):
        r = 6 + idx
        ws_piv.cell(row=r, column=8, value=irr_m).font = body_bold
        ws_piv.cell(row=r, column=9, value=float(piv2_matrix.loc[irr_m, "Barley"])).number_format = "0.00"
        ws_piv.cell(row=r, column=10, value=float(piv2_matrix.loc[irr_m, "Maize"])).number_format = "0.00"
        ws_piv.cell(row=r, column=11, value=float(piv2_matrix.loc[irr_m, "Soybean"])).number_format = "0.00"
        ws_piv.cell(row=r, column=12, value=float(piv2_matrix.loc[irr_m, "Wheat"])).number_format = "0.00"
        irr_avg = float(df[df["irrigation_type"] == irr_m]["yield_t_per_ha"].mean())
        c13 = ws_piv.cell(row=r, column=13, value=irr_avg)
        c13.number_format = "0.00"
        c13.font = num_bold
        for c in range(8, 14):
            ws_piv.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_piv.cell(row=r, column=c).fill = zebra_fill
                
    # Total row for Pivot 2
    ws_piv.cell(row=10, column=8, value="Overall Crop Mean").font = Font(name=FONT_FAMILY, size=10, bold=True, color="1E4620")
    ws_piv.cell(row=10, column=9, value=float(df[df["crop"] == "Barley"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=10, column=10, value=float(df[df["crop"] == "Maize"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=10, column=11, value=float(df[df["crop"] == "Soybean"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=10, column=12, value=float(df[df["crop"] == "Wheat"]["yield_t_per_ha"].mean())).number_format = "0.00"
    ws_piv.cell(row=10, column=13, value=float(df["yield_t_per_ha"].mean())).number_format = "0.00"
    for c in range(8, 14):
        ws_piv.cell(row=10, column=c).fill = total_fill
        ws_piv.cell(row=10, column=c).border = total_border
        
    # Pivot 3: Multi-Season Yield Trajectory (2021 - 2024)
    ws_piv["H14"] = "MODEL 3: MULTI-SEASON YIELD TRAJECTORY (2021-2024 TREND)"
    ws_piv["H14"].font = section_font
    
    piv3_headers = ["Season Year", "Field Count", "Mean Yield (t/ha)", "Median Yield (t/ha)", "Seasonal Climatic Character"]
    for c_idx, h in enumerate(piv3_headers, 8):
        ws_piv.cell(row=15, column=c_idx, value=h)
    style_table_header(ws_piv, row=15, start_col=8, end_col=12, fill=secondary_header_fill)
    
    season_clim_desc = {
        2021: "Baseline Agro-Meteorological Year",
        2022: "High Rainfall / Favorable Hydrological Regime (+25% rain)",
        2023: "Regional Drought Year / Thermal Heat Stress (-25% rain)",
        2024: "Recovery Year / Moderate Precipitation"
    }
    
    for idx, s in enumerate([2021, 2022, 2023, 2024]):
        r = 16 + idx
        ws_piv.cell(row=r, column=8, value=s).font = body_bold
        sub_s = df[df["season"] == s]
        ws_piv.cell(row=r, column=9, value=len(sub_s)).number_format = "#,##0"
        c10 = ws_piv.cell(row=r, column=10, value=float(sub_s["yield_t_per_ha"].mean()))
        c10.number_format = "0.00"
        c10.font = num_bold
        c11 = ws_piv.cell(row=r, column=11, value=float(sub_s["yield_t_per_ha"].median()))
        c11.number_format = "0.00"
        ws_piv.cell(row=r, column=12, value=season_clim_desc[s]).font = body_font
        for c in range(8, 13):
            ws_piv.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_piv.cell(row=r, column=c).fill = zebra_fill
                
    # Chart: Seasonal Trend Line Chart
    chart_season = LineChart()
    chart_season.title = "Annual Yield Trajectory Across Growing Seasons (2021-2024)"
    chart_season.style = 13
    chart_season.y_axis.title = "Average Yield (t/ha)"
    chart_season.x_axis.title = "Growing Season"
    chart_season.width = 15
    chart_season.height = 9
    
    d_ref_sea = Reference(ws_piv, min_col=10, min_row=15, max_row=19)
    c_ref_sea = Reference(ws_piv, min_col=8, min_row=16, max_row=19)
    chart_season.add_data(d_ref_sea, titles_from_data=True)
    chart_season.set_categories(c_ref_sea)
    ws_piv.add_chart(chart_season, "H22")
    
    # Slicer instructions note
    ws_piv["A26"] = "EXCEL SLICER & INTERACTIVE DASHBOARD ACTIVATION GUIDE:"
    ws_piv["A26"].font = Font(name=FONT_FAMILY, size=10, bold=True, color="1E4620")
    ws_piv["A27"] = "To connect interactive visual slicers in desktop Excel: 1. Click on table 'AgriData' in Sheet 'Cleaned Data'. 2. Go to 'Table Design' tab -> 'Insert Slicer'. 3. Select 'region', 'crop', 'season', and 'irrigation_type'. 4. Right-click each slicer -> 'Report Connections' and check all Pivot Tables to filter dynamically."
    ws_piv["A27"].font = Font(name=FONT_FAMILY, size=9, italic=True, color="444444")

    # =========================================================================
    # SHEET 1: EXECUTIVE SUMMARY (DASHBOARD)
    # =========================================================================
    print("Building Sheet 1: Executive Summary (Dashboard)...")
    ws_exec = wb.create_sheet(title="Executive Summary", index=0)
    ws_exec.views.sheetView[0].showGridLines = True
    
    # Dashboard Banner
    ws_exec["A1"] = "AgriNova Farm Analytics — Executive Insights Dashboard"
    ws_exec["A1"].font = Font(name=FONT_FAMILY, size=18, bold=True, color="1E4620")
    ws_exec["A2"] = "Understand Yield. Discover Influences. Support Better Farming. | Round 3 Competition Benchmark Submission"
    ws_exec["A2"].font = Font(name=FONT_FAMILY, size=10, italic=True, color="33691E")
    
    # KPI Cards Block (Row 4 to 6)
    kpis = [
        ("Total Field Observations", "=COUNT('Cleaned Data'!$D$2:$D$989)", "#,##0", "Across 250 commercial farms", "B4", "C4", "B5", "C5", "B6", "C6"),
        ("Agro-Climatic Regions", "=COUNTA('Yield by Region'!$A$6:$A$10)", "0", "Plains, Valley, Coast, Basin, Highlands", "D4", "E4", "D5", "E5", "D6", "E6"),
        ("Crops Analyzed", "4", "0", "Maize, Wheat, Soybean, Barley", "F4", "G4", "F5", "G5", "F6", "G6"),
        ("Average Yield (t/ha)", "='Statistical Analysis'!$B$8", "0.00", "Portfolio mean (~4,919 kg/ha)", "H4", "I4", "H5", "I5", "H6", "I6"),
        ("Median Yield (t/ha)", "='Statistical Analysis'!$B$9", "0.00", "50th percentile (~4,490 kg/ha)", "J4", "K4", "J5", "K5", "J6", "K6"),
        ("Yield Std Deviation", "='Statistical Analysis'!$B$13", "0.00", "Spread across species (~2,217 kg/ha)", "L4", "M4", "L5", "M5", "L6", "M6")
    ]
    
    for lbl, val_f, num_fmt, sub_t, c_top_l, c_top_r, c_mid_l, c_mid_r, c_bot_l, c_bot_r in kpis:
        # Merge 2 columns for card
        ws_exec.merge_cells(f"{c_top_l}:{c_top_r}")
        ws_exec.merge_cells(f"{c_mid_l}:{c_mid_r}")
        ws_exec.merge_cells(f"{c_bot_l}:{c_bot_r}")
        
        c_lbl = ws_exec[c_top_l]
        c_lbl.value = lbl
        c_lbl.font = kpi_lbl_font
        c_lbl.alignment = align_center
        c_lbl.fill = kpi_fill
        
        c_val = ws_exec[c_mid_l]
        c_val.value = val_f
        c_val.font = kpi_num_font
        c_val.number_format = num_fmt
        c_val.alignment = align_center
        c_val.fill = kpi_fill
        
        c_sub = ws_exec[c_bot_l]
        c_sub.value = sub_t
        c_sub.font = kpi_sub_font
        c_sub.alignment = align_center
        c_sub.fill = kpi_fill
        
        # Borders around merged cells
        for col_name in [c_top_l[0], c_top_r[0]]:
            for r_num in [4, 5, 6]:
                ws_exec[f"{col_name}{r_num}"].border = kpi_border
                
    # Key Business Questions & Formula-Linked Findings Table (Row 8)
    ws_exec["A8"] = "CORE BUSINESS QUESTIONS & EMPIRICAL FINDINGS (FORMULA-LINKED EVIDENCE)"
    ws_exec["A8"].font = section_font
    
    find_headers = ["Key Business Question", "Observed Empirical Answer", "Quantitative Benchmark Metric", "Statistical Evidence / Formula Source", "Agronomic Explanation & Confounding Risk"]
    for c_idx, h in enumerate(find_headers, 1):
        ws_exec.cell(row=9, column=c_idx, value=h)
    style_table_header(ws_exec, row=9, start_col=1, end_col=5, fill=primary_header_fill)
    
    findings_answers = [
        ("1. Which region has the highest average yield?", "Central Plains (5.72 t/ha)", "='Yield by Region'!$C$6", "Central Plains: 5.72 t/ha ('Yield by Region'!C6)", "High natural soil fertility (pH 7.1, 158 ppm N) and high proportion of Maize."),
        ("2. Which region has the lowest average yield?", "Eastern Highlands (3.29 t/ha)", "='Yield by Region'!$C$10", "Eastern Highlands: 3.29 t/ha ('Yield by Region'!C10)", "Chronic soil acidity (mean pH 5.5) suppresses yield despite high rainfall (>1,000 mm)."),
        ("3. What is the observed relationship with rainfall?", "Non-Linear Quadratic Saturation Curve", "='Rainfall Analysis'!$C$6", "Peak yield at 600-750 mm; linear r = -0.2886", "Diminishing returns above 850 mm; linear r is confounded by acidic Highlands."),
        ("4. Which soil factors show strongest yield link?", "Crop pH Deviation & Available Nitrogen", "='Soil Analysis'!$D$7", "Near-Neutral pH = 5.25 t/ha; Acidic pH = 3.65 t/ha", "Acidic soils (<6.0 pH) suffer aluminum toxicity and phosphorus fixation."),
        ("5. Which irrigation method has highest average yield?", "Drip Irrigation (5.53 t/ha)", "='Irrigation Analysis'!$C$6", "Drip = 5.53 t/ha vs Rainfed = 4.07 t/ha (+35.7%)", "Continuous root zone moisture without evaporative loss eliminates drought shocks."),
        ("6. Which sowing period has highest average yield?", "Early Spring (5.38 t/ha)", "='Sowing Period Analysis'!$D$6", "Early Spring = 5.38 t/ha vs Late Spring = 4.88 t/ha", "Early planting allows vegetative accumulation before summer reproductive heat waves."),
        ("7. Which fields show greatest yield variability?", "Rainfed Fields in Highlands & Southern Basin", "='Yield Variability'!$K$6", "Top volatile field CV = 28.4% (vs stable CV = 4.8%)", "Lack of irrigation infrastructure and drought-prone soils cause high inter-annual volatility.")
    ]
    
    for idx, (q, ans, met, ev, expl) in enumerate(findings_answers):
        r = 10 + idx
        ws_exec.cell(row=r, column=1, value=q).font = body_bold
        ws_exec.cell(row=r, column=2, value=ans).font = Font(name=FONT_FAMILY, size=10, bold=True, color="1B5E20")
        c3 = ws_exec.cell(row=r, column=3, value=met)
        c3.font = num_bold
        c3.number_format = "0.00" if "t/ha" not in str(met) else "@"
        c3.alignment = align_right
        ws_exec.cell(row=r, column=4, value=ev).font = Font(name=FONT_FAMILY, size=9, color="0D47A1")
        ws_exec.cell(row=r, column=5, value=expl).font = body_font
        for c in range(1, 6):
            ws_exec.cell(row=r, column=c).border = cell_border
            if r % 2 == 1:
                ws_exec.cell(row=r, column=c).fill = zebra_fill
                
    # Place Executive Charts on Dashboard
    # Chart 1: Average Yield by Region (Cloned reference to Yield by Region data)
    ch1 = BarChart()
    ch1.type = "col"
    ch1.style = 10
    ch1.title = "Average Crop Yield by Region (t/ha)"
    ch1.y_axis.title = "Yield (t/ha)"
    ch1.x_axis.title = "Agro-Region"
    ch1.legend = None
    ch1.width = 14
    ch1.height = 8.5
    d_ch1 = Reference(ws_reg, min_col=3, min_row=5, max_row=10)
    c_ch1 = Reference(ws_reg, min_col=1, min_row=6, max_row=10)
    ch1.add_data(d_ch1, titles_from_data=True)
    ch1.set_categories(c_ch1)
    ws_exec.add_chart(ch1, "A18")
    
    # Chart 2: Yield by Irrigation Method
    ch2 = BarChart()
    ch2.type = "col"
    ch2.style = 11
    ch2.title = "Yield by Irrigation Method (t/ha)"
    ch2.y_axis.title = "Yield (t/ha)"
    ch2.x_axis.title = "Irrigation Type"
    ch2.legend = None
    ch2.width = 14
    ch2.height = 8.5
    d_ch2 = Reference(ws_irr, min_col=3, min_row=5, max_row=9)
    c_ch2 = Reference(ws_irr, min_col=1, min_row=6, max_row=9)
    ch2.add_data(d_ch2, titles_from_data=True)
    ch2.set_categories(c_ch2)
    ws_exec.add_chart(ch2, "G18")
    
    # Chart 3: Yield by Sowing Period
    ch3 = BarChart()
    ch3.type = "col"
    ch3.style = 12
    ch3.title = "Yield by Sowing Window (t/ha)"
    ch3.y_axis.title = "Yield (t/ha)"
    ch3.x_axis.title = "Sowing Period"
    ch3.legend = None
    ch3.width = 14
    ch3.height = 8.5
    d_ch3 = Reference(ws_sow, min_col=4, min_row=5, max_row=9)
    c_ch3 = Reference(ws_sow, min_col=1, min_row=6, max_row=9)
    ch3.add_data(d_ch3, titles_from_data=True)
    ch3.set_categories(c_ch3)
    ws_exec.add_chart(ch3, "A32")
    
    # Chart 4: Soil pH Category Yield
    ch4 = BarChart()
    ch4.type = "col"
    ch4.style = 13
    ch4.title = "Yield by Soil pH Category (t/ha)"
    ch4.y_axis.title = "Yield (t/ha)"
    ch4.x_axis.title = "pH Category"
    ch4.legend = None
    ch4.width = 14
    ch4.height = 8.5
    d_ch4 = Reference(ws_soil, min_col=4, min_row=5, max_row=8)
    c_ch4 = Reference(ws_soil, min_col=1, min_row=6, max_row=8)
    ch4.add_data(d_ch4, titles_from_data=True)
    ch4.set_categories(c_ch4)
    ws_exec.add_chart(ch4, "G32")

    # =========================================================================
    # AUTO-FIT COLUMN WIDTHS ACROSS ALL SHEETS
    # =========================================================================
    print("Adjusting column widths and margins across all 10 worksheets...")
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            # Skip checking data sheet beyond 50 rows for speed
            sample_cells = col[:60] if sheet.title == "Cleaned Data" else col
            for cell in sample_cells:
                # Avoid title rows for width calculation
                if cell.row in [1, 2] and sheet.title != "Cleaned Data":
                    continue
                val_str = str(cell.value or "")
                if val_str.startswith("="):
                    val_str = "12345.67" # estimate formula result length
                max_len = max(max_len, len(val_str))
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)
            
    # Set generous width for Executive Dashboard columns
    for cl in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]:
        ws_exec.column_dimensions[cl].width = 18

    # Ensure Excel recalculates all formulas upon opening
    wb.calculation.calcMode = "auto"
    wb.calculation.fullCalcOnLoad = True

    # 3. Save Workbook
    out_file = Path(output_path)
    wb.save(out_file)
    print(f"\n[SUCCESS] Excel workbook successfully saved at: {out_file.resolve()}")
    
    # Also save a copy inside AgriNova/ directory if path is at root
    if "AgriNova" not in str(output_path):
        agrinova_copy = Path("AgriNova") / output_path
        agrinova_copy.parent.mkdir(parents=True, exist_ok=True)
        wb.save(agrinova_copy)
        print(f"[SUCCESS] Secondary copy saved at: {agrinova_copy.resolve()}")
        
    return out_file

if __name__ == "__main__":
    create_agrinova_excel_workbook()
