# Student creation and student-ID logins

## Current evidence update — revision 2.0, 18 November 2026

The team supplied a successful private pre-update backup and host pull to
`b3d900f4ac7c516c086708305f53ebfdebd0422d`, then reported completing the deployment
and confirmed live deletion was working (E08–E09). The current saved Linux result
is 110/110 passed in 3.087 s (E02). Exact current Windows/host 110-test results and
a complete browser/negative-path acceptance matrix were not supplied.

The main [SRS](../srs/SRS.pdf), [RTM](../rtm/RTM.xlsx) and
[diagrams](../diagrams/System_Diagrams.pdf) are now revision 2.0. The
[completion report](../review/COMPLETION_REPORT.pdf) counts 25/25 functional and
27/32 overall requirements complete (84.4%), with five Partial NFRs. Original
submission files are archived unchanged. Earlier runs and pending statements
below describe their preparation-time state, not a claim that the current
account update is still undeployed.

## Historical preparation and verification record

The current cumulative package is **Student_Account_Controls_Update.zip**.
It includes the earlier Add student/ID-login feature plus deactivation,
reactivation, and unused-account deletion. Follow
[STUDENT_ACCOUNT_CONTROLS.md](STUDENT_ACCOUNT_CONTROLS.md) for current Windows
and PythonAnywhere installation instructions and the **110-test** check.
The earlier Student_ID_Accounts_Update.zip had 83 tests; its saved result remains
in [student-id-tests.txt](student-id-tests.txt).

The Organizer continues to sign in with `organizer`. No schema migration or
extra dependency is needed. Installation does not assign IDs, rename existing
accounts, or reseed the database. There is no bulk import or automatic assignment
of classmates' IDs.

## Use your real student IDs

1. Open **Manage users → Edit details** for the existing account that belongs
   to the student. For example, change the Student ID on your existing account
   to `26677-507` if that is the exact ID you want to use.
2. Select **Save changes**. The displayed **Sign-in ID** becomes `26677-507`.
   The account's password and saved registrations/attendance stay the same.
   Its old `student1` login stops working for new sign-ins.
3. Repeat with the correct IDs for the other existing students. Do not create
   replacement accounts for students whose registrations you want to retain.
4. To add someone new, select **Add student**. Enter their first name, optional
   last name/email, actual student ID, and initial password twice. The ID is
   also the login username; the account automatically has Student access.
5. Share their ID/password privately. Use a private browser window to test a
   student login without replacing your Organizer session.

IDs are text: `26677-507` and `26677507` are different IDs, so use
the exact intended format consistently. Leading zeros are preserved. Choose
each student's actual ID rather than guessing a sequence of classmates' IDs.
The account list uses 25 rows per page, and creation has been tested with
30 additional accounts. Fresh seed data uses DEMO-001 through DEMO-004;
installing this patch does not reseed or silently rename existing users.

The new account controls are available in **Edit details → Account access**.
Use deactivation to preserve history. Permanent deletion is allowed only for
an unused Student account after typing the exact Student ID.

See [USER_MANAGEMENT.md](USER_MANAGEMENT.md) for FR019–FR025 and revised FR020.
The combined update passed 110 tests locally on Linux; Windows, hosted, and
interactive browser verification of that version remain pending.
