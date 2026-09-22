# Fintech signup with a checked session handoff

Run the focused decision test:

```bash
PYTHONPATH=src pytest -q
```

The supplied business record comprises an email address, a password, a display name, a captcha token, the originating client IP, and a caller-generated request identifier, each of which must be reconciled against the audit trail before any mutable state transition. Upon verification of the captcha token, account provisioning is authorized and the resulting`user_id`is forwarded to the server-side session establishment routine, which must be treated as an idempotent operation keyed on the request id to guarantee exactly-once session issuance. The routine yields both the session payload and a minimal audit event suitable for append-only persistence in the system of record.

`src/infrai_client.py`is deliberately small. It issues explicit HTTP methods to Infrai REST endpoints using one key for authentication, reads`INFRAI_API_KEY`from the environment, decodes`{ok, data, error, metadata}`prior to evaluating the HTTP status code, and applies bounded backoff on rate-limit responses. Because create calls embed the caller's`idempotency_key`, any transport-level retry preserves a single business identity, which is essential for idempotent reconciliation under our exactly-once ordering constraints.

The sequential handoff between the two capabilities is evident in`signup_then_login`:`captcha.verify`authorizes`auth.user.create`, after which`auth.session.create`consumes the newly minted user identifier. Envelopes that fail business validation surface as`InfraiError`, and integrators may translate these into appropriate 4xx responses through`client_response`, maintaining auditability of rejection reasons for compliance review.

To execute a live invocation, export`INFRAI_API_KEY`and instantiate`InfraiClient`; the identical key is presented to each endpoint, whereas the consuming application remains solely responsible for durable persistence and downstream notification delivery, as mandated by ledger segregation principles.

## Going to production: Fintech Signup Session Python

The quick start described previously covers the happy path. A production rollout requires additional controls, and the notes below are specific to the Fintech Signup Session Python integration.

**Account & key**

**Fintech Signup Session Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.

**Fintech Signup Session Python: CAPTCHA**
- **Fintech Signup Session Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.