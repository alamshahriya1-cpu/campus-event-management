# Application source

| Directory | Responsibility |
| --- | --- |
| `accounts/` | Login, roles, Student ID accounts, account maintenance and management commands. |
| `events/` | Event lifecycle, discovery and event services. |
| `registrations/` | Seat allocation, FIFO waitlist, cancellation and attendance. |
| `reports/` | Organizer dashboard totals. |
| `common/` | Shared API errors, middleware and backup utilities. |
| `config/` | Django settings, URL routes and WSGI application. |
| `templates/` | Server-rendered pages. |
| `static/` | CSS, JavaScript and public images. |

Run management commands from the repository root, for example
`python manage.py check` or `python manage.py test tests`.
The root launcher adds `src/` to Python's import path. Module names such as
`accounts.models` and `config.settings` remain unchanged.

Private `.env`, the default `db.sqlite3` and collected `staticfiles/` remain
at the repository root. `src/config/settings.py` explicitly distinguishes
the repository root from source assets. These runtime files do not belong in Git.

For a WSGI server, put `src/` on its import path before importing
`config.settings`. See the [migration guide](../docs/development/REPOSITORY_MIGRATION.md)
before updating the existing PythonAnywhere deployment.

[Project README](../README.md) · [Repository layout](../docs/REPOSITORY_LAYOUT.md)
