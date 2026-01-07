import csv
import io
import json

import streamlit as st
from sqlalchemy import func, or_

from ..config import RELEASE_STATUSES, SUBMISSION_STATUSES
from ..models import PlannedCatalog, Release, Submission, utcnow
from ..services.releases import create_planned_catalog, create_release
from ..storage import render_download


def build_csv(rows, fieldnames):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def export_submissions_csv(session):
    submissions = (
        session.query(Submission).order_by(Submission.created_at.desc()).all()
    )
    rows = []
    for submission in submissions:
        participants = [
            {
                "role": participant.role,
                "fullname": participant.fullname,
                "country": participant.country,
                "city": participant.city,
                "email": participant.email,
                "spotify": participant.spotify,
            }
            for participant in submission.participants
        ]
        rows.append(
            {
                "id": submission.id,
                "track_name": submission.track_name,
                "artists_display": submission.artists_display,
                "cover_option": submission.cover_option,
                "cover_link": submission.cover_link,
                "cover_file_path": submission.cover_file_path,
                "cover_brief": submission.cover_brief,
                "cover_reference_link": submission.cover_reference_link,
                "cover_label_discretion": submission.cover_label_discretion,
                "audio_link": submission.audio_link,
                "audio_file_paths": submission.audio_file_paths,
                "spotify_link": submission.spotify_link,
                "tiktok_link": submission.tiktok_link,
                "artist_email": submission.artist_email,
                "artist_legal_name": submission.artist_legal_name,
                "artist_country": submission.artist_country,
                "artist_city": submission.artist_city,
                "artists_count": submission.artists_count,
                "bulk_artist_list": submission.bulk_artist_list,
                "participants": json.dumps(participants, ensure_ascii=True),
                "status": submission.status,
                "admin_note": submission.admin_note,
                "public_token": submission.public_token,
                "created_at": submission.created_at,
                "updated_at": submission.updated_at,
            }
        )
    fieldnames = [
        "id",
        "track_name",
        "artists_display",
        "cover_option",
        "cover_link",
        "cover_file_path",
        "cover_brief",
        "cover_reference_link",
        "cover_label_discretion",
        "audio_link",
        "audio_file_paths",
        "spotify_link",
        "tiktok_link",
        "artist_email",
        "artist_legal_name",
        "artist_country",
        "artist_city",
        "artists_count",
        "bulk_artist_list",
        "participants",
        "status",
        "admin_note",
        "public_token",
        "created_at",
        "updated_at",
    ]
    return build_csv(rows, fieldnames)


def export_releases_csv(session):
    releases = (
        session.query(Release)
        .join(Submission, Release.submission_id == Submission.id)
        .order_by(Release.created_at.desc())
        .all()
    )
    rows = []
    for release in releases:
        rows.append(
            {
                "id": release.id,
                "submission_id": release.submission_id,
                "release_status": release.status,
                "release_note": release.release_note,
                "release_created_at": release.created_at,
                "release_updated_at": release.updated_at,
                "track_name": release.submission.track_name,
                "artists_display": release.submission.artists_display,
                "artist_email": release.submission.artist_email,
            }
        )
    fieldnames = [
        "id",
        "submission_id",
        "release_status",
        "release_note",
        "release_created_at",
        "release_updated_at",
        "track_name",
        "artists_display",
        "artist_email",
    ]
    return build_csv(rows, fieldnames)


def export_planned_csv(session):
    planned_items = (
        session.query(PlannedCatalog)
        .join(Release, PlannedCatalog.release_id == Release.id)
        .join(Submission, Release.submission_id == Submission.id)
        .order_by(PlannedCatalog.created_at.desc())
        .all()
    )
    rows = []
    for item in planned_items:
        rows.append(
            {
                "id": item.id,
                "release_id": item.release_id,
                "planned_created_at": item.created_at,
                "release_status": item.release.status,
                "track_name": item.release.submission.track_name,
                "artists_display": item.release.submission.artists_display,
                "artist_email": item.release.submission.artist_email,
            }
        )
    fieldnames = [
        "id",
        "release_id",
        "planned_created_at",
        "release_status",
        "track_name",
        "artists_display",
        "artist_email",
    ]
    return build_csv(rows, fieldnames)


def admin_gate():
    if st.session_state.get("user_is_admin"):
        return True
    st.error("Admin access required.")
    return False


def render_admin_applications(session):
    st.header("Admin Applications")
    if not admin_gate():
        return

    st.download_button(
        "Download Applications CSV",
        export_submissions_csv(session),
        file_name="applications.csv",
    )

    status_filter = st.selectbox("Filter by status", ["All"] + SUBMISSION_STATUSES)
    search_query = st.text_input("Search by track, artists, or email")

    query = session.query(Submission).order_by(Submission.created_at.desc())
    if status_filter != "All":
        query = query.filter(Submission.status == status_filter)
    if search_query.strip():
        pattern = f"%{search_query.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Submission.track_name).like(pattern),
                func.lower(Submission.artists_display).like(pattern),
                func.lower(Submission.artist_email).like(pattern),
            )
        )
    submissions = query.all()

    table_rows = [
        {
            "id": sub.id,
            "track_name": sub.track_name,
            "email": sub.artist_email,
            "status": sub.status,
            "created_at": sub.created_at,
        }
        for sub in submissions
    ]
    st.dataframe(table_rows, use_container_width=True)

    if not submissions:
        st.info("No submissions match the filter.")
        return

    selected = st.selectbox(
        "Select submission",
        submissions,
        format_func=lambda sub: f"{sub.id} - {sub.track_name}",
    )

    st.subheader("Submission details")
    st.write(f"Track: {selected.track_name}")
    st.write(f"Artists: {selected.artists_display}")
    st.write(f"Email: {selected.artist_email}")
    st.write(f"Cover option: {selected.cover_option}")
    if selected.cover_option == "LINK":
        if selected.cover_link:
            st.write(f"Cover link: {selected.cover_link}")
        if selected.cover_file_path:
            render_download(selected.cover_file_path, "Cover file", "cover_download")
    else:
        if selected.cover_brief:
            st.write("Design brief:")
            st.write(selected.cover_brief)
        if selected.cover_reference_link:
            st.write(f"Reference link: {selected.cover_reference_link}")
        if selected.cover_label_discretion:
            st.write("Reference: label discretion")
    if selected.audio_link:
        st.write(f"Audio link: {selected.audio_link}")
    if selected.audio_file_paths:
        audio_paths = json.loads(selected.audio_file_paths)
        st.write("Audio files:")
        for idx, path in enumerate(audio_paths, start=1):
            render_download(path, f"Audio file {idx}", f"audio_download_{idx}")
    st.write(f"Spotify: {selected.spotify_link}")
    if selected.tiktok_link:
        st.write(f"TikTok: {selected.tiktok_link}")
    st.write(
        f"Artist: {selected.artist_legal_name} ({selected.artist_country}, {selected.artist_city})"
    )
    st.write(f"Artists count: {selected.artists_count}")
    if selected.artists_count in ("2", "3", "4"):
        st.write("Participants:")
        for participant in selected.participants:
            st.write(
                f"{participant.fullname} - {participant.role} - "
                f"{participant.country}/{participant.city}"
            )
    if selected.bulk_artist_list:
        st.write("Bulk artist list:")
        st.write(selected.bulk_artist_list)

    new_status = st.selectbox(
        "Status", SUBMISSION_STATUSES, index=SUBMISSION_STATUSES.index(selected.status)
    )
    new_note = st.text_area("Admin note", value=selected.admin_note or "")
    if st.button("Save submission"):
        selected.status = new_status
        selected.admin_note = new_note.strip() if new_note else None
        selected.updated_at = utcnow()
        session.commit()
        st.success("Submission updated.")

    if selected.status == "OK":
        if st.button("Move to Releases"):
            _, created = create_release(session, selected.id)
            if created:
                st.success("Release created.")
            else:
                st.info("Release already exists.")


def render_releases(session):
    st.header("Releases")
    if not admin_gate():
        return

    st.download_button(
        "Download Releases CSV",
        export_releases_csv(session),
        file_name="releases.csv",
    )

    releases = (
        session.query(Release)
        .join(Submission, Release.submission_id == Submission.id)
        .order_by(Release.created_at.desc())
        .all()
    )

    rows = [
        {
            "id": release.id,
            "submission_id": release.submission_id,
            "track_name": release.submission.track_name,
            "status": release.status,
            "created_at": release.created_at,
        }
        for release in releases
    ]
    st.dataframe(rows, use_container_width=True)

    if not releases:
        st.info("No releases yet.")
        return

    selected = st.selectbox(
        "Select release",
        releases,
        format_func=lambda rel: f"{rel.id} - {rel.submission.track_name}",
    )
    st.subheader("Release details")
    st.write(f"Submission ID: {selected.submission_id}")
    st.write(f"Track: {selected.submission.track_name}")
    st.write(f"Artists: {selected.submission.artists_display}")
    st.write(f"Status: {selected.status}")

    new_status = st.selectbox(
        "Release status",
        RELEASE_STATUSES,
        index=RELEASE_STATUSES.index(selected.status),
    )
    release_note = st.text_area("Release note", value=selected.release_note or "")
    if st.button("Save release"):
        selected.status = new_status
        selected.release_note = release_note.strip() if release_note else None
        selected.updated_at = utcnow()
        session.commit()
        st.success("Release updated.")

    if selected.status == "APPROVED":
        if st.button("Move to Planned Catalog"):
            _, created = create_planned_catalog(session, selected.id)
            if created:
                st.success("Planned catalog entry created.")
            else:
                st.info("Planned catalog entry already exists.")


def render_planned_catalog(session):
    st.header("Planned Catalog")
    if not admin_gate():
        return

    st.download_button(
        "Download Planned Catalog CSV",
        export_planned_csv(session),
        file_name="planned_catalog.csv",
    )

    planned_items = (
        session.query(PlannedCatalog)
        .join(Release, PlannedCatalog.release_id == Release.id)
        .join(Submission, Release.submission_id == Submission.id)
        .order_by(PlannedCatalog.created_at.desc())
        .all()
    )

    rows = []
    for item in planned_items:
        rows.append(
            {
                "id": item.id,
                "release_id": item.release_id,
                "track_name": item.release.submission.track_name,
                "artists": item.release.submission.artists_display,
                "created_at": item.created_at,
            }
        )
    st.dataframe(rows, use_container_width=True)

    if not planned_items:
        st.info("No planned catalog entries yet.")
