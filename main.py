import streamlit as st

from src.config import APP_TITLE
from src.db import get_session
from src.services.auth import ensure_admin_user
from src.ui.admin_dashboard import (
    render_admin_applications,
    render_planned_catalog,
    render_releases,
)
from src.ui.artist_my_submissions import render_artist_my_submissions
from src.ui.auth import render_auth
from src.ui.artist_status import render_artist_status
from src.ui.artist_submit import render_artist_submit
from src.config import ADMIN_BOOTSTRAP_EMAIL, ADMIN_BOOTSTRAP_PASSWORD


def get_query_params():
    if hasattr(st, "query_params"):
        return dict(st.query_params)
    return st.experimental_get_query_params()


def get_query_value(params, key):
    value = params.get(key)
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)

    params = get_query_params()
    token_from_query = get_query_value(params, "token")
    page_from_query = get_query_value(params, "page")

    session = get_session()
    try:
        ensure_admin_user(session, ADMIN_BOOTSTRAP_EMAIL, ADMIN_BOOTSTRAP_PASSWORD)
        if not st.session_state.get("user_id"):
            render_auth(session)
            return

        pages = [
            "Artist Submit",
            "My Submissions",
            "Artist Status",
            "Admin Applications",
            "Releases",
            "Planned Catalog",
        ]
        default_page = "Artist Status" if token_from_query else "Artist Submit"
        if page_from_query in pages:
            default_page = page_from_query
        page_index = pages.index(default_page)
        page = st.sidebar.radio("Navigation", pages, index=page_index)

        st.sidebar.subheader("Account")
        st.sidebar.write(st.session_state.get("user_email", ""))
        if st.sidebar.button("Logout"):
            st.session_state.pop("user_id", None)
            st.session_state.pop("user_email", None)
            st.session_state.pop("user_is_admin", None)
            st.rerun()

        if page == "Artist Submit":
            render_artist_submit(session)
        elif page == "My Submissions":
            render_artist_my_submissions(session)
        elif page == "Artist Status":
            render_artist_status(session, token_from_query)
        elif page == "Admin Applications":
            render_admin_applications(session)
        elif page == "Releases":
            render_releases(session)
        elif page == "Planned Catalog":
            render_planned_catalog(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
