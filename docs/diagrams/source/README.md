# Diagram sources

`build_diagrams.py` rebuilds all 10 revision 2.0 figures and the combined PDF.
Graphviz DOT handles architecture, account use cases, ER, activity and state diagrams;
Matplotlib handles the core actor panels, the two sequences and the schedule.
The D02 DOT file preserves an alternative logical layout; the printed D02
figure uses the more compact Matplotlib actor panels. The script reads only
`docs/review/requirements.json` and does not access application databases.

Run from the repository root with Python containing matplotlib, Pillow and
reportlab, plus the Graphviz `dot` executable:

```bash
python docs/diagrams/source/build_diagrams.py
```

DOT files are editable copies of the current generated figures. For a repeatable
rebuild, also change their corresponding definitions in `build_diagrams.py`.
SVG files preserve vector output; PNG files are convenient for documents.

The original plan is archived. Current D07 bars remain planned dates; recorded
18 November evidence and remaining review work are labeled separately.
