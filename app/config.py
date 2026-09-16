"""
VulnLab configuration — kept minimal.

Unlike the old design, there is no global SECURE flag: each section chooses
vulnerable vs secure per request (a toggle in the UI). The only thing needed
here is a dev secret for Flask's session, which the CSRF section uses to hold
a per-session CSRF token. Fine to hardcode for a localhost teaching app.
"""
import os

SECRET_KEY = os.environ.get("APP_SECRET_KEY", "vulnlab-dev-key")
