from urllib.parse import urlencode

import streamlit as st
from sqlalchemy.orm import selectinload

from ..config import APP_BASE_URL, RELEASE_STATUS_COPY, STATUS_COPY
from ..models import Submission
from .common import rerun


def render_artist_my_submissions(session):
    st.header("My Submissions")
    if st.button("Refresh list"):
        rerun()
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Please log in to view your submissions.")
        return

    submissions = (
        session.query(Submission)
        .options(selectinload(Submission.release))
        .filter_by(user_id=user_id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    if not submissions:
        st.info("No submissions yet.")
        return

    rows = [
        {
            "id": sub.id,
            "track_name": sub.track_name,
            "status": sub.status,
            "release_status": sub.release.status if sub.release else "",
            "updated_at": sub.updated_at,
        }
        for sub in submissions
    ]
    st.dataframe(rows, use_container_width=True)

    selected = st.selectbox(
        "Select submission",
        submissions,
        format_func=lambda sub: f"{sub.id} - {sub.track_name}",
    )

    status_params = {"page": "Artist Status", "token": selected.public_token}
    status_url = f"{APP_BASE_URL}?{urlencode(status_params)}"

    st.subheader(selected.track_name)
    st.write(f"Artists: {selected.artists_display}")
    st.write(
        f"Submission status: {selected.status} - {STATUS_COPY.get(selected.status, '')}"
    )
    if selected.release:
        st.write(
            "Release status: "
            f"{selected.release.status} - "
            f"{RELEASE_STATUS_COPY.get(selected.release.status, '')}"
        )
    if selected.admin_note:
        st.write("Admin note:")
        st.write(selected.admin_note)
    st.write(f"Status URL: {status_url}")
    st.write(f"Last update: {selected.updated_at}")
