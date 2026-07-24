# adoc-tools

Scripts for building and maintaining ItCon's construction database: turning
the raw spreadsheet export into per-construction YAML/CoNLL-C files, parsing
example sentences into CoNLL-U, extracting catena skeletons automatically
from grouped examples, and converting CoNLL-C construction definitions into
Grew search patterns. See `../publications/tutorial/guida.md` for the
CoNLL-C format itself (the file this pipeline reads and writes).

`../ItCon/` holds the small, hand-curated, definitive subset of the
constructicon (yaml + conllc, human-reviewed). `../data/` is this pipeline's
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
pip install -r ../requirements.txt
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

## Scripts

### `export_into_yaml.py`

Entry point of the pipeline. Reads the construction spreadsheet export (CSV)
and, for every row, writes a YAML file (`data/constructions/yaml/cxn_<id>.yml`),
a draft CoNLL-C skeleton with just the header fields filled in
(`data/db_conllc(NON-definitivo)/cxn_<id>.conllc` — still needs a human to
fill in the actual construction rows, see `guida.md`), and one raw example
text stub per example sentence
(`data/db_esempi(NON-definitivo)/cxn_<id>_example_<n>.txt`). Also fuzzy-matches
each row's free-text formal/functional tags against `cc-database/cc-database.yaml`
comparative-concept IDs (Levenshtein distance ≤ 2).

Run from the repo root:

```
python3 adoc-tools/src/export_into_yaml.py data/db-export.csv
```

Flags (`--cc-database`, `--yml-out`, `--conllc-out`, `--examples-out`) override
the defaults shown above if you want to write somewhere else — see `--help`.

### `examples_into_conllu.py`

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

### `cxns_from_examples.py`

The catena-extraction engine. For every construction with more than one
example sentence in `data/examples/examples.conllu`, finds the catena
(connected dependency subgraph) common to every example, using
structural-signature matching so word-order variation (e.g. proclitic vs.
enclitic Italian clitics) doesn't block a match. Two scores are computed per
candidate match: a background log-likelihood score (how distinctive this
catena is versus the rest of the corpus) and a length+lexicalization score,
shown side by side. The winning match per construction is then greedily
expanded outward as far as every example sentence still agrees.

Reads `data/constructions/yaml/` (for construction names) and
`data/examples/examples.conllu` (all example sentences, one file — currently
assembled by hand from `data/db_esempi/*.conllu`; there's no script for that
concatenation step yet). Writes:

- `data/output/catenae_ranking.txt` — human-readable ranking (both scores,
  base + expanded catena per candidate) for every construction
- `data/output/catenae_ranking_rank1.conllu` — the winning, expanded catena
  per construction, as CoNLL-U (all constructions in one file)
- `data/constructions/conllc/<cxn_id>.conllc` — the same winning catena as a
  proper CoNLL-C table (FORM/LEMMA/UPOS/FEATS each independently resolved to
  `_` or a fixed value, `LinearOrder=Variable` in MISC where word order isn't
  consistent across examples) — **one file per construction**, directory
  cleared of stale `.conllc` files at the start of each run

Must be run from `adoc-tools/src/` (its paths are relative to its own
location, not the repo root):

```
cd adoc-tools/src
python3 cxns_from_examples.py
```

Config (corpus/output paths, catena length bounds, how many ranked
candidates to show) is a block of constants at the top of the file, not CLI
flags. Internals live in the two modules it imports, both vendored from the
`Catenae` repo's dependency-free catena extraction:

- `common_catenae.py` — `recursive_catenae_extraction` (the core algorithm:
  every connected subgraph of a dependency tree, up to a size bound) and
  admission filters
- `conllc_extraction.py` — structural-signature matching
  (`catena_signature`, `canonical_order`) and CoNLL-C table construction
  (`build_conllc_table`)

### `conll2gq.py`

Converts CoNLL-C construction files into Grew search patterns
(`pattern { ... }`, see [grew.fr/doc/request](https://grew.fr/doc/request/))
for searching UD treebanks via [Grew Match](https://universal.grew.fr/).
Handles FORM/LEMMA/UPOS/FEATS node constraints (with disjunction, negation,
regex), HEAD/DEPREL edges (including `root:X` external attachment), and the
IDENTITY/ADJACENCY/EXCLUSION CoNLL-C extensions described in `guida.md`.
SEM_FEATS/SEM_ROLES/REQUIRED and sub-word morphological rows (`A-1`) have no
plain-UD Grew equivalent and are reported as `% WARNING` comments in the
output rather than silently dropped.

Accepts two `.conllc` header dialects: `# fields = ID UD.FORM LEMMA UPOS ...`
and `cxns_from_examples.py`'s own `# ID\tFORM\tLEMMA\t...` — see
`test-cases/own_generator_dialect.*` for an example of the latter.

Run with no arguments to convert every `.conllc` file in
`data/constructions/conllc/` into a matching `.gq` file (same basename) in
`data/output/gq/` (cleared of stale `.gq` files first):

```
python3 adoc-tools/src/conll2gq.py
```

Pass explicit `<conllc_dir> <gq_dir>` arguments to convert somewhere else.
Run with `--self-test` instead to check every fixture in `test-cases/`
against its expected `.gq` output and print PASS/FAIL per case (the real
test suite is `tests/test_conll2gq.py`, see below). Import `convert_file` /
`convert_directory` from this module to convert programmatically.

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
