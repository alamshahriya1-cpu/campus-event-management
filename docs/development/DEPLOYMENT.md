# PythonAnywhere deployment and maintenance

**Live URL: https://alamshahriya1.pythonanywhere.com/**

Deployment recorded on **18 November 2026**, using application commit
`6ff589484c6c09a2d1502517bd7c3717d96b01b1`. The team demonstrated hosted
Organizer/Student sign-in, student name editing, cancellation with promotion,
rosters, and attendance. All 62 automated tests passed on the host. See
[HOSTED_VERIFICATION.md](HOSTED_VERIFICATION.md) for exact results and pending
acceptance. The professor's final evaluation is not yet recorded.

## Saved hosting configuration

| Setting | Value |
| --- | --- |
| PythonAnywhere account | `alamshahriya1` |
| Plan observed during setup | Free Beginner account |
| Hostname | `alamshahriya1.pythonanywhere.com` |
| Source code and working directory | `/home/alamshahriya1/campus-event-management` |
| Virtualenv | `/home/alamshahriya1/.virtualenvs/campusenv` |
| Python version | Python 3.12; console environment reported 3.12.8 |
| WSGI file | `/var/www/alamshahriya1_pythonanywhere_com_wsgi.py` |
| Static URL | `/static/` |
| Static directory | `/home/alamshahriya1/campus-event-management/staticfiles` |
| Database | Project `db.sqlite3`, outside source control |
| Configuration | Private project `.env`; `DJANGO_DEBUG=False` |
| Free web-app expiry observed | **18 December 2026**; check the Web tab for the current value |

The initial setup below is a reproducibility record. For the existing deployment,
use the maintenance instructions near the end. Do not recreate the database or
rerun seeding as part of a normal update.

## 1. Initial Bash setup

In the PythonAnywhere **Bash console**, run each command separately:

```bash
git clone https://github.com/alamshahriya1-cpu/campus-event-management.git
```

```bash
cd ~/campus-event-management
```

```bash
mkvirtualenv --python=/usr/bin/python3.12 campusenv
```

```bash
python -m pip install -r requirements.txt
```

To reactivate this environment in a later console, use `workon campusenv`.
Python 3.12 must also be selected for the Web app.

## 2. Create private production configuration once

The following command generates the secret on the host without displaying it.
It creates `.env` with private file permissions and refuses to overwrite an
existing file. The hostname is specific to this team's deployment.

```bash
python -c "import os,secrets; from pathlib import Path; os.umask(0o077); f=Path('.env').open('x'); f.write('DJANGO_DEBUG=False\nDJANGO_SECRET_KEY='+secrets.token_urlsafe(64)+'\nDJANGO_ALLOWED_HOSTS=alamshahriya1.pythonanywhere.com\nDJANGO_CSRF_TRUSTED_ORIGINS=https://alamshahriya1.pythonanywhere.com\nDJANGO_TRUST_PROXY=False\n'); f.close(); print('Production settings created.')"
```

`config/settings.py` loads this file from the project directory. The deployed
configuration uses `DJANGO_TRUST_PROXY=False`; HTTPS and secure requests were
verified with this setting. Keep `.env` and account passwords private. For a
different hosting account, use its exact assigned hostname and paths.

## 3. Prepare the database, static files, and accounts

Run each command separately:

```bash
python manage.py migrate --noinput
```

```bash
python manage.py collectstatic --noinput
```

```bash
python manage.py check --deploy
```

```bash
python manage.py seed_demo
```

`seed_demo` asks for a private password twice. Input is not echoed. This creates
`organizer` and `student1` through `student4`, initially sharing the chosen
password, plus five upcoming events and one past attendance example. Use a
strong private password that satisfies the configured minimum of 10 characters.
The command protects existing demo accounts from being overwritten.

Hosted accounts must not use the local development password or `--local-demo`.
Reset an individual password when needed:

```bash
python manage.py changepassword organizer
```

An Organizer can reset an existing student's password through **Manage users →
Edit details → Reset password**. Give evaluation credentials directly to the
professor; do not put them in the repository.

Run the development test suite in a separate test process:

```bash
DJANGO_DEBUG=True python manage.py test tests --noinput
```

The prefix applies only to this command. The web app retains `DJANGO_DEBUG=False`
in `.env`. With the recorded configuration, tests use a separate `test_db.sqlite3`
and synthetic data. The observed host result was **62 tests passed in 7.488 s**.

## 4. Configure the Web app

In **Web → Add a new web app**, choose the assigned free subdomain,
**Manual configuration**, and **Python 3.12**. Save the source, working directory,
and virtualenv paths from the table above.

Open the WSGI file linked from the Web tab, replace the sample application with
this configuration, and save:

```python
import os
import sys

project_path = "/home/alamshahriya1/campus-event-management"

if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Save the static mapping `/static/` to the `staticfiles` directory above. Enable
**Force HTTPS**, then use the green **Reload** button. The hosted app runs through
PythonAnywhere's WSGI service; a Bash `runserver` process is not required.

## 5. Demonstration and acceptance

Open the HTTPS URL in a separate browser session. The recorded deployment checks
are in [HOSTED_VERIFICATION.md](HOSTED_VERIFICATION.md). Complete the remaining
Chrome/Edge/mobile flows, application-restart persistence, hosted timing and
backup/restore exercises, and evaluator access before marking full requirements
acceptance complete. The URL can be listed in the README and GitHub About field
while these limits are documented.

The original seed starts the first event with `student1` and `student2` Confirmed
and `student3` Waitlisted. The recorded online cancellation test has already
promoted `student3`; the live data now differs from that initial seed. Attendance
for the past Welcome to Campus example has also been recorded. For another
presentation, create a fresh test event or deliberately establish the scenario
through the normal application rather than overwriting the live database.

## Maintaining access

The setup page showed **18 December 2026** as the free web-app expiry. Check the
current date in **Web**, and use **Run until 1 month from today** to extend it
before expiry. Recheck access before the **17 December 2026** final examination.
No automatic renewal or reminder is assumed.

Keep a private database backup and a separate recovery copy. Follow
[BACKUP_RESTORE.md](BACKUP_RESTORE.md). The hosted recovery exercise remains
pending even though automated backup/restore tests passed on the host.

## Updating the deployed version

In Bash, activate the existing environment:

```bash
workon campusenv
```

```bash
cd ~/campus-event-management
```

For application changes, create a private backup with a new filename first:

```bash
python manage.py backup_database backups/before-update-2026-11-18.sqlite3
```

Pull the reviewed source update:

```bash
git pull --ff-only
```

If Git reports a conflict or local changes, inspect the message before proceeding;
do not discard local files or replace the live database. Install changed
requirements, apply required migrations, collect static files, run relevant
checks, and reload from the Web tab. Recheck affected workflows. Documentation-only
updates do not require database setup, seeding, or an application reload.

## Official references checked 18 November 2026

- [Deploying an existing Django project](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Forcing HTTPS](https://help.pythonanywhere.com/pages/ForcingHTTPS/)
- [Django 5.2 deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
