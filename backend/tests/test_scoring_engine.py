from app.services.scoring_engine import calculate_weighted_score, map_score_to_category

def test_weighted_score_formula_matches_manual_calculation():
    # Define test inputs
    resource = 80.0
    geographic = 75.0
    infrastructure = 90.0
    environmental = 100.0
    economic = 85.0
    
    # Manual: 80*0.35 + 75*0.25 + 90*0.15 + 100*0.15 + 85*0.10
    # = 28 + 18.75 + 13.5 + 15 + 8.5
    # = 83.75
    expected = 83.75
    
    calculated = calculate_weighted_score(
        resource, geographic, infrastructure, environmental, economic
    )
    
    assert calculated == expected

def test_suitability_category_boundary_mapping():
    # Boundary testing:
    # 85.0 is the boundary for Excellent / Highly Suitable
    assert map_score_to_category(85.0) == "Excellent"
    assert map_score_to_category(85.1) == "Excellent"
    assert map_score_to_category(84.9) == "Highly Suitable"
    
    # 70.0 is the boundary for Highly Suitable / Moderately Suitable
    assert map_score_to_category(70.0) == "Highly Suitable"
    assert map_score_to_category(69.9) == "Moderately Suitable"
    
    # 50.0 is the boundary for Moderately Suitable / Low Suitability
    assert map_score_to_category(50.0) == "Moderately Suitable"
    assert map_score_to_category(49.9) == "Low Suitability"
    
    # 30.0 is the boundary for Low Suitability / Unsuitable
    assert map_score_to_category(30.0) == "Low Suitability"
    assert map_score_to_category(29.9) == "Unsuitable"
    assert map_score_to_category(0.0) == "Unsuitable"
