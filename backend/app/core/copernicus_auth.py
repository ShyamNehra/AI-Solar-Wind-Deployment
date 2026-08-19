import time
import os
import requests
import logging

logger = logging.getLogger(__name__)

COPERNICUS_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Cache structure
_cached_token = None
_token_expiry_time = 0.0

def get_copernicus_token() -> str:
    """
    Acquire an OIDC OAuth2 token from Copernicus Data Space.
    Caches the token and proactively refreshes it if expired or close to expiry.
    """
    global _cached_token, _token_expiry_time
    
    client_id = os.getenv("COPERNICUS_CLIENT_ID")
    client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        # Raise clear, explicit error as mandated by user request
        raise ValueError("Copernicus credentials not configured")
        
    current_time = time.time()
    
    # Cache hit check (with a 60s safety buffer)
    if _cached_token and current_time < (_token_expiry_time - 60.0):
        logger.info("Using cached Copernicus OAuth2 token.")
        return _cached_token
        
    logger.info("Requesting new Copernicus OAuth2 token...")
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(COPERNICUS_TOKEN_URL, data=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # default 1 hour
            
            if not access_token:
                raise RuntimeError("Token response did not contain access_token")
                
            _cached_token = access_token
            _token_expiry_time = time.time() + float(expires_in)
            
            logger.info("Successfully acquired and cached new Copernicus token.")
            return _cached_token
        else:
            raise RuntimeError(f"Copernicus Auth failed (status {response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"Error obtaining Copernicus OAuth2 token: {e}")
        raise RuntimeError(f"Copernicus authentication failure: {e}")
