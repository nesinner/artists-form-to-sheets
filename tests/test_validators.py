import io

from PIL import Image

from src import validators


class DummyUpload:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


def make_image_bytes(width, height):
    buffer = io.BytesIO()
    image = Image.new("RGB", (width, height), color=(255, 0, 0))
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_validate_cover_jpg_3000_ok():
    data = make_image_bytes(3000, 3000)
    upload = DummyUpload("cover.jpg", data)
    valid, message = validators.validate_cover_image(upload)
    assert valid
    assert message == ""


def test_validate_cover_jpg_3000_wrong_size():
    data = make_image_bytes(1000, 1000)
    upload = DummyUpload("cover.jpg", data)
    valid, message = validators.validate_cover_image(upload)
    assert not valid
    assert "3000x3000" in message


def test_validate_audio_files_wav_ok():
    upload = DummyUpload("track.wav", b"RIFF....WAVE")
    valid, message = validators.validate_audio_files([upload])
    assert valid
    assert message == ""


def test_validate_audio_files_zip_ok():
    upload = DummyUpload("tracks.zip", b"PK\x03\x04")
    valid, message = validators.validate_audio_files([upload])
    assert valid
    assert message == ""


def test_validate_audio_files_zip_and_wav_invalid():
    zip_upload = DummyUpload("tracks.zip", b"PK\x03\x04")
    wav_upload = DummyUpload("track.wav", b"RIFF....WAVE")
    valid, message = validators.validate_audio_files([zip_upload, wav_upload])
    assert not valid
    assert "single ZIP" in message
