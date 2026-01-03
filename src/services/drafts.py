import json

from ..models import Draft, utcnow


def load_draft_data(session, token):
    draft = session.query(Draft).filter_by(token=token).first()
    if not draft or not draft.data:
        return {}
    try:
        return json.loads(draft.data)
    except Exception:
        return {}


def save_draft_data(session, token, data):
    payload = json.dumps(data, ensure_ascii=True)
    draft = session.query(Draft).filter_by(token=token).first()
    if not draft:
        draft = Draft(token=token, data=payload)
        session.add(draft)
    else:
        draft.data = payload
        draft.updated_at = utcnow()
    session.commit()


def clear_draft(session, token):
    draft = session.query(Draft).filter_by(token=token).first()
    if draft:
        session.delete(draft)
        session.commit()
