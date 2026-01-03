import hashlib
import hmac
import secrets

from ..models import User, utcnow


def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return salt.hex(), derived.hex()


def create_user(session, email, display_name, password, is_admin=False):
    email = email.strip().lower()
    display_name = display_name.strip()
    salt_hex, hash_hex = _hash_password(password)
    user = User(
        email=email,
        display_name=display_name,
        password_salt=salt_hex,
        password_hash=hash_hex,
        is_admin=1 if is_admin else 0,
    )
    session.add(user)
    session.commit()
    return user


def verify_user(session, email, password):
    email = email.strip().lower()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None
    _, hash_hex = _hash_password(password, user.password_salt)
    if not hmac.compare_digest(hash_hex, user.password_hash):
        return None
    return user


def ensure_admin_user(session, email, password):
    if not email or not password:
        return None
    email = email.strip().lower()
    existing = session.query(User).filter_by(email=email).first()
    if existing:
        if not existing.is_admin:
            existing.is_admin = 1
            existing.updated_at = utcnow()
            session.commit()
        return existing
    return create_user(session, email, email, password, is_admin=True)
