---
title: YAML fields reference
parent: Guide
nav_order: 2
---

# Constructicon entry fields: a reference

Each construction is stored as an entry in the Italian Constructicon. Every entry contains a
number of fields specifying formal, functional and usage information about the construction, as
well as its relatedness to other entries. This page gives more detail on each field than the
[.yaml construction file]({% link guide/yaml-format.md %}) walkthrough — it's sourced from the
project's [wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.-Constructicon-entries:-definition-of-the-fields).

## ID

A unique and stable identifier for the constructional entry. This field is filled automatically
as a new construction is created.

## Name

Contains a "human-intelligible" name for the construction. To keep a consistent naming practice,
we use the following decision tree to work out the name for each entry:

1. Is there a standard denomination for this construction (i.e., in the literature)? If so, use
   it. If there is no commonly accepted denomination, go to 2.
2. Can the name be expressed by means of its lexicalized components (e.g. "capo-N" for *capo* +
   Noun compounds)? If so, build the name that way. If there are no lexicalized components, go to 3.
3. Can the name be expressed by means of its syntactic relations (e.g. "Sbj V Obj1 Obj2" for the
   Ditransitive construction)? If so, build the name that way as long as it is easily readable.
   If it is not, go to 4.
4. Can the name be easily expressed by the function (e.g. "Contrastive Focus")? If so, name the
   construction with reference to its function. If the name is too generic, or using the function
   as name is not possible for some other reason, go to 5.
5. If none of the previous criteria yield an easily readable/recognizable name, just be creative —
   we'll find a better name with time!

## CoNLL-X formalization

A reference to the construction's `.conllc` file — see [The CoNLL-C format]({% link guide/conllc-format.md %}).

## Definition

A description of the construction's function. Differently from the `function` metadata field in
the CoNLL-C formalization (which should be as concise as possible), this is a non-formal,
discursive description, similar to a lexicographic definition, and includes information on:

- semantics;
- pragmatic and discourse functions;
- information status and information structure features.

Differently from lexicographic definitions, it does not include examples (those go in a separate
field, see [Examples](#examples)). Definitions can be more or less elaborate, depending on the
information available in the literature. Example (from the *salta fuori che* V 'turns out that'
entry):

> A new piece of information comes to the speaker's knowledge from an external source. The
> information acquired is often unexpected or contradicts the speaker's expectations on the state
> of affairs, thus generating surprise in the speaker. However, since the moment of acquisition
> and the moment of enunciation are distinct, this construction does not convey that the speaker
> is currently surprised, but it is used to convey or generate surprise in the audience.

## Restrictions

A discursive description of the constraints on the construction's fillers. Such constraints can
be hard (categorical) or soft (violable in specific cases), and can include:

- formally or semantically defined types/categories of lemmas and/or words (e.g. motion verbs,
  two-syllable words);
- specific lemmas/words;
- formal or semantic features of the fillers (e.g. a noun cannot be plural in a specific
  construction).

Constraints on the contextual and/or co-textual environment are **not** included here — see
[Usage](#usage) and [Notes](#notes) instead. Restrictions can include both the ones already
specified in the CoNLL-C formalization, and further constraints that aren't/can't be captured in
the formalization.

## Collocational preferences

A discursive field, similar to Restrictions, but for *preferences* rather than constraints — e.g.
typical collocations for a slot. There's currently no support for listing specific lemmas here; a
description of the preferred filler types is used instead.

## Usage

Up to 3 "usage" tags for the construction, used if it is constrained or shows preferences in its
extra-linguistic behavior (i.e. if it's typically or only found in some contexts). Three possible
axes, one tag per axis:

- Style: `Formal` or `Informal`
- Modality: `Spoken` or `Written`
- Variety: `Standard` or `Non-standard`

This field cannot contain both tags of the same axis (e.g. both `Spoken` and `Written`) — in that
case the construction isn't marked for that axis at all, so the tag wouldn't be informative.
Further comments on usage (e.g. constraints on text genres) go in [Notes](#notes). If none of the
tags above is relevant, this field can be left empty.

## Formal tags

Tags describing the construction from a formal point of view. Preferably drawn from the
[Comparative Concepts list](https://comparative-concepts.github.io/cc-database/) of MoCCa (Model
of Comparative Concepts for Aligning Constructicons), limited to the `construction` and
`strategy` types. If no useful CC exists, other definitions shared in the (typological)
literature can be used instead, e.g. *prefixation*, *reduplication*, *impersonal construction*.

## Functional tags

Tags describing the construction from a functional point of view. Preferably drawn from the same
[Comparative Concepts list](https://comparative-concepts.github.io/cc-database/), limited to the
`meaning` and `information packaging` types. If no useful CC exists, other definitions shared in
the (typological) literature can be used instead.

## Complexity level tags

The construction's complexity level:

- `word`
- `phrase`
- `clause`
- `beyond-clause`

## Category tags

One or more tags indicating the construction's output category (ideally auto-filled from the
`.conllc` file):

`adjective`, `adverb`, `conjunction`, `discourse marker`, `interjection`, `noun`, `preposition`,
`pronoun`, `verb`, `onomatopoeia`, `not applicable`, `other`

## Schematicity level

The construction's schematicity level (ideally auto-filled from the `.conllc` file):

- `lexically filled`
- `partially filled/schematic`
- `fully schematic`

## CEFR level

The language-competence level the construction belongs to: `A1`, `A2`, `B1`, `B2`, `C1`, `C2`.

## Links

Two fields, ideally auto-filled from the `.conllc` file's `horizontal_links`/`vertical_links`
metadata (see [CoNLL-C field reference]({% link guide/conllc-fields-reference.md %})):

- **Horizontal links** — constructions at the same level of abstraction that are semantically
  similar to/paraphrases of this one, or otherwise in a paradigmatic relation with it (e.g.
  antonymic constructions, or ones related by a derivational series).
- **Vertical links** — constructions at a higher level of abstraction; mainly instance links.

## Examples

A collection of at least 5 examples from corpora, preferably from treebanks, with the
construction annotated — see [Annotating examples in CoNLL-Uc]({% link guide/conlluc-examples.md %}).

## Notes

Free text for anything not covered elsewhere — e.g. if Usage is `Non-standard`, specify which
variety (including diatopic), or the text genres it's found in; frequency/emergence notes; etc.

## References

Citations to the relevant literature on the construction.

## Data collector

The name (or username) of whoever entered the construction.
