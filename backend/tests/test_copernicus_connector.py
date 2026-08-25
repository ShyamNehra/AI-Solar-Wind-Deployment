import pytest
from unittest.mock import patch, MagicMock
from app.connectors.copernicus import fetch_land_cover
from app.core.copernicus_auth import get_copernicus_token

def test_copernicus_connector_fails_when_credentials_not_configured():
    # Ensure env vars are unset
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            fetch_land_cover(34.5, -115.5)
        assert "Copernicus credentials not configured" in str(exc_info.value)

def test_copernicus_connector_parses_response():
    # 1. Mock token call
    with patch("app.connectors.copernicus.get_copernicus_token", return_value="mock_token"):
        # 2. Mock requests.post response returning a binary TIFF with class 60 (Barren)
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            # A mock tiff binary where the last byte is 60
            mock_resp.content = b"\x00\x01\x3c"  # 0x3c is 60 in hex
            mock_post.return_value = mock_resp
            
            res = fetch_land_cover(34.5, -115.5)
            
            mock_post.assert_called_once()
            assert res == "Barren / Sparse Vegetation"
