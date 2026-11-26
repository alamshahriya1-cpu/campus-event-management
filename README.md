# Campus Event Registration and Waitlist Management System

A full-stack **Python / Django / SQLite** project for Software Design Part 2, Dongshin University, Graduate School of Software Convergence.

Students discover events, reserve a place, or join a waiting list when an event is full. Organizers publish events, manage participant rosters, record attendance, and review totals. The Python backend enforces capacity, permissions, deadlines, duplicate prevention, and first-in-first-out waitlist promotion.

## Current status - 18 November 2026

**Live application: [Campus Events](https://alamshahriya1.pythonanywhere.com/)**

The Django application is live. The host pulled the current account update
(`b3d900f`) after a private backup, and the team reported that deletion is working.
The saved current Linux suite passed **110 tests in 3.087 seconds**. Earlier
Windows and PythonAnywhere runs passed 62 tests; an exact new 110-test transcript
from those environments was not supplied.

The **revision 2.0 SRS, RTM and diagrams** include all current account features.
**25/25 functional requirements** are implemented and supported by automated
checks. Under the documented evidence rule, **27/32 total requirements are
complete (84.4%)**; five non-functional acceptance evidence items remain Partial.
This is not professor sign-off. See the [completion report](docs/review/COMPLETION_REPORT.pdf)
and [review guide](docs/review/REVIEW_GUIDE.md).

Online accounts use private passwords chosen by the team. Ask the team for
Student or Organizer demonstration access; the local development password below
does not apply to the hosted site.

See [hosted verification](docs/development/HOSTED_VERIFICATION.md),
[test evidence](docs/development/TEST_REPORT.md), and
[remaining checks](docs/review/ACCEPTANCE_RECORD.md). The team reports successful
phone use and a demonstration-database restore. Full Chrome/Edge/current account
form records, host-restart persistence, hosted timing, deployed security evidence
and independent professor evaluation still require their stated records.

## Run on Windows

1. Install Python 3.12, including the Python launcher.
2. Download this repository using **Code > Download ZIP**, then **Extract All**.
3. In the extracted folder containing `manage.py`, double-click **`run_local.bat`**.
4. Open **http://127.0.0.1:8000/** after setup finishes.

On a fresh local database, sign in as `organizer` or `DEMO-001` through `DEMO-004`, using the development password `CampusDemo!2026`. These are synthetic local accounts. Hosted accounts must have different, private passwords. Keep the command window open while using the app.

[Complete setup and demo](docs/development/QUICK_START.md) | [Deployment](docs/development/DEPLOYMENT.md) | [Backup and restore](docs/development/BACKUP_RESTORE.md)

## Implemented workflows

- Session login/logout with Student and Organizer roles.
- Event drafts, controlled editing, publication, and cancellation with a reason.
- Search by title/venue; category and event-date filters.
- Atomic seat allocation, duplicate prevention, and an ordered waitlist.
- Personal history, current queue rank, cancellation, and automatic promotion.
- Organizer rosters, attendance marking/correction, and summary dashboards.
- Organizer creation of Student accounts, search, name/ID/email editing, and password resets. Student IDs become login usernames on creation or save; Organizer logins are preserved.
- Organizer deactivation/reactivation of Students, preserving their registrations and attendance. Permanent deletion requires typing the Student ID and is allowed only for accounts with no linked event records.
- Server validation, CSRF protection, escaped output, and environment-based configuration.
- Migrations, synthetic demo data, backup/restore commands, and automated tests.

Organizers can provision Students through **Manage users → Add student** and manage access through **Edit details → Account access**. Organizer/master accounts are excluded from student controls. Command-line provisioning remains available for the project team; for Students, the username must equal the student number. The [current account guide](docs/development/USER_MANAGEMENT.md) maps FR019–FR025 and the revised ID-edit behavior. Public self-registration, email notifications, payments, and calendar synchronization are outside this requirements baseline. The semester Gantt chart remains in the documentation.

## Project documents

| Deliverable | View on GitHub | Editable source |
| --- | --- | --- |
| Software Requirements Specification | [SRS PDF](docs/srs/SRS.pdf) | [SRS Word document](docs/srs/SRS.docx) |
| System diagrams | [Diagram index](docs/diagrams/README.md) · [Diagram PDF](docs/diagrams/System_Diagrams.pdf) | [Diagram sources](docs/diagrams/source/) |
| Requirements Traceability Matrix | [RTM overview](docs/rtm/README.md) · [Current CSV](docs/rtm/RTM.csv) | [RTM workbook](docs/rtm/RTM.xlsx) |
| Implementation evidence | [Current status](docs/development/IMPLEMENTATION_STATUS.md) · [Test report](docs/development/TEST_REPORT.md) | [Status CSV](docs/development/IMPLEMENTATION_STATUS.csv) |
| Live demonstration | [Campus Events](https://alamshahriya1.pythonanywhere.com/) · [Hosted verification](docs/development/HOSTED_VERIFICATION.md) | [Deployment and maintenance](docs/development/DEPLOYMENT.md) |
| Developer reference | [API reference](docs/development/API.md) · [Team upload guide](docs/development/TEAM_UPLOAD.md) | Source code and tests |

The current SRS and RTM are **revision 2.0, 18 November 2026**, with 25 functional
and 7 non-functional requirements, 18 use cases and 10 diagrams. The unchanged
29 October submission is [archived](docs/archive/2026-10-29-baseline/). The Gantt
bars remain the original plan, with recorded progress separately identified.

Additional review files: [completion report](docs/review/COMPLETION_REPORT.pdf),
[test-family index](docs/review/TESTCASE_INDEX.md),
[acceptance record](docs/review/ACCEPTANCE_RECORD.md) and
[review/upload guide](docs/review/REVIEW_GUIDE.md).

## Technology and code organization

| Component | Implementation |
| --- | --- |
| Frontend | Django templates, bundled Bootstrap 5.3.8, CSS, JavaScript |
| Backend | Python 3.12, Django 5.2.19, same-origin JSON APIs |
| Database | SQLite, migrations, constraints, atomic transactions |
| Accounts | `accounts/`: roles, login, profile, provisioning and maintenance |
| Events | `events/`: lifecycle, search, details, state validation |
| Registration | `registrations/`: allocation, cancellation, FIFO, attendance |
| Reports | `reports/`: organizer counts and dashboard |
| Shared code | `common/`: API errors, authentication middleware, database copies |
| Verification | `tests/`: requirement-linked acceptance and transaction tests |
| Hosting | PythonAnywhere free tier, Python 3.12, provider subdomain and HTTPS |

JavaScript calls the coded backend; it does not decide allocation or permissions. SQLite writes are serialized inside transactions. A busy database returns a retryable error rather than an uncommitted success.

## Verify

Activate the virtual environment first; on Windows Command Prompt use `.venv\Scripts\activate`.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --verbosity 2
```

On the production host, use `DJANGO_DEBUG=True python manage.py test tests --noinput` for this development test suite. That prefix applies only to the test process; the web app retains `DJANGO_DEBUG=False`. Tests use a separate database.

The current public source commit does not include a GitHub Actions workflow. Remote CI is not claimed; the recorded runs were executed locally and in the PythonAnywhere Bash console.

## Team and milestones

| Name | Student ID | Review and presentation focus |
| --- | --- | --- |
| Alam Shahriya | 2677517 | Frontend, event forms, student workflows, configuration |
| Hossain Md Miraj | 2677529 | Backend services, constraints, organizer functions, tests |

Both members share integration, testing, deployment, and presentation. Each member should review and understand their assigned files and commit from their own account; upload ownership does not establish independent authorship.

- Semester: **1 September - 17 December 2026**.
- SRS and RTM baseline: **29 October 2026**.
- Final examination: **17 December 2026**.

Keep `.env`, databases, backups, tokens, and private demonstration passwords outside the public repository. The optional `package.json` and `scripts/preview.mjs` support development preview tooling only; Node.js is not needed to run or deploy Django.
## Team responsibilities

- [RACI responsibility matrix](docs/raci/README.md)
- [RACI PDF](docs/raci/RACI_Matrix.pdf)
