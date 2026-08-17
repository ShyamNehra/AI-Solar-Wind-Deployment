import pandas as pd

print("\n========== WIND ==========")
print(pd.read_csv("../datasets/global_wind_atlas/Wind_Sites_Dataset_India.csv").head())

print("\n========== SOLAR ==========")
print(pd.read_csv("../datasets/nasa_power/compiled solar irradiance India.csv").head())

print("\n========== SRTM ==========")
print(pd.read_csv("../datasets/srtm/india_cities_dataset_2021_2025.csv").head())

print("\n========== OSM ==========")
print(pd.read_csv("../datasets/openstreetmap/osm.csv").head())