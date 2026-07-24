---
title: CoNLL-C field reference
parent: Guide
nav_order: 4
---

# CoNLL-C field reference

A deeper, field-by-field reference for the `.conllc` format introduced in
[The CoNLL-C format]({% link guide/conllc-format.md %}), sourced from the project's
[wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.1.-Conll%E2%80%90X-formalization-guidelines).
The format has 13 fields: **ID**, **FORM**, **LEMMA**, **UPOS**, **FEATS**, **HEAD**, **DEPREL**,
**REQUIRED**, **EXCLUSION**, **SEM_FEATS**, **SEM_ROLES**, **ADJACENCY**, **IDENTITY**.

## LEMMA

For morphological constructions, the lemma at the word level is expressed as a regular
expression, while the lemma(s) for sub-word tokens are the morphemes themselves. Regexes should
use the [constructs Grew requests accept](https://grew.fr/doc/request/). Allomorphy can sometimes
be captured this way — e.g. the prefix *in-* 'in, un' has four allomorphs (*in-*, *im-*, *ir-*,
*il-*), expressible as a single regex:

```
ID   UD.FORM        LEMMA                     UPOS     ...
A       _       in.+|im.+|irr.+|ill.+         ADJ      ...
A-1     _           in                       BMORPH    ...
A-2     _            _                        ADJ      ...
```

## UPOS

For word-level tokens, values come from the
[Universal part-of-speech tags](https://universaldependencies.org/u/pos/index.html). For sub-word
tokens, there are two possibilities: elements that also exist as free lexemes keep their normal
part of speech; bound forms (affixes, combining forms, affixoids) are tagged `BMORPH` ("Bound
MORPHeme"). In a morphological construction, the word-level token still carries its own UPOS, so
the output category of the morphological process stays specified. Two more examples beyond the
`semi-` + ADJ case already shown:

Noun+Noun compounding with *capo*:

```
ID   UD.FORM     LEMMA     UPOS   ...
A       _       capo.+     NOUN   ...
A-1     _        capo      NOUN   ...
A-2     _         _        NOUN   ...
```

Neoclassical compounding (two combining forms, one lexically fixed):

```
ID   UD.FORM     LEMMA     UPOS     ...
A       _       .+logia    NOUN     ...
A-1     _         _        BMORPH   ...
A-2     _        logia     BMORPH   ...
```

## FEATS

A list of lexical types and morphosyntactic features from the
[universal feature inventory](https://universaldependencies.org/u/feat/index.html) or the
[Italian-specific extension](https://universaldependencies.org/it/index.html#features), used to
express morphosyntactic/lexical constraints on open slots, or morphosyntactic constraints on
lexically-filled slots left underspecified for form. This field does **not** annotate every
applicable feature the way a UD treebank would — only what's needed to constrain matching. Beyond
the standard inventory, two extensions:

- **Animacy** and **Aspect** are used here to express semantic constraints even though Italian
  corpora don't generally annotate them — for now this only expresses the constraint formally,
  without helping the actual matching process.
- **Definite** is extended beyond the Italian UD tagset's `definite`/`indefinite` to also allow
  `specific indefinite`, when needed.

## HEAD

The ID of the syntactic head, or `0` for the construction's root. In morphological constructions,
the full word is, by convention, the head of the root sub-word element (subword and above-word
relations form two separate graph layers).

## DEPREL

Values come from [Universal Dependency Relations](https://universaldependencies.org/u/dep/index.html)
and their [Italian-specific subtypes](https://universaldependencies.org/it/index.html). ItCon
generally follows the annotation found in UD-annotated Italian treebanks, even where a different
theoretical analysis might be preferred (mostly for chunks/MWEs) — theoretical considerations
belong in the [entry itself]({% link guide/yaml-fields-reference.md %}), while CoNLL-C's job is
matching UD-annotated patterns. Below the word level, four additional relations apply:

- **root/m** — the root within the morphological construction (the stem in derivation, the head
  of the compound in compounding)
- **der/m** — links a derivational affix to the stem
- **case/m** — links the complement to the head in subordinating compounds (e.g. *capostazione*
  'station master')
- **mod/m** — links the attribute to the head in attributive compounds (e.g. *altopiano*
  'upland')
- **conj/m** — links the second constituent to the first (the head) in coordinating compounds
  (e.g. *cartongesso* 'drywall')

## REQUIRED

Encodes whether a token must be obligatorily expressed (`1`) or can be omitted (`0`) — used to
capture formal variants like subject omission in the matching process. For example, in the
Passive Construction with *venire*, both the subject (Patient) and the *da* N prepositional
phrase (Agent) are optional:

```
ID    UD.FORM   LEMMA     UPOS                 ...    HEAD   DEPREL       REQUIRED
A        _       _        NOUN, PROPN, PRON    ...    C      nsubj:pass   0
B        _       venire   AUX                  ...    C      aux:pass     1
C        _       _        VERB                 ...    0      root         1
D        _       da       ADP                  ...    E      case         0
E        _       _        NOUN, PROPN, PRON    ...    C      obl          0
```

## EXCLUSION

Beyond the `CHILDREN:DEPREL=value` pattern shown in the main guide, EXCLUSION supports excluding
specific values from the token's own fields directly, and combining more than one constraint with
a pipe (`|`):

```
COLUMN_NAME=value1,value2|COLUMN_NAME2=value1
```

For example, to exclude *zero* and *uno* from the open numeral slot of *Num N in croce*
'barely/only Num of Ns':

```
ID    UD.FORM    LEMMA     UPOS    ...   REQUIRED    EXCLUSION
A       _         _        NUM           1           LEMMA=zero,uno
B       _         _        NOUN          0           _
C      in         in       ADP           1           _
D      croce      croce    NOUN          1           _
```

The `CHILDREN:` prefix constrains a token's children rather than the token itself — e.g. an
intransitive verb must have no `obj` child, or (using a regex as the value) a parenthetical verb
like *sembra* must have no children of any kind:

```
ID    UD.FORM    LEMMA      UPOS    ...   REQUIRED    EXCLUSION
A       _        _          VERB    ...    1          _
B       _        sembrare   VERB    ...    1          CHILDREN:DEPREL=.+
```

## SEM_FEATS

The semantic counterpart of FEATS: constraints on open slots not covered by morphosyntactic
features. Since there's no semantically annotated Italian corpus, these constraints are
descriptive — they don't currently drive the actual matching process. See
[Semantic features]({% link guide/semantic-features.md %}) for the full tagset (OntoClass from
Open Multilingual Wordnet Topics, Aktionsart from UniMorph). Formally identical to FEATS,
including the pipe (`|`) for combining multiple features on one token:

```
ID    UD.FORM    LEMMA      UPOS    ...   SEM_FEATS
A       _        fare       VERB    ...    _
B       _        _          NOUN    ...    OntoClass=feeling
```

## SEM_ROLES

Semantic roles of participants, mainly in argument structure constructions, annotated on both
open and filled slots. Like SEM_FEATS, this doesn't currently drive matching — it's there to
later annotate the roles of matched argument-structure constructions in corpora. Based on an
adapted version of the [UVI (Unified Verb Index)](https://uvi.colorado.edu/references_page#ThematicRoleHierarchy)
role hierarchy — see [Semantic roles]({% link guide/semantic-roles.md %}) for the full tagset and
its mapping to MoCCa comparative concepts.

## ADJACENCY

Constrains linear adjacency: when no element can intervene between a token and its left-adjacent
neighbor, the field holds the ID of that left-adjacent token. Also annotated in morphological
constructions. E.g. in *Num N in croce*, neither the noun-*in* nor the *in*-*croce* boundary can
have anything inserted:

```
ID    UD.FORM    LEMMA     UPOS     ...    ADJACENCY
A       _         _        NUM      ...    _
B       _         _        NOUN     ...    _
C      in         in       ADP      ...    B
D      croce      croce    NOUN     ...    C
```

## IDENTITY

Annotates coindexation. Since coindexation can apply at different levels (a whole field, or one
key inside FEATS), the value is `COLUMN_NAME:token_ID` — or `FEATS.key:token_ID` for a single
morphosyntactic feature (see the agreement example in the main
[CoNLL-C format]({% link guide/conllc-format.md %}) page). E.g. in the discontinuous reduplication
construction Noun *non* Noun 'not properly a Noun', the second noun must match the first noun's
form:

```
ID    UD.FORM    LEMMA     UPOS     ...    IDENTITY
A       _         _        NOUN     ...    _
B      non       non       ADV      ...    _
C       _         _        NOUN     ...    FORM:A
```

## Metadata

Construction-level information sits in `#`-prefixed comment lines above the token rows. Every
construction needs at least `cxn_id`, `name`, and `function`; `horizontal_links` and
`vertical_links` are optional.

- **cxn_id** — matches the [entry's ID]({% link guide/yaml-fields-reference.md %}#id).
- **name** — matches the [entry's name]({% link guide/yaml-fields-reference.md %}#name).
- **function** — a concise natural-language paraphrase of the construction's meaning (narrower
  in scope than the entry's [Definition]({% link guide/yaml-fields-reference.md %}#definition),
  which can also cover pragmatics/information structure). Can reference specific tokens with
  `ref:token_ID`:

  ```
  # cxn_id = 1
  # name = fare una PROPN-ata
  # function = ref:A does something typical of ref:D-1
  ```

- **horizontal_links** / **vertical_links** — same information as the
  [entry fields]({% link guide/yaml-fields-reference.md %}#links), space-separated IDs:

  ```
  # horizontal_links = 1 34 39
  # vertical_links = 10
  ```

### Holistic properties

Sometimes a multiword expression behaves, as a whole, differently from what its parts would
predict — e.g. *giorno dopo giorno* 'day after day' is two nouns and a preposition, but functions
as an adverb (`advmod`) in the sentence. Since UD's lexicalist approach can't assign a UPOS/DEPREL
to a multi-token span, this information is instead recorded as extra metadata lines:

```
# UPOS = ADV
# DEPREL = advmod
```

For morphological constructions this isn't an issue, since the full word already has its own
fields available for this purpose.

## Formal variation: worked example

As mentioned in [Formal variation in CoNLL-C]({% link guide/formal-variation.md %}), when formal
variants can't be captured with a regex or a disjunction, ItCon adds more than one graph to the
same entry, suffixing the ID (`a`, `b`, …). For instance, the *semi-* + ADJ construction (entry
169) can appear bonded or hyphenated — since a single graph can't represent both a morphological
and a multiword form, the file gets two `# cxn_id` blocks:

```
# cxn_id = 169
# name = semiADJ
# function = not fully or not properly ref:A-2
# ...

ID   UD.FORM     LEMMA     UPOS   ...
A       _        semi.+     ADJ   ...
A-1     _        semi     BMORPH  ...
A-2     _         _         ADJ   ...

# cxn_id = 169b
# name = semiADJ
# function = not fully or not properly ref:C
# ...

ID   UD.FORM     LEMMA     UPOS   ...
A      semi      semi       ADJ   ...
B       _         -        PUNCT  ...
C       _         _         ADJ   ...
```
