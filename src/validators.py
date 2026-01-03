import io


def is_http_url(value):
    if not value:
        return False
    return value.startswith("http://") or value.startswith("https://")


def validate_cover_image(uploaded_file):
    if uploaded_file is None:
        return True, ""
    name = uploaded_file.name.lower()
    if not (name.endswith(".jpg") or name.endswith(".jpeg")):
        return False, "Cover must be a JPG file."
    try:
        from PIL import Image
    except Exception:
        return False, "Pillow is required for cover validation."
    try:
        data = uploaded_file.getvalue()
        with Image.open(io.BytesIO(data)) as img:
            width, height = img.size
            if width != 3000 or height != 3000:
                return False, "Cover must be exactly 3000x3000."
            if img.format not in ("JPEG", "JPG"):
                return False, "Cover must be a JPG image."
    except Exception as exc:
        return False, f"Invalid cover image: {exc}"
    return True, ""


def validate_audio_files(uploaded_files):
    if not uploaded_files:
        return True, ""
    names = [file.name.lower() for file in uploaded_files]
    if any(name.endswith(".zip") for name in names):
        if len(uploaded_files) != 1 or not names[0].endswith(".zip"):
            return False, "Upload a single ZIP file for multi-track audio."
        return True, ""
    if not all(name.endswith(".wav") for name in names):
        return False, "Audio files must be WAV or a single ZIP."
    return True, ""
