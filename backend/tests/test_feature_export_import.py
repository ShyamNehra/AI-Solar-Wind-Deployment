"""
Unit and Integration Tests for Feature Store CSV and Excel Export/Import Functionality.

Verifies:
1. CSV and Excel exports produce identical datasets, row counts, column counts, and column header names.
2. CSV export uses UTF-8 BOM encoding (\ufeff) to render degree symbols (°C, °) correctly.
3. CSV import parses valid records and rejects malformed CSV files with HTTP 400.
"""

import io
import csv
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.models.feature_store import FeatureStore
from app.models.feature import Feature
from app.utils.export_utils import (
    EXPORT_HEADERS,
    generate_csv_export_bytes,
    generate_excel_export_bytes,
    parse_and_validate_csv_import,
    map_feature_record_to_export_dict
)

client = TestClient(app)


@pytest.fixture
def auth_headers():
    username = "export_test_user_unique_1"
    password = "password123"
    client.post("/auth/register", json={"username": username, "password": password, "role": "Renewable Energy Planner"})
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json().get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_feature_records():
    return [
        {
            "id": 101,
            "site_id": 1,
            "site_name": "Kanyakumari Solar Farm",
            "latitude": 8.0883,
            "longitude": 77.5385,
            "solar_irradiance": 6.45,
            "wind_speed": 8.2,
            "temperature": 28.5,
            "humidity": 65.0,
            "elevation": 45.0,
            "slope": 2.1,
            "road_distance": 1.5,
            "substation_distance": 4.2,
            "capacity_factor": 32.5,
            "wind_class": "Excellent",
            "terrain_score": 88.0,
            "accessibility_score": 92.0,
            "created_at": "2026-07-31 12:00:00"
        },
        {
            "id": 102,
            "site_id": 2,
            "site_name": "Jaisalmer Wind Park",
            "latitude": 26.9157,
            "longitude": 70.9083,
            "solar_irradiance": 6.9,
            "wind_speed": 7.8,
            "temperature": 34.0,
            "humidity": 30.0,
            "elevation": 225.0,
            "slope": 1.5,
            "road_distance": 3.8,
            "substation_distance": 12.0,
            "capacity_factor": 38.0,
            "wind_class": "Excellent",
            "terrain_score": 90.0,
            "accessibility_score": 85.0,
            "created_at": "2026-07-31 12:30:00"
        }
    ]


def test_export_dict_mapping_parity(sample_feature_records):
    """
    Verifies that map_feature_record_to_export_dict yields exact 17 export headers.
    """
    rec = sample_feature_records[0]
    mapped = map_feature_record_to_export_dict(rec)

    assert list(mapped.keys()) == EXPORT_HEADERS
    assert mapped["ID"] == 101
    assert mapped["Site"] == "Kanyakumari Solar Farm"
    assert mapped["Latitude"] == 8.0883
    assert mapped["Longitude"] == 77.5385
    assert mapped["Solar Irradiance (kWh/m²/day)"] == 6.45
    assert mapped["Wind Speed (m/s)"] == 8.2
    assert mapped["Temperature (°C)"] == 28.5
    assert mapped["Slope (°)"] == 2.1
    assert mapped["Wind Class"] == "Excellent"


def test_csv_and_excel_export_dataset_parity(sample_feature_records):
    """
    Verifies CSV and Excel exports contain identical row counts, column counts,
    column headers, and exact cell values.
    """
    csv_bytes = generate_csv_export_bytes(sample_feature_records)
    excel_bytes = generate_excel_export_bytes(sample_feature_records)

    # Decode CSV (using utf-8-sig to strip BOM)
    csv_str = csv_bytes.decode("utf-8-sig")
    csv_df = pd.read_csv(io.StringIO(csv_str))

    # Read Excel
    excel_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name="Feature Store")

    # 1. Identical column headers
    assert list(csv_df.columns) == EXPORT_HEADERS
    assert list(excel_df.columns) == EXPORT_HEADERS

    # 2. Identical dimensions
    assert csv_df.shape == excel_df.shape == (2, 17)

    # 3. Identical key values
    assert list(csv_df["ID"]) == list(excel_df["ID"]) == [101, 102]
    assert list(csv_df["Site"]) == list(excel_df["Site"]) == ["Kanyakumari Solar Farm", "Jaisalmer Wind Park"]
    assert list(csv_df["Solar Irradiance (kWh/m²/day)"]) == list(excel_df["Solar Irradiance (kWh/m²/day)"]) == [6.45, 6.9]
    assert list(csv_df["Wind Speed (m/s)"]) == list(excel_df["Wind Speed (m/s)"]) == [8.2, 7.8]
    assert list(csv_df["Temperature (°C)"]) == list(excel_df["Temperature (°C)"]) == [28.5, 34.0]
    assert list(csv_df["Slope (°)"]) == list(excel_df["Slope (°)"]) == [2.1, 1.5]


def test_csv_utf8_bom_encoding(sample_feature_records):
    """
    Verifies CSV export begins with UTF-8 Byte Order Mark (\ufeff / 0xEF 0xBB 0xBF)
    so Excel renders degree symbols (°C, °) correctly without corruption like Â°.
    """
    csv_bytes = generate_csv_export_bytes(sample_feature_records)

    # Check UTF-8 BOM bytes 0xEF, 0xBB, 0xBF
    assert csv_bytes[:3] == b"\xef\xbb\xbf"

    csv_text = csv_bytes.decode("utf-8-sig")
    assert "Temperature (°C)" in csv_text
    assert "Slope (°)" in csv_text
    assert "Â°" not in csv_text  # Guarantees no corrupted symbol output


def test_csv_import_parsing_valid():
    """
    Verifies parse_and_validate_csv_import correctly parses valid CSV content.
    """
    valid_csv = (
        "Latitude,Longitude,Solar Irradiance (kWh/m²/day),Wind Speed (m/s),Temperature (°C),Humidity (%),Elevation (m),Slope (°)\n"
        "12.9716,77.5946,5.8,7.2,26.0,55,100,2.5\n"
        "13.0827,80.2707,6.1,6.8,29.0,70,10,1.0\n"
    ).encode("utf-8-sig")

    parsed = parse_and_validate_csv_import(valid_csv)
    assert len(parsed) == 2
    assert parsed[0]["latitude"] == 12.9716
    assert parsed[0]["longitude"] == 77.5946
    assert parsed[0]["solar_irradiance"] == 5.8
    assert parsed[0]["wind_speed"] == 7.2
    assert parsed[1]["latitude"] == 13.0827


def test_csv_import_parsing_invalid():
    """
    Verifies parse_and_validate_csv_import rejects invalid/malformed CSVs with ValueError.
    """
    # 1. Missing required columns (no latitude/longitude)
    invalid_cols_csv = "Solar Irradiance,Wind Speed\n5.5,6.2\n".encode("utf-8")
    with pytest.raises(ValueError) as exc1:
        parse_and_validate_csv_import(invalid_cols_csv)
    assert "must contain 'Latitude' and 'Longitude'" in str(exc1.value)

    # 2. Out-of-bounds latitude
    invalid_range_csv = "Latitude,Longitude\n150.0,77.5\n".encode("utf-8")
    with pytest.raises(ValueError) as exc2:
        parse_and_validate_csv_import(invalid_range_csv)
    assert "Latitude 150.0 out of range" in str(exc2.value)


def test_fastapi_export_and_import_endpoints(auth_headers):
    """
    Integration tests for FastAPI GET /features/export/csv, GET /features/export/excel,
    and POST /features/import/csv endpoints.
    """
    # 1. Test CSV export endpoint
    csv_resp = client.get("/features/export/csv", headers=auth_headers)
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    assert csv_resp.content[:3] == b"\xef\xbb\xbf"  # UTF-8 BOM present

    # 2. Test Excel export endpoint
    excel_resp = client.get("/features/export/excel", headers=auth_headers)
    assert excel_resp.status_code == 200
    assert "spreadsheetml" in excel_resp.headers["content-type"]

    # 3. Test CSV import endpoint with valid file
    import_csv_data = (
        "Latitude,Longitude,Solar Irradiance (kWh/m²/day),Wind Speed (m/s)\n"
        "28.6139,77.2090,5.6,6.4\n"
    ).encode("utf-8-sig")

    files = {"file": ("test_import.csv", import_csv_data, "text/csv")}
    import_resp = client.post("/features/import/csv", files=files, headers=auth_headers)
    assert import_resp.status_code == 201
    assert import_resp.json()["status"] == "Success"
    assert import_resp.json()["count"] == 1
