---
title: Semantic features
parent: Guide
nav_order: 5
---

# Semantic features (SEM_FEATS)

The tagsets used to fill the **SEM_FEATS** field, described in the
[CoNLL-C field reference]({% link guide/conllc-fields-reference.md %}#sem_feats). Sourced from the
project's [wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.1.1.-Semantic-features).

## OntoClass

The ontological class for nouns and verbs. We use the
[Topics](https://omwn.org/doc/topics.html) of Open Multilingual Wordnet — also known as
[lexicographer files](https://wordnet.princeton.edu/documentation/lexnames5wn) in Princeton
WordNet. Not used for adjectives and adverbs, since no such hierarchy exists for those classes.

| POS | Topic | Abbr. | Definition |
|---|---|---|---|
| noun | Tops | top | unique beginner for nouns |
| noun | act | act | nouns denoting acts or actions |
| noun | animal | anm | nouns denoting animals or animal parts |
| noun | artifact | art | nouns denoting man-made objects |
| noun | attribute | att | nouns denoting attributes of people and objects |
| noun | body | bod | nouns denoting human body parts |
| noun | cognition | cog | nouns denoting cognitive processes and contents |
| noun | communication | com | nouns denoting communicative processes and contents, including languages and computation |
| noun | event | evt | nouns denoting natural events |
| noun | feeling | flg | nouns denoting feelings and emotions |
| noun | food | fod | nouns denoting foods and drinks |
| noun | group | grp | nouns denoting groupings of people or objects |
| noun | location | loc | nouns denoting spatial position |
| noun | motive | mtv | nouns denoting goals |
| noun | object | obj | nouns denoting natural objects (not man-made) |
| noun | person | per | nouns denoting people |
| noun | phenomenon | phn | nouns denoting natural phenomena |
| noun | plant | pln | nouns denoting plants or plant parts |
| noun | possession | pos | nouns denoting possession and transfer of possession |
| noun | process | prc | nouns denoting natural processes |
| noun | quantity | qnt | nouns denoting quantities and units of measure |
| noun | relation | rln | nouns denoting relations between people, things, or ideas |
| noun | shape | shp | nouns denoting two- and three-dimensional shapes |
| noun | state | stt | nouns denoting stable states of affairs |
| noun | substance | sub | nouns denoting substances |
| noun | time | tim | nouns denoting time and temporal relations |
| adj | all | all | all adjective clusters |
| adj | pert | prt | relational adjectives (pertainyms) |
| adj | ppl | ppl | participial adjectives |
| verb | body | bod | verbs of grooming, dressing and bodily care |
| verb | change | chn | verbs of size, temperature change, intensifying, etc. |
| verb | cognition | cog | verbs of thinking, judging, analyzing, doubting |
| verb | communication | com | verbs of telling, asking, ordering, singing |
| verb | competition | cmp | verbs of fighting, athletic activities |
| verb | consumption | con | verbs of eating and drinking |
| verb | contact | cnt | verbs of touching, hitting, tying, digging |
| verb | creation | crt | verbs of sewing, baking, painting, performing |
| verb | emotion | emo | verbs of feeling |
| verb | motion | mot | verbs of walking, flying, swimming |
| verb | perception | pcp | verbs of seeing, hearing, feeling |
| verb | possession | pos | verbs of buying, selling, owning |
| verb | social | soc | verbs of political and social activities and events |
| verb | stative | stv | verbs of being, having, spatial relations |
| verb | weather | wet | verbs of raining, snowing, thawing, thundering |

## Aktionsart

The aktionsart of verbs, using the [UniMorph](https://unimorph.github.io/doc/unimorph-schema.pdf)
label scheme, distinguishing between traits and classes.

Traits:

| Trait | Label | Definition |
|---|---|---|
| Atelic | ATEL | The event has no terminal point/culmination. |
| Durative | DUR | The event can extend over a time span. |
| Dynamic | DYN | The event is dynamic (i.e. it is not a static situation). |
| Punctual | PCT | The event does not extend over a time span, has no duration. |
| Telic | TEL | The event has a terminal point/culmination. |

Classes (and their corresponding trait combinations):

| Class | Label | Traits |
|---|---|---|
| Accomplishment | ACCMP | DYN, TEL, DUR |
| Achievement | ACH | DYN, TEL, PCT |
| Activity | ACTY | DYN, ATEL, DUR |
| Semelfactive | SEMEL | DYN, ATEL, PCT |
| Stative | STAT | ATEL, DUR |

An element can be *constrained* to a single class, but in some cases it's useful to specify just
a trait, so as to include every class that shares it.

## Adjectives and adverbs

There's no single agreed-upon semantic classification for Italian adjectives and adverbs yet.
For now:

- **Adjectives** use [Dixon's (2004)](http://www.lrec-conf.org/proceedings/lrec2000/pdf/129.pdf)
  semantic classes:

  | Class | Examples |
  |---|---|
  | dimension | *grande* 'big', *piccolo* 'small', *lungo* 'long', *alto* 'tall', *corto* 'short' |
  | age | *nuovo* 'new', *vecchio* 'old', *giovane* 'young' |
  | value | *buono* 'good', *atroce* 'atrocious', *perfetto* 'perfect', *necessario* 'necessary', *strano* 'strange' |
  | colour | *rosso* 'red', *giallo* 'yellow', *blu* 'blue' |
  | physical_property | *duro* 'hard', *pesante* 'heavy', *umido* 'wet', *forte* 'strong', *pulito* 'clean' |
  | human_propensity | *geloso* 'jealous', *intelligente* 'intelligent', *felice* 'happy', *orgoglioso* 'proud', *ansioso* 'anxious' |
  | speed | *veloce* 'fast', *lento* 'slow' |
  | difficulty | *difficile* 'difficult, hard', *facile* 'easy' |
  | similarity | *simile* 'similar', *diverso* 'different' |
  | qualification | *vero* 'true', *comune* 'common', *corretto* 'correct', *normale* 'normal', *ragionevole* 'sensible', *appropriato* 'appropriate' |
  | quantification | *alcuni* 'some', *tutto/tutti* 'all', *poco/pochi* 'few' |
  | position | *vicino* 'near', *distante* 'distant' |
  | cardinal_number | *primo* 'first', *ultimo* 'last' |

- **Adverbs** use a semantic classification adapted from the
  [Adjective-Adverb Interfaces in Romance](https://gams.uni-graz.at/context:aaif) project (which
  doesn't itself include Italian data):

  | Class | Definition |
  |---|---|
  | manner | Adverbs that characterize a manner-property of an element |
  | quantity | Quantify on a scale or a semantic characteristic, or the degree of a semantic property expressed by the segment they modify |
  | time | Adverbs expressing temporal circumstances |
  | location | Adverbs expressing a local circumstance of the event expressed |
  | discourse | Adverbs expressing metalinguistic, pragmatic and/or discursive extra-propositional characterizations or speaker attitudes |
  | specification | Focus adverbs expressing a semantic specification of the segment they modify; their syntactic scope is mostly a noun or any verbless syntagm |

  Both classifications for adjectives and adverbs are still under discussion; other options
  considered for adjectives include ItalWordNet's adjective roots and the PAROLE-SIMPLE-CLIPS
  ontology.
