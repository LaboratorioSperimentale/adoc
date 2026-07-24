---
title: export_into_yaml.py
parent: Tools
nav_order: 1
---

# `export_into_yaml.py`

Entry point of the pipeline. Reads the construction spreadsheet export (CSV)
and, for every row, writes a YAML file (`data/constructions/yaml/cxn_<id>.yml`),
a draft CoNLL-C skeleton with just the header fields filled in
(`data/db_conllc(NON-definitivo)/cxn_<id>.conllc` — still needs a human to
fill in the actual construction rows, see the [CoNLL-C format guide]({% link guide/conllc-format.md %})),
and one raw example text stub per example sentence
(`data/db_esempi(NON-definitivo)/cxn_<id>_example_<n>.txt`). Also fuzzy-matches
each row's free-text formal/functional tags against `cc-database/cc-database.yaml`
comparative-concept IDs (Levenshtein distance ≤ 2).

Run from the repo root:

```
python3 adoc-tools/src/export_into_yaml.py data/db-export.csv
```

Flags (`--cc-database`, `--yml-out`, `--conllc-out`, `--examples-out`) override
the defaults shown above if you want to write somewhere else — see `--help`.
