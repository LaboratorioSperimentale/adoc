---
title: Home
layout: home
nav_order: 1
---

# ItCon: a Machine-Readable Constructicon for Italian

ItCon aims to be a Machine-Readable Constructicon.

It is composed of several elements that interact with each other to allow
consulting and updating the constructicon according to multiple use cases.
In particular:

- a **database** of constructions
- a **graph** that organizes the constructions into a network
- a **corpus** of incrementally annotated examples
- an **interface** for querying and visualization

To make this possible, it is necessary to precisely define the construction
object, which represents the core of the resource.

## Where to start

- **[Guide]({% link guide/index.md %})** — how to formalize a construction
  for ItCon: the `.yaml` file, the `CoNLL-C` and `CoNLL-Uc` formats, and the
  step-by-step annotation workflow.
- **[Tools]({% link tools/index.md %})** — the `adoc-tools` pipeline that
  turns a spreadsheet export into YAML/CoNLL-C construction files, parses
  and extracts catena skeletons from example sentences, and converts
  CoNLL-C into Grew search patterns.
- **[Publications]({% link publications/index.md %})** — papers describing
  ItCon and its formalization.
