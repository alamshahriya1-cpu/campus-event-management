# Requirements Traceability Matrix — revision 2.0

- [RTM.xlsx](RTM.xlsx): editable workbook with the original two tabs retained.
- [RTM.csv](RTM.csv): the same 32 requirement rows and 19 mapping/evidence columns.
- [Original baseline](../archive/2026-10-29-baseline/RTM.xlsx): unchanged Planned records.

The **Group Members** tab contains formula-based completion totals. The
**Requirements Traceability Matri** tab retains its original Excel sheet name
and maps each requirement to its SRS section, use case, module/entity, test family,
diagram IDs, source/test files, evidence and remaining acceptance work. Filter
the Status column for Partial to see the five open quality acceptance items.

**25/25 functional requirements are implemented and automatically checked.**
Under the evidence rule, **27/32 total requirements are complete (84.4%)**;
original scope is **20/25 (80.0%)**. All 32 requirements have traceability.
Verified is not instructor approval. NFR007 uses a team-reported manual restore
comparison. The 110-test Linux result is a separate execution metric.

Status is an editable dropdown (Verified / Partial / Planned). Change it only
when supporting evidence changes. Summary formulas update automatically.
Update the corresponding evidence, SRS and report at the same time; a workbook
edit alone does not regenerate the other files.

See [COMPLETION_REPORT.pdf](../review/COMPLETION_REPORT.pdf) for denominators and
[TESTCASE_INDEX.md](../review/TESTCASE_INDEX.md) for the 110 test methods. TC023
and TC024 include manual setup/evaluator acceptance; a TC ID is not necessarily
one executable test method.
