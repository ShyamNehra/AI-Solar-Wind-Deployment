from unittest.mock import patch, MagicMock
from app.connectors.osm import fetch_infrastructure_proximity, haversine_distance

def test_osm_connector_parses_response():
    mock_elements = [
        {
            "type": "way",
            "id": 1,
            "geometry": [
                {"lat": 34.501, "lon": -115.501}
            ],
            "tags": {
                "highway": "primary"
            }
        },
        {
            "type": "node",
            "id": 2,
            "lat": 34.505,
            "lon": -115.505,
            "tags": {
                "power": "substation"
            }
        }
    ]
    
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"elements": mock_elements}
        mock_post.return_value = mock_resp
        
        lat, lon = 34.5, -115.5
        res = fetch_infrastructure_proximity(lat, lon, radius_km=10.0)
        
        mock_post.assert_called_once()
        
        expected_road_dist = haversine_distance(lat, lon, 34.501, -115.501)
        expected_substation_dist = haversine_distance(lat, lon, 34.505, -115.505)
        
        assert res["nearest_road_km"] == expected_road_dist
        assert res["nearest_substation_km"] == expected_substation_dist
        assert res["nearest_urban_area_km"] is None
        assert res["nearest_protected_zone_km"] is None
        assert res["nearest_water_body_km"] is None
