from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.environmental_data import EnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.suitability_score import SuitabilityScore
from app.models.report import Report


class PersistenceService:
    """
    Helper service to auto-persist analysis, prediction, scoring, and report execution
    records to the database without breaking real-time response flows.
    """

    @staticmethod
    def save_environmental_data(db: Session, site_id: int, env_features: Dict[str, Any], data_source: str = "NASA_POWER") -> EnvironmentalData:
        record = EnvironmentalData(
            site_id=site_id,
            data_source=data_source,
            solar_irradiance=float(env_features.get("solar_irradiance", env_features.get("env_solar_irradiance", 0.0))),
            wind_speed=float(env_features.get("wind_speed", env_features.get("env_wind_speed", 0.0))),
            temperature=float(env_features.get("temperature", env_features.get("env_temperature", 25.0))),
            rainfall=float(env_features.get("rainfall", env_features.get("env_rainfall", 0.0))),
            cloud_cover=float(env_features.get("cloud_cover", env_features.get("env_cloud_cover", 0.0))),
            slope_percent=float(env_features.get("slope", env_features.get("env_slope", 0.0))),
            land_cover_type=str(env_features.get("land_use_type", env_features.get("land_cover", "clear")))
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def save_solar_prediction(db: Session, site_id: int, solar_metrics: Dict[str, Any], model_version: str = "XGBoost-RF-Ensemble-v1") -> SolarPrediction:
        record = SolarPrediction(
            site_id=site_id,
            annual_irradiance=float(solar_metrics.get("annual_irradiance", 0.0)),
            peak_sun_hours=float(solar_metrics.get("peak_sun_hours", 0.0)),
            expected_energy_output_kwh=float(solar_metrics.get("expected_energy_output_kwh", 0.0)),
            capacity_factor=float(solar_metrics.get("capacity_factor", 0.0)),
            performance_ratio=float(solar_metrics.get("performance_ratio", 0.0)),
            model_version=model_version
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def save_wind_prediction(db: Session, site_id: int, wind_metrics: Dict[str, Any], model_version: str = "XGBoost-RF-Ensemble-v1") -> WindPrediction:
        record = WindPrediction(
            site_id=site_id,
            average_wind_speed=float(wind_metrics.get("average_wind_speed", 0.0)),
            wind_power_density=float(wind_metrics.get("wind_power_density", 0.0)),
            turbulence_intensity=float(wind_metrics.get("turbulence_intensity", 0.0)),
            capacity_factor=float(wind_metrics.get("capacity_factor", 0.0)),
            expected_annual_energy_kwh=float(wind_metrics.get("expected_annual_energy_kwh", 0.0)),
            model_version=model_version
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def save_suitability_score(db: Session, site_id: int, suitability_result: Dict[str, Any]) -> SuitabilityScore:
        sub_scores = suitability_result.get("sub_scores", {})
        record = SuitabilityScore(
            site_id=site_id,
            resource_score=float(sub_scores.get("resource_score", sub_scores.get("renewable_resource_availability", 0.0))),
            geographic_score=float(sub_scores.get("geographic_score", sub_scores.get("geographic_suitability", 0.0))),
            infrastructure_score=float(sub_scores.get("infrastructure_score", sub_scores.get("infrastructure_accessibility", 0.0))),
            environmental_score=float(sub_scores.get("environmental_score", sub_scores.get("environmental_impact", 0.0))),
            economic_score=float(sub_scores.get("economic_score", sub_scores.get("economic_feasibility", 0.0))),
            overall_score=float(suitability_result.get("overall_score", 0.0)),
            suitability_category=str(suitability_result.get("category", suitability_result.get("suitability_category", "Moderately Suitable")))
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def save_report_metadata(
        db: Session, 
        project_id: int, 
        report_type: str, 
        file_format: str, 
        file_path: str, 
        site_id: Optional[int] = None, 
        generated_by: Optional[int] = None
    ) -> Report:
        record = Report(
            project_id=project_id,
            site_id=site_id,
            report_type=report_type,
            file_format=file_format,
            file_path=file_path,
            generated_by=generated_by
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
