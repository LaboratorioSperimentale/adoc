---
title: Morphology
parent: Guide
nav_order: 7
---

# Morphology

The constructions we want to represent obviously do not necessarily operate at the level of the
sentence. They may also affect lower levels, such as the morphological level,
or higher levels, such as the textual level.

The CoNLL-C format can be used for constructions at the morphological level.
In this case we must represent the elements at the morphological level (below the word level)
that constitute the construction.

Let's consider the case of the construction **X-issimo**, which creates superlatives of
adjectives.
We can model the construction as follows:

| ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION |
|----|------|-------|------|-------|------|--------|----------|-----------|-----------|
| A | r".\*issim[oaie]" | _ | ADJ | Degree=Sup | 0 | root | _ | _ | _ |
| A-1 | _ | _ | ADJ | _ | A | root/m | _ | _ | _ |
| A-2 | _ | -issmo | BMORPH | _ | A-1 | der/m | _ | _ | _ |

Morphological elements are characterized by:

- **ID** composed of two components: a letter identifying the word they refer to and a progressive
  number
- As part of speech, elements that exist as free lexemes retain their part of speech, while bound forms
  (affixes, affixoids, combining forms) are annotated as **BMORPH**
- For dependencies, at the morpheme level we introduce the following relations:
  - **root/m**: the root within the morphological construction. In derivation it corresponds to the stem, in compounding it corresponds to the head of the compound.
  - **der/m**: the relation that links the derivational affix to the stem
  - **case/m**: the relation that links the complement to the head in subordinating compounds (e.g., *capostazione*)
  - **mod/m**: the relation that links the attribute to the head in attributive compounds (e.g., *altopiano*)
  - **conj/m**: the relation that links the second constituent to the first in coordinating compounds (e.g., *cartongesso*)

## More examples

Two more worked examples beyond derivation with a suffix, from the
[wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.1.-Conll%E2%80%90X-formalization-guidelines#deprel):
Noun+Noun compounding with *capo* ('head, boss'), and neoclassical compounding with two combining
forms (one of them, *-logia*, lexically fixed):

```
# name = capoN
# function = head or boss of ref:A-2

ID   UD.FORM     LEMMA     UPOS   ...   HEAD   DEPREL
A       _       capo.+     NOUN   ...   0      root
A-1     _        capo      NOUN   ...   A      root/m
A-2     _         _        NOUN   ...   A-1    case/m
```

```
# name = Xlogia
# function = study of ref:A-1

ID   UD.FORM     LEMMA     UPOS     ...   HEAD   DEPREL
A       _       .+logia    NOUN     ...   0      root
A-1     _         _        BMORPH   ...   A      case/m
A-2     _        logia     BMORPH   ...   A-1    root/m
```

A full example, with the corresponding dependency graph, for the light-verb construction *fare
una* PROPN*-ata* ('to do something typical of PROPN'), where the noun slot is itself filled by a
morphological construction (proper noun + *-ata* suffix):

*Gianni **ha fatto una** Berluscon**ata*** — 'Gianni did something typical of Berlusconi/something
Berlusconi-like'

```
# cxn_id = 1
# name = fare una PROPN-ata
# function = ref:A does something typical of ref:D-1
# horizontal_links =
# vertical_links = 10
```

| ID | UD.FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | REQUIRED |
|---|---|---|---|---|---|---|---|
| A | _ | _ | NOUN, PROPN, PRON | _ | B | nsubj | 0 |
| B | _ | fare | VERB | _ | 0 | root | 1 |
| C | una | uno | DET | Gender=Fem | D | det | 1 |
| D | _ | _ | NOUN | Gender=Fem | B | obj | 1 |
| D-1 | _ | _ | PROPN | Animacy=Hum | D | root/m | 1 |
| D-2 | _ | -ata | BMORPH | _ | D-1 | der/m | 1 |

![Dependency representation for "fare una PROPN-ata"](/adoc/assets/images/fare_una_Nata.png)

Since subword and above-word relations form two separate graph layers, the morphological part
(`D-1`/`D-2`) can also be shown on its own:

![Dependency representation for "PROPN-ata"](/adoc/assets/images/Nata.png)

## Other approaches in the literature

Representing sub-word tokens and relations this way is a design choice — other recent proposals
handle it differently. [Bedir et al. (2021)](https://aclanthology.org/2021.law-1.12.pdf) use
`dep:der` for the relation between a derivational affix and its stem.
[Zeman (2023)](https://unidive.lisn.upsaclay.fr/lib/exe/fetch.php?media=meetings:2023-saclay:abstracts:39_zeman_subword_relations_superword_features.pdf)
only covers compounding, using an ordinary syntactic dependency relation plus `wroot` to mark the
compound's head. The approach closest to ItCon's is
[Guillaume et al. (2024)](https://aclanthology.org/2024.lrec-main.836), whose `/m`-suffixed
subword relations and use of syntactic dependencies in compounds we adopted — they instead use a
single `comp/m` label (further specified per subordinative relation, e.g. `comp:obj/m`) where
ItCon distinguishes `case/m`, `mod/m`, and `conj/m`. Guillaume et al. also tag bound morphemes
with the UD tag `X` rather than `BMORPH`, leaving the subword element's status to be specified
later via a `TokenType` feature (`Root`, `InflAff`, `DerAff`, `Word`).
