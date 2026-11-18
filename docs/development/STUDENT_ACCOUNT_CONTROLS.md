# Install student account controls

Prepared **18 November 2026**. This cumulative update includes **Add student**,
student-ID logins, **Deactivate/Reactivate**, and **Delete unused account**.
It supersedes Student_ID_Accounts_Update.zip and can be installed whether or not
that earlier patch was copied. The Organizer account remains protected.

**Verification: 110 tests passed locally on Linux in 3.087 seconds.** Windows,
hosted, and interactive browser checks of this update remain pending. There are
no new dependencies or schema migrations. Installation does not change account
names, passwords, active states, or delete any student automatically.

## Windows: install and test

1. Stop the local server with Ctrl+C. Close that Command Prompt and open a fresh
   one so a previous restore-test DJANGO_DB_PATH override is cleared.
2. Open the existing project:

```bat
cd /d B:\ALL\DSU\Project\campus-event-management-main
```

3. Make a private backup using a new filename:

```bat
.venv\Scripts\python.exe manage.py backup_database backups/before-account-controls.sqlite3
```

If the file already exists, choose another filename. Keep the pre-update source
files too, or retain the earlier ZIP/source commit for rollback.

4. Extract **Student_Account_Controls_Update.zip** into a separate folder.
   Copy everything **inside its project folder** into the existing project
   folder containing manage.py. Merge the folders and replace matching files;
   do not replace the whole project directory. The package has **30 project
   files**, plus the outer README_INSTALL.txt. It contains no database, private
   configuration, virtual environment, or real account passwords.
5. Run the full suite:

```bat
.venv\Scripts\python.exe manage.py test tests --noinput
```

Expect **110 tests** and **OK**. Tests use a separate database.

6. Start the local app:

```bat
.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in with the existing local Organizer
credentials. Refresh the page after installation. Your live site is a separate
installation and will not change until you publish and reload it.

## Use the account controls

Open **Manage users → Edit details**. In **Account access**:

| Control | Confirmation and result |
| --- | --- |
| Deactivate account | Review the student, tick confirmation, and submit. Blocks login and signs out stored sessions on the next request. Keeps their password, ID, registrations, reserved places, waitlist entries, and attendance. |
| Reactivate account | Review and confirm. Restores login with the existing password; a fresh sign-in is required. |
| Review deletion | If unused, type the exact Student ID and select Permanently delete account. Removes that account and profile. There is no undo button. |

Any registration prevents deletion, even Cancelled registrations and past events.
Attendance audit links or events created/cancelled by that account also prevent
deletion. Deactivate accounts with history. Deactivation does not cancel
registrations or free reserved places; existing waitlist entries remain eligible
for ordinary promotion. Organizer, staff, superuser, and mixed-role accounts are
excluded from these controls.

The earlier ID features are included: **Add student** creates more accounts,
and saving an existing Student's details makes their Student ID the login
username while retaining their password and records. See
[STUDENT_ACCOUNT_UPDATE.md](STUDENT_ACCOUNT_UPDATE.md) for ID usage.

## Manual checks before publishing

Use a disposable test student for deletion; keep the backup private.

1. Keep Organizer signed in in one browser and a test Student signed in in a
   private window. Deactivate the Student, then refresh their protected page.
   Confirm access and a new sign-in attempt are rejected.
2. Reactivate the Student. Their old browser session must not resume; sign in
   again using the same password. Check their registration and attendance data.
3. Create a disposable Student with a unique test ID. Open Review deletion;
   submitting a wrong ID must fail. Submit the exact ID and confirm the account
   disappears from the list and cannot sign in.
4. Open Review deletion for a Student with registration history. The page must
   explain that deletion is unavailable. The account and records must remain.
5. As a Student, try the Organizer control URLs directly; access must be denied.
   Check that Organizer access still works and other students remain signed in.
6. Check the new pages on mobile and in Chrome/Edge. Record tester, date, device,
   and browser version. Automated HTML tests do not replace these checks.

## Update GitHub and PythonAnywhere

After the local tests pass, upload **only the contents of project/** from this
ZIP to the repository root, retaining subfolders. Do not upload the ZIP or the
outer README_INSTALL.txt. Suggested commit message:

`Add student creation, ID logins and account access controls`

In the existing PythonAnywhere **Bash console**, run each command separately:

```bash
workon campusenv
```

```bash
cd ~/campus-event-management
```

```bash
python manage.py backup_database backups/before-account-controls.sqlite3
```

Choose another filename if this backup exists. Then fetch the committed code:

```bash
git pull --ff-only
```

If Git reports conflicting local changes, stop at that message; do not discard
or reset them. After a successful pull:

```bash
DJANGO_DEBUG=True python manage.py test tests --noinput
```

Expect **110 tests** and **OK**. This DEBUG override applies only to this test
process, leaving the web application's production configuration unchanged.

```bash
python manage.py collectstatic --noinput
```

```bash
python manage.py check --deploy
```

Select **PythonAnywhere → Web → Reload**. Repeat the manual checks on
https://alamshahriya1.pythonanywhere.com/ using a disposable test account for
deletion. Local account changes do not automatically change hosted accounts.
Do not rerun seed_demo or upload a local database over the live one.

## Recovery and evidence

Source rollback does not undo saved ID changes, deactivations, or account
deletions. Reactivate a retained account through the app; recover mistakenly
deleted data from a private backup using [BACKUP_RESTORE.md](BACKUP_RESTORE.md).
Restore to a separate file and verify it before switching databases. A full
database restore also rolls back later changes, so do not overwrite a running
database casually.

The requirement addendum and mapping are in
[USER_MANAGEMENT.md](USER_MANAGEMENT.md) and
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). The original SRS/RTM
baseline files are unchanged. New local evidence is in
[student-lifecycle-tests.txt](student-lifecycle-tests.txt); previous 62-test host
and Windows results do not verify this new version.
