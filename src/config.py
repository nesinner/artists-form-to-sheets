import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

APP_TITLE = "Artist Submissions Portal"

SUBMISSION_STATUSES = ["NEW", "OK", "NEEDS_FIX", "DESIGN_REQUESTED", "REJECTED"]
RELEASE_STATUSES = ["IN_PREP", "APPROVED", "SCHEDULED", "REJECTED"]

STATUS_COPY = {
    "NEW": "Submission received",
    "OK": "Approved for release preparation",
    "NEEDS_FIX": "Needs fixes",
    "DESIGN_REQUESTED": "Design requested",
    "REJECTED": "Rejected",
}

RELEASE_STATUS_COPY = {
    "IN_PREP": "In preparation",
    "APPROVED": "Approved",
    "SCHEDULED": "Scheduled",
    "REJECTED": "Rejected",
}

DEFAULT_DB_URL = "sqlite:///data/app.db"


def _get_secret(name, default=""):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
    except Exception:
        return default
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


DB_URL = _get_secret("DB_URL", DEFAULT_DB_URL)
UPLOAD_DIR = Path(_get_secret("UPLOAD_DIR", "data/uploads"))
APP_BASE_URL = _get_secret("APP_BASE_URL", "http://localhost:8501")
ADMIN_BOOTSTRAP_EMAIL = _get_secret("ADMIN_BOOTSTRAP_EMAIL", "")
ADMIN_BOOTSTRAP_PASSWORD = _get_secret("ADMIN_BOOTSTRAP_PASSWORD", "")
