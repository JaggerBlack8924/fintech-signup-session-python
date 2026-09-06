from dataclasses import dataclass
from infrai_client import InfraiClient, InfraiError


@dataclass
class LoginResult:
    user_id: str
    session: dict
    audit_event: dict


def signup_then_login(email, password, name, captcha_token, ip, request_id, client=None):
    client = client or InfraiClient()
    client.verify_captcha(captcha_token, ip)
    user = client.create_user(email, password, name, request_id)
    user_id = user["user_id"]
    session = client.create_session(user_id)
    return LoginResult(user_id, session, {"event": "account_login", "subject_id": user_id, "request_id": request_id})


def client_response(exc):
    if isinstance(exc, InfraiError) and exc.status < 500:
        return {"status": exc.status, "error": exc.code}
    return {"status": 503, "error": "service_unavailable"}
