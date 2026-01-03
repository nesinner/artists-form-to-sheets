import os
from pathlib import Path

import streamlit as st


def ensure_upload_dir(upload_dir):
    upload_dir.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name):
    base = os.path.basename(name)
    cleaned = []
    for char in base:
        if char.isascii() and (char.isalnum() or char in "._-"):
            cleaned.append(char)
        else:
            cleaned.append("_")
    safe = "".join(cleaned).strip("._")
    return safe or "file"


def save_upload(uploaded_file, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(uploaded_file.name)
    destination = dest_dir / filename
    destination.write_bytes(uploaded_file.getvalue())
    return str(destination)


def save_uploads(uploaded_files, dest_dir):
    paths = []
    for uploaded_file in uploaded_files:
        paths.append(save_upload(uploaded_file, dest_dir))
    return paths


def render_download(path, label, key):
    st.write(f"{label}: {path}")
    if not path:
        return
    if os.path.exists(path):
        with open(path, "rb") as handle:
            st.download_button(
                f"Download {label}",
                handle.read(),
                file_name=Path(path).name,
                key=key,
            )
