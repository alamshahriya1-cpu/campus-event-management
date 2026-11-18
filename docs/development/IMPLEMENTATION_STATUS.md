# Requirement implementation status

Evidence date: **18 November 2026**. The submitted SRS/RTM retain their
**29 October 2026** baseline. This supplement records implementation and observed
verification; it does not certify professor acceptance.

**Live application: https://alamshahriya1.pythonanywhere.com/**

All 18 baseline functional requirements and seven user-management extension
requirements have implementations and passing automated checks. The latest
**110-test suite passed on Linux**. The previous **62-test version passed on
Windows and PythonAnywhere**; the new version awaits those runs and deployment. Hosted browser
screenshots confirm the specific actions identified below. Remaining acceptance
is retained in the [CSV source mapping](IMPLEMENTATION_STATUS.csv),
[hosted verification record](HOSTED_VERIFICATION.md), and
[test report](TEST_REPORT.md).

| Requirement | Feature | Test ID | Current evidence |
| --- | --- | --- | --- |
| FR001 | Authentication | TC001 | Automated tests passed; hosted sign-in observed |
| FR002 | Sign-out | TC002 | Automated tests passed |
| FR003 | Roles and ownership | TC003 | Automated tests passed; hosted role views observed |
| FR004 | Create Draft | TC004 | Automated tests passed; Windows draft creation observed |
| FR005 | Controlled edits | TC005 | Automated tests passed |
| FR006 | Publication | TC006 | Automated tests passed; Windows publication observed |
| FR007 | Catalog search/filter | TC007 | Automated tests passed |
| FR008 | Event details/privacy | TC008 | Automated tests passed |
| FR009 | Atomic seat allocation | TC009 | Automated tests passed; hosted capacity preserved in promotion |
| FR010 | Duplicate prevention | TC010 | Automated tests passed |
| FR011 | Personal history/rank | TC011 | Automated tests passed; hosted personal history observed |
| FR012 | Cancel and rejoin | TC012 | Automated tests passed; hosted cancellation passed |
| FR013 | FIFO promotion | TC013 | Automated tests passed; hosted promotion passed |
| FR014 | Cancel event | TC014 | Automated tests passed |
| FR015 | Organizer roster | TC015 | Automated tests passed; hosted roster observed |
| FR016 | Attendance/audit | TC016 | Automated tests passed; hosted attendance marking passed |
| FR017 | Dashboard counts | TC017 | Automated tests passed; initial hosted totals observed |
| FR018 | Backend validation | TC018 | Automated tests passed |
| FR019 | Student account search and access | TC026 | Extension - automated tests passed; hosted list observed |
| FR020 | Student detail editing (revised ID synchronization) | TC027, TC030 | Local tests passed; previous hosted name edit observed |
| FR021 | Student password resets | TC028 | Extension - automated tests passed; manual reset acceptance pending |
| FR022 | Organizer student creation | TC029 | Implemented locally - 110-test suite passed; host acceptance pending |
| FR023 | Student ID login | TC030 | Implemented locally - preservation and login tests passed; host acceptance pending |
| FR024 | Student deactivation/reactivation | TC031 | Implemented locally - login/session and record-preservation checks passed; host acceptance pending |
| FR025 | Delete unused student account | TC032 | Implemented locally - confirmation, linked-record protection, permissions, and rollback checks passed; host acceptance pending |
| NFR001 | Response time | TC019 | Partial - in-process benchmark only |
| NFR002 | Security configuration | TC020 | Partial - production configuration and public HTTPS checked |
| NFR003 | Integrity and persistence | TC021 | Partial - transaction tests and hosted saved-state checks passed |
| NFR004 | Browser/mobile usability | TC022 | Partial - desktop evidence and team-reported phone checks; full matrix pending |
| NFR005 | Maintainable setup | TC023 | Implemented - Windows and hosted setup verified |
| NFR006 | Free live deployment | TC024 | Deployed - evaluator acceptance pending |
| NFR007 | Backup and restore | TC025 | Verified by team report - demonstration backup restored locally and compared |

The new requirements and revised FR020 criteria are specified in
[USER_MANAGEMENT.md](USER_MANAGEMENT.md). The original SRS/RTM baseline is
unchanged; this supplement now maps 32 requirements (25 FR and 7 NFR).

## Outstanding acceptance

Install and verify the combined student-account patch on Windows and
PythonAnywhere, following [STUDENT_ACCOUNT_CONTROLS.md](STUDENT_ACCOUNT_CONTROLS.md).
Earlier deployment evidence does not certify the new behavior.


1. Complete remaining hosted journeys and direct Student access-denial cases.
   Record the password-reset and old-session invalidation sequence separately.
2. Record the full Chrome, Edge, and 390px/mobile browser matrix, including versions.
3. Verify saved registrations and attendance after a full Web-app restart and
   from a separate session/device.
4. Measure NFR001 through the actual HTTPS URL with the baseline dataset and
   connection details; retain the private recovery copy from the team-reported NFR007 exercise.
5. Share private Student/Organizer access with the professor and record independent
   evaluation. The free-app expiry was observed as **18 December 2026**; recheck
   and extend it before assessment.

The source containing the logo and user-management changes was uploaded as
`6ff589484c6c09a2d1502517bd7c3717d96b01b1`. The current public commit has no
GitHub Actions workflow, so remote CI is not claimed. The Windows application
was started manually; batch-launcher execution remains unverified.

A requirement stays partial where its complete acceptance criteria have not
been demonstrated. Passing automated tests, successful hosting, and professor
acceptance are recorded as distinct evidence.
