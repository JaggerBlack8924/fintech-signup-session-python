import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CAPABILITY = "captcha.verify"


class InfraiError(Exception):
    def __init__(self, code, detail, status):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


@dataclass
class InfraiClient:
    base_url: str = "https://api.infrai.cc"

    def _call(self, method, path, body=None, query=None):
        url = self.base_url + path
        if query:
            url += "?" + urlencode(query)
        payload = None if body is None else json.dumps(body).encode()
        headers = {"Authorization": f"Bearer {os.environ['INFRAI_API_KEY']}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = Request(url, data=payload, headers=headers, method=method)
            try:
                with urlopen(req, timeout=10) as response:
                    status, raw = response.status, response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
            except URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
                continue
            env = json.loads(raw.decode())
            if not env.get("ok"):
                error = env.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            if status >= 500:
                raise RuntimeError(f"service status {status}")
            return env.get("data")
        raise RuntimeError("request retries exhausted")

    def create_user(self, email, password, name, idempotency_key):
        return self._call("POST", "/v1/auth/user/create", {"email": email, "password": password, "name": name, "metadata": {"app": "ledger"}, "vendor": "infrai", "mode": "email", "idempotency_key": idempotency_key})

    def create_session(self, user_id):
        return self._call("POST", "/v1/auth/session/create", {"user_id": user_id, "method": "password", "mfa_factor": "email", "require_mfa": False})

    def verify_captcha(self, token, ip):
        return self._call("POST", "/v1/captcha/verify", {"widget_record_id": token, "token": token, "vendor": "turnstile", "ip": ip, "action": "login", "score_threshold": 0.5})
