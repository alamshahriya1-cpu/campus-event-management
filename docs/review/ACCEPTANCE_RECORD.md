# Remaining acceptance record — fill with observed results

Prepared 18 November 2026. Blank fields are intentionally unverified; no result
is implied. Keep credentials, private database copies and account-sensitive
screenshots outside the public repository. Use synthetic/disposable accounts.

Release / commit: ______  Tester: ______  Date/time/timezone: ______
Live URL: ______  Browser/version: ______  Device/OS: ______  Network: ______

## NFR001 / TC019 — hosted timing

Use the required 30-event/300-registration dataset on a controlled demonstration
or staging instance. Record how the dataset was verified; do not overwrite the
live database to create it. In the browser Network panel, record 20 sequential
event-list request durations after one warm-up request. Record whether timings
include cache and network transfer; use the same method for every request.

Dataset count evidence: ______  Hosting configuration: ______
Timings in seconds (1–20): ______
Requests strictly below 3 s: ____ / 20 (required: at least 19)
Expected / actual / evidence: ______  Result: ______

## NFR002 / TC020 — current hosted security

Use a Student session to open Organizer pages/actions directly, including
`/organizer/users/` and `/organizer/users/new/`. Record denied access. Verify HTTPS,
production deployment checks, missing-CSRF rejection, escaped display text and
password-hash storage without publishing secret values. Automated source checks
already exist; record the current deployed checks separately.

Student URL-denial result: ______  HTTPS/configuration result: ______
CSRF / escaping / hash evidence: ______  Result: ______

## NFR003 / TC021 — host restart persistence

Record current user/event counts, registrations/statuses, queue order and
attendance. Reload the application from PythonAnywhere’s Web tab. Sign in from
a separate browser/session and compare the same data. This check complements
the passing automated atomicity/concurrency tests.

Before: ______  Reload time: ______  After: ______
Comparison / evidence: ______  Result: ______

## NFR004 / TC022 — browser and mobile matrix

Record actual browser versions and the 390-pixel mobile viewport. Test core
browse/register/waitlist/status/cancel flows; labels, KST dates and errors must
be readable. Also test create/edit/ID login, password reset, deactivate/reactivate,
and exact-ID deletion confirmation. Use an unused test account for deletion and
a linked test account to verify blocking. Record each environment separately.

| Environment | Version / device | Core flows | New account forms | Evidence / issues |
| --- | --- | --- | --- | --- |
| Chrome desktop | | | | |
| Edge desktop | | | | |
| Mobile, 390 px | | | | |

Result: ______

## NFR006 / TC024 — evaluator access and deployment

Check the public HTTPS URL and current hosting expiry. Provide Student and
Organizer access privately. From an independent session/device, have the evaluator
register, cancel, perform Organizer actions and reload to confirm saved results.

Expiry rechecked: ______  Private access supplied: ______
Evaluator / device: ______  Actions and persistence: ______
Evidence / issues: ______  Result: ______

## Evidence accepted for complete requirements

NFR007 currently counts the team's reported restore comparison. If the evaluator
needs an independently recorded comparison, repeat it on a separate restored
database, comparing users/events, all statuses, confirmed totals, queue order and
attendance. Never overwrite a running database for the test.

## Updating the status after review

Only mark a requirement Verified when its acceptance criterion has evidence.
Update Status and Evidence in RTM.xlsx, its matching CSV and requirements.json,
then refresh the SRS, completion report and implementation summary together.
The workbook recalculates percentages automatically. Each newly completed NFR
adds 1/32 = 3.125 percentage points to current-scope completion.
