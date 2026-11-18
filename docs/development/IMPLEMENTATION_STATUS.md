# Requirement implementation status

Evidence date: **18 November 2026**. The submitted SRS/RTM retain their
**29 October 2026** baseline. This supplement records implementation and observed
verification; it does not certify professor acceptance.

**Live application: https://alamshahriya1.pythonanywhere.com/**

All 18 baseline functional requirements and the three user-management extension
requirements have implementations and passing automated checks. The full
**62-test suite passed on Linux, Windows, and PythonAnywhere**. Hosted browser
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
| FR020 | Student detail editing | TC027 | Extension - automated tests passed; hosted name edit passed |
| FR021 | Student password resets | TC028 | Extension - automated tests passed; manual reset acceptance pending |
| NFR001 | Response time | TC019 | Partial - in-process benchmark only |
| NFR002 | Security configuration | TC020 | Partial - production configuration and public HTTPS checked |
| NFR003 | Integrity and persistence | TC021 | Partial - transaction tests and hosted saved-state checks passed |
| NFR004 | Browser/mobile usability | TC022 | Partial - hosted desktop flows observed |
| NFR005 | Maintainable setup | TC023 | Implemented - Windows and hosted setup verified |
| NFR006 | Free live deployment | TC024 | Deployed - evaluator acceptance pending |
| NFR007 | Backup and restore | TC025 | Partial - automated backup/restore passed on host |

## Outstanding acceptance

1. Complete remaining hosted journeys and direct Student access-denial cases.
   Record the password-reset and old-session invalidation sequence separately.
2. Record the full Chrome, Edge, and 390px/mobile browser matrix, including versions.
3. Verify saved registrations and attendance after a full Web-app restart and
   from a separate session/device.
4. Measure NFR001 through the actual HTTPS URL with the baseline dataset and
   connection details; complete NFR007 recovery using a demonstration-database copy.
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
