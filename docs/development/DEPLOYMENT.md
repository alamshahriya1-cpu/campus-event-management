# Deploy Django on PythonAnywhere

Status: prepared instructions; **no production deployment has been performed**. This step requires a PythonAnywhere account controlled by the team. The GitHub repository is a source repository, not the running application.

PythonAnywhere's Beginner plan currently provides one web app, one worker, a provider subdomain and 512 MiB storage. The free app has a one-month expiry; check its renewal/extension control and expiry before the assessment. Confirm current terms in the linked official documentation. No paid domain is required.

## 1. Prepare the source and account

Upload both application packages to the existing repository first. Create or sign in to a free PythonAnywhere account. Keep passwords and tokens private. In its **Consoles** page, open a Bash console.

```bash
git clone https://github.com/alamshahriya1-cpu/campus-event-management.git
cd campus-event-management
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
python -c "import secrets; print(secrets.token_urlsafe(60))"
```

Choose Python 3.12 for both the console virtual environment and the Web app. If it is not available in your account, select a Python version supported by Django 5.2 and use that same version everywhere; verify the tests before continuing.

## 2. Set private configuration

Use PythonAnywhere's file editor to edit `.env` inside the project. Replace the example secret with the generated value. Set:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-generated-secret-value
DJANGO_ALLOWED_HOSTS=your-actual-hostname.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-actual-hostname.pythonanywhere.com
DJANGO_TRUST_PROXY=True
```

Use the exact hostname assigned to your account, including `.eu.pythonanywhere.com` if applicable. Do not use a wildcard host. `DJANGO_TRUST_PROXY=True` is for PythonAnywhere's trusted proxy, not an arbitrary untrusted reverse proxy. `.env` is loaded by Django and must stay outside source control.

## 3. Create the database and private demonstration accounts

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
python manage.py check --deploy
DJANGO_DEBUG=True python manage.py test tests --noinput
```

When `seed_demo` prompts, choose a strong private demonstration password. Do not use `--local-demo` on the hosted app. Share credentials with the professor privately; do not put them in the public README. Individual passwords can be set with `python manage.py changepassword USERNAME`.

Production tests require secure requests. For the development test suite, run tests with `DJANGO_DEBUG=True python manage.py test tests --noinput` in the console only. This environment variable applies to that single command; leave `.env` set to `False` for the actual Web app. The test runner creates a separate `test_db.sqlite3`, never the live database.

## 4. Configure the Web app

In **Web → Add a new web app**, choose the free assigned subdomain, **Manual configuration**, and Python 3.12. Set the virtualenv path to:

```text
/home/YOUR_USERNAME/campus-event-management/.venv
```

Open the WSGI configuration file linked from the Web tab. Replace its sample content with this, changing `YOUR_USERNAME`:

```python
import os
import sys

project = '/home/YOUR_USERNAME/campus-event-management'
if project not in sys.path:
    sys.path.insert(0, project)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

The project loads `.env` from its own directory. Static files are served by the included WhiteNoise middleware after `collectstatic`. Alternatively configure `/static/` to `/home/YOUR_USERNAME/campus-event-management/staticfiles` under PythonAnywhere's static mappings. Turn on **Force HTTPS**, then **Reload** the Web app.

## 5. Acceptance before sharing

Open the assigned **HTTPS URL from a separate device/session**. Verify login, search, registration, waitlisting, cancellation, promotion, organizer event creation, attendance, and sign-out. Reload the app and verify persisted data. Check Chrome, Edge, and a 390-pixel mobile viewport. Record the date, device/browser, URL, results and any defects in `TEST_REPORT.md`.

Verify no debug tracebacks are shown, run the backup/restore exercise, and note the hosting expiry date. Only then change NFR006/TC024 to Verified and add the actual URL to the repository's About field and README.

## Updating a deployed version

Back up first. Pull reviewed changes with `git pull --ff-only`, activate the virtual environment, install changed requirements, run migrations and `collectstatic`, then reload the app. Do not replace the live database with a developer's database. Confirm critical flows again after deployment changes.

## Official references checked 18 November 2026

- [Deploying an existing Django project](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
- [Free account features and expiry](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/)
- [PythonAnywhere plans](https://www.pythonanywhere.com/pricing/)
- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
