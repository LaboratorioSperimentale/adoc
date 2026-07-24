---
title: The .yaml construction file
parent: Guide
nav_order: 1
---

# Construction Identikit

Each construction in ItCon is defined by a main file, in `.yaml` format.

## What is YAML?

**YAML** (recursive acronym for *YAML Ain't Markup Language*) is a **textual format**, easily
readable by both humans and machines, used to represent structured data and widely
used for data exchange.

### Key features

- **Simplicity and readability**: the syntax is minimal and intuitive.
- **Indentation-based**: the data structure is determined by spaces, not by brackets or tags.
- **Support for common data types**: strings, numbers, booleans, lists, dictionaries (maps/objects).
- **Compatibility**: often used as a more readable alternative to JSON and XML.

### Example

```yaml
person:
  name: John Doe
  age: 30
  address:
    street: 123 Main St
    city: Example City
```

### Fundamental YAML rules

1. **Indentation with spaces**: The structure is defined by spaces at the beginning of lines (typically 2).
   ```yaml
   person:
    name: Anna
    age: 28
   ```
2. **Comments**: the `#` character is interpreted as a comment, and any text after it
   is ignored.
   ```yaml
   person:     # add new person
     name: Anna
     age: 28
   ```
3. **Key–value pairs**: Keys must be unique at the same level.
   In the previous example, `name` and `age` are keys, while `Anna` and `28` are values.
   Each `person` can have only one `name` and one `age`.
4. **Data types**:
   We can represent strings (also multiline), numbers, boolean values (true/false),
   null values (`null`).
5. **Lists**: Each list element starts with `-` followed by a space.
   ```yaml
   person:
     name: Anna
     age: 28
     languages:
       - Italian
       - English
       - French
   ```
6. **Multiline strings**:
   ```yaml
   person:
     name: Anna
     age: 28
     biography: |
       This biography of Anna will preserve line breaks.
       We can write text on multiple lines.
     short-bio: >
       This biography of Anna is
       instead wrapped only to improve
       readability in yaml.
   ```

## The content of a construction in `.yaml` format

```yaml

id: 68                                  # integer (for now chosen arbitrarily)
                                        # that uniquely identifies the construction

name: salta fuori che V                 # "human-readable" name of the construction
                                        # (to remind us what we're talking about)

cxn-machine-readable: cxn_68.conllc     # reference to a file we'll talk about shortly

definition: |                           # string describing the construction
    A new piece of information comes to the speaker's knowledge from an external source.
    The information acquired is often unexpected or contradicts the speaker's expectations on the state of affairs, thus generating surprise in the speaker.
    However, since the moment of acquisition and the moment of enunciation are distinct, this construction does not convey that the speaker is currently surprised, but it is used to convey or generate surprise in the audience.

restrictions: |                         # description of the restrictions that apply to the construction
    The main verb saltare fuori is always impersonal, so it has no subject and it is always found in the 3rd person singular.
    The verb in the complement clause is always in a finite form.

coll-preferences:                       # description of collocational preferences

usage:                                  # description of collocational preferences

form-tags:                              # tags describing the construction from a formal point of view
                                        # (constructions and strategies in MoCCa)
    - cc:cxn:complement-clause-construction
    - impersonal construction


function-tags:                          # tags describing the construction from a functional point of view
                                        # (meanings and information packaging in MoCCa)
    - cc:sem:evidentiality
    - cc:sem:mirative


complexity-level:                       # complexity level of the construction
    - clause

category-tags:                          # output category of the construction
    - not applicable

schematicity: partially filled/schematic # level of schematicity

cefr-level:                             # CEFR

horizontal-links:                       # horizontal and vertical links
    - 167
vertical-links:

examples:                               # IDs of sentences in which the construction occurs (wait for it)
    - 1_Paisà_FP06072024
    - 2_Paisà_FP06072024
    - 3_Paisà_FP06072024
    - 4_Paisà_FP06072024
    - 5_Paisà_FP06072024

references:                             # possible bibliographic reference
    - Pisciotta2023confini

collector: Flavio                       # your username

note: |                                 # further info
    This construction can have both an evidential and a mirative reading, depending on the surrounding context.
    It is often found in adversative (example1, example5), temporal, or more generally, coordinate clauses (example3), which favour a mirative 'counterexpectation' reading (i.e., the event or state in the complement clause is in contrast with the speaker's expectations).
    More rarely, the external source of information is specified in the context, triggering an evidential interpretation (i.e., the speaker gets to know something from a source).
```

### How to fill in this file?

No panic! It's not important that all fields are completed right away.

What matters is that the `.yaml` file is well-formed in the end.

For more information on how to fill in individual fields: [tentative wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.-Constructicon-entries:-definition-of-the-fields)
