import pytest
from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.models.project import Project
from app.models.site import Site
from app.models.site_scores import SiteScore
from app.services.optimization_engine import optimize_project_deployment

def test_optimization_rules_and_capacity_calculations(db_session: Session):
    # 1. Create User and Project
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    user = User(email="opt_test@example.com", hashed_password="password", is_active=True)
    user.roles.append(planner_role)
    db_session.add(user)
    db_session.commit()

    project = Project(name="Optimization Project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    # 2. Create 3 Sites with different land areas in acres
    site_solar = Site(project_id=project.id, name="Solar Site", geom="SRID=4326;POINT(-115.5 34.5)", land_area=10.0) # 10 acres
    site_wind = Site(project_id=project.id, name="Wind Site", geom="SRID=4326;POINT(-115.6 34.6)", land_area=50.0)   # 50 acres
    site_hybrid = Site(project_id=project.id, name="Hybrid Site", geom="SRID=4326;POINT(-115.7 34.7)", land_area=None) # Null area
    
    db_session.add(site_solar)
    db_session.add(site_wind)
    db_session.add(site_hybrid)
    db_session.commit()

    # 3. Create site scores for Site A (Solar Dominant)
    score_solar = SiteScore(
        site_id=site_solar.id,
        solar_score=85.0,
        wind_score=70.0,  # Diff = 15.0 > 10.0
        overall_deployment_score=77.5,
        suitability_category="Highly Suitable"
    )
    # Site B (Wind Dominant)
    score_wind = SiteScore(
        site_id=site_wind.id,
        solar_score=60.0,
        wind_score=80.0,  # Diff = 20.0 > 10.0
        overall_deployment_score=70.0,
        suitability_category="Highly Suitable"
    )
    # Site C (Hybrid)
    score_hybrid = SiteScore(
        site_id=site_hybrid.id,
        solar_score=80.0,
        wind_score=82.0,  # Diff = 2.0 <= 10.0
        overall_deployment_score=81.0,
        suitability_category="Highly Suitable"
    )
    db_session.add(score_solar)
    db_session.add(score_wind)
    db_session.add(score_hybrid)
    db_session.commit()

    # 4. Run optimization
    res = optimize_project_deployment(project.id, db_session)
    
    recs = res["recommendations"]
    assert len(recs) == 3
    
    # 5. Verify ranking order (descending by overall_deployment_score)
    # Hybrid Site: 81.0 (Priority 1)
    # Solar Site: 77.5 (Priority 2)
    # Wind Site: 70.0 (Priority 3)
    assert recs[0]["site_id"] == site_hybrid.id
    assert recs[0]["expansion_priority"] == 1
    assert recs[1]["site_id"] == site_solar.id
    assert recs[1]["expansion_priority"] == 2
    assert recs[2]["site_id"] == site_wind.id
    assert recs[2]["expansion_priority"] == 3
    
    # 6. Verify technology recommendations
    # Solar Site (site_solar) -> "solar"
    solar_rec = next(r for r in recs if r["site_id"] == site_solar.id)
    assert solar_rec["technology_recommendation"] == "solar"
    
    # Wind Site (site_wind) -> "wind"
    wind_rec = next(r for r in recs if r["site_id"] == site_wind.id)
    assert wind_rec["technology_recommendation"] == "wind"
    
    # Hybrid Site (site_hybrid) -> "hybrid"
    hybrid_rec = next(r for r in recs if r["site_id"] == site_hybrid.id)
    assert hybrid_rec["technology_recommendation"] == "hybrid"
    assert hybrid_rec["co_location_viability"] is True

    # 7. Verify capacity planning calculations
    # Solar capacity: 10.0 acres * 4046.85642 m²/acre * 0.031 kW/m² = 1254.53 kW
    assert solar_rec["recommended_capacity_kw"] == 1254.53
    
    # Wind capacity: 50.0 acres * 4046.85642 m²/acre * 0.005 kW/m² = 1011.71 kW
    assert wind_rec["recommended_capacity_kw"] == 1011.71
    
    # Hybrid capacity: default land fallback 5.0 acres * 4046.85642 m²/acre * 0.036 = 728.43 kW
    assert hybrid_rec["recommended_capacity_kw"] == 728.43

def test_capacity_planning_realistic_range(db_session: Session):
    # Setup site with 5.2 acres (SiteA)
    planner_role = db_session.query(Role).filter(Role.name == "Planner").first()
    user = User(email="range_test@example.com", hashed_password="password", is_active=True)
    user.roles.append(planner_role)
    db_session.add(user)
    db_session.commit()

    project = Project(name="Range Project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    site = Site(project_id=project.id, name="Range Site", geom="SRID=4326;POINT(-115.5 34.5)", land_area=5.2)
    db_session.add(site)
    db_session.commit()

    score = SiteScore(
        site_id=site.id,
        solar_score=88.35,
        wind_score=73.34,
        overall_deployment_score=80.84,
        suitability_category="Highly Suitable"
    )
    db_session.add(score)
    db_session.commit()

    res = optimize_project_deployment(project.id, db_session)
    rec = res["recommendations"][0]
    
    assert rec["technology_recommendation"] == "solar"
    # Expected solar capacity: 5.2 acres * 4046.85642 m²/acre * 0.031 kW/m² = 652.35 kW
    assert rec["recommended_capacity_kw"] == 652.35
    # Verify it is in realistic range: > 10.0 kW
    assert rec["recommended_capacity_kw"] >= 10.0
