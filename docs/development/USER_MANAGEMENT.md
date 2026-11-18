# Organizer user management

Updated **18 November 2026**. This SRS/RTM addendum records FR019–FR025 and
the revised FR020 acceptance criteria. The submitted **29 October baseline**
is retained. Student creation, ID-based login, access controls, and unused-account
deletion are implemented locally. Windows and hosted acceptance of the combined
update remains pending.

## Student accounts

Sign in as `organizer` and open **Manage users**.

- Choose **Add student**, enter the student's first name, optional last name,
  student ID, optional email, and the initial password twice. Select **Create
  student**. The student ID is also the username, and the role is always Student.
- IDs are text, not numbers: leading zeros and hyphens are preserved. Use
  1–20 ASCII letters or digits, with hyphens or underscores; start with a letter
  or digit. Surrounding whitespace is trimmed. Sign in using the exact saved ID.
- ID and username collisions are rejected case-insensitively, including names
  held by inactive or privileged accounts. Passwords must pass the configured
  Django validators, including the 10-character minimum, and are stored as hashes.
- Share the ID and initial password privately. Passwords are not redisplayed.
- Search by name, current username, ID, or email. Lists have 25 accounts per
  page; four demonstration accounts are not an account limit. A test creates
  30 additional students and checks both pages.

## Change existing logins without replacing accounts

For an existing `student1`–`student4` account, choose **Edit details**, enter
its correct student ID, and save. Saving synchronizes its username to the ID,
including when saving another detail while retaining the same ID. The sidebar
shows the current sign-in ID and explains the change before submission.

The previous username stops working for new sign-ins once it changes. The
password, internal user ID, registrations, queue order, attendance, role,
and active/inactive state remain unchanged. Existing signed-in sessions remain
valid because the account and password hash are unchanged. The Organizer
username and password are unaffected. Install alone does not rename existing
users; the Organizer assigns each account its correct ID through the form.

**Reset password** remains available for normal Student accounts. Both entries
must match and satisfy password validation. A password reset invalidates the
student's existing sessions; an inactive account stays inactive.

Organizers, staff/superusers, mixed business roles, and accounts without a
StudentProfile are not editable through these pages. These protected accounts
also cannot be deactivated, reactivated, or deleted through student controls.
Role changes, public signup, and bulk CSV import are outside this extension.

## Deactivate, reactivate, or delete an unused account

Open **Manage users → Edit details → Account access**.

- **Deactivate account** opens a confirmation page. Confirming blocks sign-in
  and removes that student's stored database sessions. The student is signed out
  on their next request. Their password, ID, registrations, reserved places,
  waitlist entries, and attendance are preserved. Existing waitlist entries remain
  eligible for normal promotion; deactivation does not cancel a registration.
- **Reactivate account** restores sign-in with the same password and current
  sign-in ID. The student must sign in again; stored old session cookies do not
  resume the previous session. Repeating a request for the current state is a
  no-op, not a toggle. Other users' sessions are retained.
- **Review deletion** opens a separate page identifying the account and checking
  its links. To delete an unused student, type the exact displayed Student ID and
  select **Permanently delete account**. This removes the user, profile, membership,
  and their stored sessions. There is no undo button.
- Any registration blocks deletion, including Cancelled registrations and past
  events. Attendance audit references and event creation/cancellation references
  also block deletion. Use deactivation for an account with saved history.

The controls do not act on real accounts merely by installing the update or
visiting a confirmation page. They require an Organizer's confirmed POST.
The session-expiration helper is designed for this project's configured Django
database session backend; changing session storage requires adapting that helper.

## SRS/RTM extension mapping

| Requirement | Acceptance criteria | Test ID | Implementation |
| --- | --- | --- | --- |
| FR019: Organizers shall search and browse student accounts. | Organizer-only navigation and server checks; search by name/login/ID/email; 25 accounts per page; protected target accounts excluded. | TC026 | `accounts/user_views.py`; `templates/accounts/user_list.html`; `tests/test_user_management.py` |
| FR020 (revised): Organizers shall edit student names, IDs, and email addresses. | First name and ID required; lengths validated; duplicate ID/login rejected, including case variants. Username is synchronized to Student ID under FR023. User/profile writes commit together. Password, role, active flags, internal user ID, and registration rows remain unchanged. | TC027, TC030 | `accounts/user_forms.py`; `accounts/student_ids.py`; `accounts/user_views.py`; `tests/test_user_management.py`; `tests/test_student_accounts.py` |
| FR021: Organizers shall reset a student account's password. | Matching validated passwords, hashes only, no password redisplay; old password and old student sessions rejected after reset; other accounts unaffected. | TC028 | `accounts/user_forms.py`; `accounts/user_views.py`; `tests/test_user_management.py` |
| FR022: Organizers shall create additional Student accounts through Manage users. | First name, unique ID, and matching validated password required; optional last name/email. New account is active Student only, with matching username/profile ID. Account, profile, and membership are atomic. Students/anonymous users cannot create accounts. Duplicate/replayed submissions never overwrite an account. | TC029 | `accounts/user_forms.py`; `accounts/user_views.py`; `templates/accounts/user_create.html`; `tests/test_student_accounts.py` |
| FR023: Student IDs shall serve as login usernames for new and updated students. | Text IDs preserve leading zeros and hyphens; login succeeds with the saved ID/password. Saving an existing student's details updates username/profile together; old username fails after a change. Organizer login, passwords, roles, inactive state, user IDs, registrations, queue order, and attendance are preserved. | TC030 | `accounts/student_ids.py`; `accounts/user_forms.py`; `accounts/forms.py`; provisioning commands; `tests/test_student_accounts.py` |
| FR024: Organizers shall deactivate and reactivate normal Student accounts. | Separate confirmation pages and CSRF-protected POSTs set an explicit active state. Inactive accounts cannot sign in; stored student sessions are removed on state transitions, requiring fresh login after reactivation. Passwords, account identity, registrations, waitlist eligibility, and attendance are preserved. Other accounts and master accounts are protected. | TC031 | `accounts/user_views.py`; `accounts/user_lifecycle.py`; `accounts/user_forms.py`; `templates/accounts/user_action.html`; `tests/test_student_lifecycle.py` |
| FR025: Organizers shall permanently delete only unused Student accounts. | Require the exact Student ID typed at confirmation. Reject targets with any registration, attendance audit link, or event creator/canceller reference. Recheck target and links in the write transaction. Profile, user, membership, and session removal commit together; errors roll back all changes. Protect Organizer/staff/superuser/mixed-role accounts. | TC032 | `accounts/user_views.py`; `accounts/user_lifecycle.py`; `accounts/user_forms.py`; `templates/accounts/user_action.html`; `tests/test_student_lifecycle.py` |

FR023 replaces FR020's earlier promise that a username would never change.
This is an explicit requirement change requested by the project team. FR024–FR025
add the team's requested account controls. FR025 permits only unused-account
removal; referenced users remain protected and no historical record is cascaded.

## Routes and transaction behavior

| Route | Methods | Access |
| --- | --- | --- |
| `/organizer/users/` | GET, HEAD | Organizer |
| `/organizer/users/new/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/edit/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/password/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/deactivate/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/reactivate/` | GET, POST | Organizer |
| `/organizer/users/<user_id>/delete/` | GET, POST | Organizer |

These HTML forms use ordinary CSRF-protected POSTs and work without JavaScript.
Successful writes redirect to details, or to the list after deletion. Invalid input returns 400;
missing targets return 404; unauthorized Students get 403; anonymous users are
redirected to login. Other write methods are rejected, GET does not mutate,
and account pages use no-store cache headers. Unexpected fields such as
`username`, `role`, `groups`, `is_staff`, and `is_superuser` are rejected.

Transactions cover validation and all related writes. SQLite's configured
IMMEDIATE transaction serializes writers. Integrity failures roll back the
operation; database lock failures return 503 with Retry-After. Linked-record or
integrity conflicts during lifecycle actions return 409. A failed profile
write leaves no new user/membership and cannot partially rename an existing user.
No new dependencies or database schema migrations are required.

## Verification

**110 automated tests passed on Linux**, Python 3.12.14 / Django 5.2.19, in
**3.087 seconds**. See [student-lifecycle-tests.txt](student-lifecycle-tests.txt).
The 27 new TC031–TC032 tests exercise access changes, session invalidation,
record preservation, unused-account removal, all linked-record blockers, master
account protection, CSRF, confirmation, stale review pages, rollback, and lock
handling. The prior 83 tests include creation/ID validation and normal event,
registration, concurrency, and backup regressions. See the earlier
[student-id-tests.txt](student-id-tests.txt) for the 83-test historical run.
`makemigrations --check --dry-run` reported no changes.

The prior 62-test version passed on Windows and PythonAnywhere. Those historical
runs do not verify this 110-test version. Browser rendering of the new forms and
Windows/host testing remain pending; no new live deployment is claimed.

## Installation and manual acceptance

Follow [STUDENT_ACCOUNT_CONTROLS.md](STUDENT_ACCOUNT_CONTROLS.md). Record environment,
browser, tester, and date for each result:

1. Run all 110 tests in the environment receiving the patch.
2. Create a student with a unique actual/synthetic ID; log in as that student
   in a private window, browse events, and register for an available event.
3. Edit an existing student's ID. Verify old login fails, new login succeeds
   with the same password, and registrations/queue/attendance match the baseline.
4. Try a duplicate ID and a weak/mismatched password; confirm no account is added.
5. Check Organizer login remains unchanged. As a Student, visit
   `/organizer/users/new/` directly and confirm access is rejected.
6. Check the new create/edit forms at a mobile viewport and in Chrome/Edge.
7. In separate Organizer and Student browsers, deactivate the Student. Confirm
   their next protected request/sign-in fails. Reactivate and require a fresh
   sign-in with the unchanged password. Compare registrations and attendance.
8. Create a disposable unused account, review deletion, try a wrong confirmation
   ID, then delete with the correct ID. Verify another account with registration
   history is blocked from deletion, including after it is deactivated.

## Framework references

- [Django authentication](https://docs.djangoproject.com/en/5.2/topics/auth/default/)
- [Django password validation](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/)
- [Django transactions](https://docs.djangoproject.com/en/5.2/topics/db/transactions/)
