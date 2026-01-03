from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import models


def make_session(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url)
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_submission_to_planned_flow(tmp_path):
    session = make_session(tmp_path)
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
        status="NEW",
        admin_note=None,
        public_token="token-123",
    )
    session.add(submission)
    session.commit()

    submission.status = "OK"
    session.commit()

    release = models.Release(submission_id=submission.id, status="IN_PREP")
    session.add(release)
    session.commit()

    release.status = "APPROVED"
    session.commit()

    planned = models.PlannedCatalog(release_id=release.id)
    session.add(planned)
    session.commit()

    assert session.query(models.Submission).count() == 1
    assert session.query(models.Release).count() == 1
    assert session.query(models.PlannedCatalog).count() == 1
