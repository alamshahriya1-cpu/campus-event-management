# Professor review guide

Review copy: 18 November 2026, revision 2.0, source `b3d900f`.

1. Open [COMPLETION_REPORT.pdf](COMPLETION_REPORT.pdf) for completion figures and the evidence rule.
2. Open [SRS.pdf](../../plans/srs/SRS.pdf), [RTM.xlsx](../../plans/rtm/RTM.xlsx) and [System_Diagrams.pdf](../diagrams/System_Diagrams.pdf).
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

## Document locations and repository updates

The [planning index](../../plans/README.md) groups the current SRS, RTM, RACI
and schedule. The [repository layout](../REPOSITORY_LAYOUT.md) records the
old-to-new locations. Supporting models and evidence remain under `docs/`.

The folder organization package supplies updated links and generator output
paths. Follow its upload guide, including removal of the three old planning
directories after their replacements are present. Uploading files does not
remove old paths automatically. The earlier `Campus_Project_Review_Update.zip`
predates this layout and would recreate the former locations.

After committing, open `plans/srs/SRS.pdf`, `plans/rtm/RTM.xlsx`,
`plans/raci/RACI_Matrix.pdf`, `docs/diagrams/System_Diagrams.pdf` and
`docs/review/COMPLETION_REPORT.pdf` on GitHub. Confirm that the planning index
links resolve and that the SRS/RTM still describe the same 32 requirements.

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

## Source layout update — 25 November 2026

Planning files now live in `plans/` and application files in `src/`. The RTM
source references and the current SRS/report code paths follow this layout.
This structural change does not close any remaining acceptance item or change
the recorded requirement-completion percentage. See the
[folder map](../REPOSITORY_LAYOUT.md) and
[migration guide](../development/REPOSITORY_MIGRATION.md).
