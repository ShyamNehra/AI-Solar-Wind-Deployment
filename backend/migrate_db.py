from sqlalchemy import text
from app.database.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.site import Site
from app.models.feature import Feature
from app.models.report import Report
from app.models.assessment import Assessment
from app.models.environmental_data import EnvironmentalData
from app.models.solar_prediction import SolarPrediction
from app.models.wind_prediction import WindPrediction
from app.models.feature_store import FeatureStore
from app.auth.auth_handler import get_password_hash
from app.feature_engineering.feature_builder import FeatureBuilder
import json

def migrate():
    with engine.connect() as conn:
        print("Ensuring users table columns are up to date...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);"))
            conn.commit()
            print("Successfully checked users table.")
        except Exception as e:
            print(f"Users table migration failed: {e}")

        print("Dropping old tables to fix schema alignment (projects, sites, features, reports, assessments, feature_store)...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS assessments CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS feature_store CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS environmental_data CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS solar_predictions CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS wind_predictions CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS reports CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS features CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS sites CASCADE;"))
            conn.execute(text("DROP TABLE IF EXISTS projects CASCADE;"))
            conn.commit()
            print("Successfully dropped mismatched tables.")
        except Exception as e:
            print(f"Drop tables failed: {e}")

    print("Generating all database schemas...")
    Base.metadata.create_all(bind=engine)
    print("Database schemas created.")

    # Seeding sample data
    db = SessionLocal()
    try:
        # 1. Seed default user if not exists
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Seeding default Administrator user...")
            user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="Administrator",
                email="admin@renewable-intelligence.com",
                full_name="Admin Director"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        planner = db.query(User).filter(User.username == "planner").first()
        if not planner:
            print("Seeding default Renewable Energy Planner user...")
            planner = User(
                username="planner",
                hashed_password=get_password_hash("planner123"),
                role="Renewable Energy Planner",
                email="planner@renewable-intelligence.com",
                full_name="Lead Planner"
            )
            db.add(planner)
            db.commit()
            db.refresh(planner)

        # 2. Seed default project
        project = db.query(Project).first()
        if not project:
            print("Seeding default projects...")
            project1 = Project(
                project_name="Rajasthan Solar Farm Phase 1",
                region="Jaipur, Rajasthan",
                description="Large scale grid-connected utility PV installation study.",
                status="Active",
                user_id=user.id
            )
            project2 = Project(
                project_name="Tamil Nadu Wind Corridor",
                region="Kanyakumari, Tamil Nadu",
                description="Onshore wind resource assessment and micro-siting study.",
                status="Active",
                user_id=user.id
            )
            db.add(project1)
            db.add(project2)
            db.commit()
            db.refresh(project1)
            project = project1

        # 3. Seed default site
        site = db.query(Site).first()
        if not site:
            print("Seeding default sites...")
            site1 = Site(
                latitude=26.9124,
                longitude=75.7873,
                elevation=431.0,
                land_area=150.0,
                region="Jaipur, Rajasthan",
                infrastructure="Near NH-48 highway, grid connection feasible within 12km",
                ownership="Government",
                project_id=project.id
            )
            site2 = Site(
                latitude=8.0883,
                longitude=77.5385,
                elevation=10.0,
                land_area=80.0,
                region="Kanyakumari, Tamil Nadu",
                infrastructure="Coastal access road, transmission lines 5km away",
                ownership="Private",
                project_id=project2.id
            )
            db.add(site1)
            db.add(site2)
            db.commit()
            db.refresh(site1)
            site = site1

        # 4. Seed feature for both sites
        feat = db.query(Feature).first()
        if not feat:
            print("Seeding default features for site1 and site2...")
            builder = FeatureBuilder()
            
            # Site 1 (Rajasthan)
            feats1 = builder.build_features(site1.latitude, site1.longitude)
            feature_record1 = Feature(
                latitude=site1.latitude,
                longitude=site1.longitude,
                solar_irradiance=feats1.get("solar_irradiance") or 4.92,
                wind_speed=feats1.get("wind_speed") or 5.38,
                temperature=feats1.get("temperature") or 26.5,
                humidity=feats1.get("humidity") or 62.0,
                elevation=site1.elevation,
                slope=feats1.get("slope") or 1.5,
                road_distance=feats1.get("road_distance") or 2.1,
                substation_distance=feats1.get("substation_distance") or 8.4,
                capacity_factor=feats1.get("capacity_factor") or 18.5,
                wind_class=feats1.get("wind_class") or "Moderate",
                terrain_score=feats1.get("terrain_score") or 82.0,
                accessibility_score=feats1.get("accessibility_score") or 78.0,
                site_id=site1.id
            )
            fs_record1 = FeatureStore(
                latitude=site1.latitude,
                longitude=site1.longitude,
                solar_irradiance=feats1.get("solar_irradiance") or 4.92,
                wind_speed=feats1.get("wind_speed") or 5.38,
                elevation=site1.elevation,
                temperature=feats1.get("temperature") or 26.5,
                humidity=feats1.get("humidity") or 62.0,
                slope=feats1.get("slope") or 1.5,
                road_distance=feats1.get("road_distance") or 2.1,
                substation_distance=feats1.get("substation_distance") or 8.4,
                suitability_score=68.0,
                site_id=site1.id
            )

            # Site 2 (Tamil Nadu)
            feats2 = builder.build_features(site2.latitude, site2.longitude)
            feature_record2 = Feature(
                latitude=site2.latitude,
                longitude=site2.longitude,
                solar_irradiance=feats2.get("solar_irradiance") or 5.04,
                wind_speed=feats2.get("wind_speed") or 5.56,
                temperature=feats2.get("temperature") or 28.0,
                humidity=feats2.get("humidity") or 72.0,
                elevation=site2.elevation,
                slope=feats2.get("slope") or 0.8,
                road_distance=feats2.get("road_distance") or 1.2,
                substation_distance=feats2.get("substation_distance") or 5.0,
                capacity_factor=feats2.get("capacity_factor") or 22.4,
                wind_class=feats2.get("wind_class") or "High",
                terrain_score=feats2.get("terrain_score") or 88.0,
                accessibility_score=feats2.get("accessibility_score") or 85.0,
                site_id=site2.id
            )
            fs_record2 = FeatureStore(
                latitude=site2.latitude,
                longitude=site2.longitude,
                solar_irradiance=feats2.get("solar_irradiance") or 5.04,
                wind_speed=feats2.get("wind_speed") or 5.56,
                elevation=site2.elevation,
                temperature=feats2.get("temperature") or 28.0,
                humidity=feats2.get("humidity") or 72.0,
                slope=feats2.get("slope") or 0.8,
                road_distance=feats2.get("road_distance") or 1.2,
                substation_distance=feats2.get("substation_distance") or 5.0,
                suitability_score=71.0,
                site_id=site2.id
            )

            db.add(feature_record1)
            db.add(fs_record1)
            db.add(feature_record2)
            db.add(fs_record2)
            db.commit()

            # Seed full pipeline Assessment and Report records
            from app.services.workflow_pipeline_service import WorkflowPipelineService
            from app.models.assessment import Assessment
            from app.models.report import Report
            import json

            pipeline_svc = WorkflowPipelineService()
            pipeline_res1 = pipeline_svc.run_pipeline(site1.latitude, site1.longitude, site_id=site1.id)
            pipeline_res2 = pipeline_svc.run_pipeline(site2.latitude, site2.longitude, site_id=site2.id)

            ass1 = Assessment(
                latitude=site1.latitude,
                longitude=site1.longitude,
                overall_score=68.0,
                category="Highly Suitable",
                deployment_recommendation="Solar Priority Hybrid",
                confidence=85.0,
                reason="Optimal solar GHI irradiance and favorable flat topography",
                result_json=json.dumps(pipeline_res1),
                site_id=site1.id,
                user_id=1
            )
            ass2 = Assessment(
                latitude=site2.latitude,
                longitude=site2.longitude,
                overall_score=71.0,
                category="Highly Suitable",
                deployment_recommendation="Wind Priority Hybrid",
                confidence=88.0,
                reason="Excellent coastal wind resources and high capacity factor",
                result_json=json.dumps(pipeline_res2),
                site_id=site2.id,
                user_id=1
            )

            rep1 = Report(
                title="Rajasthan Solar Farm Assessment & Investment Report",
                report_type="Assessment",
                site_id=site1.id,
                summary=json.dumps(pipeline_res1),
                user_id=1
            )
            rep2 = Report(
                title="Tamil Nadu Wind Corridor Feasibility Report",
                report_type="Feasibility",
                site_id=site2.id,
                summary=json.dumps(pipeline_res2),
                user_id=1
            )

            db.add(ass1)
            db.add(ass2)
            db.add(rep1)
            db.add(rep2)
            db.commit()

        print("Seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
