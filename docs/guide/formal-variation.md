---
title: Formal variation in CoNLL-C
parent: Guide
nav_order: 8
---

# Formal variation in CoNLL-C

It may happen that the constraints illustrated so far are not enough to satisfactorily represent the
construction in a way compatible with Universal Dependencies, often due to orthographic
variations or idiosyncrasies of the format.

For example, the construction **semiX** or **similX** can be instantiated either as a univerb,
with the presence of a hyphen **-**, or via modification.

In such cases, the `conllc` file can contain more than one structure — see the worked
[*semi-* + ADJ example]({% link guide/conllc-fields-reference.md %}#formal-variation-worked-example)
in the field reference.
