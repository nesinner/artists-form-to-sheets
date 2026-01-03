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

DEFAULT_DB_URL = "sqlite:///data/app.db"

DB_URL = os.getenv("DB_URL", DEFAULT_DB_URL)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")
ADMIN_BOOTSTRAP_EMAIL = os.getenv("ADMIN_BOOTSTRAP_EMAIL", "")
ADMIN_BOOTSTRAP_PASSWORD = os.getenv("ADMIN_BOOTSTRAP_PASSWORD", "")
