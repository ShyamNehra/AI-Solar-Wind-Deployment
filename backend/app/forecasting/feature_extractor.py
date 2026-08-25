class TimeFeatureExtractor:
    """
    Extract useful time-based features
    from a date column.
    """

    def extract_features(self, data):
        """
        Add time-based features to the dataset.

        Parameters:
            data (pandas.DataFrame)

        Returns:
            pandas.DataFrame
        """

        data["date"] = data["date"].astype("datetime64[ns]")

        data["year"] = data["date"].dt.year

        data["month"] = data["date"].dt.month

        data["day"] = data["date"].dt.day

        data["day_of_year"] = data["date"].dt.dayofyear

        data["week_number"] = data["date"].dt.isocalendar().week.astype(int)

        return data