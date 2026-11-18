# Campus Event Registration and Waitlist Management System

A full-stack **Python / Django / SQLite** project for Software Design Part 2, Dongshin University, Graduate School of Software Convergence.

Students discover events, reserve a place, or join a waiting list when an event is full. Organizers publish events, manage participant rosters, record attendance, and review totals. The Python backend enforces capacity, permissions, deadlines, duplicate prevention, and first-in-first-out waitlist promotion.

## Current status - 18 November 2026

**Live application: [Campus Events](https://alamshahriya1.pythonanywhere.com/)**

The previously deployed Django application is running on PythonAnywhere with Dongshin University branding and organizer user management. Its **62-test version passed on Linux, Windows, and PythonAnywhere**. The combined **student creation, student-ID login, deactivate/reactivate, and unused-account deletion update passed 110 tests locally on Linux**. The team reported copying the earlier account-creation files to Windows; no new Windows/host test result is recorded. See the [current installation guide](docs/development/STUDENT_ACCOUNT_CONTROLS.md). Hosted browser evidence below belongs to the earlier version and confirms Organizer and Student sign-in, student name editing, personal registrations, cancellation with automatic waitlist promotion, participant rosters, and attendance marking.

The online accounts use private passwords chosen by the team. Ask the project team for Student or Organizer demonstration access; the local development password below does not apply to the hosted site.

See the [hosted verification record](docs/development/HOSTED_VERIFICATION.md), [test report](docs/development/TEST_REPORT.md), and [requirement status](docs/development/IMPLEMENTATION_STATUS.md). The team reports successful phone checks and a demonstration-database restore on Windows. Full Chrome/Edge evidence, separately recorded host-restart persistence, hosted performance, and professor evaluation remain open. The new account forms need their own browser/host checks.

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

Organizers can provision Students through **Manage users → Add student** and manage access through **Edit details → Account access**. Organizer/master accounts are excluded from student controls. Command-line provisioning remains available for the project team; for Students, the username must equal the student number. The [user-management addendum](docs/development/USER_MANAGEMENT.md) maps FR019–FR025 and the revised ID-edit behavior. Public self-registration, email notifications, payments, and calendar synchronization are outside this requirements baseline. The semester Gantt chart remains in the documentation.

## Project documents

| Deliverable | View on GitHub | Editable source |
| --- | --- | --- |
| Software Requirements Specification | [SRS PDF](docs/srs/SRS.pdf) | [SRS Word document](docs/srs/SRS.docx) |
| System diagrams | [Diagram index](docs/diagrams/README.md) · [Diagram PDF](docs/diagrams/System_Diagrams.pdf) | [Diagram sources](docs/diagrams/source/) |
| Requirements Traceability Matrix | [RTM overview](docs/rtm/README.md) · [Baseline CSV](docs/rtm/RTM.csv) | [RTM workbook](docs/rtm/RTM.xlsx) |
| Implementation evidence | [Current status](docs/development/IMPLEMENTATION_STATUS.md) · [Test report](docs/development/TEST_REPORT.md) | [Status CSV](docs/development/IMPLEMENTATION_STATUS.csv) |
| Live demonstration | [Campus Events](https://alamshahriya1.pythonanywhere.com/) · [Hosted verification](docs/development/HOSTED_VERIFICATION.md) | [Deployment and maintenance](docs/development/DEPLOYMENT.md) |
| Developer reference | [API reference](docs/development/API.md) · [Team upload guide](docs/development/TEAM_UPLOAD.md) | Source code and tests |

The SRS and RTM retain their **29 October 2026** baseline. Their original Planned records are preserved; the implementation supplement records newer evidence. The user-management addendum supplies the additional SRS requirements and RTM mapping, including FR022–FR025. Diagrams were prepared on **18 November 2026**. The original Gantt chart is a plan, not a claim of actual completion.

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
