# Run the application locally

The application uses Python 3.12, Django 5.2.19 and SQLite. All dependency versions are pinned in `requirements.txt`. Local demo data is synthetic.

## Windows: simplest route

1. Install Python 3.12 from [python.org](https://www.python.org/downloads/). Include the Python launcher during installation.
2. After both code uploads are committed, download the repository with **Code → Download ZIP**, then **Extract All**. You can also use `git clone https://github.com/alamshahriya1-cpu/campus-event-management.git`.
3. Open the extracted project folder containing `manage.py` and double-click `run_local.bat`.
4. Wait for dependency installation and database setup. Open **http://127.0.0.1:8000/**.
5. Sign in as `organizer` or `student1`, `student2`, `student3`, `student4`. The first-run **local-only** password is `CampusDemo!2026`.

Leave the command window open while using the app. Press Ctrl+C there to stop it. Reopening the script preserves the existing database and accounts.

If setup stops, keep the error message and share it with your teammate. The script never deletes the existing database. If you changed the local password, use that new password; the initial demo password will no longer work.

## Manual setup: Windows, macOS or Linux

From the project folder:

```bash
python -m venv .venv
```

Activate the environment with `.venv\Scripts\activate` in Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux. Then:

```bash
python -m pip install -r requirements.txt
python scripts/setup_local.py
python manage.py migrate
python manage.py seed_demo --local-demo
python manage.py runserver
```

Run `seed_demo` once on a fresh database. A repeat attempt refuses to overwrite existing demo accounts. `setup_local.py` creates a random local secret in `.env` without overwriting existing settings. Do not upload `.env`, databases, backups, or `.venv` to GitHub.

## Demonstrate the main business rule

1. Sign in as `student3`. Open **My registrations**: Build Your First Web App shows **Waitlisted**, queue position **1**.
2. Sign out; sign in as `student1`. Open the same event and cancel the confirmed registration.
3. Sign out; sign in again as `student3`. The registration now shows **Confirmed**.
4. Sign in as `student1` again and rejoin the full event. The original record is reused with a new queue time.
5. Sign in as `organizer`. Open the event roster to inspect the results.
6. Open the past **Welcome to Campus** event as organizer. Mark and clear attendance to demonstrate corrections.

The seeded dates are calculated when the command runs. If the demonstration has passed its deadlines, create and publish a fresh event through the organizer interface. Keep historical records.

## Verify the code

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --verbosity 2
```

See [TEST_REPORT.md](TEST_REPORT.md) for the recorded local run, its scope, and remaining acceptance checks. To reset a password without exposing it in command history, run `python manage.py changepassword USERNAME` and follow the private prompts.
