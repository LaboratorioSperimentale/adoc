# Archive

Prior generations of the ItCon extraction/annotation pipeline, kept for
reference and history rather than active use. The current pipeline lives in
`data/` (`db_yaml`, `db_esempi`, `db_conllc`) and `adoc-tools/`.

- `src/` — the earliest version of the toolchain (graph building, corpus
  parsing, an earlier `conllc2gq.py`). Superseded by `adoc-tools/src/`.
- `formalizzazioni/`, `formalizzazioni_gq/`, `examples_grew/` — an
  intermediate generation's construction formalizations and their Grew
  query output. Superseded by `adoc-tools/src/conll2gq.py` +
  `adoc-tools/test-cases/`.
- `graph/` — an earlier snapshot of the constructicon network graph.
- `UD_examples/` — raw UD sample sentences used before `data/db_esempi`
  existed.
- `data/db_esempi_NON-definitivo/`, `data/db_conllc_NON-definitivo/` —
  earlier drafts of `data/db_esempi/` and `data/db_conllc/`.
- `data/export.csv` — an earlier construction-database export, superseded
  by `data/db-export.csv`.
