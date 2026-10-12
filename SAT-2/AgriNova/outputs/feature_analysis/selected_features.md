# AgriNova Farm Analytics - Feature Importance & Selection Analysis

### Model Evaluation (RandomForestRegressor on Field-Grouped Split)
- **Test R²**: 0.8689
- **Test RMSE**: 741.80 kg/ha
- **Test MAE**: 589.47 kg/ha

### Feature Importance Ranking

| feature                         |   permutation_importance |   mutual_information |
|:--------------------------------|-------------------------:|---------------------:|
| crop_Maize                      |              0.814768    |           0.272531   |
| crop_ph_deviation               |              0.253861    |           0.126555   |
| seasonal_rainfall_mm            |              0.204012    |           0.187285   |
| irrigation_type_Rainfed         |              0.0901822   |           0.0454446  |
| soil_ph                         |              0.045462    |           0.190535   |
| crop_Soybean                    |              0.0276687   |           0.0899051  |
| fertilizer_type_Minimal/None    |              0.0214161   |           0.0293332  |
| temperature_range_c             |              0.0187105   |           0.08368    |
| crop_Wheat                      |              0.0164639   |           0.0318879  |
| irrigation_type_Flood           |              0.0104434   |           0.0181027  |
| soil_npk_total                  |              0.00721268  |           0.0735586  |
| fertilizer_type_Synthetic NPK   |              0.00541944  |           0.0320659  |
| mean_humidity_pct               |              0.00450111  |           0.116307   |
| sowing_day_of_year              |              0.004075    |           0.0860745  |
| rain_per_rainy_day              |              0.00272407  |           0.116863   |
| nitrogen_ppm                    |              0.00240517  |           0.0421113  |
| sowing_period_Late Spring       |              0.0017141   |           0          |
| mean_temperature_c              |              0.00130902  |           0.110632   |
| sowing_month                    |              0.0006747   |           0.0736279  |
| irrigation_type_Sprinkler       |              0.000553922 |           0.0075187  |
| region_North Valley             |              0.000542522 |           0.0321549  |
| soil_tested                     |              0.00046736  |           0.00653293 |
| region_Eastern Highlands        |              0.000411234 |           0.0723747  |
| potassium_ppm                   |              0.000348806 |           0.0550999  |
| phosphorus_ppm                  |              0.000226679 |           0.0126008  |
| heat_stress_index               |              0.000170421 |           0.036758   |
| sowing_period_Early Spring      |              0.000127135 |           0          |
| region_Western Coast            |              7.09337e-05 |           0          |
| region_Southern Basin           |             -0.000103492 |           0.027809   |
| rainy_days_count                |             -0.000158595 |           0.120533   |
| fertilizer_type_Organic Compost |             -0.000263886 |           0          |
| soil_n_p_ratio                  |             -0.000860076 |           0          |
| soil_moisture_pct               |             -0.000967545 |           0.0110002  |
| area_hectares                   |             -0.00176392  |           0.0433806  |

> **Methodological Note on Causation vs Prediction:**
> High permutation and mutual information scores indicate variables with high predictive utility.
> They do NOT establish direct counterfactual causation without controlled agronomic trials.
