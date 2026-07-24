---
title: Annotating examples in CoNLL-Uc
parent: Guide
nav_order: 5
---

# Examples in CoNLL-Uc

Once the formalization is complete, we can use it to annotate instances of the
construction in the corpora at our disposal, in particular by aligning our elements with
UD annotation.

As we have seen, the CoNLL-U format consists of 10 columns. To these we add an additional
column with our annotation.

Consider the following CoNLL-U example:

```
# sent_id = 3214_it_postwita
# source = http://hdl.handle.net/11234/1-5502 UD_Italian-PoSTWITA/it_postwita-ud-train 3214
# text = Pensa se alla fine di tutto sto casino viene fuori che Borghezio è l'unico onesto
```

| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC |
|----|------|-------|------|------|-------|------|--------|------|------|
| 1 | Pensa | pensare | VERB | V | Mood=Imp\|Number=Sing\|Person=2\|Tense=Pres\|VerbForm=Fin | 0 | root | _ | _ |
| 2 | se | se | SCONJ | CS | _ | 10 | mark | _ | _ |
| 3-4 | alla | _ | _ | _ | _ | _ | _ | _ | _ |
| 3 | a | a | ADP | E | _ | 5 | case | _ | _ |
| 4 | la | il | DET | RD | Definite=Def\|Gender=Fem\|Number=Sing\|PronType=Art | 5 | det | _ | _ |
| 5 | fine | fine | NOUN | S | Gender=Fem\|Number=Sing | 10 | obl | _ | _ |
| 6 | di | di | ADP | E | _ | 9 | case | _ | _ |
| 7 | tutto | tutto | DET | DI | PronType=Ind | 9 | det:predet | _ | _ |
| 8 | sto | questo | DET | DD | PronType=Dem | 9 | det | _ | _ |
| 9 | casino | casino | NOUN | S | Gender=Masc\|Number=Sing | 5 | nmod | _ | _ |
| 10 | viene | venire | VERB | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 1 | ccomp | _ | CXN=167:A |
| 11 | fuori | fuori | ADV | B | _ | 10 | advmod | _ | CXN=167:B |
| 12 | che | che | SCONJ | CS | _ | 17 | mark | _ | CXN=167:C |
| 13 | Borghezio | Borghezio | PROPN | SP | _ | 17 | nsubj | _ | _ |
| 14 | è | essere | AUX | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 17 | cop | _ | _ |
| 15 | l' | il | DET | RD | Definite=Def\|Number=Sing\|PronType=Art | 17 | det | _ | SpaceAfter=No |
| 16 | unico | unico | ADJ | A | Gender=Masc\|Number=Sing | 17 | amod | _ | _ |
| 17 | onesto | onesto | ADJ | A | Gender=Masc\|Number=Sing | 10 | ccomp | _ | _ |

Given a CoNLL-C formalization for the construction *viene fuori che X* as follows:

| ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | REQUIRED | EXCLUSION | SEM_FEATS | SEM_ROLES | ADJACENCY | IDENTITY |
|----|------|-------|------|-------|------|--------|----------|-----------|-----------|-----------|-----------|----------|
| A | _ | venire | VERB | Number=Sing\|Person=3 | 0 | root | 1 | CHILDREN:DEPREL=nsubj | _ | _ | _ | _ |
| B | fuori | fuori | ADV | _ | A | advmod | 1 | _ | _ | _ | _ | _ |
| C | che | che | SCONJ | _ | D | mark | 1 | _ | _ | _ | _ | _ |
| D | _ | _ | VERB,NOUN,ADJ | VerbForm=Fin | A | csubj,ccomp | 1 | _ | _ | Eventuality | _ | _ |

We can proceed to annotate the sentence by adding the necessary elements:

| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC | CONSTRUCTION |
|----|------|-------|------|------|-------|------|--------|------|------|--------------|
| 1 | Pensa | pensare | VERB | V | Mood=Imp\|Number=Sing\|Person=2\|Tense=Pres\|VerbForm=Fin | 0 | root | _ | _ | _ |
| 2 | se | se | SCONJ | CS | _ | 10 | mark | _ | _ | _ |
| 3-4 | alla | _ | _ | _ | _ | _ | _ | _ | _ | _ |
| 3 | a | a | ADP | E | _ | 5 | case | _ | _ | _ |
| 4 | la | il | DET | RD | Definite=Def\|Gender=Fem\|Number=Sing\|PronType=Art | 5 | det | _ | _ | _ |
| 5 | fine | fine | NOUN | S | Gender=Fem\|Number=Sing | 10 | obl | _ | _ | _ |
| 6 | di | di | ADP | E | _ | 9 | case | _ | _ | _ |
| 7 | tutto | tutto | DET | DI | PronType=Ind | 9 | det:predet | _ | _ | _ |
| 8 | sto | questo | DET | DD | PronType=Dem | 9 | det | _ | _ | _ |
| 9 | casino | casino | NOUN | S | Gender=Masc\|Number=Sing | 5 | nmod | _ | _ | _ |
| 10 | viene | venire | VERB | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 1 | ccomp | _ | _ | 167:A |
| 11 | fuori | fuori | ADV | B | _ | 10 | advmod | _ | _ | 167:B |
| 12 | che | che | SCONJ | CS | _ | 17 | mark | _ | _ | 167:C |
| 13 | Borghezio | Borghezio | PROPN | SP | _ | 17 | nsubj | _ | _ | _ |
| 14 | è | essere | AUX | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 17 | cop | _ | _ | _ |
| 15 | l' | il | DET | RD | Definite=Def\|Number=Sing\|PronType=Art | 17 | det | _ | SpaceAfter=No | _ |
| 16 | unico | unico | ADJ | A | Gender=Masc\|Number=Sing | 17 | amod | _ | _ | _ |
| 17 | onesto | onesto | ADJ | A | Gender=Masc\|Number=Sing | 10 | ccomp | _ | | 167:D |

The same sentence—and even the same element—can bear annotations for multiple constructions.
When this happens, they are linked with pipes (`|`).

In the case of morphological constructions, elements below the word level must be added
to the example.

```
# sent_id = VIT-8523
# source = http://hdl.handle.net/11234/1-5502 UD_Italian-VIT/it_vit-ud-train VIT-8523
# text = Pochi, i cittadini di buona volontà, e seminascosti da un ingente presidio di poliziotti e di militari.
```

| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC | CONSTRUCTION |
|----|------|-------|------|------|-------|------|--------|------|------|--------------|
| 1 | Pochi | poco | PRON | PI | Gender=Masc\|Number=Plur\|PronType=Ind | 0 | root | _ | SpaceAfter=No | _ |
| 2 | , | , | PUNCT | FF | _ | 1 | punct | _ | _ | _ |
| 3 | i | il | DET | RD | Definite=Def\|Gender=Masc\|Number=Plur\|PronType=Art | 4 | det | _ | _ | _ |
| 4 | cittadini | cittadino | NOUN | S | Gender=Masc\|Number=Plur | 1 | appos | _ | _ | _ |
| 5 | di | di | ADP | E | _ | 7 | case | _ | _ | _ |
| 6 | buona | buono | ADJ | A | Gender=Fem\|Number=Sing | 7 | amod | _ | _ | _ |
| 7 | volontà | volontà | NOUN | S | Gender=Fem | 4 | nmod | _ | SpaceAfter=No | _ |
| 8 | , | , | PUNCT | FF | _ | 10 | punct | _ | _ | _ |
| 9 | e | e | CCONJ | CC | _ | 10 | cc | _ | _ | _ |
| 10 | seminascosti | seminascosto | ADJ | A | Gender=Masc\|Number=Plur | 1 | conj | _  | _ | 169a:A |
| 10.1 | semi | semi | BMORPH | _ | _ | 10.2 | der/m | _ | _ | 169a:A.1 |
| 10.2 | nascosti | nascosto | ADJ | A | Gender=Masc\|Number=Plur | 10 | root/m | _ | _ | 169a:A.2 |
| 11 | da | da | ADP | E | _ | 14 | case | _ | _ | _ |
| 12 | un | uno | DET | RI | Definite=Ind\|Gender=Masc\|Number=Sing\|PronType=Art | 14 | det | _ | _ | _ |
| 13 | ingente | ingente | ADJ | A | Number=Sing | 14 | amod | _ | _ | _ |
| 14 | presidio | presidio | NOUN | S | Gender=Masc\|Number=Sing | 10 | obl | _ | _ | _ |
| 15 | di | di | ADP | E | _ | 16 | case | _ | _ | _ |
| 16 | poliziotti | poliziotto | NOUN | S | Gender=Masc\|Number=Plur | 14 | nmod | _ | _ | _ |
| 17 | e | e | CCONJ | CC | _ | 19 | cc | _ | _ | _ |
| 18 | di | di | ADP | E | _ | 19 | case | _ | _ | _ |
| 19 | militari | militare | NOUN | S | Gender=Masc\|Number=Plur | 16 | conj | _ | SpaceAfter=No | _ |
| 20 | . | . | PUNCT | FS | _ | 1 | punct | _ | _ | _ |
