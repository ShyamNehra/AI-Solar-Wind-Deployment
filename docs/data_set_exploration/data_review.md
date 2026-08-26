============================================================
DATASET REVIEW
============================================================

1. Shape
(6650, 56)

2. Columns
['city', 'iso_alpha3', 'latitude', 'longitude', 'continent', 'who_region', 'wb_income_group', 'year', 'data_days', 'temp_mean_c', 'temp_max_c', 'temp_min_c', 'temp_std_c', 'temp_range_mean_c', 'temp_seasonal_amp', 'temp_yoy_change', 'temp_5yr_mean', 'temp_anomaly', 'days_above_35c', 'days_above_40c', 'days_below_0c', 'days_below_minus10c', 'heat_stress_index', 'cold_stress_index', 'drought_stress_days', 'ideal_climate_days', 'precip_total_mm', 'precip_mean_mm', 'precip_max_day_mm', 'precip_std_mm', 'precip_yoy_change', 'days_heavy_rain', 'days_moderate_rain', 'days_dry', 'rh_mean_pct', 'rh_max_pct', 'dewpoint_mean_c', 'humidity_stress_days', 'wind_mean_ms', 'wind_max_ms', 'wind_std_ms', 'high_wind_days', 'wind_power_density', 'solar_total_mj', 'solar_mean_mj', 'solar_clear_mean_mj', 'solar_clearness_idx', 'solar_peak_days', 'solar_annual_kwh_m2', 'pressure_mean_kpa', 'pressure_std_kpa', 'climate_volatility', 'gdp_per_capita_usd', 'population', 'urban_pop_pct', 'energy_use_kg_oil_eq']

3. Data Types
city                     object
iso_alpha3               object
latitude                float64
longitude               float64
continent                object
who_region               object
wb_income_group          object
year                      int64
data_days               float64
temp_mean_c             float64
temp_max_c              float64
temp_min_c              float64
temp_std_c              float64
temp_range_mean_c       float64
temp_seasonal_amp       float64
temp_yoy_change         float64
temp_5yr_mean           float64
temp_anomaly            float64
days_above_35c          float64
days_above_40c          float64
days_below_0c           float64
days_below_minus10c     float64
heat_stress_index       float64
cold_stress_index       float64
drought_stress_days     float64
ideal_climate_days      float64
precip_total_mm         float64
precip_mean_mm          float64
precip_max_day_mm       float64
precip_std_mm           float64
precip_yoy_change       float64
days_heavy_rain         float64
days_moderate_rain      float64
days_dry                float64
rh_mean_pct             float64
rh_max_pct              float64
dewpoint_mean_c         float64
humidity_stress_days    float64
wind_mean_ms            float64
wind_max_ms             float64
wind_std_ms             float64
high_wind_days          float64
wind_power_density      float64
solar_total_mj          float64
solar_mean_mj           float64
solar_clear_mean_mj     float64
solar_clearness_idx     float64
solar_peak_days         float64
solar_annual_kwh_m2     float64
pressure_mean_kpa       float64
pressure_std_kpa        float64
climate_volatility      float64
gdp_per_capita_usd      float64
population              float64
urban_pop_pct           float64
energy_use_kg_oil_eq    float64
dtype: object

4. Missing Values
city                       0
iso_alpha3                 0
latitude                   0
longitude                  0
continent                  0
who_region                 0
wb_income_group            0
year                       0
data_days                  0
temp_mean_c                0
temp_max_c                 0
temp_min_c                 0
temp_std_c                 0
temp_range_mean_c          0
temp_seasonal_amp          0
temp_yoy_change          190
temp_5yr_mean            380
temp_anomaly             380
days_above_35c             0
days_above_40c             0
days_below_0c              0
days_below_minus10c        0
heat_stress_index          0
cold_stress_index          0
drought_stress_days        0
ideal_climate_days         0
precip_total_mm            0
precip_mean_mm             0
precip_max_day_mm          0
precip_std_mm              0
precip_yoy_change        190
days_heavy_rain            0
days_moderate_rain         0
days_dry                   0
rh_mean_pct                0
rh_max_pct                 0
dewpoint_mean_c            0
humidity_stress_days       0
wind_mean_ms               0
wind_max_ms                0
wind_std_ms                0
high_wind_days             0
wind_power_density         0
solar_total_mj             0
solar_mean_mj              0
solar_clear_mean_mj        0
solar_clearness_idx     2090
solar_peak_days            0
solar_annual_kwh_m2        0
pressure_mean_kpa          0
pressure_std_kpa           0
climate_volatility         0
gdp_per_capita_usd       185
population                70
urban_pop_pct             70
energy_use_kg_oil_eq    1600
dtype: int64

5. Duplicate Rows
0

6. Unique Values
city                     190
iso_alpha3               190
latitude                 188
longitude                189
continent                  7
who_region                 7
wb_income_group            5
year                      35
data_days                  4
temp_mean_c             6606
temp_max_c              2110
temp_min_c              3646
temp_std_c              6615
temp_range_mean_c       6595
temp_seasonal_amp       6589
temp_yoy_change         5478
temp_5yr_mean           6107
temp_anomaly            5082
days_above_35c           266
days_above_40c           141
days_below_0c            226
days_below_minus10c      134
heat_stress_index         85
cold_stress_index        159
drought_stress_days      274
ideal_climate_days       255
precip_total_mm         6542
precip_mean_mm          6567
precip_max_day_mm       4441
precip_std_mm           6615
precip_yoy_change       6170
days_heavy_rain           74
days_moderate_rain       255
days_dry                 360
rh_mean_pct             6607
rh_max_pct              1850
dewpoint_mean_c         6604
humidity_stress_days     395
wind_mean_ms            6561
wind_max_ms             1366
wind_std_ms             6615
high_wind_days            59
wind_power_density      6526
solar_total_mj          6474
solar_mean_mj           6474
solar_clear_mean_mj     6472
solar_clearness_idx     4025
solar_peak_days            1
solar_annual_kwh_m2     5872
pressure_mean_kpa       6568
pressure_std_kpa        6615
climate_volatility      5633
gdp_per_capita_usd      6465
population              6574
urban_pop_pct           6466
energy_use_kg_oil_eq    5050
dtype: int64

7. Summary Statistics
             city iso_alpha3     latitude    longitude continent who_region  \
count        6650       6650  6650.000000  6650.000000      6650       6650   
unique        190        190          NaN          NaN         7          7   
top     Abu Dhabi        ARE          NaN          NaN    Europe        EUR   
freq           35         35          NaN          NaN      1715       1715   
mean          NaN        NaN    18.572421    22.186158       NaN        NaN   
std           NaN        NaN    24.232271    66.202217       NaN        NaN   
min           NaN        NaN   -41.290000  -175.200000       NaN        NaN   
25%           NaN        NaN     3.870000    -6.830000       NaN        NaN   
50%           NaN        NaN    15.450000    21.090000       NaN        NaN   
75%           NaN        NaN    39.920000    49.870000       NaN        NaN   
max           NaN        NaN    64.140000   179.200000       NaN        NaN   

       wb_income_group         year    data_days  temp_mean_c  ...  \
count             6650  6650.000000  6650.000000  6650.000000  ...   
unique               5          NaN          NaN          NaN  ...   
top           UpperMid          NaN          NaN          NaN  ...   
freq              1890          NaN          NaN          NaN  ...   
mean               NaN  2007.000000   367.179549    19.676911  ...   
std                NaN    10.100264    26.434372     7.560244  ...   
min                NaN  1990.000000   365.000000    -3.075355  ...   
25%                NaN  1998.000000   365.000000    13.222832  ...   
50%                NaN  2007.000000   365.000000    21.572223  ...   
75%                NaN  2016.000000   366.000000    26.564868  ...   
max                NaN  2024.000000   732.000000    30.141311  ...   

        solar_clearness_idx  solar_peak_days  solar_annual_kwh_m2  \
count           4560.000000           6650.0          6650.000000   
unique                  NaN              NaN                  NaN   
top                     NaN              NaN                  NaN   
freq                    NaN              NaN                  NaN   
mean               0.536499              0.0           489.724138   
std                0.074366              0.0           108.850770   
min                0.365726              0.0           213.390000   
25%                0.481500              0.0           423.240000   
50%                0.543712              0.0           507.275000   
75%                0.594252              0.0           563.645000   
max                0.706384              0.0          1185.660000   

        pressure_mean_kpa  pressure_std_kpa  climate_volatility  \
count         6650.000000       6650.000000         6650.000000   
unique                NaN               NaN                 NaN   
top                   NaN               NaN                 NaN   
freq                  NaN               NaN                 NaN   
mean            96.442585          0.435515            1.565950   
std              6.426781          0.303449            2.198223   
min             67.358388          0.069549            0.003300   
25%             93.720856          0.163692            0.248825   
50%             99.460219          0.350805            0.655950   
75%            100.849740          0.656594            2.032200   
max            101.945863          1.684677           30.616700   

        gdp_per_capita_usd    population  urban_pop_pct  energy_use_kg_oil_eq  
count          6465.000000  6.580000e+03    6580.000000           5050.000000  
unique                 NaN           NaN            NaN                   NaN  
top                    NaN           NaN            NaN                   NaN  
freq                   NaN           NaN            NaN                   NaN  
mean          10944.947814  3.555906e+07      54.797910           2274.443035  
std           18783.848991  1.330653e+08      23.016545           2757.956448  
min              22.952133  8.798000e+03       5.274941              0.000000  
25%            1014.402797  1.956066e+06      35.424115            496.586814  
50%            3435.288047  7.381301e+06      55.623062           1249.437479  
75%           11501.226519  2.312902e+07      73.249034           2893.639612  
max          206780.590353  1.450936e+09     100.000000          21557.475076  

[11 rows x 56 columns]

8. First 5 Rows
city	iso_alpha3	latitude	longitude	continent	who_region	wb_income_group	year	data_days	temp_mean_c	...	solar_clearness_idx	solar_peak_days	solar_annual_kwh_m2	pressure_mean_kpa	pressure_std_kpa	climate_volatility	gdp_per_capita_usd	population	urban_pop_pct	energy_use_kg_oil_eq
0	Abu Dhabi	ARE	24.47	54.37	E.Mediterranean	EMR	High	1990	365.0	27.695068	...	NaN	0.0	579.30	100.775370	0.801732	0.1810	26709.993440	1898220.0	78.685768	10740.842922
1	Abu Dhabi	ARE	24.47	54.37	E.Mediterranean	EMR	High	1991	365.0	27.084274	...	NaN	0.0	556.38	100.800055	0.766893	0.0809	25690.968632	2006626.0	78.553863	11690.097020
2	Abu Dhabi	ARE	24.47	54.37	E.Mediterranean	EMR	High	1992	366.0	26.680383	...	NaN	0.0	546.73	100.900656	0.778965	0.3512	25648.272776	2114730.0	78.441374	10562.899438
3	Abu Dhabi	ARE	24.47	54.37	E.Mediterranean	EMR	High	1993	365.0	27.617425	...	NaN	0.0	571.01	100.864959	0.770028	0.5771	25032.782270	2222093.0	78.351924	10572.669831
4	Abu Dhabi	ARE	24.47	54.37	E.Mediterranean	EMR	High	1994	365.0	27.643479	...	NaN	0.0	565.40	100.801123	0.834037	0.0204	25472.639658	2328188.0	78.289134	11178.398481
5 rows × 56 columns