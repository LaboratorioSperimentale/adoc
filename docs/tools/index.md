---
title: Tools
nav_order: 3
has_children: true
---

# adoc-tools

Scripts for building and maintaining ItCon's construction database: turning
the raw spreadsheet export into per-construction YAML/CoNLL-C files, parsing
example sentences into CoNLL-U, extracting catena skeletons automatically
from grouped examples, and converting CoNLL-C construction definitions into
Grew search patterns. See the [Guide]({% link guide/index.md %}) for the
CoNLL-C format itself (the file this pipeline reads and writes). Source:
[`adoc-tools/`](https://github.com/LaboratorioSperimentale/adoc/tree/main/adoc-tools)
in the repository.

`ItCon/` holds the small, hand-curated, definitive subset of the
constructicon (yaml + conllc, human-reviewed). `data/` is this pipeline's
own working directory — the bulk, auto-generated/draft data these scripts
read and write. The two aren't kept in sync automatically.

## Layout

```
adoc-tools/
  src/          all scripts (flat, no subfolders)
  test-cases/   .conllc / .gq fixture pairs used by tests/test_conll2gq.py
  tests/        pytest suite
```

## Setup

```
pip install -r requirements.txt
pip install conllu pytest   # used by cxns_from_examples.py and the test suite; not in the root requirements file
```

## The pipeline, in order

```
data/db-export.csv
        │  export_into_yaml.py
        ▼
data/constructions/yaml/*.yml  +  data/db_conllc(NON-definitivo)/*.conllc  +  data/db_esempi(NON-definitivo)/*.txt
                                                                          │  examples_into_conllu.py (UDPipe API)
                                                                          ▼
                                                                  data/db_esempi/*.conllu
                                                                          │
                                                                          ▼  (manually concatenated into one file)
                                                                  data/examples/examples.conllu
                                                                          │  cxns_from_examples.py
                                                                          ▼
     data/output/catenae_ranking.txt + data/output/catenae_ranking_rank1.conllu + data/constructions/conllc/*.conllc
                                                                          │  conll2gq.py
                                                                          ▼
                                                                  data/output/gq/*.gq
```

Each stage is documented on its own page:

1. [export_into_yaml.py](export-into-yaml) — spreadsheet → YAML + draft CoNLL-C + example stubs
2. [examples_into_conllu.py](examples-into-conllu) — example stubs → parsed CoNLL-U
3. [cxns_from_examples.py](cxns-from-examples) — grouped examples → catena skeletons
4. [conll2gq.py](conll2gq) — CoNLL-C → Grew search patterns

## Tests

```
cd adoc-tools
pytest tests/
```

Currently covers `conll2gq.py` only: every `test-cases/<name>.conllc` is
converted and compared line-for-line against the matching
`test-cases/<name>.gq`. Add a new case by dropping a `.conllc`/`.gq` pair
into `test-cases/` — the test discovers fixtures by filename, nothing else
to wire up.
