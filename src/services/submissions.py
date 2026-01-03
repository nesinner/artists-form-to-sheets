import secrets

from ..models import ArtistParticipant, Submission


def generate_unique_token(session):
    for _ in range(5):
        token = secrets.token_urlsafe(16)
        exists = session.query(Submission).filter_by(public_token=token).first()
        if not exists:
            return token
    raise RuntimeError("Failed to generate a unique token.")


def create_submission(
    session,
    data,
    participants,
):
    token = generate_unique_token(session)
    submission = Submission(public_token=token, **data)
    session.add(submission)
    session.flush()

    for participant in participants:
        session.add(
            ArtistParticipant(
                submission_id=submission.id,
                role=participant["role"].strip(),
                fullname=participant["fullname"].strip(),
                country=participant["country"].strip(),
                city=participant["city"].strip(),
                email=participant["email"].strip(),
                spotify=participant["spotify"].strip(),
            )
        )

    session.commit()
    return submission
