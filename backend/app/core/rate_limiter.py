from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize central rate limiter with IP tracking
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
