from app.utils.geo_utils import Coordinate, validate_coordinates
from app.utils.raster_processor import RasterProcessor
from app.utils.vector_processor import VectorProcessor

class SpatialAnalysisService:
    """Coordinates and merges spatial rasters and vector grids into a single suitability analysis."""

    def __init__(self):
        # Placeholders pointing to your dataset storage pathways
        self.srtm_processor = RasterProcessor("datasets/srtm/output_SRTMGL1.tif")
        self.wind_processor = RasterProcessor("datasets/global_wind_atlas/IND_wind-speed_100m.tif")
        self.osm_processor = VectorProcessor("datasets/openstreetmap/OpenStreetMap.pbf")

    def analyze_site_suitability(self, latitude: float, longitude: float) -> dict:
        """
        Coordinates the stacking process of solar, wind, terrain, and road distance.
        
        Inputs:
            latitude (float), longitude (float)
            
        Outputs:
            dict: Comprehensive suitability package containing spatial calculations.
        """
        # Task 1: Validate coordinate integrity first
        validate_coordinates(latitude, longitude)
        coord = Coordinate(latitude=latitude, longitude=longitude)

        # Task 2 & 3: Trigger loaders and fetch calculations (Mock placeholders)
        self.srtm_processor.load_raster()
        elevation = self.srtm_processor.sample_value(coord.latitude, coord.longitude)

        self.osm_processor.load_vector_layer("roads")
        road_proximity = self.osm_processor.find_nearest_feature(coord.latitude, coord.longitude)

        # Mock-up logic showing how we will combine these into a unified response
        return {
            "coordinate_context": {"latitude": coord.latitude, "longitude": coord.longitude},
            "spatial_metrics": {
                "elevation_m": elevation,
                "distance_to_road_m": road_proximity["distance_meters"],
                "is_construction_allowed": True
            },
            "suitability_status": "Ready for ML Layer Evaluation"
        }