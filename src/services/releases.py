from ..models import PlannedCatalog, Release


def create_release(session, submission_id):
    existing = session.query(Release).filter_by(submission_id=submission_id).first()
    if existing:
        return existing, False
    release = Release(submission_id=submission_id, status="IN_PREP")
    session.add(release)
    session.commit()
    return release, True


def create_planned_catalog(session, release_id):
    existing = session.query(PlannedCatalog).filter_by(release_id=release_id).first()
    if existing:
        return existing, False
    planned = PlannedCatalog(release_id=release_id)
    session.add(planned)
    session.commit()
    return planned, True
