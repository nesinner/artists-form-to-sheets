import csv
import io
import sys
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import models
from src.ui import admin_dashboard


def build_session():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_url = f"sqlite:///{temp_file.name}"
    engine = create_engine(db_url)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def parse_csv(data):
    reader = csv.DictReader(io.StringIO(data))
    return list(reader)


def seed_data(session):
    submission = models.Submission(
        track_name="Track",
        artists_display="Artist",
        cover_option="LABEL_DESIGN",
        cover_link=None,
        cover_file_path=None,
        audio_link="http://example.com/audio",
        audio_file_paths=None,
        spotify_link="http://example.com/spotify",
        tiktok_link=None,
        artist_email="test@example.com",
        artist_legal_name="Legal Name",
        artist_country="Country",
        artist_city="City",
        artists_count="1",
        bulk_artist_list=None,
        status="OK",
        admin_note=None,
        public_token="token-123",
    )
    session.add(submission)
    session.commit()

    release = models.Release(submission_id=submission.id, status="APPROVED")
    session.add(release)
    session.commit()

    planned = models.PlannedCatalog(release_id=release.id)
    session.add(planned)
    session.commit()


def main():
    session = build_session()
    try:
        seed_data(session)

        applications_csv = admin_dashboard.export_submissions_csv(session)
        releases_csv = admin_dashboard.export_releases_csv(session)
        planned_csv = admin_dashboard.export_planned_csv(session)

        applications_rows = parse_csv(applications_csv)
        releases_rows = parse_csv(releases_csv)
        planned_rows = parse_csv(planned_csv)

        assert len(applications_rows) == 1
        assert len(releases_rows) == 1
        assert len(planned_rows) == 1

        assert applications_rows[0]["track_name"] == "Track"
        assert releases_rows[0]["release_status"] == "APPROVED"
        assert planned_rows[0]["track_name"] == "Track"
    finally:
        session.close()

    print("CSV export check: OK")


if __name__ == "__main__":
    main()
