"""
Application configuration.
"""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_planner.db")
ARTIC_BASE_URL = os.getenv("ARTIC_BASE_URL", "https://api.artic.edu/api/v1")
MAX_PLACES_PER_PROJECT = 10
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

# Art Institute API response cache (seconds). 0 = disable.
ARTIC_CACHE_TTL = int(os.getenv("ARTIC_CACHE_TTL", "3600"))

# Basic auth (optional). If both set, all project/place endpoints require auth.
BASIC_AUTH_USER = os.getenv("BASIC_AUTH_USER", "").strip()
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD", "").strip()
BASIC_AUTH_ENABLED = bool(BASIC_AUTH_USER and BASIC_AUTH_PASSWORD)
