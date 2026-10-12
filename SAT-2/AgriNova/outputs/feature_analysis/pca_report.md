# AgriNova - Principal Component Analysis (PCA) on Environmental Features

### Variance Explained by Principal Components

| Component   |   Variance Explained (%) |   Cumulative Variance (%) |
|:------------|-------------------------:|--------------------------:|
| PC1         |                    52.08 |                     52.08 |
| PC2         |                    12.46 |                     64.55 |
| PC3         |                    11.2  |                     75.74 |
| PC4         |                     9.53 |                     85.28 |
| PC5         |                     5.97 |                     91.25 |
| PC6         |                     4.84 |                     96.09 |
| PC7         |                     2.51 |                     98.6  |
| PC8         |                     1.14 |                     99.73 |
| PC9         |                     0.27 |                    100    |

### Factor Loadings (First 4 Components)

|                      |     PC1 |     PC2 |     PC3 |     PC4 |
|:---------------------|--------:|--------:|--------:|--------:|
| seasonal_rainfall_mm |  0.4334 |  0.0751 |  0.0377 | -0.0287 |
| mean_temperature_c   | -0.4258 | -0.2154 | -0.0439 |  0.0913 |
| temperature_range_c  | -0.3716 | -0.0041 |  0.0703 |  0.0152 |
| mean_humidity_pct    |  0.4291 |  0.2687 |  0.0298 | -0.1461 |
| soil_ph              | -0.4055 | -0.1711 | -0.0631 |  0.0338 |
| soil_moisture_pct    | -0.0206 | -0.0338 |  0.9815 |  0.1602 |
| nitrogen_ppm         | -0.2652 |  0.467  |  0.0823 | -0.3794 |
| phosphorus_ppm       | -0.1033 |  0.6208 | -0.1108 |  0.7662 |
| potassium_ppm        | -0.2505 |  0.4917 |  0.0666 | -0.4599 |

> **Strategic Decision:** While PC1-PC3 explain ~65% of environmental variance, raw engineered variables (e.g., pH deviation, rainfall) are far more interpretable for agronomic decision-making. Therefore, non-reduced features are retained for primary predictive modeling.
