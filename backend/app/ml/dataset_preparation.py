from pathlib import Path
import pandas as pd
import numpy as np


class DatasetPreparation:
    """
    Prepare the ML training dataset by integrating
    Wind, Solar, SRTM and OSM datasets.
    """

    def __init__(self):

        project_root = Path(__file__).resolve().parents[2]

        self.wind_file = (
            project_root /
            "datasets/global_wind_atlas/Wind_Sites_Dataset_India.csv"
        )

        self.solar_file = (
            project_root /
            "datasets/nasa_power/compiled solar irradiance India.csv"
        )

        self.srtm_file = (
            project_root /
            "datasets/srtm/india_cities_dataset_2021_2025.csv"
        )

        self.osm_file = (
            project_root /
            "datasets/openstreetmap/osm.csv"
        )

        self.output_file = (
            Path(__file__).parent /
            "training_data.csv"
        )

    def prepare_training_dataset(self):

        np.random.seed(42)

        # -------------------------
        # Load datasets
        # -------------------------

        wind = pd.read_csv(self.wind_file)

        solar = pd.read_csv(self.solar_file)

        srtm = pd.read_csv(self.srtm_file)

        osm = pd.read_csv(self.osm_file)

        # -------------------------
        # Randomly assign values
        # -------------------------

        wind["AnnualSolarIrradiance"] = np.random.choice(
            solar["Annual"].dropna(),
            len(wind)
        )

        wind["AverageNDVI"] = np.random.choice(
            srtm["NDVI"].dropna(),
            len(wind)
        )

        wind["AverageNDBI"] = np.random.choice(
            srtm["NDBI"].dropna(),
            len(wind)
        )

        wind["AverageNDWI"] = np.random.choice(
            srtm["NDWI"].dropna(),
            len(wind)
        )

        wind["AverageLST"] = np.random.choice(
            srtm["LST (°C)"].dropna(),
            len(wind)
        )

        wind["AverageCityElevation"] = np.random.choice(
            srtm["Elevation (m)"].dropna(),
            len(wind)
        )

        wind["AverageDistrictPopulation"] = np.random.choice(
            osm["totalpopul,N,8,0"].dropna(),
            len(wind)
        )

        wind["AverageDistrictArea"] = np.random.choice(
            osm["distarea,N,5,0"].dropna(),
            len(wind)
        )

        # -------------------------
        # Select features
        # -------------------------

        training_data = wind[
            [
                "Slope",
                "Elevation",
                "TurbulenceIntensity",
                "Yearly-AirTemperature",
                "Yearly-RelativeHumidity",
                "Yearly-Precipitation",
                "Yearly-WindSpeed",
                "Yearly-WindGustSpeed",
                "Yearly-AirPressure",
                "AnnualSolarIrradiance",
                "AverageNDVI",
                "AverageNDBI",
                "AverageNDWI",
                "AverageLST",
                "AverageCityElevation",
                "AverageDistrictPopulation",
                "AverageDistrictArea"
            ]
        ].copy()

        # -------------------------
        # Fill missing values
        # -------------------------

        training_data = training_data.fillna(
            training_data.median(numeric_only=True)
        )

        # -------------------------
        # Create Label
        # -------------------------

        def generate_label(row):

            score = 0

            if row["Slope"] < 15:
                score += 1

            if row["Yearly-WindSpeed"] >= 6:
                score += 1

            if row["AnnualSolarIrradiance"] >= 5:
                score += 1

            if row["Elevation"] < 2000:
                score += 1

            if row["AverageNDVI"] > 0.30:
                score += 1

            return "Yes" if score >= 3 else "No"

        training_data["Label"] = training_data.apply(
            generate_label,
            axis=1
        )

        # -------------------------
        # Save dataset
        # -------------------------

        training_data.to_csv(
            self.output_file,
            index=False
        )

        print("\nTraining dataset created successfully.\n")

        print(training_data.head())

        print("\nSaved to:")

        print(self.output_file)

        return training_data


if __name__ == "__main__":

    DatasetPreparation().prepare_training_dataset()