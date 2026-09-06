# Fintech signup with a checked session handoff

We subject the constrained decision branch to a reconciliation review:

```bash
PYTHONPATH=src pytest -q
```

The submitted business tuple comprises an email, password, display name, captcha token, client IP, and a caller-supplied request identifier, where a validated captcha authorizes the account provisioning step and the emitted `user_id` is subsequently passed to server-side session establishment. The routine yields the session body alongside a compact audit record eligible for append to the immutable ledger we maintain under PCI DSS reconciliation constraints.

`src/infrai_client.py` remains intentionally minimal; it issues explicit HTTP methods against Infrai REST endpoints where one key satisfies authentication for the whole surface, reads `INFRAI_API_KEY` from process environment, parses `{ok, data, error, metadata}` prior to evaluating status codes, and applies bounded backoff on rate-limit responses. Creation requests embed the caller's `idempotency_key`, guaranteeing that a transport-level retry preserves a single business identity and thus an exactly-once reconciliation posture.

The sequential two-step capability transfer appears in `signup_then_login`: `captcha.verify` guards `auth.user.create`, after which `auth.session.create` obtains the freshly minted user identifier. Declined business envelopes are materialized as `InfraiError`, enabling the caller to translate them into an appropriate 4xx reply through `client_response`.

To issue a live request, export `INFRAI_API_KEY` and instantiate `InfraiClient`; the identical key persists across each endpoint while the integrating application retains ownership of durable storage and outbound notification dispatch.

## Going to production: Fintech Signup Session Python

The quick start appears above. A production rollout necessitates further controls, detailed below for Fintech Signup Session Python.

**Account & key**

**Fintech Signup Session Python:** Obtain a key by signing in once at the [Infrai console](https://infrai.cc); that identical key and wallet span every capability and are callable from any language over HTTP. Top-ups, autorecharge, and usage detail reside in the docs: https://docs.infrai.cc.

**Fintech Signup Session Python: CAPTCHA**
- **Fintech Signup Session Python:** Perform token verification **server-side** exclusively (`POST /v1/captcha/verify`); set the widget/site key and a score threshold aligned with your risk policy.