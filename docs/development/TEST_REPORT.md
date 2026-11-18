# Verification report

**Recorded: 18 November 2026**
**Latest result: all 62 automated tests passed on Linux, Windows, and PythonAnywhere. The HTTPS application is live, and the hosted workflows listed below were demonstrated.**

Live URL: **https://alamshahriya1.pythonanywhere.com/**

## Deployment and hosted verification - 18 November 2026

Application source: GitHub commit `6ff589484c6c09a2d1502517bd7c3717d96b01b1`
(`Add university logo and organizer user management`). The test and browser
evidence was supplied by the team during deployment. Public HTTP checks were
performed independently without account credentials.

| Environment / check | Recorded result | Evidence scope |
| --- | --- | --- |
| Linux, Python 3.12.14, Django 5.2.19 | 62 tests passed in 1.589 s | [Saved test output](user-management-tests.txt) |
| Windows, Python 3.12, Django 5.2.19 | 62 tests passed in 4.059 s | Team terminal screenshot; test database cleanup completed |
| PythonAnywhere, Python 3.12.8, Django 5.2.19 | 62 tests passed in 7.488 s | Team Bash screenshot; command: `DJANGO_DEBUG=True python manage.py test tests --noinput` |
| Host database migrations | All migrations reported OK | Fresh host database, followed by private demo-account seeding |
| Host `collectstatic --noinput` | 7 copied, 6 post-processed | Logo, styles, and JavaScript collected |
| Host `python manage.py check --deploy` | No issues | Production `.env` uses `DJANGO_DEBUG=False`; this is a configuration check |
| Public HTTP / HTTPS | HTTP 302 redirects to HTTPS; HTTPS login returns 200 | Separate unauthenticated HTTP client |
| Static assets | Application CSS, user-management CSS, JavaScript, and university logo return 200 | Correct CSS / JavaScript / PNG content types |
| Anonymous user-management access | Redirects to sign-in | `/organizer/users/` did not expose the account list |

Team browser screenshots confirm Organizer sign-in and the initial dashboard;
listing four student accounts; saving a new name for `student1`; Student sign-in
with the updated name; and viewing the account's two existing registrations.
The name also appeared in the participant rosters, demonstrating that editing
the profile retained the account's registrations.

For **Build Your First Web App**, `student1` cancelled a Confirmed registration.
The organizer roster then showed `student1` Cancelled, `student2` and `student3`
Confirmed, **2/2 Confirmed**, **0 Waitlisted**, and **1 Cancelled**. This verifies
the demonstrated hosted cancellation/promotion path; multi-user ordering and
concurrent requests remain covered by the automated tests.

For **Welcome to Campus**, the organizer marked `student1` attended. The roster
showed **1 Attended**, with an attended marker on the Confirmed registration.
The future event correctly displayed attendance as unavailable before its start.

See [HOSTED_VERIFICATION.md](HOSTED_VERIFICATION.md) for the evidence boundaries
and remaining evaluation checks. Screenshots did not record a full browser/version
matrix or a separate password-reset success/session-invalidation demonstration.

## User-management extension - 18 November 2026

The full suite passed **62 tests in 1.589 seconds**, including 19 new checks for
FR019–FR021. The [recorded output](user-management-tests.txt) includes the
existing event, waitlist, transaction, and Windows SQLite cleanup regressions.
Django system checks passed and no model/migration changes were detected.
See [USER_MANAGEMENT.md](USER_MANAGEMENT.md) for requirements and manual checks.

An earlier Windows run passed **43 tests in 3.226 seconds** after the SQLite
connection-cleanup fix. The later **62-test Windows run** and hosted results
above supersede the earlier pending status. Local screenshots also showed the
university logo and the new Manage users page.

The remaining sections retain the initial 39-test execution record as history.

## Initial 39-test record: version and environment

- Repository baseline: `3cc4593ed1999ddf3dfca17f46fd95731beff3a0` plus the application source supplied in this delivery. No new source commit or remote Actions execution was claimed at preparation time.
- Linux execution environment, Python 3.12.14, Django 5.2.19, SQLite, pinned dependencies in `requirements.txt`.
- Development settings for tests, separate file-backed test database, synthetic records only. Transaction tests use independent database connections and competing threads.
- Automated test password hashing is accelerated with an MD5 hasher override inside test classes only. Runtime settings use Django's default password hashers; the test override is not a production setting.

## Recorded checks

| Check | Result | Scope |
| --- | --- | --- |
| `python manage.py test tests --verbosity 2 --noinput` | 39 passed in 1.285 seconds | Local Django request/service and database tests |
| `python manage.py check` | No issues | Development configuration |
| `python manage.py makemigrations --check --dry-run` | No changes detected | Models match supplied migrations |
| `python manage.py collectstatic --noinput` | Completed | Bundled CSS/JavaScript available for production |
| `DJANGO_DEBUG=False python manage.py check --deploy` | No issues | Configuration check, not an actual HTTPS deployment |
| Initial migrations and `seed_demo --local-demo` | Completed | Fresh SQLite database and synthetic demonstration users/events |
| Combined ZIP extraction and setup | Passed | Fresh source directory: generate configuration, migrate, seed and system check using the existing pinned dependency environment; Windows launcher not executed |
| JavaScript syntax and Markdown links | Passed | Application/preview syntax; repository-relative documentation links |

The [test output](test-results.txt) preserves the run, with internal absolute paths replaced by `<PROJECT_ROOT>` for portability.

## Critical behavior exercised

The tests cover login/logout and role boundaries; Draft creation/edit/publication rules; combined filters and participant privacy; closing-time equality; duplicate requests; rejoining with new queue priority; FIFO order including timestamp ties; rollback after injected promotion/event-cancellation failures; organizer rosters and attendance correction/audit; dashboard totals; malformed/tampered API input; CSRF; output escaping; and rendering of required HTML pages.

Five simultaneous requests for one remaining seat yielded exactly **one Confirmed and four Waitlisted** registrations. Four concurrent requests from the same student produced **one** registration. Reconnecting to the database preserved the saved registration. Backup/restore compared all rows of the user, user-group, profile, event and registration tables and checked database integrity; existing destinations were protected from overwrite.

## TC019 local benchmark

Dataset: **30 events and 300 registrations**. One warm-up request, then 20 sequential event-list requests through Django's in-process test client. No browser/network round trip or hosting latency is included.

- Below 3 seconds: **20/20**.
- Median: **3.53 ms**. Maximum: **6.82 ms**.
- Seconds, in order: `0.006819, 0.003535, 0.003864, 0.003375, 0.003734, 0.003525, 0.003288, 0.003387, 0.003731, 0.003652, 0.00353, 0.003761, 0.003286, 0.003388, 0.003249, 0.00311, 0.003322, 0.003676, 0.003822, 0.00363`.

This is a local regression baseline. It does **not** satisfy the deployed connection/device recording portion of NFR001 by itself. Repeat on the final hosted URL with the stated dataset and record the real connection and hosting configuration.

## Initial browser inspection (historical)

Chrome visually rendered the actual local sign-in page. Student catalog, event details, personal registrations, event editor, organizer roster and dashboard were inspected as read-only HTML fixtures generated from Django's authenticated test client with synthetic data. The catalog was also inspected in a 390px iframe to assess narrow layout.

Those initial fixture checks established appearance only. The later hosted
screenshots now establish the specific interactive workflows recorded above.
They do not establish the entire Chrome, Edge, and genuine mobile acceptance
matrix. A successful HTML response is not a browser interaction test.

## Acceptance still pending

- Complete the remaining live journeys: create/edit/publish/cancel an event, search/filter, a fresh reservation and waitlist join, rejoin, sign-out, validation errors, and direct Student access-denial checks. Automated coverage already passes.
- Record full Chrome, Edge, and 390px/mobile browser checks, including browser versions and device/network details.
- Demonstrate the password-reset form, old-password rejection, and invalidation of an existing student session on the host.
- Reload the host application after recording saved results and verify persistence from a separate session/device.
- Repeat the NFR001 performance measurement and NFR007 backup/restore exercise against the demonstration deployment.
- Give the professor private Student/Organizer access and complete evaluator acceptance. Hosting expiry was observed as **18 December 2026**; recheck and extend before evaluation.
- Add and inspect a GitHub Actions workflow if remote CI evidence is required. The current source commit has no workflow; successful console runs do not establish CI execution.

The Windows application was started manually after Windows blocked the batch
launcher. Manual Windows setup succeeded; successful launcher execution is not
claimed.

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the requirement-level distinction between local evidence and acceptance still pending.
