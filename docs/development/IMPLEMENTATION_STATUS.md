# Requirement implementation status

Evidence date: **18 November 2026**. The submitted SRS/RTM are preserved as the 29 October baseline. This supplement records the first coded version; it does not certify deployment or professor acceptance.

All 18 baseline functional requirements have implementations and passing local automated tests. The [user-management addendum](USER_MANAGEMENT.md) adds FR019–FR021 with passing local automated tests; Windows/browser acceptance for this extension is pending. Seven non-functional requirements have the evidence and limits below. See [TEST_REPORT.md](TEST_REPORT.md) and [the full source mapping](IMPLEMENTATION_STATUS.csv).

| Requirement | Feature | Test ID | Current evidence |
| --- | --- | --- | --- |
| FR001 | Authentication | TC001 | Implemented - local tests passed |
| FR002 | Sign-out | TC002 | Implemented - local tests passed |
| FR003 | Roles and ownership | TC003 | Implemented - local tests passed |
| FR004 | Create Draft | TC004 | Implemented - local tests passed |
| FR005 | Controlled edits | TC005 | Implemented - local tests passed |
| FR006 | Publication | TC006 | Implemented - local tests passed |
| FR007 | Catalog search/filter | TC007 | Implemented - local tests passed |
| FR008 | Event details/privacy | TC008 | Implemented - local tests passed |
| FR009 | Atomic seat allocation | TC009 | Implemented - local tests passed |
| FR010 | Duplicate prevention | TC010 | Implemented - local tests passed |
| FR011 | Personal history/rank | TC011 | Implemented - local tests passed |
| FR012 | Cancel and rejoin | TC012 | Implemented - local tests passed |
| FR013 | FIFO promotion | TC013 | Implemented - local tests passed |
| FR014 | Cancel event | TC014 | Implemented - local tests passed |
| FR015 | Organizer roster | TC015 | Implemented - local tests passed |
| FR016 | Attendance/audit | TC016 | Implemented - local tests passed |
| FR017 | Dashboard counts | TC017 | Implemented - local tests passed |
| FR018 | Backend validation | TC018 | Implemented - local tests passed |
| FR019 | Student account search and access | TC026 | Extension - local tests passed; browser acceptance pending |
| FR020 | Student detail editing | TC027 | Extension - local tests passed; browser acceptance pending |
| FR021 | Student password resets | TC028 | Extension - local tests passed; browser acceptance pending |
| NFR001 | Response time | TC019 | Partial - local benchmark only |
| NFR002 | Security configuration | TC020 | Partial - local security checks passed |
| NFR003 | Integrity and persistence | TC021 | Local transaction tests passed |
| NFR004 | Browser/mobile usability | TC022 | Partial - layout and render checks |
| NFR005 | Maintainable setup | TC023 | Implemented - local setup verified |
| NFR006 | Free live deployment | TC024 | Pending - not deployed |
| NFR007 | Backup and restore | TC025 | Partial - local restore passed |

## Outstanding acceptance

1. Upload the latest logo and user-management changes; inspect GitHub Actions once the workflow is present.
2. The earlier 43-test version passed on Windows and the logo was visually checked. Rerun the expanded 62-test suite on Windows and complete the new user-management browser demonstration.
3. Deploy the Django backend and frontend under the team's hosting account.
4. Test complete flows in Chrome, Edge and a 390px viewport; verify HTTPS and data persistence.
5. Record deployed performance, backup/restore results and hosting expiry. Share private Student/Organizer access with the professor.

Update this supplement with the actual URL, date and evidence as checks are completed. Do not change a requirement to Verified solely because code exists or a configuration check passes.
