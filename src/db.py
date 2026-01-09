from pathlib import Path

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DB_URL
from .models import Base


def ensure_db_dir(db_url):
    if not db_url.startswith("sqlite"):
        return
    if db_url.startswith("sqlite:////"):
        db_path = "/" + db_url.replace("sqlite:////", "", 1)
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "", 1)
    else:
        return
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def ensure_sqlite_columns(engine, db_url):
    if not db_url.startswith("sqlite"):
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
def get_engine(db_url):
    ensure_db_dir(db_url)
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine_kwargs = {"connect_args": connect_args}
    if not db_url.startswith("sqlite"):
        # Keep stale connections from breaking after app sleep.
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 1800
    return create_engine(db_url, **engine_kwargs)


@st.cache_resource
def get_session_factory(db_url):
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    ensure_sqlite_columns(engine, db_url)
    return sessionmaker(bind=engine)


def get_session():
    return get_session_factory(DB_URL)()
