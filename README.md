# Campus Event Registration and Waitlist Management System

A full-stack course project for **Software Design Part 2**, Dongshin University, Graduate School of Software Convergence.

The proposed application allows students to discover campus events, register for available places, and join a waiting list when an event is full. Organizers manage events, participant rosters, and attendance. Backend services enforce capacity, prevent duplicate registrations, and promote the earliest eligible waiting student when a confirmed place is cancelled.

## Project documents

| Deliverable | View on GitHub | Editable source |
| --- | --- | --- |
| Software Requirements Specification | [SRS PDF](docs/srs/SRS.pdf) | [SRS Word document](docs/srs/SRS.docx) |
| System diagrams | [Diagram index and images](docs/diagrams/README.md) · [Diagram PDF](docs/diagrams/System_Diagrams.pdf) | [Diagram sources](docs/diagrams/source/) |
| Requirements Traceability Matrix | [RTM overview](docs/rtm/README.md) · [RTM CSV](docs/rtm/RTM.csv) | [RTM Excel workbook](docs/rtm/RTM.xlsx) |

## Team

| Name | Student ID | Planned responsibilities |
| --- | --- | --- |
| Alam Shahriya | 2677517 | Frontend, event forms, student workflows |
| Hossain Md Miraj | 2677529 | Registration services, database constraints, organizer functions |

Both members share integration, testing, deployment, and presentation responsibilities. Upload ownership is recorded by GitHub commits; the table describes planned development responsibilities.

## Planned features

- Student and Organizer authentication with role-based access.
- Event creation, publication, search, and details.
- Capacity-controlled registration and automatic waiting lists.
- Duplicate prevention and first-in-first-out waitlist promotion.
- Personal registration history and cancellation.
- Organizer rosters, attendance, and summary dashboards.

## Planned technology

| Layer | Technology |
| --- | --- |
| Frontend | HTML, Bootstrap, JavaScript |
| Backend | Python and Django |
| Database | SQLite |
| Deployment target | PythonAnywhere free tier and provider subdomain, subject to verification at deployment |

## Documentation status

This package establishes the requirements and design baseline. It does not include executable application code, test-execution results, or a live deployment. All 25 RTM requirements remain **Planned** until implementation and verification are recorded. Documentation availability must not be interpreted as completion of the software.

The SRS and RTM retain their **29 October 2026** submission date. The diagram package was prepared on **18 November 2026**. The Gantt chart preserves the original planning baseline; actual progress has not been assessed in this documentation update.

## Academic milestones

- Semester begins: **1 September 2026**.
- SRS and RTM submission: **29 October 2026**.
- Final examination and semester end: **17 December 2026**.

## Development workflow

Implement each feature against its requirement ID and acceptance criteria. Record work in meaningful commits, link verification evidence to the RTM test IDs, and update the documentation when an approved requirement changes. Add installation instructions and the live application URL when those deliverables are available.
