import streamlit as st

from ..models import User
from ..services.auth import create_user, verify_user


def _set_session_user(user):
    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email
    st.session_state["user_is_admin"] = bool(user.is_admin)


def render_auth(session):
    st.header("Welcome")
    st.write("Please sign in or create an account to continue.")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if not email.strip() or not password:
                st.error("Email and password are required.")
            else:
                user = verify_user(session, email, password)
                if user:
                    _set_session_user(user)
                    st.success("Logged in.")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab_register:
        name = st.text_input("Display name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input(
            "Password", type="password", key="register_password"
        )
        confirm = st.text_input(
            "Confirm password", type="password", key="register_confirm"
        )
        if st.button("Create account"):
            if not name.strip():
                st.error("Display name is required.")
            elif not email.strip():
                st.error("Email is required.")
            elif not password:
                st.error("Password is required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                email_norm = email.strip().lower()
                if session.query(User).filter_by(email=email_norm).first():
                    st.error("This email is already registered.")
                else:
                    user = create_user(session, email, name, password, is_admin=False)
                    _set_session_user(user)
                    st.success("Account created.")
                    st.rerun()
