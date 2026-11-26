# Current system diagrams — revision 2.0

Prepared 18 November 2026 against application source `b3d900f`.

[Combined diagram PDF](System_Diagrams.pdf) · [SRS](../../plans/srs/SRS.pdf) · [RTM](../../plans/rtm/RTM.xlsx)

| ID | Diagram | PNG | SVG | Scope |
| --- | --- | --- | --- | --- |
| D01 | System architecture | [PNG](01_system_architecture.png) | [SVG](01_system_architecture.svg) | Modules, hosting boundary, sessions, static assets and private recovery copies. |
| D02 | Core use cases | [PNG](02_use_cases.png) | [SVG](02_use_cases.svg) | UC001–UC012; student and organizer permissions. |
| D03 | Entity relationships | [PNG](03_entity_relationships.png) | [SVG](03_entity_relationships.svg) | Physical core entities, cardinalities, audit references and deletion protection. |
| D04 | Registration activity | [PNG](04_registration_activity.png) | [SVG](04_registration_activity.svg) | Validation, serialization, duplicate/rejoin behavior and seat/waitlist allocation. |
| D05 | Cancellation and FIFO sequence | [PNG](05_cancellation_sequence.png) | [SVG](05_cancellation_sequence.svg) | One transaction cancels the owned record and promotes the earliest waiter if applicable. |
| D06 | Event lifecycle | [PNG](06_event_lifecycle.png) | [SVG](06_event_lifecycle.svg) | Only Draft, Published and Cancelled are stored states; time-based restrictions are guards. |
| D07 | Schedule and recorded progress | [PNG](07_project_gantt.png) | [SVG](07_project_gantt.svg) | Original planned dates alongside known November evidence and remaining acceptance work. |
| D08 | Student account use cases | [PNG](08_account_use_cases.png) | [SVG](08_account_use_cases.svg) | UC013–UC018 plus the Student ID login relationship to UC001. |
| D09 | Student account lifecycle | [PNG](09_account_lifecycle.png) | [SVG](09_account_lifecycle.svg) | Active/inactive transitions, session expiry and gated unused-account deletion. |
| D10 | Student creation and ID edit sequence | [PNG](10_student_identity_sequence.png) | [SVG](10_student_identity_sequence.svg) | Atomic User/profile/membership creation and identity-preserving edits. |

Each RTM row names its applicable diagram IDs. D07 retains the original planned
bars and distinguishes recorded progress from future review/presentation work;
it is not a measurement of actual effort or a requirement-completion claim.

Account controls are implemented without changing the database schema. The
updated models show stable user identity, username/Student ID synchronization,
session invalidation, retained waitlist eligibility during deactivation and
deletion blocked by any registration or audit reference. No separate Admin role,
Completed event state or Waitlist table has been invented.

Editable sources are in [source/](source/). The combined PDF has an index and
one page per model. The archived original schedule remains under
[docs/archive/](../archive/2026-10-29-baseline/Original_Project_Gantt.png).
