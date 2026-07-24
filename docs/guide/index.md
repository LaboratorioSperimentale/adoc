---
title: Guide
nav_order: 2
has_children: true
---

# Formalizing a Construction for ItCon: A Practical Guide

Each construction in ItCon is defined by a main file, in `.yaml` format, and
a machine-readable formalization in `CoNLL-C` format — a UD-compatible
convention for expressing the constraints a construction must satisfy.
This guide walks through both, plus how to annotate construction instances
in a corpus (`CoNLL-Uc`) and the overall annotation workflow.

This is based on the project's authoritative guide,
[`publications/tutorial/guida.md`](https://github.com/LaboratorioSperimentale/adoc/blob/main/publications/tutorial/guida.md)
(Italian) in the repository, integrated with additional detail from the
[project wiki](https://github.com/LaboratorioSperimentale/adoc/wiki) where the wiki goes deeper
than the guide itself — those pages are marked as such and linked from the relevant section below.

1. [The `.yaml` construction file](yaml-format)
2. [YAML fields reference](yaml-fields-reference) — extra detail, from the wiki
3. [The CoNLL-C format](conllc-format)
4. [CoNLL-C field reference](conllc-fields-reference) — extra detail, from the wiki
5. [Semantic features](semantic-features) — extra detail, from the wiki
6. [Semantic roles](semantic-roles) — extra detail, from the wiki
7. [Morphology](morphology)
8. [Formal variation in CoNLL-C](formal-variation)
9. [Annotating examples in CoNLL-Uc](conlluc-examples)
10. [Workflow: how to formalize a construction](workflow)
