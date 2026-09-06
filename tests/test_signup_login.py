from signup_login_service import signup_then_login


class FakeClient:
    def __init__(self):
        self.calls = []

    def verify_captcha(self, token, ip):
        self.calls.append(("captcha", token, ip))
        return {"verified": True}

    def create_user(self, email, password, name, idempotency_key):
        self.calls.append(("user", email, idempotency_key))
        return {"user_id": "u_42"}

    def create_session(self, user_id):
        self.calls.append(("session", user_id))
        return {"session_id": "s_42"}


def test_signup_login_handoff_creates_session_and_audit_event():
    fake = FakeClient()
    result = signup_then_login("ada@example.com", "secret", "Ada", "captcha-ok", "203.0.113.5", "req-7", fake)
    assert result.user_id == "u_42"
    assert result.session["session_id"] == "s_42"
    assert result.audit_event == {"event": "account_login", "subject_id": "u_42", "request_id": "req-7"}
    assert [call[0] for call in fake.calls] == ["captcha", "user", "session"]
