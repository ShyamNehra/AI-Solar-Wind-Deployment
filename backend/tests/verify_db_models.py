import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup Python Path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

# Use an in-memory SQLite engine for fast schema validation
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database.database import Base
from app.models import (
    User, Project, Site, FeatureRecord,
    EnvironmentalData, SolarPrediction, WindPrediction,
    SuitabilityScore, Report
)
from app.services.persistence_service import PersistenceService


def verify_database_schema():
    print("==================================================================")
    print("     VERIFYING 8-TABLE DATABASE SCHEMA & ORM PERSISTENCE        ")
    print("==================================================================")

    # 1. Create all tables in-memory
    Base.metadata.create_all(bind=engine)
    print("\n[SUCCESS] Base.metadata.create_all() executed cleanly!")

    # Verify Table Names registered in SQLAlchemy metadata
    table_names = sorted(list(Base.metadata.tables.keys()))
    print(f"Registered Table Count: {len(table_names)}")
    print(f"Registered Tables     : {', '.join(table_names)}")

    db = TestingSessionLocal()
    try:
        # 2. Test User Creation
        user = User(
            email="planner@renewable.ai",
            username="solar_planner",
            hashed_password="hashed_secret_pass",
            full_name="Alex Mercer",
            role="renewable_energy_planner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"\n[1/8] Created User            : ID={user.id} | Email={user.email} | Role={user.role}")

        # 3. Test Project Creation
        project = Project(
            project_name="Bhadla Solar & Wind Park Phase 1",
            description="Utility scale hybrid renewable plant",
            state="Rajasthan",
            region="Jodhpur Division",
            created_by=user.id,
            project_type="hybrid",
            status="active"
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"[2/8] Created Project         : ID={project.id} | Name={project.project_name} | Type={project.project_type}")

        # 4. Test Site Creation
        site = Site(
            project_id=project.id,
            latitude=27.5397,
            longitude=71.9152,
            region="Bhadla Sector 4",
            area_sq_meters=500000.0,
            elevation_m=169.0,
            land_ownership="Government Leasehold",
            existing_infrastructure="Near 400kV Substation & Grid Line"
        )
        db.add(site)
        db.commit()
        db.refresh(site)
        print(f"[3/8] Created Site            : ID={site.id} | Coords=({site.latitude}, {site.longitude}) | Area={site.area_sq_meters}m²")

        # 5. Test EnvironmentalData via PersistenceService
        env_record = PersistenceService.save_environmental_data(
            db=db,
            site_id=site.id,
            env_features={"solar_irradiance": 6.2, "wind_speed": 4.8, "temperature": 32.0, "rainfall": 12.5, "cloud_cover": 15.0, "slope": 2.1, "land_use_type": "barren_desert"},
            data_source="NASA_POWER"
        )
        print(f"[4/8] Saved EnvironmentalData : ID={env_record.id} | GHI={env_record.solar_irradiance} kWh/m² | Wind={env_record.wind_speed} m/s")

        # 6. Test SolarPrediction via PersistenceService
        solar_rec = PersistenceService.save_solar_prediction(
            db=db,
            site_id=site.id,
            solar_metrics={"annual_irradiance": 2150.0, "peak_sun_hours": 5.8, "expected_energy_output_kwh": 8500000.0, "capacity_factor": 0.24, "performance_ratio": 0.82}
        )
        print(f"[5/8] Saved SolarPrediction   : ID={solar_rec.id} | Expected Energy={solar_rec.expected_energy_output_kwh} kWh | CF={solar_rec.capacity_factor}")

        # 7. Test WindPrediction via PersistenceService
        wind_rec = PersistenceService.save_wind_prediction(
            db=db,
            site_id=site.id,
            wind_metrics={"average_wind_speed": 6.4, "wind_power_density": 280.0, "turbulence_intensity": 0.11, "capacity_factor": 0.31, "expected_annual_energy_kwh": 11000000.0}
        )
        print(f"[6/8] Saved WindPrediction    : ID={wind_rec.id} | Average Speed={wind_rec.average_wind_speed} m/s | WPD={wind_rec.wind_power_density} W/m²")

        # 8. Test SuitabilityScore via PersistenceService
        score_rec = PersistenceService.save_suitability_score(
            db=db,
            site_id=site.id,
            suitability_result={
                "overall_score": 87.5,
                "category": "Excellent",
                "sub_scores": {
                    "resource_score": 92.0,
                    "geographic_score": 85.0,
                    "infrastructure_score": 88.0,
                    "environmental_score": 84.0,
                    "economic_score": 89.0
                }
            }
        )
        print(f"[7/8] Saved SuitabilityScore  : ID={score_rec.id} | Category={score_rec.suitability_category} | Score={score_rec.overall_score}/100")

        # 9. Test Report Metadata via PersistenceService
        report_rec = PersistenceService.save_report_metadata(
            db=db,
            project_id=project.id,
            site_id=site.id,
            report_type="feasibility",
            file_format="PDF",
            file_path="/reports/feasibility_bhadla_p1.pdf",
            generated_by=user.id
        )
        print(f"[8/8] Saved Report Metadata   : ID={report_rec.id} | Type={report_rec.report_type} | Format={report_rec.file_format} | Path={report_rec.file_path}")

        print("\n==================================================================")
        print("  [SUCCESS] All 8 DB Tables Verified & Persistence Functional!  ")
        print("==================================================================")

    except Exception as e:
        print(f"\n[ERROR] Schema verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    verify_database_schema()
