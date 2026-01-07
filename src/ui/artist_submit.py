from urllib.parse import urlencode
import secrets

import streamlit as st

from ..config import APP_BASE_URL
from ..services.drafts import clear_draft, load_draft_data, save_draft_data
from ..services.submissions import create_submission
from ..validators import is_http_url


PARTICIPANT_FIELDS = ["role", "fullname", "country", "city", "email", "spotify"]


def get_query_params():
    if hasattr(st, "query_params"):
        return dict(st.query_params)
    return st.experimental_get_query_params()


def get_query_value(params, key):
    value = params.get(key)
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


def set_query_params(params):
    if hasattr(st, "query_params"):
        for key, value in params.items():
            if value is None:
                if key in st.query_params:
                    del st.query_params[key]
            else:
                st.query_params[key] = value
        return
    existing = get_query_params()
    merged = dict(existing)
    merged.update({key: value for key, value in params.items() if value is not None})
    st.experimental_set_query_params(**merged)


def initialize_form_state(draft_data):
    defaults = {
        "track_name": "",
        "artists_display": "",
        "cover_option": "LINK",
        "cover_link": "",
        "cover_brief": "",
        "cover_reference_link": "",
        "cover_label_discretion": False,
        "audio_link": "",
        "spotify_link": "",
        "tiktok_link": "",
        "artist_email": "",
        "artist_legal_name": "",
        "artist_country": "",
        "artist_city": "",
        "artists_count": "1",
        "bulk_artist_list": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, draft_data.get(key, value))
    for idx in range(1, 5):
        for field in PARTICIPANT_FIELDS:
            state_key = f"participant_{idx}_{field}"
            st.session_state.setdefault(state_key, draft_data.get(state_key, ""))


def collect_draft_payload():
    payload = {
        "track_name": st.session_state.get("track_name", ""),
        "artists_display": st.session_state.get("artists_display", ""),
        "cover_option": st.session_state.get("cover_option", "LINK"),
        "cover_link": st.session_state.get("cover_link", ""),
        "cover_brief": st.session_state.get("cover_brief", ""),
        "cover_reference_link": st.session_state.get("cover_reference_link", ""),
        "cover_label_discretion": st.session_state.get("cover_label_discretion", False),
        "audio_link": st.session_state.get("audio_link", ""),
        "spotify_link": st.session_state.get("spotify_link", ""),
        "tiktok_link": st.session_state.get("tiktok_link", ""),
        "artist_email": st.session_state.get("artist_email", ""),
        "artist_legal_name": st.session_state.get("artist_legal_name", ""),
        "artist_country": st.session_state.get("artist_country", ""),
        "artist_city": st.session_state.get("artist_city", ""),
        "artists_count": st.session_state.get("artists_count", "1"),
        "bulk_artist_list": st.session_state.get("bulk_artist_list", ""),
    }
    for idx in range(1, 5):
        for field in PARTICIPANT_FIELDS:
            state_key = f"participant_{idx}_{field}"
            payload[state_key] = st.session_state.get(state_key, "")
    return payload


def reset_form_state():
    st.session_state.update(
        {
            "track_name": "",
            "artists_display": "",
            "cover_option": "LINK",
            "cover_link": "",
            "cover_brief": "",
            "cover_reference_link": "",
            "cover_label_discretion": False,
            "audio_link": "",
            "spotify_link": "",
            "tiktok_link": "",
            "artist_email": "",
            "artist_legal_name": "",
            "artist_country": "",
            "artist_city": "",
            "artists_count": "1",
            "bulk_artist_list": "",
        }
    )
    for idx in range(1, 5):
        for field in PARTICIPANT_FIELDS:
            st.session_state[f"participant_{idx}_{field}"] = ""


def render_artist_submit(session):
    st.header("Artist Submit")

    if st.session_state.pop("reset_form_pending", False):
        reset_form_state()

    success_payload = st.session_state.pop("submission_success", None)
    if success_payload:
        status_params = {
            "page": "Artist Status",
            "token": success_payload["token"],
        }
        status_url = f"{APP_BASE_URL}?{urlencode(status_params)}"
        st.success("Submission created.")
        st.write(f"Submission ID: {success_payload['id']}")
        st.write(f"Status URL: {status_url}")

    params = get_query_params()
    draft_token = get_query_value(params, "draft") or st.session_state.get(
        "draft_token"
    )
    if not draft_token:
        draft_token = secrets.token_urlsafe(8)
        st.session_state["draft_token"] = draft_token
        set_query_params({"draft": draft_token})

    draft_data = load_draft_data(session, draft_token)
    initialize_form_state(draft_data)

    last_token = st.session_state.get("last_submission_token") or get_query_value(
        params, "last_token"
    )
    if last_token:
        status_params = {"page": "Artist Status", "token": last_token}
        status_url = f"{APP_BASE_URL}?{urlencode(status_params)}"
        st.info(f"Your tracking token: {last_token}")
        st.write(f"Status URL: {status_url}")

    st.subheader("Release info")
    st.text_input("Track name *", key="track_name")
    st.text_input("Artists display *", key="artists_display")

    st.subheader("Materials")
    st.selectbox("Cover option *", ["LINK", "LABEL_DESIGN"], key="cover_option")
    cover_link = ""
    cover_option = st.session_state.get("cover_option", "LINK")
    if cover_option == "LINK":
        cover_link = st.text_input("Cover link *", key="cover_link")
    else:
        st.text_area("Design brief *", key="cover_brief")
        st.text_input("Reference link (optional)", key="cover_reference_link")
        st.checkbox(
            "No references, leave to label",
            key="cover_label_discretion",
        )
    st.text_input("Audio link *", key="audio_link")

    st.subheader("Profiles")
    st.text_input("Spotify link *", key="spotify_link")
    st.text_input("TikTok link (optional)", key="tiktok_link")

    st.subheader("Contact and legal")
    st.text_input("Artist email *", key="artist_email")
    st.text_input("Artist legal name *", key="artist_legal_name")
    st.text_input("Artist country *", key="artist_country")
    st.text_input("Artist city *", key="artist_city")

    st.subheader("Artists count")
    st.selectbox("Artists count *", ["1", "2", "3", "4", "5+"], key="artists_count")

    participants = []
    bulk_artist_list = ""
    artists_count = st.session_state.get("artists_count", "1")
    if artists_count in ("2", "3", "4"):
        count = int(artists_count)
        st.subheader("Participants")
        for idx in range(1, 5):
            with st.expander(
                f"Participant {idx}", expanded=True if idx <= count else False
            ):
                role = st.text_input(
                    "Role" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_role",
                )
                fullname = st.text_input(
                    "Full name" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_fullname",
                )
                country = st.text_input(
                    "Country" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_country",
                )
                city = st.text_input(
                    "City" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_city",
                )
                email = st.text_input(
                    "Email" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_email",
                )
                spotify = st.text_input(
                    "Spotify" + (" *" if idx <= count else ""),
                    key=f"participant_{idx}_spotify",
                )
                if idx <= count:
                    participants.append(
                        {
                            "role": role,
                            "fullname": fullname,
                            "country": country,
                            "city": city,
                            "email": email,
                            "spotify": spotify,
                        }
                    )
    elif artists_count == "5+":
        bulk_artist_list = st.text_area("Bulk artist list *", key="bulk_artist_list")

    submitted = st.button("Submit")

    if not submitted:
        save_draft_data(session, draft_token, collect_draft_payload())
        return

    errors = []
    track_name = st.session_state.get("track_name", "").strip()
    artists_display = st.session_state.get("artists_display", "").strip()
    cover_option = st.session_state.get("cover_option", "LINK")
    cover_brief = st.session_state.get("cover_brief", "").strip()
    cover_reference_link = st.session_state.get("cover_reference_link", "").strip()
    cover_label_discretion = bool(
        st.session_state.get("cover_label_discretion", False)
    )
    audio_link = st.session_state.get("audio_link", "").strip()
    spotify_link = st.session_state.get("spotify_link", "").strip()
    tiktok_link = st.session_state.get("tiktok_link", "").strip()
    artist_email = st.session_state.get("artist_email", "").strip()
    artist_legal_name = st.session_state.get("artist_legal_name", "").strip()
    artist_country = st.session_state.get("artist_country", "").strip()
    artist_city = st.session_state.get("artist_city", "").strip()
    bulk_artist_list = st.session_state.get("bulk_artist_list", "").strip()

    if not track_name:
        errors.append("Track name is required.")
    if not artists_display:
        errors.append("Artists display is required.")
    if cover_option == "LINK":
        cover_link = st.session_state.get("cover_link", "").strip()
        if not cover_link:
            errors.append("Cover link is required.")
        elif not is_http_url(cover_link):
            errors.append("Cover link must start with http:// or https://.")
    else:
        if not cover_brief:
            errors.append("Design brief is required for label design.")
        if cover_reference_link and not is_http_url(cover_reference_link):
            errors.append("Reference link must start with http:// or https://.")
        if not cover_reference_link and not cover_label_discretion:
            errors.append(
                "Provide a reference link or choose label discretion for label design."
            )
    if not audio_link:
        errors.append("Audio link is required.")
    if audio_link and not is_http_url(audio_link):
        errors.append("Audio link must start with http:// or https://.")
    if not spotify_link:
        errors.append("Spotify link is required.")
    if spotify_link and not is_http_url(spotify_link):
        errors.append("Spotify link must start with http:// or https://.")
    if tiktok_link and not is_http_url(tiktok_link):
        errors.append("TikTok link must start with http:// or https://.")
    if not artist_email:
        errors.append("Artist email is required.")
    if not artist_legal_name:
        errors.append("Artist legal name is required.")
    if not artist_country:
        errors.append("Artist country is required.")
    if not artist_city:
        errors.append("Artist city is required.")

    if artists_count in ("2", "3", "4"):
        for idx, participant in enumerate(participants, start=1):
            missing = [key for key, value in participant.items() if not value.strip()]
            if missing:
                errors.append(f"Participant {idx} has missing fields.")
                break
    if artists_count == "5+" and not bulk_artist_list:
        errors.append("Bulk artist list is required for 5+ artists.")

    if errors:
        for error in errors:
            st.error(error)
        save_draft_data(session, draft_token, collect_draft_payload())
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error("Login required to submit.")
        save_draft_data(session, draft_token, collect_draft_payload())
        return

    data = {
        "user_id": user_id,
        "track_name": track_name,
        "artists_display": artists_display,
        "cover_option": cover_option,
        "cover_link": cover_link.strip() if cover_option == "LINK" else None,
        "cover_file_path": None,
        "cover_brief": cover_brief if cover_option == "LABEL_DESIGN" else None,
        "cover_reference_link": (
            cover_reference_link
            if cover_option == "LABEL_DESIGN" and cover_reference_link
            else None
        ),
        "cover_label_discretion": (
            1 if cover_option == "LABEL_DESIGN" and cover_label_discretion else 0
        ),
        "audio_link": audio_link,
        "audio_file_paths": None,
        "spotify_link": spotify_link,
        "tiktok_link": tiktok_link if tiktok_link else None,
        "artist_email": artist_email,
        "artist_legal_name": artist_legal_name,
        "artist_country": artist_country,
        "artist_city": artist_city,
        "artists_count": artists_count,
        "bulk_artist_list": bulk_artist_list if bulk_artist_list else None,
        "status": "NEW",
        "admin_note": None,
    }

    submission = create_submission(
        session=session,
        data=data,
        participants=participants,
    )

    status_params = {"page": "Artist Status", "token": submission.public_token}
    status_url = f"{APP_BASE_URL}?{urlencode(status_params)}"
    st.session_state["last_submission_token"] = submission.public_token
    set_query_params({"last_token": submission.public_token})

    clear_draft(session, draft_token)
    st.session_state["submission_success"] = {
        "id": submission.id,
        "token": submission.public_token,
    }
    st.session_state["reset_form_pending"] = True
    st.rerun()
