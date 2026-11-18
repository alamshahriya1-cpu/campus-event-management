# Local verification report

**Recorded: 18 November 2026**
**Result: 39 automated tests passed; live deployment acceptance remains pending.**

## Version and environment

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

## Browser inspection

Chrome visually rendered the actual local sign-in page. Student catalog, event details, personal registrations, event editor, organizer roster and dashboard were inspected as read-only HTML fixtures generated from Django's authenticated test client with synthetic data. The catalog was also inspected in a 390px iframe to assess narrow layout.

These checks establish page appearance only. They do not establish authenticated JavaScript journeys in a live browser. Live sign-in, register, cancel, promote and organizer workflows in Chrome, Edge and a genuine mobile viewport remain to be completed by the team. A successful HTML response is not a browser interaction test.

## Acceptance still pending

- Review/commit both upload packages and inspect the remote GitHub Actions run.
- Run the Windows launcher and complete interactive end-to-end browser flows.
- Create the free hosting deployment, verify HTTPS with DEBUG disabled, and share private demonstration access.
- Verify persistence after full host application restart and from an independent session/device.
- Repeat performance and backup/restore checks on the actual demonstration deployment.
- Record hosting expiry/extension and complete the professor's final acceptance demonstration.

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for the requirement-level distinction between local evidence and acceptance still pending.
