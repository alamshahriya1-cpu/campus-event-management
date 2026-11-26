# Document generation sources

`../requirements.json` is the canonical revision 2.0 register. It includes all
32 requirements, use cases, model IDs, evidence and 110 current test method names.

- `build_documents.py`: builds `plans/srs/SRS.docx` and `docs/review/COMPLETION_REPORT.docx` with python-docx/Pillow (paths relative to the repository root).
- `build_rtm.mjs`: imports the archived baseline and builds the revised workbook in `plans/rtm/` with `@oai/artifact-tool`, preserving the two tabs and adding formula-based totals. `REVIEW_OUTPUT_DIR` selects an alternate working output folder.
- `../../diagrams/source/build_diagrams.py`: rebuilds model figures and their combined PDF with Graphviz/Matplotlib/ReportLab.

These are documentation generators, not application dependencies. They do not
read the live database or change Django behavior. Word documents were rendered
to the supplied PDFs and checked after generation. If editing the documents
manually, update the canonical register and matching exports to keep traceability.
