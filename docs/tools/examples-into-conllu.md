---
title: examples_into_conllu.py
parent: Tools
nav_order: 2
---

# `examples_into_conllu.py`

Takes the raw example text stubs `export_into_yaml.py` wrote to
`data/db_esempi(NON-definitivo)/` and parses each one through the public
UDPipe API (`italian-isdt-ud-2.17` model), writing the result to
`data/db_esempi/cxn_<id>_example_<n>.conllu`.

Run from the repo root:

```
python3 adoc-tools/src/examples_into_conllu.py
```

Requires network access (calls `https://lindat.mff.cuni.cz/services/udpipe/`).
Input/output folders are hardcoded at the top of the file, not CLI flags.
