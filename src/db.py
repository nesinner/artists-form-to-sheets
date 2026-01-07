from pathlib import Path

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DB_URL
from .models import Base


def ensure_db_dir():
    if not DB_URL.startswith("sqlite"):
        return
    if DB_URL.startswith("sqlite:////"):
        db_path = "/" + DB_URL.replace("sqlite:////", "", 1)
    elif DB_URL.startswith("sqlite:///"):
        db_path = DB_URL.replace("sqlite:///", "", 1)
    else:
        return
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def ensure_sqlite_columns(engine):
    if not DB_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        result = conn.exec_driver_sql("PRAGMA table_info(submissions)")
        columns = {row[1] for row in result}
        if "user_id" not in columns:
            conn.exec_driver_sql("ALTER TABLE submissions ADD COLUMN user_id INTEGER")
        if "cover_brief" not in columns:
            conn.exec_driver_sql("ALTER TABLE submissions ADD COLUMN cover_brief TEXT")
        if "cover_reference_link" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE submissions ADD COLUMN cover_reference_link TEXT"
            )
        if "cover_label_discretion" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE submissions ADD COLUMN cover_label_discretion INTEGER"
            )


@st.cache_resource
def get_engine():
    ensure_db_dir()
    connect_args = {}
    if DB_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(DB_URL, connect_args=connect_args)


@st.cache_resource
def get_session_factory():
    engine = get_engine()
    Base.metadata.create_all(engine)
    ensure_sqlite_columns(engine)
    return sessionmaker(bind=engine)


def get_session():
    return get_session_factory()()
