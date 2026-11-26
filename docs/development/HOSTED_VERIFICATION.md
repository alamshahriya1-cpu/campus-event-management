# Hosted verification record

## Current verification — repository layout update

The repository layout update was merged into `main` as commit
`8341805`. Application code is now under `src/`, while SRS, RTM
and RACI documents are under `plans/`.

| Verification | Result |
| --- | --- |
| Windows automated tests | 110 tests passed in 5.015 seconds |
| PythonAnywhere automated tests | 110 tests passed in 12.048 seconds |
| PythonAnywhere deployment check | No issues identified |
| Migration consistency check | No changes detected |
| PythonAnywhere static collection | 7 files copied; 6 post-processed |

Evidence: team-provided Windows and PythonAnywhere terminal
screenshots. After the deployment update, the team confirmed
that the live website and existing student, event and
registration data were working correctly.

These results supersede the earlier test-run summaries below.
Earlier dated sections remain as historical records.
The SRS/RTM requirement acceptance statuses and completion
percentages have not been recalculated by this update.

## Historical evidence baseline — revision 2.0, 18 November 2026

The team supplied a successful private pre-update backup and host pull to
`b3d900f4ac7c516c086708305f53ebfdebd0422d`, then reported completing the deployment
and confirmed live deletion was working (E08–E09). The current saved Linux result
is 110/110 passed in 3.087 s (E02). Exact current Windows/host 110-test results and
a complete browser/negative-path acceptance matrix were not supplied.

The main [SRS](../../plans/srs/SRS.pdf), [RTM](../../plans/rtm/RTM.xlsx) and
[diagrams](../diagrams/System_Diagrams.pdf) are now revision 2.0. The
[completion report](../review/COMPLETION_REPORT.pdf) counts 25/25 functional and
27/32 overall requirements complete (84.4%), with five Partial NFRs. Original
submission files are archived unchanged. Earlier runs and pending statements
below describe their preparation-time state, not a claim that the current
account update is still undeployed.

## Historical preparation and verification record

## Later team confirmation and pending account update

On 18 November, Shahriya reported that he and Miraj checked the website on their
phones successfully. Phone/browser models and versions were not recorded.
Screenshots then showed PythonAnywhere creating `backups/final-check.sqlite3`
and `backups/restored-check.sqlite3`, followed by the Windows local server on
port 8001. After being asked to compare accounts, events, registration states,
queue order, and attendance, the team reported "all done". The manual recovery
exercise is team-verified; no independent database row comparison was performed.
The full host-restart comparison was not separately evidenced.

The combined **Add student, ID-based login, deactivate/reactivate, and unused
account deletion extension** passed 110 tests locally on Linux. The team reported
copying the earlier creation/ID files to Windows, but no subsequent test result
was supplied. The latest package has not been verified on Windows/PythonAnywhere
or in a browser. Earlier screenshots and the 62-test hosted run below belong to
the previous version. See [STUDENT_ACCOUNT_CONTROLS.md](STUDENT_ACCOUNT_CONTROLS.md).

## Previous hosted record

**Recorded: 18 November 2026**  
**Application: https://alamshahriya1.pythonanywhere.com/**  
**Application commit: `6ff589484c6c09a2d1502517bd7c3717d96b01b1`**

The complete Django application is reachable on the team's PythonAnywhere free
provider subdomain. This record distinguishes observed deployment results from
remaining course acceptance criteria. The original 29 October SRS/RTM baseline
is unchanged.

## Evidence and method

The team supplied terminal and browser screenshots while performing the setup
and interactive actions. Separate unauthenticated HTTP requests checked public
reachability, static assets, redirects, and response headers. Those requests did
not log in, inspect private records, or exercise authenticated browser controls.

The hosted environment reported Python 3.12.8 and used Django 5.2.19 with pinned
requirements. Production configuration was created with `DJANGO_DEBUG=False`,
an exact allowed hostname, an HTTPS CSRF trusted origin, and a newly generated
private secret. Secret and password values were not part of the recorded evidence.

The screenshots establish the flows below, but do not establish browser versions,
a full Chrome/Edge comparison, a genuine mobile viewport, or the professor's
independent evaluation. Event dates and times in the application are **KST**;
the evidence date above is **18 November 2026** (the demonstration crossed into
19 November in KST).

## Observed results

| Check | Observation | Result |
| --- | --- | --- |
| Database preparation | All initial migrations reported OK; private demo-account seeding completed | Passed |
| Production configuration check | `python manage.py check --deploy` reported no issues | Passed as a configuration check |
| Host automated suite | `DJANGO_DEBUG=True python manage.py test tests --noinput`: 62 tests in 7.488 s, OK; test database destroyed normally | Passed |
| Public HTTPS entry | Root resolves to the sign-in page with HTTP 200 | Passed |
| HTTP redirect | HTTP root returns 302 with Location pointing to the HTTPS root | Passed |
| Static files | App CSS, user CSS, JavaScript, and university PNG each return HTTP 200 | Passed |
| Anonymous account-list access | `/organizer/users/` redirects to sign-in | Passed |
| Organizer session | Organizer dashboard rendered with university logo, 5 upcoming events, 2 confirmed places, 1 waiting, and 0 attendance initially | Observed |
| Student list and name edit | Four student accounts listed; a saved name for `student1` appeared in the list, Student header, and rosters | Passed for the demonstrated edit |
| Student session and history | Student navigation and two existing Confirmed registrations displayed after the profile edit | Observed |
| Cancellation and promotion | First event: `student1` Cancelled; `student2` and `student3` Confirmed; 2/2 Confirmed, 0 Waitlisted, 1 Cancelled | Passed |
| Attendance | Past Welcome to Campus event: `student1` remained Confirmed and was marked Attended; total Attended became 1 | Passed |
| Future-event attendance restriction | Future first event showed attendance Unavailable before its start | Observed |

The seed's first event had one waitlisted account before cancellation. This
checks a real automatic promotion on the hosted app. Multiple-waiter FIFO order,
timestamp ties, concurrent allocation, and injected rollback failures were
covered by the automated suite, not repeated against live user sessions.

## Public response checks

The HTTPS sign-in response returned these headers:

| Header or cookie attribute | Observed value |
| --- | --- |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` |
| X-Frame-Options | `DENY` |
| X-Content-Type-Options | `nosniff` |
| Referrer-Policy | `same-origin` |
| CSRF cookie | `Secure`; `SameSite=Lax` |

No authenticated session-cookie flags were inspected by the independent client.
Successful page loading and header checks are not a complete security audit.
Automated CSRF, role-boundary, escaping, password, and transaction tests passed;
the remaining Student direct-access checks are listed below.

## Remaining acceptance

- Fresh reservation and joining the waitlist through the hosted UI; rejoining
  after cancellation; multi-waiter order demonstration if required by evaluation.
- Hosted event creation, controlled editing, publication, event cancellation,
  search/filter, sign-out, and visible validation/error cases.
- Direct protected-URL access with a Student session, plus user-search and
  negative student-edit validation examples.
- Password reset success, failure with the old password, and invalidation of an
  existing student session. Student sign-in succeeded after reset instructions,
  but the separate reset result and invalidation sequence were not captured.
- Full browser matrix for current Chrome, Edge, and a 390px/mobile viewport,
  recording device, version, network, and usability results.
- Persistence after a full Web-app reload/restart, checked against recorded
  registrations and attendance from a separate session/device.
- NFR001 external timing with 30 events/300 registrations and 20 warm requests.
  The in-process TC019 output is not a network/browser benchmark.
- Retain the private recovery copy and record the team-reported NFR007 manual
  restore result described above; repeat if the evaluated database changes.
- Private Student/Organizer access for the professor and independent evaluator
  acceptance. No credentials have been published or sent on the team's behalf.

## Hosting and source delivery

The Web configuration showed free-app expiry on **18 December 2026**. The team
must check and extend the current expiry before evaluation. No renewal automation
has been created.

The current public source commit contains the SQLite cleanup fix, university
logo, and organizer user management. It does not contain a GitHub Actions
workflow, so remote CI execution is not claimed. This documentation update
records observed results; uploading it is separate from changing application
code or live database records.

See [TEST_REPORT.md](TEST_REPORT.md), [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md),
and [DEPLOYMENT.md](DEPLOYMENT.md).
