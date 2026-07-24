---
title: Morphology
parent: Guide
nav_order: 3
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
