# Organizer user management

Added on 18 November 2026 as an extension to the 29 October SRS/RTM baseline.
The original submitted documents are retained. This addendum records the new
requirements, their implementation, and the remaining acceptance checks.

## Using the feature

Sign in as an Organizer and open **Manage users** in the header.

1. Find a student by name, username, student ID, or email. Results are paginated
   with 25 accounts per page.
2. Select **Edit details**. Change the first name, optional last name, student
   ID, or optional email address, then select **Save changes**.
3. The success message confirms the save. The corrected name and student ID
   also appear in participant rosters.
4. To reset access, select **Reset password**, enter the new password twice,
   and submit. Share it directly with the student. Existing student sessions
   must authenticate again; the organizer remains signed in.

The page maintains existing student accounts. Usernames, roles, active flags,
staff/superuser permissions, account creation, and deletion are not editable.
Existing account provisioning remains the project team's maintenance task.
Organizer accounts and staff/superuser accounts are excluded from this page,
even if they have a Student group. Invalid mixed business roles and accounts
without a student profile are also excluded.

## Requirements and traceability

| Requirement | Acceptance criteria | Test ID | Implementation |
| --- | --- | --- | --- |
| FR019: Organizers shall search and browse existing student accounts. | Only active authorized organizers can access these pages. Students cannot see the navigation item or access another account by changing a URL. Search matches name, username, ID, or email; 25 results per page. Privileged and invalid-role target accounts remain unavailable. | TC026 | `accounts/user_views.py`; `templates/accounts/user_list.html`; `tests/test_user_management.py` |
| FR020: Organizers shall edit student names, IDs, and email addresses. | First name and ID are required. Names are at most 150 characters, IDs 20, email 254. A student ID assigned to another account, including a case variant, is rejected. User/profile writes commit together. Username, password, role, account state, and every registration field remain unchanged. | TC027 | `accounts/user_forms.py`; `accounts/user_views.py`; `templates/accounts/user_edit.html`; `tests/test_user_management.py` |
| FR021: Organizers shall reset a student account's password. | Both entries match and pass configured Django password validation, including the 10-character minimum. Only a hash is stored; forms do not redisplay passwords. The old password and existing student sessions no longer authenticate. Other accounts and the organizer's session are unaffected. | TC028 | `accounts/user_forms.py`; `accounts/user_views.py`; `templates/accounts/user_password.html`; `tests/test_user_management.py` |

## Request handling and data preservation

These are Django-rendered HTML pages with ordinary CSRF-protected form POSTs.
They do not require JavaScript to save account changes.

| Route | Methods | Access |
| --- | --- | --- |
| `/organizer/users/` | GET, HEAD | Organizer |
| `/organizer/users/<user_id>/edit/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/password/` | GET, POST | Organizer |

Successful POSTs redirect to the details page and display a success message.
Invalid submissions return the form with errors (400); missing target accounts
return 404; unauthorized students receive 403; anonymous users go to sign-in.
Write methods other than POST are rejected. GET does not change records.
All three pages send no-store cache headers. Unexpected fields, including
privilege and role fields, are rejected rather than assigned to the model.

Database transactions cover validation and related writes. An integrity conflict
rolls back the edit and shows an error. A locked database returns 503 with a
retry instruction. Editing an ID does not replace the user: registration rows
still point to the same internal user ID, preserving status, attendance, dates,
and FIFO queue position. An inactive student's password reset does not activate
the account.

No new dependencies or database migrations are required. Do not recreate or
reseed the existing database when installing this update.

## Verification

- **62 automated tests passed** locally on Linux with Python 3.12.14 and Django
  5.2.19, including 19 new user-management tests. See
  [the complete run](user-management-tests.txt).
- Django system checks passed; `makemigrations --check --dry-run` reported no
  model changes.
- Tests include CSRF enforcement, organizer/student boundaries, protected target
  accounts, injected transaction failures, duplicate ID prevention, tampered
  fields, escaped output, search/pagination, password validation, session
  invalidation, and unchanged registration rows after a profile edit.
- The expanded **62-test suite passed on Windows in 4.059 seconds** and on
  **PythonAnywhere in 7.488 seconds**. The earlier SQLite cleanup failure did
  not recur in those reported runs.
- On the [live site](https://alamshahriya1.pythonanywhere.com/), the organizer
  listed the four demo students and saved a new name for `student1`. The updated
  name appeared on the list, Student header, and participant rosters. Existing
  registrations were still present after the edit.
- Student sign-in was demonstrated after password-reset instructions. A separate
  hosted reset success, old-password rejection, and session-invalidation sequence
  was not captured, so those manual acceptance items remain open. Automated tests
  cover them. See [HOSTED_VERIFICATION.md](HOSTED_VERIFICATION.md).

### Repeatable acceptance checklist

Use synthetic demo accounts in the environment being evaluated. Record which
environment and browser were used; do not treat the completed subset above as
evidence that every step below has been performed.

1. Run `.venv\Scripts\python.exe manage.py test tests --noinput` in the project
   folder. Expect **62 tests** and **OK**.
2. Start the local app, sign in as `organizer`, and open **Manage users**.
3. Search for `student4`; change its first name to `Updated Demo`, retain its
   existing student ID, and save. Check the name in the event participant roster.
4. Try assigning another student's ID. Confirm an error appears and the existing
   details remain saved. Restore the original demo name when finished.
5. Optional password check: use a strong private test password for `student4`.
   Verify the old password fails and the new one succeeds. The default local
   demo password no longer works for that account after a reset.
6. Sign in as a Student. Confirm **Manage users** is absent and direct access to
   `/organizer/users/` is rejected.
7. Check the pages and navigation in Chrome, Edge, and a 390px mobile viewport.
   Record browser versions and results for the final evaluation.

## Framework references

- Django authentication: https://docs.djangoproject.com/en/5.2/topics/auth/default/
- Password validation and hashing: https://docs.djangoproject.com/en/5.2/topics/auth/passwords/
- Transactions: https://docs.djangoproject.com/en/5.2/topics/db/transactions/
