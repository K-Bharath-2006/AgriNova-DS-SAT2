# AgriNova Farm Analytics - Data Quality Audit Table

| Dataset       |   Rows |   Columns |   Exact Duplicates |   Key Duplicates | Missing Values                                                                                                    |
|:--------------|-------:|----------:|-------------------:|-----------------:|:------------------------------------------------------------------------------------------------------------------|
| fields.csv    |    250 |         4 |                  0 |                0 | None                                                                                                              |
| soil.csv      |    894 |         7 |                 12 |               12 | soil_moisture_pct (56), phosphorus_ppm (36)                                                                       |
| weather.csv   |   7300 |         9 |                  0 |             7296 | rainfall_mm (262), temperature_mean_c (262), temperature_min_c (262), temperature_max_c (262), humidity_pct (262) |
| practices.csv |   1025 |         5 |                 11 |               25 | None                                                                                                              |
| harvest.csv   |   1015 |         5 |                 15 |               15 | None                                                                                                              |

### Identified Data Quality Vulnerabilities:
1. **Inconsistent Crop Names**: Mixed casing ('maize', 'MAIZE'), whitespace (' wheat '), and synonyms ('Corn', 'Soy').
2. **Duplicate Records**: Duplicate (field_id, season) pairs in practices, soil, and harvest tables.
3. **Severe Yield Outliers**: Physically impossible negative yields and 10x data-entry typos (>15,000 kg/ha).
4. **Missing Soil Tests**: Missing field-season soil testing records, plus missing nutrient sub-measurements.
5. **Weather Data Gaps**: Distinguishing genuine zero rainfall from missing meteorological sensor logs.
