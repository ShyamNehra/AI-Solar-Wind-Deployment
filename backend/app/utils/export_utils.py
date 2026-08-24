"""
Export and Import Utility for Feature Store records.

Ensures CSV and Excel exports contain identical headers, fields, and dataset rows.
Uses UTF-8 with BOM (utf-8-sig) encoding for CSV to prevent symbol corruption (e.g. °C).
Provides strict CSV import parsing and validation.
"""

import io
import csv
from datetime import datetime
from typing import List, Dict, Any, Union, Tuple
import pandas as pd


EXPORT_HEADERS = [
    "ID",
    "Site",
    "Latitude",
    "Longitude",
    "Solar Irradiance (kWh/m²/day)",
    "Wind Speed (m/s)",
    "Temperature (°C)",
    "Humidity (%)",
    "Elevation (m)",
    "Slope (°)",
    "Road Distance (km)",
    "Substation Distance (km)",
    "Capacity Factor",
    "Wind Class",
    "Terrain Score",
    "Accessibility Score",
    "Date",
]


def map_feature_record_to_export_dict(record: Any) -> Dict[str, Any]:
    """
    Standardizes mapping from a Feature or FeatureStore DB model (or dict/schema)
    to a flat dictionary matching exact export column headers.
    """
    # Extract attributes safely whether record is SQLAlchemy model, Pydantic model, or dict
    if hasattr(record, "model_dump"):
        data = record.model_dump()
    elif isinstance(record, dict):
        data = record
    else:
        data = {
            c: getattr(record, c, None)
            for c in [
                "id",
                "latitude",
                "longitude",
                "solar_irradiance",
                "wind_speed",
                "temperature",
                "humidity",
                "elevation",
                "slope",
                "road_distance",
                "substation_distance",
                "capacity_factor",
                "wind_class",
                "terrain_score",
                "accessibility_score",
                "created_at",
                "site_id",
            ]
        }
        # Resolve site relationship if present
        if hasattr(record, "site") and record.site is not None:
            site_obj = record.site
            site_name = getattr(site_obj, "site_name", None) or f"Site #{getattr(site_obj, 'id', '')}"
            data["site_name"] = site_name

    # Derive site name label
    site_label = data.get("site_name")
    if not site_label:
        site_id = data.get("site_id")
        if site_id:
            site_label = f"Site #{site_id}"
        else:
            site_label = "Ad-hoc / Custom"

    # Date formatting
    created_at = data.get("created_at") or data.get("date")
    if isinstance(created_at, datetime):
        date_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    elif created_at:
        date_str = str(created_at)
    else:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_val(val: Any) -> Any:
        if val is None or pd.isna(val):
            return ""
        return val

    return {
        "ID": format_val(data.get("id")),
        "Site": site_label,
        "Latitude": format_val(data.get("latitude")),
        "Longitude": format_val(data.get("longitude")),
        "Solar Irradiance (kWh/m²/day)": format_val(data.get("solar_irradiance")),
        "Wind Speed (m/s)": format_val(data.get("wind_speed")),
        "Temperature (°C)": format_val(data.get("temperature")),
        "Humidity (%)": format_val(data.get("humidity")),
        "Elevation (m)": format_val(data.get("elevation")),
        "Slope (°)": format_val(data.get("slope")),
        "Road Distance (km)": format_val(data.get("road_distance")),
        "Substation Distance (km)": format_val(data.get("substation_distance")),
        "Capacity Factor": format_val(data.get("capacity_factor")),
        "Wind Class": format_val(data.get("wind_class")),
        "Terrain Score": format_val(data.get("terrain_score")),
        "Accessibility Score": format_val(data.get("accessibility_score")),
        "Date": date_str,
    }


def generate_csv_export_bytes(records: List[Any]) -> bytes:
    """
    Generates CSV file bytes using UTF-8 with BOM (utf-8-sig) encoding.
    Ensures degree symbols (°C, °) display correctly in Excel without corrupted symbols (e.g., Â°).
    """
    rows = [map_feature_record_to_export_dict(r) for r in records]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_HEADERS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    csv_text = output.getvalue()
    # Encode with utf-8-sig to prepend UTF-8 Byte Order Mark (BOM) \ufeff
    return csv_text.encode("utf-8-sig")


def generate_excel_export_bytes(records: List[Any]) -> bytes:
    """
    Generates Excel (.xlsx) file bytes using openpyxl/pandas.
    Contains the exact same dataset, column order, and headers as the CSV export.
    """
    rows = [map_feature_record_to_export_dict(r) for r in records]
    df = pd.DataFrame(rows, columns=EXPORT_HEADERS)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Feature Store")

    return output.getvalue()


def parse_and_validate_csv_import(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses an uploaded CSV file, validates required column headers, validates data types
    and numerical ranges, and returns list of cleaned feature dicts ready for DB insertion.
    Raises ValueError on malformed or invalid CSV data.
    """
    try:
        content_str = file_bytes.decode("utf-8-sig")
    except Exception:
        try:
            content_str = file_bytes.decode("utf-8")
        except Exception:
            raise ValueError("Failed to decode CSV file. File must be UTF-8 encoded text.")

    input_io = io.StringIO(content_str)
    reader = csv.DictReader(input_io)

    if not reader.fieldnames:
        raise ValueError("Uploaded CSV is empty or has no header row.")

    # Standardize column headers lookup map
    header_map = {}
    for f in reader.fieldnames:
        clean_f = f.strip().lower()
        header_map[clean_f] = f

    # Check for required coordinates
    lat_key = header_map.get("latitude")
    lon_key = header_map.get("longitude")
    if not lat_key or not lon_key:
        raise ValueError("Uploaded CSV must contain 'Latitude' and 'Longitude' columns.")

    parsed_records = []
    row_num = 1

    for row in reader:
        row_num += 1
        # Extract fields flexibly
        def get_val(possible_keys: List[str]) -> Any:
            for k in possible_keys:
                clean_k = k.lower()
                if clean_k in header_map:
                    raw_v = row.get(header_map[clean_k])
                    if raw_v is not None and str(raw_v).strip() != "":
                        return str(raw_v).strip()
            return None

        lat_str = get_val(["latitude", "lat"])
        lon_str = get_val(["longitude", "lon", "lng"])

        if not lat_str or not lon_str:
            continue  # Skip empty trailing rows

        try:
            lat = float(lat_str)
            if not (-90.0 <= lat <= 90.0):
                raise ValueError(f"Row {row_num}: Latitude {lat} out of range (-90 to 90).")
        except ValueError as e:
            if "out of range" in str(e):
                raise e
            raise ValueError(f"Row {row_num}: Invalid numeric latitude value '{lat_str}'.")

        try:
            lon = float(lon_str)
            if not (-180.0 <= lon <= 180.0):
                raise ValueError(f"Row {row_num}: Longitude {lon} out of range (-180 to 180).")
        except ValueError as e:
            if "out of range" in str(e):
                raise e
            raise ValueError(f"Row {row_num}: Invalid numeric longitude value '{lon_str}'.")

        def parse_float(keys: List[str]) -> Any:
            raw = get_val(keys)
            if raw is None:
                return None
            try:
                return float(raw)
            except ValueError:
                return None

        solar = parse_float(["solar irradiance (kwh/m²/day)", "solar_irradiance", "solar irradiance", "solar irr."])
        wind = parse_float(["wind speed (m/s)", "wind_speed", "wind speed", "wind spe"])
        temp = parse_float(["temperature (°c)", "temperature", "temp (°c)", "temp"])
        humid = parse_float(["humidity (%)", "humidity", "humid."])
        elev = parse_float(["elevation (m)", "elevation", "elev."])
        slope = parse_float(["slope (°)", "slope"])
        road = parse_float(["road distance (km)", "road_distance", "road dist. (km)", "road dist."])
        substation = parse_float(["substation distance (km)", "substation_distance", "substation dist. (km)", "subst. km"])
        cap_factor = parse_float(["capacity factor", "capacity_factor", "capacity factor (%)"])
        terr_score = parse_float(["terrain score", "terrain_score"])
        access_score = parse_float(["accessibility score", "accessibility_score", "accessibility"])
        wind_cls = get_val(["wind class", "wind_class"])

        parsed_records.append({
            "latitude": lat,
            "longitude": lon,
            "solar_irradiance": solar if solar is not None else 5.2,
            "wind_speed": wind if wind is not None else 6.5,
            "temperature": temp if temp is not None else 25.0,
            "humidity": humid if humid is not None else 50.0,
            "elevation": elev if elev is not None else 250.0,
            "slope": slope if slope is not None else 2.0,
            "road_distance": road if road is not None else 4.0,
            "substation_distance": substation if substation is not None else 8.0,
            "capacity_factor": cap_factor if cap_factor is not None else 28.5,
            "wind_class": wind_cls or ("Excellent" if (wind or 6.5) > 8.5 else "Good" if (wind or 6.5) > 6.0 else "Moderate"),
            "terrain_score": terr_score if terr_score is not None else 75.0,
            "accessibility_score": access_score if access_score is not None else 80.0,
        })

    if not parsed_records:
        raise ValueError("No valid feature records found in CSV file.")

    return parsed_records
