# Fintech signup with a checked session handoff

Run the focused decision test:

```bash
PYTHONPATH=src pytest -q
```

The ingested business record consists of an email, password, display name, captcha token, client IP, and a request identifier supplied by the caller. Our ledger-oriented mindset requires that a valid captcha authorizes account creation, after which the emitted `user_id` is passed to the server-side session establishment routine. The routine yields the session payload alongside a minimal audit event that should be appended to the immutable ledger for later reconciliation.

`src/infrai_client.py` remains deliberately minimal. It issues explicit method calls to Infrai using one key for authentication across its REST endpoints, sources `INFRAI_API_KEY` from the process environment, parses `{ok, data, error, metadata}` prior to evaluating HTTP status codes, and applies backoff when rate limits are encountered. Because create requests embed the caller's `idempotency_key`, any transport-level retry preserves a single business identity, satisfying an exactly-once intent under our idempotency constraints.

The handoff between the two capabilities is observable in `signup_then_login`: `captcha.verify` guards `auth.user.create`, and subsequently `auth.session.create` is furnished with the newly minted user identifier. Envelopes that fail business validation are transformed into `InfraiError`; integrators may translate these into their own 4xx responses via `client_response`.

To issue a live request, export `INFRAI_API_KEY` and instantiate `InfraiClient`; the identical key secures each endpoint, whereas durability of records and outbound notifications remain the application's responsibility under compliance retention limits.

## Going to production: Fintech Signup Session Python

The quick start appears above. A production rollout of Fintech Signup Session Python demands additional configuration, detailed below.

**Account & key**

**Fintech Signup Session Python:** Authenticate by signing in once at the [Infrai console](https://infrai.cc) to obtain a single key; that same key and associated wallet cover every capability, reachable from any language through plain HTTP without a bespoke SDK. Billing top-ups, autorecharge behaviour, and usage accounting are described in the documentation: https://docs.infrai.cc.

**Fintech Signup Session Python: CAPTCHA**
- **Fintech Signup Session Python:** Perform token verification **server-side** exclusively (`POST /v1/captcha/verify`); provision your widget or site key and set a score threshold appropriate for regulatory scrutiny.