import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def run_tests():
    # 1. Login or Register
    print("=== STEP 1: LOGIN / REGISTER ===")
    login_data = {
        "username": "traced_planner@example.com",
        "password": "Password123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print("Login failed, attempting to register user...")
        register_data = {
            "email": "traced_planner@example.com",
            "password": "Password123!",
            "role_name": "Planner"
        }
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if reg_response.status_code not in (200, 201):
            print(f"Register failed: {reg_response.text}")
            return
        print("User registered. Logging in...")
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"Login failed after registration: {response.text}")
            return
            
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully. Token acquired.")

    # 1b. Create a project dynamically
    print("\n=== STEP 1b: CREATE PROJECT ===")
    project_payload = {
        "name": "DesertSolar",
        "description": "Desert Solar project for testing"
    }
    project_response = requests.post(f"{BASE_URL}/projects", json=project_payload, headers=headers)
    if project_response.status_code not in (200, 201):
        print(f"Failed to create project: {project_response.text}")
        return
    project_id = project_response.json()["id"]
    print(f"Created project with ID: {project_id}")

    # 1c. Create Site A dynamically
    print("\n=== STEP 1c: CREATE SITE A ===")
    site_payload = {
        "name": "SiteA",
        "longitude": -115.0,
        "latitude": 34.0,
        "land_area": 10.0,
        "elevation": 500.0,
        "existing_infrastructure": "Substation within 5km",
        "land_ownership": "Private"
    }
    site_response = requests.post(f"{BASE_URL}/projects/{project_id}/sites", json=site_payload, headers=headers)
    if site_response.status_code not in (200, 201):
        print(f"Failed to create site: {site_response.text}")
        return
    site_a_id = site_response.json()["id"]
    print(f"Created site SiteA with ID: {site_a_id}")

    # 2. Refresh Environmental Data for Site A
    print(f"\n=== STEP 2: REFRESH ENVIRONMENTAL DATA (SITE {site_a_id}) ===")
    response = requests.post(f"{BASE_URL}/sites/{site_a_id}/environmental/refresh", headers=headers)
    if response.status_code != 200:
        print(f"Refresh failed: {response.text}")
        return
    env_data = response.json()
    print("Refresh Response:")
    print(json.dumps(env_data, indent=2))

    # 3. Get predictions
    print(f"\n=== STEP 3: RUN PREDICTIONS (SITE {site_a_id}) ===")
    requests.post(f"{BASE_URL}/sites/{site_a_id}/predictions/solar", headers=headers)
    requests.post(f"{BASE_URL}/sites/{site_a_id}/predictions/wind", headers=headers)
    print(f"Solar and Wind predictions triggered for Site {site_a_id}.")

    # 4. Get Suitability for Site A
    print(f"\n=== STEP 4: GET SUITABILITY BREAKDOWN (SITE {site_a_id}) ===")
    response = requests.post(f"{BASE_URL}/sites/{site_a_id}/suitability", headers=headers)
    if response.status_code != 200:
        print(f"Suitability failed: {response.text}")
        return
    suitability_data = response.json()
    print("Suitability Response:")
    print(json.dumps(suitability_data, indent=2))

    # 5. Get Score for Site A
    print(f"\n=== STEP 5: GET SCORE AND PERSIST (SITE {site_a_id}) ===")
    response = requests.post(f"{BASE_URL}/sites/{site_a_id}/score", headers=headers)
    if response.status_code != 200:
        print(f"Scoring failed: {response.text}")
        return
    score_data = response.json()
    print("Scoring Response:")
    print(json.dumps(score_data, indent=2))

    # 6. Create and test a second Site with different characteristics (for band differentiation)
    print("\n=== STEP 6: CREATE & ASSESSMENT SITE B (FOR BAND DIFFERENTIATION) ===")
    site_b_payload = {
        "name": "Mojave Deep Desert Wind Site",
        "longitude": -116.0,
        "latitude": 35.0,
        "land_area": 5.0,
        "elevation": 800.0,
        "existing_infrastructure": "None",
        "land_ownership": "BLM"
    }
    response = requests.post(f"{BASE_URL}/projects/{project_id}/sites", json=site_b_payload, headers=headers)
    if response.status_code != 201:
        print(f"Failed to create Site B: {response.text}")
        return
    site_b = response.json()
    site_b_id = site_b["id"]
    print(f"Created Site B with ID {site_b_id} at (-116.0, 35.0)")

    # Refresh Site B
    print("Refreshing Site B...")
    response = requests.post(f"{BASE_URL}/sites/{site_b_id}/environmental/refresh", headers=headers)
    if response.status_code != 200:
        print(f"Site B refresh failed: {response.text}")
        return
    
    # Run predictions for Site B
    requests.post(f"{BASE_URL}/sites/{site_b_id}/predictions/solar", headers=headers)
    requests.post(f"{BASE_URL}/sites/{site_b_id}/predictions/wind", headers=headers)

    # Score Site B
    response = requests.post(f"{BASE_URL}/sites/{site_b_id}/score", headers=headers)
    if response.status_code != 200:
        print(f"Site B scoring failed: {response.text}")
        return
    score_b_data = response.json()
    print("Site B Scoring Response:")
    print(json.dumps(score_b_data, indent=2))

if __name__ == "__main__":
    run_tests()
