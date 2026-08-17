import pandas as pd


class TimeSeriesDataLoader:
    """
    Loads historical renewable energy data
    for forecasting.
    """

    def load_data(self, file_path: str):
        """
        Load historical data from a CSV file.

        Parameters:
            file_path (str)

        Returns:
            pandas.DataFrame
        """

        data = pd.read_csv(file_path)

        return data

    def sort_by_date(self, data):
        """
        Preserve chronological ordering.
        """

        data["date"] = pd.to_datetime(data["date"])

        data = data.sort_values(by="date")

        data = data.reset_index(drop=True)

        return data

    def prepare_data(self, file_path: str):
        """
        Load and prepare historical data
        for forecasting.
        """

        data = self.load_data(file_path)

        data = self.sort_by_date(data)

        return data