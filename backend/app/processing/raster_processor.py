from typing import Any


class RasterProcessor:
    """
    Skeleton class for raster data processing.

    This class defines the interface for working with raster datasets
    such as elevation maps, solar irradiance rasters, and land cover maps.

    Note:
    Actual raster processing will be implemented in a future module.
    """

    def load_raster(self, file_path: str) -> None:
        """
        Load a raster dataset.

        Parameters:
            file_path (str):
                Path to the raster (.tif) file.

        Raises:
            FileNotFoundError:
                If the raster file does not exist.
        """
        raise NotImplementedError("Raster loading will be implemented later.")


    def sample_value(self, latitude: float, longitude: float) -> float:
        """
        Sample a raster value at a given geographic coordinate.

        Parameters:
            latitude (float):
                Latitude of the location.

            longitude (float):
                Longitude of the location.

        Returns:
            float:
                Raster value at the specified location.

        Raises:
            ValueError:
                If coordinates are invalid.
        """
        raise NotImplementedError("Raster sampling will be implemented later.")


    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing the raster.

        Example metadata:
            - CRS
            - Resolution
            - Width
            - Height
            - Number of bands

        Returns:
            dict
        """
        raise NotImplementedError("Metadata retrieval will be implemented later.")