> **Historical upload instructions.** The repository has since moved to `src/` and `plans/`.
> For current work, clone the repository and follow [the layout migration guide](REPOSITORY_MIGRATION.md).
> Do not re-upload the old two-part source packages; their paths would recreate the previous layout.

# Upload the application in two parts

Historical guide for the initial application upload. For the current
documentation folders, start with the [planning index](../../plans/README.md)
and [repository layout](../REPOSITORY_LAYOUT.md). The existing application is
already combined; the steps below record the original handoff.

These packages add code to `alamshahriya1-cpu/campus-event-management`. **Both uploads are required.** Keep the existing SRS, RTM and diagrams in place.

## Shahriya - first upload

1. Download and extract `Shahriya_Application_Upload.zip`.
2. Open the repository's **Code** tab at its top level, where `README.md` and `docs` are visible.
3. Choose **Add file > Upload files**. Drag the extracted package's **contents** into the area. Do not drag the ZIP or an enclosing folder.
4. Check `manage.py`, `requirements.txt`, `run_local.bat`, `config/`, `templates/`, `static/`, `scripts/`, and `docs/development/`. Include `.env.example` and the updated `.gitignore`; `.env.example` contains placeholders, not a real secret.
5. Review and commit using **Add Django interface, configuration and setup guides**.

This supplies the interface, configuration and documentation. It cannot run until Miraj's backend is uploaded.

## Miraj - second upload

1. Sign in with `hossainmdmiraj923-cmd` and open the same repository using collaborator access.
2. Download and extract `Miraj_Application_Upload.zip`.
3. At the repository root, choose **Add file > Upload files** and drag the extracted contents into the area.
4. Check `accounts/`, `events/`, `registrations/`, `reports/`, `common/`, `tests/` and `.github/workflows/tests.yml`. Include all migrations and `__init__.py` files, even empty ones.
5. Review and commit using **Add Django backend, migrations and acceptance tests**.

The packages have no overlapping paths. Each member should review and understand their files and accurately describe their contribution. Upload from your own account.

## Verify the combined repository

Open **Actions > Django application tests** and inspect the latest run. Expect green after the second upload; do not claim a remote pass until you see it. A partial first upload is not runnable.

Confirm `manage.py`, `requirements.txt`, the application folders, `templates`, `static`, and `tests` exist at the top level. Open the README's SRS, diagrams, RTM and status links; existing documents should remain available.

Follow [QUICK_START.md](QUICK_START.md) to download the combined repository, extract it, and run `run_local.bat`. The next external milestone is live deployment, covered in [DEPLOYMENT.md](DEPLOYMENT.md).

## Upload troubleshooting

Use paths such as `accounts/models.py`, not `Miraj_Application_Upload/accounts/models.py`. If an enclosing folder appears, remove it from the pending upload and select its contents instead. If the browser ignores an empty file or hidden folder, use **Add file > Create new file** with the exact path and content. An empty `__init__.py` may contain `# Python package.`.

Do not upload `.venv`, `.env`, databases, backups, temporary previews or login tokens. No existing repository files need to be deleted.
