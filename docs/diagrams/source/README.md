# Editable diagram sources

Files 01, 02, 03, 04 and 06 use Graphviz DOT. Render a modified diagram with Graphviz, for example:

```bash
dot -Tpng -Gdpi=180 01_system_architecture.dot -o ../01_system_architecture.png
```

The cancellation sequence uses Python and Matplotlib. From this directory:

```bash
python -m pip install matplotlib
python 05_cancellation_sequence.py
```

The Gantt image is extracted from the original SRS to preserve its baseline dates. Revise the SRS and chart together if the project schedule changes. After editing diagrams, update the combined PDF and check the requirement mappings.
