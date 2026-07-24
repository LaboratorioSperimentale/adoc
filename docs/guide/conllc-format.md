---
title: The CoNLL-C format
parent: Guide
nav_order: 2
---

# `conll-c`, `conllu-c` and interoperability with UD

Let's now look specifically at the `cxn-machine-readable:` and `examples` fields of the `yaml` file.

Although formal properties (i.e., morphosyntactic ones) are only part of the elements needed
to represent a construction, the vast majority of the corpora at our disposal are based
on such annotations.

This implies two things:

- we have a lot of tools that allow us to manipulate formal and structural properties
  annotated on resources
- if we hope to leverage the automatic population of ItCon in the future, we need to understand how
  to make the most of the annotation we already have available

In the case of ItCon, we chose the formalism offered by **Universal Dependencies** for a
number of reasons:

- 'light' syntactic formalism
- cross-linguistic compatibility
- wide availability of tools
- interoperability with **[grew match](https://universal.grew.fr/)**
- accuracy of automatic annotation

We therefore developed two formats (`CoNLL-C` and `CoNLL-Uc`) to represent the constructicon
in a way that is interoperable with UD resources and at the same time model the development of the resource
independently and in a machine-readable way.

## The [CoNLL-U](https://universaldependencies.org/format.html) format

UD corpora are annotated in a tabular format.

A treebank consists of a sequence of sentences: [example](https://github.com/UniversalDependencies/UD_Italian-MarkIT/blob/master/it_markit-ud-test.conllu)

Each sentence contains:

- lines relating to words, consisting of 10 tab-separated fields. Each field expresses an annotation
  or a property relating to the word
- comments and metadata (identified by `#`)

Each sentence represents a tree:

![CoNLL-U Example](/adoc/assets/images/84_0.svg "CoNLL-U Example")

## The CoNLL-C format

In ItCon each construction is associated with a file in `.conllc` format.

CoNLL-C builds on the CoNLL-U guidelines and extends them to represent the constraints required
by our representation.

To start with, we can think of a construction as defined by a
[catena](/adoc/assets/publications/osborne-catenae.pdf)
on a dependency tree, i.e., a set of nodes bound together by syntactic relations.

![CoNLL-U Example](/adoc/assets/images/10107_0.svg "CoNLL-U Example")

![CoNLL-U Example](/adoc/assets/images/1087_0.svg "CoNLL-U Example")

![CoNLL-U Example](/adoc/assets/images/10587_0.svg "CoNLL-U Example")

We want to represent our construction as an object of this kind:

![CoNLL-U Example](/adoc/assets/images/cxn.svg "CoNLL-U Example")

## The fields in CoNLL-C

### The CoNLL-U base

As in CoNLL-U, in our format we also distinguish two types of lines:

- lines that represent minimal elements of the construction (typically, words), whose properties
  are expressed in tab-delimited fields
- lines introduced by `#`, which represent properties of the construction as a whole.

Let's focus on the element-lines and their fields.
The previous construction, viewed in tabular format, looks like this:

| ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC |
|----|------|-------|------|------|-------|------|--------|------|------|
| 1 | _ | _ | NOUN | S | Number=Sing | 4 | obl | _ | _ |
| 2 | dopo | dopo | ADP | E | _ | 3 | case | _ | _ |
| 3 | _ | _ | NOUN | S | Number=Sing | 1 | nmod | _ | _ |
| 4 | _ | _ | _ | V | _ | 0 | root | _ | _ |

In CoNLL-C we focus only on the internal elements of the construction, which will therefore have 3 elements
(instead of 4).
The basic idea is to use the fields to express the constraints that the construction must satisfy

- the **ID** field consists of letters rather than numbers. This is because in CoNLL-U numbers
  also indicate that the elements must appear in that order and be adjacent. In our case, we want
  the structure to allow not fixing the order or
  inserting other material between one element and another of the construction. The ID field is the only
  mandatory field in the format; for all the others it is possible to insert the value `_` to indicate that
  no constraint is imposed on the field
- the **form** field should be filled in when the form is fixed. For example, in the construction
  above (N dopo N), **dopo** is a token fixed at the form level.
  The form field can be expressed using a regular expression (by prefixing the string with `r`).
- the **lemma** field expresses constraints at the lemma level. For example, in the construction
  *salta fuori che X*, the first element (*salta*) can vary within the paradigm of the lemma *saltare*, which
  is the constraint we want to fix
- the **upos** field expresses constraints at the part-of-speech level and contains values
  from the [Universal Dependencies inventory](https://universaldependencies.org/u/pos/index.html)
- the **feats** field contains annotations on [morphological features](https://universaldependencies.org/u/feat/index.html)
  (e.g., constraints on gender, number, tense and mood of verbs…)
- the **head** field contains one of the identifiers in the ID field, or `0` for the *head* of the construction
- the **deprel** field contains values from the [Universal Dependencies inventory](https://universaldependencies.org/u/dep/index.html),
  and `root` for the head of the construction

So far we have essentially expressed the same format as above, with minimal changes:

| ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL |
|----|------|-------|------|-------|------|--------|
| A | _ | _ | NOUN | Number=Sing | 0 | root |
| B | dopo | dopo | ADP | _ | C | case |
| C | _ | _ | NOUN | Number=Sing | A | nmod |

### Further restrictions

Let's now introduce additional constraints that take our format further away from CoNLL-U.

- A first difference concerns the possible presence of an external constraint on the dependency.
  In our case, the construction **N dopo N** that we want to formalize appears as a modifier
  in the wider context of the sentence. In fact, in the examples above, *ora*, *giorno*, and *settore*
  are linked by the relation **obl** to another element of the sentence.
  We can express this external constraint by specifying the relation **root** and indicating
  **root:obl** in the `DEPREL` field of element A.
- As formalized so far, our construction expresses more patterns than we want.
  The construction **N dopo N**, in fact, requires the two **N**s to be identical. We can express this
  constraint in the **IDENTITY** field, which has the following syntax: `field_name:ID`.

  | ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY |
  |----|------|-------|------|-------|------|--------|----------|
  | A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C |
  | B | dopo | dopo | ADP | _ | C | case | _ |
  | C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A |

  In the same way, agreement constraints can also be expressed (e.g., Subject and Verb must
  agree in number).
- In the case of the **N dopo N** construction, we need to consider other aspects (in this case, partially
  overlapping)

  ![CoNLL-U Example](/adoc/assets/images/1444_0.svg "CoNLL-U Example")

  On the one hand, the construction requires the three elements to be all adjacent, with no material
  either between **N** and **dopo**, or between **dopo** and **N**.
  We can express this in the **ADJACENCY** field: if the adjacency field of element X contains
  the ID Y, it means that X must immediately precede Y in the sentence.
  Another aspect often related to the presence of other material is the possibility that the elements
  of the construction exhibit further modification.

  | ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY |
  |----|------|-------|------|-------|------|--------|----------|-----------|
  | A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _ |
  | B | dopo | dopo | ADP | _ | C | case | _ | A |
  | C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B |

  Likewise, we can impose constraints on the kinds of other dependencies an element has.
  For example, in this case we want to filter cases like *casa sua dopo casa mia* that are not
  instances of the **N dopo N** we are looking for.
  This type of constraint should be reported in the **EXCLUSION** field, whose syntax is:
  `KEYWORD:FIELD=VALUE`.
  Currently the only implemented keyword is `CHILDREN`, to indicate the types of relations we
  want to exclude. In our case, we want both nouns in the construction not to have,
  for example, adjectives modifying them: we can express this with the constraint `CHILDREN:DEPREL=amod`.

  | ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION |
  |----|------|-------|------|-------|------|--------|----------|-----------|-----------|
  | A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _ | CHILDREN:DEPREL=amod |
  | B | dopo | dopo | ADP | _ | C | case | _ | A | _ |
  | C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B | CHILDREN:DEPREL=amod |

### Semantic restrictions

Often important restrictions on the productivity of the construction come from the semantic field
linked to a slot.
Although UD does not provide for this type of annotation, in CoNLL-C two fields (**SEM_FEATS** and **SEM_ROLES**)
are dedicated to specifying such restrictions.

- For semantic features (**SEM_FEATS**), it is possible to specify the ontological class for nouns and
  verbs (`OntoClass`), the **Aktionsart** for verbs (`Aktionsart`), and the class from dedicated ontologies for
  adjectives and adverbs (`AdjClass` and `AdvClass`).
  If, for example, we want to formalize a subconstruction of the previous construction,
  restricting productivity to time nouns (*ora dopo ora*, *giorno dopo giorno*, but excluding
  *settore dopo settore*), we can express it as follows

  | ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION | SEM_FEATS |
  |----|------|-------|------|-------|------|--------|----------|-----------|-----------|-----------|
  | A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _ | CHILDREN:DEPREL=amod | time |
  | B | dopo | dopo | ADP | _ | C | case | _ | A | _ | _ |
  | C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B | CHILDREN:DEPREL=amod | time |

- Similarly, we can annotate the semantic role realized by the elements of the construction,
  following the taxonomy provided by the [Unified Verb Index](https://uvi.colorado.edu/references_page#ThematicRoleHierarchy).

### Notes on field syntax

If we think in terms of constraints, to best express the possible restrictions on
slots, we need to introduce some operations on possible values:

- **disjunction**: if we think of the construction *che X!*, we cannot express the part of speech
  to be assigned to X with a single label. We want to represent different constructions, which
  include both adjectives (*Che bello!*) and nouns (*Che noia!*).
  To express the disjunction between two values ("ADJ" or "NOUN") we can generally use
  a comma.

  | ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION |
  |----|------|-------|------|-------|------|--------|----------|-----------|-----------|
  | A | che | che | DET | _ | B | det | _ | _ | _ |
  | B | _ | _ | ADJ,NOUN | _ | 0 | root | _ | _ | _ |

  Disjunction can occur:
  - in the **LEMMA** field (e.g., `che,qual`)
  - for each morphosyntactic feature (e.g., `VerbForm=Fin,Part`)
  - for the dependency relation *except root* (e.g., `det,amod`)
  - for semantic roles and semantic features

- **negation**: similarly, we may want to restrict productivity by excluding a value
  rather than listing possible values (for example: the slot can be filled by any
  category **except** a proper noun). In this case we use the exclamation mark to indicate it
  (`!PROPN`).

  Negation can occur:
  - in the **LEMMA** field (e.g., `!che`)
  - for each morphosyntactic feature (e.g., `VerbForm=!Fin`)
  - for the dependency relation *except root* (e.g., `!det`)
  - for semantic roles and semantic features

- **conjunction**: in the case of features and filters we wish to apply (**EXCLUSION**),
  we may want to express more than one constraint. For example, a certain element must be a noun of
  feminine gender and singular number.
  In continuity with the CoNLL-U format, this is expressed by the pipe symbol (`|`, for example
  `Gender=Fem|Number=Sing`).

Another aspect to consider is **optionality**. In the construction above (*che bello!*), we may
want to include the exclamation mark as optional. For this, the **REQUIRED** field can contain
values `0` or `1`.
