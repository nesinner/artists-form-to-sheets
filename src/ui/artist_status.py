import streamlit as st

from ..config import STATUS_COPY
from ..models import Submission


def render_artist_status(session, token_from_query):
    st.header("Artist Status")
    token = st.text_input("Status token", value=token_from_query)
    if not token.strip():
        st.info("Enter your status token to see the latest update.")
        return
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Please log in to view your status.")
        return

    query = session.query(Submission).filter_by(public_token=token.strip())
    if not st.session_state.get("user_is_admin"):
        query = query.filter_by(user_id=user_id)
    submission = query.first()
    if not submission:
        st.error("Submission not found or access denied.")
        return

    st.subheader(submission.track_name)
    st.write(f"Artists: {submission.artists_display}")
    st.write(f"Status: {submission.status} - {STATUS_COPY.get(submission.status, '')}")
    if submission.admin_note:
        st.write("Admin note:")
        st.write(submission.admin_note)
    st.write(f"Last update: {submission.updated_at}")
