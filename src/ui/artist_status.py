import streamlit as st
from sqlalchemy.orm import selectinload

from ..config import RELEASE_STATUS_COPY, STATUS_COPY
from ..models import Submission
from .common import rerun


def render_artist_status(session, token_from_query):
    st.header("Artist Status")
    session.expire_all()
    token = st.text_input("Status token", value=token_from_query).strip()
    if not token:
        st.info("Enter your status token to see the latest update.")
        return

    if st.button("Refresh status"):
        rerun()

    query = (
        session.query(Submission)
        .options(selectinload(Submission.release))
        .filter_by(public_token=token)
    )
    submission = query.first()
    if not submission:
        st.error("Submission not found.")
        return

    st.subheader(submission.track_name)
    st.write(f"Artists: {submission.artists_display}")
    st.write(f"Submission status: {submission.status} - {STATUS_COPY.get(submission.status, '')}")
    if submission.release:
        st.write(
            "Release status: "
            f"{submission.release.status} - "
            f"{RELEASE_STATUS_COPY.get(submission.release.status, '')}"
        )
    if submission.admin_note:
        st.write("Admin note:")
        st.write(submission.admin_note)
    st.write(f"Last update: {submission.updated_at}")
