from os import getenv
from slowapi import Limiter as _slowapiLimiter

limiter = _slowapiLimiter(key_func=lambda request: request.client.host, default_limits=[getenv("REGULAR_RATE_LIMIT", "30/minute")])