---
title: conll2gq.py
parent: Tools
nav_order: 4
---

# `conll2gq.py`

Converts CoNLL-C construction files into Grew search patterns
(`pattern { ... }`, see [grew.fr/doc/request](https://grew.fr/doc/request/))
for searching UD treebanks via [Grew Match](https://universal.grew.fr/).
Handles FORM/LEMMA/UPOS/FEATS node constraints (with disjunction, negation,
regex), HEAD/DEPREL edges (including `root:X` external attachment), and the
IDENTITY/ADJACENCY/EXCLUSION CoNLL-C extensions described in the
[Guide]({% link guide/conllc-format.md %}). SEM_FEATS/SEM_ROLES/REQUIRED and
sub-word morphological rows (`A-1`) have no plain-UD Grew equivalent and are
reported as `% WARNING` comments in the output rather than silently dropped.

Accepts two `.conllc` header dialects: `# fields = ID UD.FORM LEMMA UPOS ...`
and `cxns_from_examples.py`'s own `# ID\tFORM\tLEMMA\t...` — see
`test-cases/own_generator_dialect.*` in the repository for an example of the
latter.

Run with no arguments to convert every `.conllc` file in
`data/constructions/conllc/` into a matching `.gq` file (same basename) in
`data/output/gq/` (cleared of stale `.gq` files first):

```
python3 adoc-tools/src/conll2gq.py
```

Pass explicit `<conllc_dir> <gq_dir>` arguments to convert somewhere else.
Run with `--self-test` instead to check every fixture in `test-cases/`
against its expected `.gq` output and print PASS/FAIL per case (the real
test suite is `tests/test_conll2gq.py`). Import `convert_file` /
`convert_directory` from this module to convert programmatically.
