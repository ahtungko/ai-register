# ApiMail Provider Design

## Goal
Add a new mail provider named `apimail` so the existing registration flows can create inboxes and fetch verification emails through a worker-backed temp-mail API.

## Architecture
The integration will follow the existing `MailProvider` abstraction. A new `ApiMailProvider` will encapsulate mailbox creation and inbox fetching over HTTP, while `util/mail.py` will register and instantiate it based on `mail_provider: apimail`.

## Configuration
`apimail` will support both `config.yaml` and environment variable overrides. Config keys:
- `mail_providers.apimail.worker_url`
- `mail_providers.apimail.domain`
- `mail_providers.apimail.site_password`
- `mail_providers.apimail.prefix`

Environment variables override config values:
- `APIMAIL_WORKER_URL`
- `APIMAIL_DOMAIN`
- `APIMAIL_SITE_PASSWORD`
- `APIMAIL_PREFIX`

## Data Flow
1. `create_temp_email()` POSTs to `/api/new_address` with a generated or configured name and the configured domain.
2. The API returns `address`/`email` plus a bearer token.
3. `fetch_emails()` GETs `/api/mails?limit=20&offset=0` with bearer auth and optional `x-custom-auth`.
4. Messages are normalized into the project's common mail schema.
5. `fetch_email_detail()` resolves from the normalized list because only the list endpoint is specified.

## Error Handling
- Missing `worker_url` or `domain` should fail fast during provider creation.
- Non-2xx responses should raise `MailProviderError` with status/text context.
- Invalid create responses without email/token should raise `MailProviderError`.
- `fetch_emails()` should return normalized empty lists only when the upstream returns an empty list, not on HTTP errors.

## Testing
Focused unit tests will verify:
- environment/config resolution for `apimail`
- mailbox creation request formatting and response parsing
- inbox fetch normalization
- detail lookup behavior
