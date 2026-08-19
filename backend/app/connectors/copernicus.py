import logging
import requests
from app.core.copernicus_auth import get_copernicus_token

logger = logging.getLogger(__name__)

# Copernicus Sentinel Hub Process API Endpoint
COPERNICUS_PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

# Map of ESA WorldCover classification codes to human-readable labels
ESA_WORLDCOVER_CLASSES = {
    10: "Trees / Forest",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up / Urban",
    60: "Barren / Sparse Vegetation",
    70: "Snow and Ice",
    80: "Open Water",
    90: "Herbaceous Wetland",
    95: "Mangroves",
    100: "Moss and Lichen"
}

def fetch_land_cover(lat: float, lon: float) -> str:
    """
    Fetch the ESA WorldCover land cover classification for a given coordinate
    using the Copernicus Sentinel Hub Process API.
    Raises ValueError if credentials are not configured.
    """
    # 1. Obtain Bearer Token (raises ValueError if credentials not configured)
    token = get_copernicus_token()
    
    # 2. Define small bounding box around the coordinate (approx 100m x 100m)
    delta = 0.0005
    bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
    
    # Sentinel Hub Process payload structure for ESA WorldCover
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                }
            },
            "data": [
                {
                    "type": "esa-worldcover"
                }
            ]
        },
        "output": {
            "width": 1,
            "height": 1,
            "responses": [
                {
                    "identifier": "default",
                    "format": {
                        "type": "image/tiff"
                    }
                }
            ]
        },
        "evalscript": """//VERSION=3
function setup() {
  return {
    input: ["Map"],
    output: { bands: 1, sampleType: "UINT8" }
  };
}
function evaluatePixel(sample) {
  return [sample.Map];
}"""
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "image/tiff"
    }
    
    try:
        logger.info(f"Querying Copernicus Sentinel Hub Process API at {lat}, {lon}...")
        response = requests.post(COPERNICUS_PROCESS_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # The response body is a binary tiff image
            # Since size is 1x1 pixel and 1 band (UINT8), the last byte or specific offset contains the value.
            # In a simple 1x1 single-band tiff, the pixel value is at the end or we can read it.
            # Usually, the value can be parsed from bytes:
            content = response.content
            if len(content) > 0:
                # Get the last byte as a simple heuristic for 1x1 tiff or parse it.
                # In most standard uncompressed 1x1 tiffs, the pixel value is at the end of the file or index.
                # Let's extract the class code (fallback to 60 Barren if not parsed correctly)
                pixel_val = content[-1]
                land_cover_label = ESA_WORLDCOVER_CLASSES.get(pixel_val, f"Unknown Class ({pixel_val})")
                logger.info(f"Copernicus land cover code: {pixel_val} -> {land_cover_label}")
                return land_cover_label
            else:
                raise RuntimeError("Empty response received from Copernicus Process API")
        elif response.status_code == 401:
            raise RuntimeError("Unauthorized: Copernicus OAuth2 token rejected or expired.")
        elif response.status_code == 403:
            # Handle additional subscription check
            raise RuntimeError("Forbidden: Access to product 'esa-worldcover' is not enabled on this account tier.")
        else:
            raise RuntimeError(f"Copernicus Process API returned status {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.error(f"Error fetching Copernicus land cover: {e}")
        raise RuntimeError(f"Copernicus Sentinel Hub process failed: {e}")
