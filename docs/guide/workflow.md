---
title: "Workflow: how to formalize a construction"
parent: Guide
nav_order: 6
---

# So how do we do it?

Once the system is fully operational, there will be automated steps in the process and the annotation will be mediated by an interface.
For now, follow these steps:

1. Create the `.yaml` file for your construction starting from the template. Assign an ID arbitrarily.
   The only requirement is that it has not already been chosen.
2. Fill in the YAML as far as possible, and create the corresponding `.conllc` file.
3. Try to search for some examples of the construction you want to formalize with **grew match**,
   across all Italian corpora.
4. If you cannot find examples (the corpora are relatively small),
   look for something similar in related languages (e.g., other Romance languages or, more generally, languages you
   speak where you can find a similar structure).
5. Choose the syntactic representation that seems most faithful to what you want to represent
   and start from that to build the CoNLL-C file (using a spreadsheet can also help to better
   fill in the tabular format).
6. Look for examples preferably already in UD corpora (via **grew match**).
   1. If you find them, save the example in a dedicated file and add the annotation of the elements.
   2. If you do not find any example already in UD, look for it in other resources. You can parse it in UD
      using tools such as [udpipe](https://lindat.mff.cuni.cz/services/udpipe/) or, at minimum,
      tokenize it by putting each token on a separate line. The annotation provided by UDPipe will likely
      not be perfect but should be easy to modify. At that point you can add
      the example in a dedicated file and add the annotation related to your construction.
7. Check that the examples already present for other constructions do not also contain examples of your
   construction. If they do, add the relevant annotation.

For the automated side of steps 2–3 (turning a spreadsheet row into YAML +
draft CoNLL-C, and searching a corpus via a Grew query built from a CoNLL-C
file), see the [Tools]({% link tools/index.md %}) section.
