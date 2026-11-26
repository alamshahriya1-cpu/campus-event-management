# Repository layout

Layout prepared 25 November 2026 from commit
`208722a3830c1b507c22892af4e672654f97c072`.

The classroom sketch clearly identifies **Project → plans**. The repository
root is Project. The remaining names are a practical organization for this
project; the lower handwritten labels were not legible.

## Folder map

| Repository-relative path | Contents |
| --- | --- |
| [plans/](../plans/README.md) | Planning index. |
| [plans/srs/](../plans/srs/README.md) | Current SRS PDF and Word document. |
| [plans/rtm/](../plans/rtm/README.md) | Current RTM workbook and CSV. |
| [plans/raci/](../plans/raci/README.md) | Two-member RACI workbook, PDF and image. |
| [plans/schedule/](../plans/schedule/README.md) | Schedule notes and canonical D07 Gantt links. |
| [src/](../src/README.md) | Application source, configuration, templates and assets. |
| `src/accounts/` | Roles, sign-in, student identity and account management. |
| `src/events/` | Event lifecycle, discovery and validation. |
| `src/registrations/` | Seat allocation, queue promotion and attendance. |
| `src/reports/` | Organizer dashboard and totals. |
| `src/common/`, `src/config/` | Shared services, Django settings, URLs and WSGI. |
| `src/templates/`, `src/static/` | HTML templates and source CSS, JavaScript and images. |
| `tests/` | Application, database and transaction tests. |
| `scripts/` | Local setup and optional preview tooling. |
| [docs/diagrams/](diagrams/README.md) | D01–D10, combined PDF and diagram sources. |
| [docs/development/](development/QUICK_START.md) | Setup, operations, API and test evidence. |
| [docs/review/](review/REVIEW_GUIDE.md) | Completion/acceptance records and document generators. |
| [docs/archive/](archive/2026-10-29-baseline/README.md) | Unchanged original submitted baseline. |
| `manage.py`, `run_local.bat`, `requirements.txt` | Root launchers and Python dependencies. |

## Moves and runtime paths

| Previous path | Current path |
| --- | --- |
| `docs/srs/` | `plans/srs/` |
| `docs/rtm/` | `plans/rtm/` |
| `docs/raci/` | `plans/raci/` |
| `accounts/`, `events/`, `registrations/`, `reports/` | Corresponding directories under `src/` |
| `common/`, `config/`, `templates/`, `static/` | Corresponding directories under `src/` |

Run management commands from the repository root as before. `manage.py` adds
`src/` to the Python module search path. Imports such as `accounts.models`
retain their names; database table names, migration labels and website URLs do
not change. `src/config/settings.py` keeps `BASE_DIR` at the repository root and
uses `SOURCE_DIR` for templates and static source files.

The private root `.env`, `db.sqlite3`, `backups/`, `.venv/` and generated
`staticfiles/` are not moved or included in the public repository. A configured
`DJANGO_DB_PATH` remains in effect. Existing account and event data must be kept.

## Documents and evidence

Each current deliverable has one canonical location. SRS/report references and
RTM source-file mappings now use `src/`; requirement IDs, acceptance statuses,
completion percentages and the 18 November evidence baseline are unchanged.
The archived baseline and all RACI assignments remain unchanged.

- `docs/review/source/build_documents.py` writes the SRS to `plans/srs/SRS.docx`;
  the completion report stays in `docs/review/`.
- `docs/review/source/build_rtm.mjs` defaults to `plans/rtm/`.
- `docs/review/requirements.json` remains the shared requirements register.
- System models and the Gantt stay in `docs/diagrams/`. Their logical modules and
  relationships are unchanged by moving the source files.

## Apply and deploy

Use the reviewed `refactor/repository-layout` branch. Review the moves and run
checks in the [migration guide](development/REPOSITORY_MIGRATION.md) before
merging. Do not upload an older source or document package over this layout.

This is an application path change. An existing PythonAnywhere web app needs a
one-time **external WSGI import-path update and Reload**. Its URL, virtualenv,
static mapping and private database can stay in place. No database schema
change or account reseeding is required for this refactor.

[Project README](../README.md) · [Planning index](../plans/README.md)
