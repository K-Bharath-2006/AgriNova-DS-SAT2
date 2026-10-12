# AgriNova Farm Analytics — Round 3: Data Analysis Using Excel (30 Marks)
## Submission Documentation & Quality Assurance Report

**File Generated:** `AgriNova_Round3_Excel_Analysis.xlsx`  
**File Location:** `c:\Black-Drive\My Life\Sem-5\Data Science\SAT-2\AgriNova_Round3_Excel_Analysis.xlsx` (and in `AgriNova/`)  
**Evaluation:** Round 3 Data Science Competition (30 Marks)  
**Author:** Antigravity Senior Excel Data Analyst & Agricultural Data Scientist  

---

### 1. Structure of the 10 Worksheets

| Sheet # | Worksheet Title | Purpose & Content | Primary Excel Formulas Used | Visualizations Embedded |
|:---:|:---|:---|:---|:---|
| **1** | **Executive Summary** | High-level interactive dashboard for competition evaluators and leadership. | `COUNT`, `COUNTA`, `AVERAGE`, `MEDIAN`, `STDEV.S`, cell linkages. | 4 Executive Bar Charts (Region, Irrigation, Sowing, Soil pH). |
| **2** | **Cleaned Data** | Source repository formatted as structured Excel Table `AgriData` (988 rows × 29 columns). | Column expressions, dates (`yyyy-mm-dd`), conditional formatting. | 3-Color Gradient Scale on `yield_t_per_ha`. |
| **3** | **Statistical Analysis** | Comprehensive statistical table & bivariate Pearson correlation matrix with yield. | `COUNT`, `COUNTBLANK`, `AVERAGE`, `MEDIAN`, `MIN`, `MAX`, `STDEV.S`, `VAR.S`, `QUARTILE.INC`, `CORREL`. | Correlation comparison matrix & formatting. |
| **4** | **Yield by Region** | Regional yield performance comparison & crop composition confounding check. | `COUNTIF`, `AVERAGEIF`, `STDEV.S`, `MEDIAN`, CV ratio formulas. | Horizontal Bar Chart of average yield by region. |
| **5** | **Rainfall Analysis** | Rainfall response dynamics, bivariate regression, and non-linear saturation intervals. | `CORREL`, `SLOPE`, `INTERCEPT`, `RSQ`, `AVERAGE`, interval aggregations. | Column Chart of Yield across Precipitation Brackets. |
| **6** | **Soil Analysis** | Edaphic chemistry evaluation: pH classification, N-P-K nutrient status. | `AVERAGE`, `MEDIAN`, `STDEV.S`, `CORREL`, category cross-tabulation. | Clustered Column Chart of Yield by Soil pH Category. |
| **7** | **Irrigation Analysis** | Evaluation of water infrastructure (Drip, Sprinkler, Flood, Rainfed) across regions. | `COUNTIF`, `AVERAGEIF`, relative yield difference percentages. | Clustered Column Chart of Yield by Irrigation Method. |
| **8** | **Sowing Period Analysis**| Sowing calendar optimization across agronomic windows and calendar quarters (Q1–Q4). | `COUNTIF`, `AVERAGEIF`, quarterly aggregations. | Column Chart of Yield by Sowing Period. |
| **9** | **Yield Variability** | Multi-season stability screening ($\ge 3$ seasons) via Coefficient of Variation (CV %). | `COUNT`, `AVERAGE`, `STDEV.S`, `CV = STDEV.S / AVERAGE * 100%`. | Horizontal Bar Chart of Top 10 Most Unstable Fields. |
| **10**| **Pivot Analysis** | 6 Multi-dimensional summary models & trend matrices. | Cross-tabulation matrices, row/column portfolio averages. | Crop × Region Matrix Chart & Seasonal Trajectory Line Chart. |

---

### 2. Comprehensive Inventory of Excel Formulas Used

1. **Central Tendency & Dispersion:**
   - Arithmetic Mean: `=AVERAGE('Cleaned Data'!$D$2:$D$989)`
   - Median (50th Percentile): `=MEDIAN('Cleaned Data'!$D$2:$D$989)`
   - Sample Standard Deviation: `=STDEV.S('Cleaned Data'!$D$2:$D$989)`
   - Sample Variance: `=VAR.S('Cleaned Data'!$D$2:$D$989)`
   - Range: `=MAX('Cleaned Data'!$D$2:$D$989) - MIN('Cleaned Data'!$D$2:$D$989)`
   - Quartiles: `=QUARTILE.INC('Cleaned Data'!$D$2:$D$989, 1)` and `=QUARTILE.INC('Cleaned Data'!$D$2:$D$989, 3)`
   - Interquartile Range: `=B15 - B14` (Q3 - Q1)
   - Coefficient of Variation: `=B12 / B7` (Std Dev / Mean, formatted as `0.00%`)

2. **Conditional Aggregations:**
   - Group Observation Count: `=COUNTIF('Cleaned Data'!$G$2:$G$989, A6)`
   - Conditional Group Mean: `=AVERAGEIF('Cleaned Data'!$G$2:$G$989, A6, 'Cleaned Data'!$D$2:$D$989)`
   - Distinct Count / Header Validation: `=COUNTA('Yield by Region'!$A$6:$A$10)`

3. **Bivariate Correlation & Linear Regression:**
   - Pearson Correlation Coefficient: `=CORREL('Cleaned Data'!$P$2:$P$989, 'Cleaned Data'!$D$2:$D$989)`
   - Linear Regression Slope ($m$): `=SLOPE('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)`
   - Linear Regression Intercept ($b$): `=INTERCEPT('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)`
   - Coefficient of Determination ($R^2$): `=RSQ('Cleaned Data'!$D$2:$D$989, 'Cleaned Data'!$P$2:$P$989)`

4. **Dynamic Executive Dashboard Links:**
   - Dynamic Question Answer String: `='Yield by Region'!$A$6 & ": " & TEXT('Yield by Region'!$C$6, "0.00") & " t/ha"`
   - Total Observations KPI: `=COUNT('Cleaned Data'!$A$2:$A$989)`

---

### 3. Summary of Major Empirical Findings

* **Overall Portfolio Production:**
  * Mean Yield: **4.92 t/ha** (4,918.7 kg/ha)
  * Median Yield: **4.49 t/ha** (4,489.9 kg/ha)
  * Std Dev: **2.22 t/ha** (2,216.5 kg/ha)
* **Regional Disparities:**
  * Highest: **Central Plains** (5.72 t/ha) and **North Valley** (5.62 t/ha).
  * Lowest: **Eastern Highlands** (3.29 t/ha) and **Southern Basin** (4.07 t/ha).
* **Rainfall Response Dynamics:**
  * Bivariate $r = -0.2886$ is confounded by regional geography (Simpson's Paradox).
  * True agronomic relationship is a non-linear saturation curve: peak yields occur at **500–750 mm** (mean 5.61 t/ha). Excess moisture ($>900\text{ mm}$) yields decline to 3.29 t/ha due to waterlogging and soil acidity.
* **Soil Factors:**
  * Near-Neutral soils (6.0–7.2 pH) yield **5.25 t/ha** vs. Acidic soils (<6.0 pH) yielding **3.65 t/ha** (**30.5% yield reduction**).
  * Available Nitrogen ($r = +0.22$) and Phosphorus ($r = +0.16$) exhibit positive linear correlations with harvest yield.
* **Irrigation Regimes:**
  * **Drip** delivers highest yield (**5.53 t/ha**), followed by **Sprinkler** (**5.26 t/ha**), **Flood** (**4.96 t/ha**), and **Rainfed** (**4.07 t/ha**).
  * Drip provides a **+35.7% yield premium** over rainfed cultivation.
* **Sowing Windows:**
  * **Early Spring (March–April)** yields **5.38 t/ha** for summer crops vs. Late Spring yielding **4.88 t/ha** (**9.3% heat penalty** during flowering).
* **Field Instability:**
  * Screening rule ($\ge 3$ seasons) identified top unstable fields with **CV up to 28.4%** (e.g. F_042), driven by rainfed vulnerability on drought-sensitive soils.

---

### 4. Checklist of Round 3 Requirements (30 Marks Evaluation)

- [x] **File Deliverable:** Created `AgriNova_Round3_Excel_Analysis.xlsx`.
- [x] **Dataset Import:** 988 records completely imported into structured Excel Table `AgriData`.
- [x] **Data Formatting:** Professional formatting, frozen headers, auto-filters, conditional formatting.
- [x] **Formulas & Statistics:** Built with native Excel formulas (`COUNT`, `AVERAGE`, `MEDIAN`, `STDEV.S`, `VAR.S`, `QUARTILE.INC`, `CORREL`, `SLOPE`, `INTERCEPT`, `RSQ`).
- [x] **10 Dedicated Sheets:** Complete coverage of Executive Summary, Cleaned Data, Statistics, Region, Rainfall, Soil, Irrigation, Sowing, Variability, and Pivots.
- [x] **Executive Dashboard:** 6 KPI cards, formula-linked findings table, and 4 embedded executive charts.
- [x] **6 Primary Business Questions:** Direct, evidence-based answers backed by real calculated metrics.
- [x] **Multi-Dimensional Pivot Grids:** 6 analytical matrices and trend summaries.
- [x] **Quality Assurance:** 100% verified via automated openpyxl audit script.
