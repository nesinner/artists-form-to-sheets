from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow():
    return datetime.utcnow()


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    track_name = Column(String, nullable=False)
    artists_display = Column(String, nullable=False)
    cover_option = Column(String, nullable=False)
    cover_link = Column(Text)
    cover_file_path = Column(Text)
    cover_brief = Column(Text)
    cover_reference_link = Column(Text)
    cover_label_discretion = Column(Integer)
    audio_link = Column(Text)
    audio_file_paths = Column(Text)
    spotify_link = Column(Text, nullable=False)
    tiktok_link = Column(Text)
    artist_email = Column(String, nullable=False)
    artist_legal_name = Column(String, nullable=False)
    artist_country = Column(String, nullable=False)
    artist_city = Column(String, nullable=False)
    artists_count = Column(String, nullable=False)
    bulk_artist_list = Column(Text)
    status = Column(String, nullable=False, default="NEW")
    admin_note = Column(Text)
    public_token = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    participants = relationship(
        "ArtistParticipant", back_populates="submission", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="submissions")
    release = relationship("Release", back_populates="submission", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    submissions = relationship("Submission", back_populates="user")


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False, unique=True)
    data = Column(Text)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)


class ArtistParticipant(Base):
    __tablename__ = "artist_participants"

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    role = Column(String, nullable=False)
    fullname = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    email = Column(String, nullable=False)
    spotify = Column(String, nullable=False)

    submission = relationship("Submission", back_populates="participants")


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True)
    submission_id = Column(
        Integer, ForeignKey("submissions.id"), nullable=False, unique=True
    )
    status = Column(String, nullable=False, default="IN_PREP")
    release_note = Column(Text)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    submission = relationship("Submission", back_populates="release")
    planned_item = relationship(
        "PlannedCatalog", back_populates="release", uselist=False
    )


class PlannedCatalog(Base):
    __tablename__ = "planned_catalog"

    id = Column(Integer, primary_key=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    release = relationship("Release", back_populates="planned_item")
