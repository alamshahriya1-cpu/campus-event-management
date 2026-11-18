# Professor review guide

Review copy: 18 November 2026, revision 2.0, source `b3d900f`.

1. Open [COMPLETION_REPORT.pdf](COMPLETION_REPORT.pdf) for completion figures and the evidence rule.
2. Open [SRS.pdf](../srs/SRS.pdf), [RTM.xlsx](../rtm/RTM.xlsx) and [System_Diagrams.pdf](../diagrams/System_Diagrams.pdf).
3. Demonstrate the live site: https://alamshahriya1.pythonanywhere.com/ . Supply Organizer and Student credentials privately.
4. Show the repository: https://github.com/alamshahriya1-cpu/campus-event-management . Explain individual contributions using commits and code walkthroughs, without inventing contribution percentages.
5. Demonstrate a two-seat event, FIFO promotion after cancellation, roster/attendance, Student ID login, account creation/editing, deactivation/reactivation and deletion of a disposable unused account. Show that a linked Student is protected.
6. Trace FR025 → SRS 3.2.25 → UC018 → D03/D08/D09 → TC032 → the lifecycle tests and E02/E09.
7. Review the five Partial NFRs and record actual results in [ACCEPTANCE_RECORD.md](ACCEPTANCE_RECORD.md).

## Accurate progress statement

All **25 functional requirements** are implemented and supported by automated
checks: the original 18 plus 7 account additions. The saved current Linux suite
passes 110 tests. **27/32 total requirements meet the recorded evidence rule
(84.4%)**; the original scope is **20/25 (80.0%)**. Five NFR evidence items remain
Partial. The website is live; latest deletion success is team-reported. Final
presentation, final report and professor acceptance are separate milestones.

The main documents now reflect the new features; the original October baseline
is preserved under `docs/archive/2026-10-29-baseline/`. Requirement coverage,
test-pass percentage and overall acceptance must not be treated as the same metric.

## Update the repository with this documentation package

Extract `Campus_Project_Review_Update.zip`. Copy the contents of its `project/`
folder into your existing project root (the folder with `manage.py`), merging
folders and replacing matching documentation files. Do not delete other files.
This package contains documentation only, plus generators for those documents.

On GitHub, open the repository root → Add file → Upload files. Upload the
contents of `project/`, preserving their subfolders. Do not upload the outer ZIP
or `README_INSTALL.txt`. Suggested commit message:

`Update SRS RTM diagrams and requirements completion report`

After committing, open `docs/srs/SRS.pdf`, `docs/rtm/RTM.xlsx`,
`docs/diagrams/System_Diagrams.pdf` and `docs/review/COMPLETION_REPORT.pdf` on GitHub
to confirm the new versions are present. Check the version/date and the 32 RTM rows.

No PythonAnywhere code deployment, migration, account change or Web reload is
needed for this documentation-only update. If you want the host’s repository
copy to contain the same documents, use your existing Bash console:

```bash
workon campusenv
cd ~/campus-event-management
git pull --ff-only
```

Run each line separately. If Git reports local conflicts, retain them and review
the conflict; do not reset or discard work. Do not reseed or replace the live
database. Documents do not change the application’s accounts or data.
