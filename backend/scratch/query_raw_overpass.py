import requests
import json
import time

URLS = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
headers = {
    "User-Agent": "SolarWindDeploymentPlatform/1.0"
}

def query_overpass(query_name, ql_query):
    print(f"=== RAW OVERPASS RESPONSE FOR: {query_name} ===")
    full_query = f"[out:json][timeout:15];{ql_query}"
    
    time.sleep(5) # Wait 5s between requests to avoid rate limits
    
    for url in URLS:
        try:
            r = requests.post(url, data=full_query, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                elements = data.get("elements", [])
                metadata = {
                    "version": data.get("version"),
                    "generator": data.get("generator"),
                    "osm3s": data.get("osm3s"),
                    "elements_count": len(elements)
                }
                print(f"Server: {url}")
                print("Metadata:")
                print(json.dumps(metadata, indent=2))
                if elements:
                    print("First matching element:")
                    print(json.dumps(elements[0], indent=2))
                else:
                    print("No elements matched within the search radius.")
                return
            elif r.status_code == 429:
                print(f"Server {url} rate limited. Retrying next mirror...")
                continue
            else:
                print(f"Server {url} returned {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Server {url} failed: {e}")
            
    print("All mirrors failed or rate limited.")
    print()

def main():
    # Using 2000m radius to run fast and avoid heavy queries
    query_overpass("Power / Substation / Transmission", "(node[\"power\"](around:2000, 34.5, -115.5);way[\"power\"](around:2000, 34.5, -115.5););out geom;")
    query_overpass("Urban Landuse / Place", "(node[\"place\"](around:2000, 34.5, -115.5);way[\"landuse\"=\"residential\"](around:2000, 34.5, -115.5););out geom;")
    query_overpass("Protected Area / Nature Reserve", "(way[\"boundary\"=\"protected_area\"](around:2000, 34.5, -115.5);way[\"leisure\"=\"nature_reserve\"](around:2000, 34.5, -115.5););out geom;")
    query_overpass("Water Body / Waterway", "(way[\"natural\"=\"water\"](around:2000, 34.5, -115.5);way[\"waterway\"](around:2000, 34.5, -115.5););out geom;")

if __name__ == "__main__":
    main()
