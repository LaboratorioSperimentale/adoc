---
title: Semantic roles
parent: Guide
nav_order: 6
---

# Semantic roles (SEM_ROLES)

The role hierarchy used to fill the **SEM_ROLES** field, described in the
[CoNLL-C field reference]({% link guide/conllc-fields-reference.md %}#sem_roles). Adapted from the
[Unified Verb Index (UVI)](https://uvi.colorado.edu/references_page#themRoles) reference page —
sourced from the project's
[wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.1.2.-Semantic-roles), which is
itself the authority for definitions quoted here.

Compared to the original UVI tagset, a few roles were dropped: *Locus* (no UVI definition, and
redundant with *Location*), *Maleficiary* (too fine-grained a distinction from *Beneficiary*),
and the *Co-\** roles (*Co-agent*, *Co-patient*, *Co-theme*, *Subeventuality* — a second
participant sharing another's role, judged unlikely to be needed in abstract/semi-schematic
constructions). *Initial_location* and *Destination* were split by whether they occur in stative
or dynamic events.

## 1. Affector

### 1.1 Causer
An actor in an event that initiates and effects the event and that exists independently of the
event. If the Causer is animate and volitional, use **Agent** (1.1.1) instead.

> *Il fulmine ha bruciato l'albero.* — 'The lightning burnt down the tree.'

#### 1.1.1 Agent
An actor in an event who initiates and carries out the event intentionally or consciously, and
who exists independently of the event.

> *Il postino mi consegnò una lettera.* — 'The postman handed me a letter.'

### 1.2 Stimulus
A cause in an event that elicits an emotional or psychological response. Specific to
experiential events, involving both physical perception and mental/internal states.

> *Ieri ho visto l'arcobaleno.* — 'Yesterday I saw a rainbow.'
>
> *A Garfield piacciono le lasagne.* — 'Garfield likes lasagna.'

### 1.3 Precondition
An event or state of affairs that precedes or partially precedes another event or state and is
necessary for it to occur. Both nouns and subordinate clauses can be tagged as Precondition.

> *Una parata del portiere ha salvato il risultato.* — 'A save by the goalkeeper secured the
> result.'

## 2. Undergoer

### 2.1 Pivot
A theme that participates in an event with another theme unequally and is much more central to
the event — e.g. the possessor in possessive constructions, or the comparee in comparative
constructions.

### 2.2 Instrument
An undergoer that is manipulated by an agent, with which an intentional act is performed; exists
independently of the event.

### 2.3 Patient
An undergoer that is usually structurally changed (e.g. a change of state or condition); often
acted upon by an agent; causally involved or directly affected by other participants; exists
independently of the event.

#### 2.3.1 Experiencer
A Patient aware of the event undergone, often involving an emotional or psychological response
elicited by a Stimulus (specific to perception events).

### 2.4 Theme
An undergoer central to an event or state that has no control over how the event occurs, is not
structurally changed by it, and/or is characterized as being in a certain position or condition
throughout the state.

#### 2.4.1 Topic
A Theme characterized by information content.

#### 2.4.2 Asset
A Theme considered valuable to one or more participants in the event, especially money.

### 2.5 Beneficiary
An undergoer in a state or event that is (potentially) advantaged or disadvantaged by it.

### 2.6 Eventuality
An event, expressed either as a secondary predication or by an event noun (no definition given
in UVI itself).

## 3. Property

### 3.1 Attribute
A circumstance that is a property of an entity or entities, as opposed to the entity itself.

### 3.2 Manner
The way or style of performing an action, or the degree/strength of a cognitive or emotional
state.

### 3.3 Value
A place along a formal scale.

#### 3.3.1 Extent
A value indicating the amount of measurable change to a participant over the course of the
event.

##### 3.3.1.1 Duration
Length or extent of time.

## 4. Place

### 4.1 Location
A place that is concrete.

#### 4.1.1 Axis
The point or object around which the Theme travels in elliptical motion.

#### 4.1.2 Initial_location_st
A Source indicating the concrete, physical location where an event begins or a state becomes
true.

> *L'autostrada va da Milano a Napoli.* — 'The motorway runs from Milan to Naples.'

#### 4.1.3 Destination_st
A Goal that is a concrete, physical location.

### 4.2 Source
The starting point (possibly metaphoric) of an action; exists independently of the event.

#### 4.2.1 Initial_location_dyn
Source in a dynamic event.

#### 4.2.2 Material
A Patient existing at the starting point of the action (inherited from Source), transformed
through the event into a new entity; concrete or abstract.

#### 4.2.3 Initial_state
A Source indicating the state in which an entity begins.

### 4.3 Goal
The end point (possibly metaphoric) of the action; exists independently of the event.

#### 4.3.1 Destination_dyn
Goal in a dynamic event.

##### 4.3.1.1 Recipient
An animate end point of the action (a subtype of Destination).

#### 4.3.2 Result
A Goal that comes into existence through the event.

##### 4.3.2.1 Product
A concrete object that is the end point of the action and comes into existence through it (a
subtype of Result).

### 4.4 Trajectory
The path or 'region' the motion traverses when the motion event expresses a change of location.

## UVI and Comparative Concepts alignment

A tentative mapping between MoCCa comparative concepts and UVI semantic roles, so that
constructions can eventually be aligned with other Constructicons using MoCCa. Only semantic
roles listed in Croft's (2023) *Morphosyntax* glossary are included.

| MoCCa semantic role | UVI semantic role(s) |
|---|---|
| [beneficiary](https://comparative-concepts.github.io/cc-database/#sem:beneficiary) | Beneficiary |
| [comparee](https://comparative-concepts.github.io/cc-database/#sem:comparee) | Pivot |
| [experiencer](https://comparative-concepts.github.io/cc-database/#sem:experiencer) | Experiencer |
| [expertum](https://comparative-concepts.github.io/cc-database/#sem:expertum) | — |
| [agent](https://comparative-concepts.github.io/cc-database/#sem:agent) | Agent |
| [cause](https://comparative-concepts.github.io/cc-database/#sem:cause) | Precondition |
| [causee](https://comparative-concepts.github.io/cc-database/#sem:causee) | Agent, Causer (?) |
| [causer](https://comparative-concepts.github.io/cc-database/#sem:causer) | Causer |
| [comitative](https://comparative-concepts.github.io/cc-database/#sem:comitative) | *(dropped: Co-agent/Co-patient/Co-theme)* |
| [force](https://comparative-concepts.github.io/cc-database/#sem:force) | Causer |
| [instrumental](https://comparative-concepts.github.io/cc-database/#sem:instrumental) | Instrument |
| [figure](https://comparative-concepts.github.io/cc-database/#sem:figure) | Theme |
| [ground](https://comparative-concepts.github.io/cc-database/#sem:ground) | Location |
| [maleficiary](https://comparative-concepts.github.io/cc-database/#sem:maleficiary) | Beneficiary *(Maleficiary dropped)* |
| [patient](https://comparative-concepts.github.io/cc-database/#sem:patient) | Patient |
| [possessor role](https://comparative-concepts.github.io/cc-database/#sem:possessum-role) | Pivot |
| [possessum role](https://comparative-concepts.github.io/cc-database/#sem:possessum-role) | Theme |
| [recipient](https://comparative-concepts.github.io/cc-database/#sem:recipient) | Recipient |
| [standard](https://comparative-concepts.github.io/cc-database/#sem:standard) | Theme |
| [stimulus](https://comparative-concepts.github.io/cc-database/#sem:stimulus) | Stimulus |
| [theme](https://comparative-concepts.github.io/cc-database/#sem:theme) | Theme |

## Example: annotating SEM_ROLES

The Passive Construction with *venire* 'come' as auxiliary — the participant expressed by the
*da* N prepositional phrase could be an animate Affector (an Agent), an inanimate one (a Causer),
or an event (a Precondition). Since the role hierarchy lets us annotate at different levels of
generality, we can just use the most general applicable role, **Affector**:

```
ID    UD.FORM   LEMMA     UPOS                 ...    HEAD   DEPREL       ...   SEM_ROLES
A        _       _        NOUN, PROPN, PRON    ...    C      nsubj:pass   ...   Patient
B        _       venire   AUX                  ...    C      aux:pass     ...   //
C        _       _        VERB                 ...    0      root         ...   //
D        _       da       ADP                  ...    E      case         ...   //
E        _       _        NOUN, PROPN, PRON    ...    C      obl          ...   Affector
```
