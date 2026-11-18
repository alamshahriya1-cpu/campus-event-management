# Campus Event Registration and Waitlist Management System

A full-stack **Python / Django / SQLite** project for Software Design Part 2, Dongshin University, Graduate School of Software Convergence.

Students discover events, reserve a place, or join a waiting list when an event is full. Organizers publish events, manage participant rosters, record attendance, and review totals. The Python backend enforces capacity, permissions, deadlines, duplicate prevention, and first-in-first-out waitlist promotion.

## Current status - 18 November 2026

The first executable version is implemented. **39 automated local tests passed**, including competing requests for the final seat and transaction rollback. Django's production configuration check passed. **The application has not yet been deployed to a public URL.** Live hosting, complete Chrome/Edge user journeys, and final assessment acceptance are pending.

See the [test report](docs/development/TEST_REPORT.md) and [requirement implementation status](docs/development/IMPLEMENTATION_STATUS.md) for local evidence and outstanding checks.

## Run on Windows

1. Install Python 3.12, including the Python launcher.
2. Download this repository using **Code > Download ZIP**, then **Extract All**.
3. In the extracted folder containing `manage.py`, double-click **`run_local.bat`**.
4. Open **http://127.0.0.1:8000/** after setup finishes.

On a fresh local database, sign in as `organizer` or `student1` through `student4`, using the development password `CampusDemo!2026`. These are synthetic local accounts. Hosted accounts must have different, private passwords. Keep the command window open while using the app.

[Complete setup and demo](docs/development/QUICK_START.md) | [Deployment](docs/development/DEPLOYMENT.md) | [Backup and restore](docs/development/BACKUP_RESTORE.md)

## Implemented workflows

- Session login/logout with Student and Organizer roles.
- Event drafts, controlled editing, publication, and cancellation with a reason.
- Search by title/venue; category and event-date filters.
- Atomic seat allocation, duplicate prevention, and an ordered waitlist.
- Personal history, current queue rank, cancellation, and automatic promotion.
- Organizer rosters, attendance marking/correction, and summary dashboards.
- Server validation, CSRF protection, escaped output, and environment-based configuration.
- Migrations, synthetic demo data, backup/restore commands, and automated tests.

Account provisioning uses a management command. Public self-registration, email notifications, payments, and calendar synchronization are outside this requirements baseline. The semester Gantt chart remains in the documentation.

## Project documents

| Deliverable | View on GitHub | Editable source |
| --- | --- | --- |
| Software Requirements Specification | [SRS PDF](docs/srs/SRS.pdf) | [SRS Word document](docs/srs/SRS.docx) |
| System diagrams | [Diagram index](docs/diagrams/README.md) · [Diagram PDF](docs/diagrams/System_Diagrams.pdf) | [Diagram sources](docs/diagrams/source/) |
| Requirements Traceability Matrix | [RTM overview](docs/rtm/README.md) · [Baseline CSV](docs/rtm/RTM.csv) | [RTM workbook](docs/rtm/RTM.xlsx) |
| Implementation evidence | [Current status](docs/development/IMPLEMENTATION_STATUS.md) · [Test report](docs/development/TEST_REPORT.md) | [Status CSV](docs/development/IMPLEMENTATION_STATUS.csv) |
| Developer reference | [API reference](docs/development/API.md) · [Team upload guide](docs/development/TEAM_UPLOAD.md) | Source code and tests |

The SRS and RTM retain their **29 October 2026** baseline. Their original Planned records are preserved; the implementation supplement records newer evidence. Diagrams were prepared on **18 November 2026**. The original Gantt chart is a plan, not a claim of actual completion.

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
| Deployment target | PythonAnywhere free tier/provider subdomain; live verification pending |

JavaScript calls the coded backend; it does not decide allocation or permissions. SQLite writes are serialized inside transactions. A busy database returns a retryable error rather than an uncommitted success.

## Verify

Activate the virtual environment first; on Windows Command Prompt use `.venv\Scripts\activate`.

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --verbosity 2
```

GitHub Actions runs these checks after upload. Inspect its remote result; a local pass does not establish that Actions has run.

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
