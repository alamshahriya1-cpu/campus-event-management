# Requirements implementation and evidence status

Revision **2.0**, reviewed **18 November 2026**, against application commit
`b3d900f4ac7c516c086708305f53ebfdebd0422d`.

The main [SRS](../srs/SRS.pdf), [RTM](../rtm/RTM.xlsx) and
[diagrams](../diagrams/System_Diagrams.pdf) now include the current account
features. The unchanged submitted baseline is [archived](../archive/2026-10-29-baseline/).

| Measure | Complete / total | Percentage |
| --- | ---: | ---: |
| Original functional requirements | 18 / 18 | 100.0% |
| Added account requirements | 7 / 7 | 100.0% |
| Current functional requirements | 25 / 25 | 100.0% |
| Non-functional requirements | 2 / 7 | 28.6% |
| Original total scope | 20 / 25 | 80.0% |
| Current total scope | 27 / 32 | 84.4% |

Verified means complete under the documented evidence rule, not professor
sign-off. Each requirement has equal weight; Partial receives no full-completion
credit. Functional rows use inspected source and automated checks. Browser,
hosted security, performance and evaluator criteria are assessed separately.
The saved Linux test result is **110/110 passed in 3.087 s**; this is a separate
test-pass metric. NFR007 accepts the team's reported restore comparison.

The host pulled the account update after a private backup, and the team reported
successful live deletion. An exact new Windows/host 110-test transcript was not
supplied. See the [completion report](../review/COMPLETION_REPORT.pdf),
[evidence register](../review/requirements.json) and
[remaining acceptance record](../review/ACCEPTANCE_RECORD.md).

| ID | Feature | Status | Test family | Evidence |
| --- | --- | --- | --- | --- |
| FR001 | Authentication | Verified | TC001 | E01, E02; E05 |
| FR002 | Sign-out | Verified | TC002 | E01, E02 |
| FR003 | Roles and ownership | Verified | TC003 | E01, E02; E05 |
| FR004 | Create a draft event | Verified | TC004 | E01, E02 |
| FR005 | Controlled event editing | Verified | TC005 | E01, E02 |
| FR006 | Publish an event | Verified | TC006 | E01, E02 |
| FR007 | Browse and filter events | Verified | TC007 | E01, E02 |
| FR008 | Event details and privacy | Verified | TC008 | E01, E02 |
| FR009 | Atomic seat allocation | Verified | TC009 | E01, E02 |
| FR010 | Prevent duplicate registrations | Verified | TC010 | E01, E02 |
| FR011 | Personal history and queue rank | Verified | TC011 | E01, E02; E05 |
| FR012 | Cancel and rejoin | Verified | TC012 | E01, E02; E05 |
| FR013 | FIFO waitlist promotion | Verified | TC013 | E01, E02; E05 |
| FR014 | Cancel an event | Verified | TC014 | E01, E02 |
| FR015 | Organizer participant roster | Verified | TC015 | E01, E02; E05 |
| FR016 | Attendance and audit | Verified | TC016 | E01, E02; E05 |
| FR017 | Organizer dashboard | Verified | TC017 | E01, E02; E05 |
| FR018 | Server validation | Verified | TC018 | E01, E02 |
| FR019 | Search student accounts | Verified | TC026 | E01, E02; E05 |
| FR020 | Edit student details | Verified | TC027, TC030 | E01, E02; E05, E08 |
| FR021 | Reset student passwords | Verified | TC028 | E01, E02 |
| FR022 | Create student accounts | Verified | TC029 | E01, E02; E08 |
| FR023 | Use Student ID for login | Verified | TC030 | E01, E02; E08 |
| FR024 | Deactivate and reactivate | Verified | TC031 | E01, E02; E08 |
| FR025 | Delete an unused student | Verified | TC032 | E01, E02; E08, E09 |
| NFR001 | Response time | Partial | TC019 | E02 |
| NFR002 | Deployed security | Partial | TC020 | E02, E04, E05 |
| NFR003 | Integrity and persistence | Partial | TC021 | E02, E05 |
| NFR004 | Browser and mobile usability | Partial | TC022 | E02, E05, E06 |
| NFR005 | Maintainable setup | Verified | TC023 | E01, E02, E03, E04 |
| NFR006 | Live deployment and evaluator access | Partial | TC024 | E04, E05, E08, E09 |
| NFR007 | Backup and restore | Verified | TC025 | E02, E07, E08 |

## Remaining non-functional acceptance

- **NFR001 (TC019):** Measure 20 warm requests through the deployed URL using 30 events/300 registrations; record environment and show at least 19 below 3 seconds.
- **NFR002 (TC020):** Record current-release hosted Student direct-URL denial and the deployed security checklist, without publishing secrets.
- **NFR003 (TC021):** Compare registrations, statuses, queue and attendance before and after a full PythonAnywhere application reload/restart using a separate session.
- **NFR004 (TC022):** Record Chrome and Edge versions and a 390-pixel viewport; complete core flows and the new account forms with readable controls, errors and timezone labels.
- **NFR006 (TC024):** Give the professor private Student and Organizer access; record independent evaluator flows/reload persistence and recheck hosting expiry before evaluation.
