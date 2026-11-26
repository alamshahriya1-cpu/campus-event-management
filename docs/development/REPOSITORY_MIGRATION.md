# Migrate the repository layout without recreating the site

Prepared 25 November 2026. This is a structural update, not a new deployment or
a database reset. See the [folder map](../REPOSITORY_LAYOUT.md).

## Local Windows clone

Use the existing clone and the `refactor/repository-layout` branch in GitHub
Desktop. Keep the migration package outside the clone. Its helper checks the
branch, baseline commit and clean tracked files before applying its Git patch;
it does not commit, push, merge or deploy.

After the helper succeeds, review the Changes tab. Git may show a moved file as
a deletion and an addition before commit; check that its destination exists.
Use a virtualenv with the pinned dependencies. From the repository root:

```bat
.venv\Scripts\activate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tests --noinput
```

These commands assume this clone already has a configured local environment.
For a fresh clone only, `run_local.bat` creates its own local environment and
synthetic demonstration database. It does not connect to PythonAnywhere.
If the local `.env` has `DJANGO_DEBUG=False`, open a separate CMD window, run
`set DJANGO_DEBUG=True` for the development tests, then close that window after
testing. Never use a production database as `CAMPUS_TEST_DB`.

Run `run_local.bat` and check login, discovery, registration, organizer rosters
and student management. Existing local private files stay at the root. Commit
with `Organize source and project planning folders`, publish the branch, and
review/merge it into `main` after local checks pass. Changing this local branch
alone does not change the hosted website.

## Existing PythonAnywhere app: one-time transition

Complete this only after the tested branch is merged into `main`. Keep the
existing web app, hostname, virtualenv and database. Do not rerun `seed_demo`.

### 1. Record the old revision and take a private backup

In the existing Bash console:

```bash
workon campusenv
cd ~/campus-event-management
git status --short
git rev-parse HEAD
layout_stamp=$(date +%Y%m%d-%H%M%S)
python manage.py backup_database "backups/before-layout-${layout_stamp}.sqlite3"
cp /var/www/alamshahriya1_pythonanywhere_com_wsgi.py "backups/wsgi-before-layout-${layout_stamp}.py"
```

Keep the printed commit hash for recovery. Stop if there are unexplained tracked
changes or the backup fails. Keep a separate private backup too; do not publish
the backup or `.env`.

### 2. Make the external WSGI file support both layouts

In Web, open `/var/www/alamshahriya1_pythonanywhere_com_wsgi.py` and use:

```python
import os
import sys

project_path = "/home/alamshahriya1/campus-event-management"
source_path = project_path + "/src"

# Supports the old root modules and the new src modules during this transition.
for path in (project_path, source_path):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

Save, Reload and check the existing website before pulling the refactor. With
the old layout still on disk, the root path continues to work. Keep the virtualenv
and static mapping. Source-code metadata and the working directory may remain
`/home/alamshahriya1/campus-event-management`.

### 3. Pull the reviewed update and check it

Back in the same Bash console, from the existing project root:

```bash
git pull --ff-only
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

Expected migration result: `No changes detected`. This folder change needs no
new database migrations. If a command fails, stop and keep its output. Do not
delete `.env`, database files or the virtualenv to resolve a path error.

For the automated suite, use a separate test process:

```bash
DJANGO_DEBUG=True python manage.py test tests --noinput
```

The test database is separate from the live database under the saved settings.
The `DJANGO_DEBUG` override affects only that test command.

### 4. Reload the same web app and verify saved data

Use Web → Reload. Check the HTTPS site, both role logins, static styling, event
details, existing registrations, queue order and student management. Compare
saved counts with the pre-update state. Record this as a new hosted check; the
local Linux test result is not a hosted verification result.

The `/static/` mapping continues to point to
`/home/alamshahriya1/campus-event-management/staticfiles`. The private `.env` and
default `db.sqlite3` remain at the repository root.

### Recovery if the new layout does not load

Read the PythonAnywhere error log first. A common transition error is the
external WSGI file still adding only the root path. Correct it and Reload.
If returning to the old code is necessary, and tracked files are clean, run
`git switch --detach OLD_COMMIT_HASH` with the exact hash recorded in step 1,
then Reload. The compatibility WSGI supports the old layout too. This changes
tracked code only; it does not restore, replace or reset the live database.
Return to `main` after the issue is understood and fixed.

## Validation and scope

The migration package includes recorded local verification results. These are
Linux checks of the prepared change; the Windows clone and hosted deployment
must still be checked at their own stages. Requirement evidence, completion
percentages and outstanding acceptance records are unchanged.

[Deployment guide](DEPLOYMENT.md) · [Backup and restore](BACKUP_RESTORE.md)
