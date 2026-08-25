from app.services.scoring_engine import map_score_to_category

def test_boundaries():
    test_cases = [84.9, 85.0, 29.9, 30.0]
    print("=== BOUNDARY TESTS ===")
    for score in test_cases:
        category = map_score_to_category(score)
        print(f"Score: {score} -> Category: {category}")

if __name__ == "__main__":
    test_boundaries()
