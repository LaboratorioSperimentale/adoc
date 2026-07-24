---
title: cxns_from_examples.py
parent: Tools
nav_order: 3
---

# `cxns_from_examples.py`

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
