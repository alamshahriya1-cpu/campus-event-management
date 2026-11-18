# Backend API reference

All routes use the same Django session as the HTML interface. JSON mutations require `Content-Type: application/json` and a valid `X-CSRFToken`. IDs and roles come from the session/database, never a client-supplied student/status field. Submitted timestamps must include a timezone offset. UI times are labeled KST (UTC+9).

| Method | Route | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/api/events/` | Student / Organizer | Catalog; `q`, `category`, `date` filters |
| POST | `/api/events/` | Organizer | Create a Draft |
| GET | `/api/events/{id}/` | Authorized viewer | Event and own registration status |
| PATCH | `/api/events/{id}/` | Organizer | Edit permitted fields |
| POST | `/api/events/{id}/publish/` | Organizer | Publish a valid Draft |
| POST | `/api/events/{id}/cancel/` | Organizer | Cancel event/registrations; `{"reason":"..."}` |
| POST | `/api/events/{id}/register/` | Student | Register or return existing active status |
| GET | `/api/my-registrations/` | Student | Personal history and queue positions |
| POST | `/api/registrations/{id}/cancel/` | Owning Student | Cancel; promote a waiter when appropriate |
| GET | `/api/events/{id}/participants/` | Organizer | Roster; optional `status` filter |
| PATCH | `/api/registrations/{id}/attendance/` | Organizer | `{"attended":true}` or `false` |
| GET | `/api/reports/dashboard/` | Organizer | Upcoming totals and per-event counts |

Create fields: `title`, `description`, `category`, `venue`, integer `capacity`, `registration_closes_at`, `start_at`, `end_at`. Capacity: 1-200. Server time must precede closing, closing must precede start, and start must precede end. Published events allow descriptive edits only before start. Started/Cancelled events are read-only.

Students cannot view Drafts or participant identities. A Cancelled event remains visible through the student's own history. Date filtering uses the campus timezone.

## Responses and retries

Reads/updates normally return 200; a new registration/event returns 201. Repeated active registration returns its current result without allocating again. Cancellation is idempotent while permitted by its time/state rules.

Errors use `{"error":"Readable message","code":"machine_code"}`: 400 invalid data, 401 no session, 403 role/CSRF, 404 unavailable record, 405 method, 409 conflict, 503 busy database. A 503 includes `Retry-After: 1`. Refresh status before retrying after an uncertain network response.

GET never mutates data. Database constraints and transactions preserve allocation rules across retries. See `tests/test_application.py` and `tests/test_transactions.py` for executable examples.
