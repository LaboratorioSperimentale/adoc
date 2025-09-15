# Formalizzare una costruzione per ItCon: una guida pratica

ItCon si pone come obiettivo quello di essere un Constructicon Machine Readable.

Si compone di diversi elementi che interagiscono tra loro per poter consultare ed aggiornare
il constructicon secondo molteplici casi d'uso.

In particolare:

- un database di costruzioni
- un grafo che organizza le costruzioni in un network
- un corpus di esempi incrementalmente annotati
- un'interfaccia per il querying e la visualizzazione

Per fare sì che questo sia possibile, è necessario definire con precisioni l'oggetto-costruzione,
che rappresenta il nucleo della risorsa.

## Identikit di una costruzione

Ogni costruzione in ItCon è definita da un file principale, in formato `.yaml`.

### Cos’è YAML?

**YAML** (acronimo ricorsivo di YAML Ain’t Markup Language) è un **formato testuale**, facilmente
leggibile sia dagli umani che dalle macchine, usato per rappresentare dati strutturati e molto
diffuso nello scambio di dati.

#### Caratteristiche principali

- Semplicità e leggibilità: la sintassi è minimale e intuitiva.
- Basato sull’indentazione: la struttura dei dati è determinata dagli spazi, non da parentesi o tag.
- Supporto a tipi di dato comuni: stringhe, numeri, booleani, liste, dizionari (mappe/oggetti).
- Compatibilità: spesso usato come alternativa più leggibile a JSON e XML.

#### Esempio

```yaml
person:
  name: John Doe
  age: 30
  address:
    street: 123 Main St
    city: Example City
```

#### Regole fondamentali di YAML

1. Indentazione con spazi: La struttura è definita dagli spazi all’inizio delle righe (tipicamente 2).
   ```yaml
   persona:
    nome: Anna
    età: 28
   ```
2. Commenti: il carattere `#` viene interpretato come commento, e qualsiasi testo dopo di esso
   viene ignorato
   ```yaml
   persona:     # inserire nuova persona
     nome: Anna
    età: 28
   ```
3. Coppie chiave–valore: Le chiavi devono essere uniche nello stesso livello.
   Nell'esempio precedente, `nome` e `età` sono chiavi, mentre `Anna` e `28` sono valori.
   Ogni `persona` può avere un solo `nome` e una sola `età`
4. Tipi di dato:
   Possiamo rappresentare stringhe (anche su più righe), numeri, valori booleani (vero/falso),
   valori nulli (`null`).
5. Liste: Ogni elemento di lista inizia con - seguito da uno spazio.
  ```yaml
  persona:
    nome: Anna
    età: 28
    lingue:
      - italiano
      - inglese
      - francese
   ```
6. Stringhe su più righe:
  ```yaml
  persona:
    nome: Anna
    età: 28
    biografia: |
      Questa biografia di Anna manterrà i ritorni a capo.
      Possiamo scrivere un testo su più righe.
    short-bio: >
      Questa biografia di Anna viene
      invece spezzata solo per migliorarne
      la leggibilità nello yaml.
  ```

### Il contenuto di una costruzione in formato `.yaml`

```yaml

id: 68                                  # numero intero (per ora scelto a caso)
                                        # che identifica univocamente la costruzione

name: salta fuori che V                 # nome "human-readable" della costruzione
                                        # (per ricordarci di cosa stiamo parlando)

cxn-machine-readable: cxn_68.conllc     # riferimento a un file di cui parleremo tra poco

definition: |                           # stringa che descrive la costruzione
    A new piece of information comes to the speaker's knowledge from an external source.
    The information acquired is often unexpected or contradicts the speaker's expectations on the state of affairs, thus generating surprise in the speaker.
    However, since the moment of acquisition and the moment of enunciation are distinct, this construction does not convey that the speaker is currently surprised, but it is used to convey or generate surprise in the audience.

restrictions: |                         # descrizione delle restrizioni che si applicano alla costruzione
    The main verb saltare fuori is always impersonal, so it has no subject and it is always found in the 3rd person singular.
    The verb in the complement clause is always in a finite form.

coll-preferences:                       # descrizione delle preferenze collocazionali

usage:                                  # descrizione delle preferenze collocazionali

form-tags:                              # tag che descrivono la costruzione dal punto di vista formale
                                        # (constructions and strategies in MoCCa)
    - cc:cxn:complement-clause-construction
    - impersonal construction


function-tags:                          # tag che descrivono la costruzione dal punto di vista formale
                                        # (meanings and information packaging in MoCCa)
    - cc:sem:evidentiality
    - cc:sem:mirative


complexity-level:                       # livello di complessità della costruzione
    - clause

category-tags:                          # categoria di output della costruzione
    - not applicable

schematicity: partially filled/schematic # livello di schematicità

cefr-level:                             # CEFR

horizontal-links:                       # link orizzontali e verticali
    - 167
vertical-links:

examples:                               # id di frasi in cui c'è la costruzione (wait for it)
    - 1_Paisà_FP06072024
    - 2_Paisà_FP06072024
    - 3_Paisà_FP06072024
    - 4_Paisà_FP06072024
    - 5_Paisà_FP06072024

references:                             # eventuale riferimento bibliografico
    - Pisciotta2023confini

collector: Flavio                       # il vostro username

note: |                                 # ulteriori info
    This construction can have both an evidential and a mirative reading, depending on the surrounding context.
    It is often found in adversative (example1, example5), temporal, or more generally, coordinate clauses (example3), which favour a mirative 'counterexpectation' reading (i.e., the event or state in the complement clause is in contrast with the speaker's expectations).
    More rarely, the external source of information is specified in the context, triggering an evidential interpretation (i.e., the speaker gets to know something from a source).
```

#### Come compilare questo file?

Niente panico! Non è importante che tutti i campi vengano compilati subito.

Potete partire dal file [xxx]() e cercare di compilarlo al meglio per ciò che riuscite.
L'importante è che alla fine il file `.yaml` sia ben formato.

Per maggiori info su come compilare i singoli campi: [tentative wiki](https://github.com/LaboratorioSperimentale/adoc/wiki/3.-Constructicon-entries:-definition-of-the-fields)

## `conll-c`, `conllu-c` e interoperabilità con UD

Guardiamo adesso nello specifico ai campi `cxn-machine-readable:` e `examples` del file `yaml`.

Sebbene le proprietà formali (i.e., morfosintattiche) siano solo una parte degli elementi necessari
a rappresentare una costruzione, la quasi totalità dei corpora a nostra disposizione si basa
su annotazioni di questo tipo.

Questo implica due cose:

- abbiamo moltissimi tool che ci permettono di manipolare le proprietà formali e strutturali
  annotate sulle risorse
- se speriamo di avvalerci del popolamento automatico di ItCon in futuro, dobbiamo capire come
  sfruttare al meglio l'annotazione che abbiamo già a dispoizione

Nel caso di ItCon, abbiamo scelto il formalismo offerto da [**Universal Dependencies**]() per una
serie di ragioni:

- formalismo sintattico 'light'
- compatibilità cross-linguistica
- grande disponibilità di tool
- interoperabilità con [**grew match**]()
- accuratezza dell'annotazione automatica

Abbiamo quindi sviluppato due formati (`CoNLL-C` e `CoNLL-Uc`) per poter rappresentare il constructicon
in modo interoperabile con le risorse UD e allo stesso tempo modellare lo sviluppo della risorsa
in modo indipendente e machine readable.

### Il formato [CoNLL-U](https://universaldependencies.org/format.html)

I corpora UD sono annotati in un formato tabulare.

Una treebank è costituita da una sequenza di frasi: [esempio](https://github.com/UniversalDependencies/UD_Italian-MarkIT/blob/master/it_markit-ud-test.conllu)

Ogni frase contiene:

- righe relative a parole, costituite da 10 campi separati da tabulazione. Ogni campo esprime un'annotazione
  o una proprietà relativa alla parola
- commenti e metadati (identificati da '#')

Ogni frase rappresenta un albero:
![Esempio CoNLL-U](84_0.svg "Esempio CoNLL-U")

## Il formato CoNLL-C

In ItCon ad ogni costruzione è associato un file di formato `.conllc`.

CoNLL-C si basa sulle guidelines CoNLL-U e le estende per poter rappresentare i vincoli richiesti
dalla nostra rappresentazione.

Per iniziare possiamo pensare a una costruzione come definita da una [catena](osborne-catenae.pdf)
su un albero a dipendenze, ovvero un insieme di nodi legati insieme da relazioni sintattiche.

![Esempio CoNLL-U](10107_0.svg "Esempio CoNLL-U")

![Esempio CoNLL-U](1087_0.svg "Esempio CoNLL-U")

![Esempio CoNLL-U](10587_0.svg "Esempio CoNLL-U")

Vogliamo rappresentare la nostra costruzione come un oggetto del genere:

![Esempio CoNLL-U](cxn.svg "Esempio CoNLL-U")

### I campi in CoNLL-C

#### La base CoNLL-U

Come in CoNLL-U, anche nel nostro formato si distinguono due tipi di righe:

- righe che rappresentano elementi minimi della costruzione (tipicamente, parole), le cui caratteristiche
  sono espresse in campi delimitati da tabulazione
- righe introdotte da '#', che rappresentano proprietà della costruzione nella sua interezza.

Occupiamoci delle righe-elemento e dei loro campi.
La costruzione precedente, guardata in formato tabulare, assume questo aspetto:

ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | -------
1 | _ | _ | NOUN | S | Number=Sing | 4 | obl | _ | _
2 | dopo | dopo | ADP | E | _ | 3 | case | _ | _
3 | _ | _ | NOUN | S | Number=Sing | 1 | nmod | _ | _
4 | _ | _ | _ | V | _ | 0 | root | _ | _

In CoNLL-C ci concentriamo solo sugli elementi interni della costruzione, che avrà quindi 3 elementi
(invece di 4).
L'idea di base è usare i campi per esprimere le restrizioni che la costruzione deve rispettare

- il campo **ID** è costituito da lettere invece che da numeri. Questo perchè in CoNLL-U i numeri
  indicano anche che gli elementi devono trovarsi in quell'ordine e che gli elementi devono essere
  adiacenti. Nel nostro caso, vogliamo che la struttura dia la possibilità di non fissare l'ordine o
  di inserire altro materiale tra un elemento e l'altro della costruzione. Il campo ID è l'unico campo
  obbligatorio del formato, per tutti gli altri è possibile inserire il valore "_" per segnalare che
  nessuna restrizione è imposta sul campo
- il campo **form** va compilato nel caso in cui la forma sia fissa. Ad esempio, nella costruzione
  di cui sopra (N dopo N), "dopo" è un token fissato a livello di forma.
  Il campo form può essere espresso tramite espressione regolare.
- il campo **lemma** esprime restrizioni a livello di lemma. Ad esempio, nella costruzione
  "salta fuori che X", il primo elemento ("salta") può variare nel paradigma del lemma "saltare" che
  è la restrizione che ci interessa fissare
- il campo **upos** esprime restrizoni a livello di parte del discorso e contiene valori
  dall'[inventario](https://universaldependencies.org/u/pos/index.html) universal dependencies
- il campo **feats** contiene annotazioni sulle [features morfologiche](https://universaldependencies.org/u/feat/index.html)
  (es. restrizioni su genere, numero, tempo e modo dei verbi...)
- il campo **head** contiene uno degli identificatori nel campo ID, '0' per la *testa* della costruzione
- il campo **deprel** contiene valori dell'[inventario](https://universaldependencies.org/u/dep/index.html)
  universal dependencies, *root* per la testa della costruzione

Fin qui abbiamo espresso sostanzialmente lo stesso formato visto sopra, con minime modifiche:

ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL
------- | ------- | ------- | ------- | ------- | ------- | -------
A | _ | _ | NOUN | Number=Sing | 0 | root
B | dopo | dopo | ADP | _ | C | case
C | _ | _ | NOUN | Number=Sing | A | nmod

#### Restrizioni ulteriori

Iniziamo ora con restrizioni aggiuntive che allontanano il nostro formato dal formato CoNLL-U

- una prima differenza riguarda l'eventuale presenza di una restrizione esterna sulla dipendenza.
  Nel nostro caso, la costruzione N dopo N che vogliamo formalizzare appare come modificatore
  nel contesto più ampio della frase. Infatti, negli esempi sopra, 'ora', 'giorno' e 'settore'
  sono legati dalla relazione *obl* a un altro elemento della frase.
  Possiamo esprimere questa restrizione esterna specificando la relazione *root* e indicando
  **root:obl** nel campo 'DEPREL' dell'elemento A.
- così formalizzata la nostra costruzione esprime più pattern di quelli che vogliamo.
  La costruzione N dopo N, infatti, prevede che i due N coincidano. Possiamo esprimere questa
  restrizione nel campo **IDENTITY**, che ha la seguente sintassi: `field_name:ID`.

  ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY
  ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------
  A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C
  B | dopo | dopo | ADP | _ | C | case | _
  C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A

  Nello stesso modo si possono esprimere anche vincoli di agreement (es. Soggetto e Verbo devono
  concordare in numero).
- Nel caso della costruzione N dopo N, dobbiamo considerare altri aspetti (in questo caso, parzialmente
  coincidenti)
  ![Esempio CoNLL-U](1444_0.svg "Esempio CoNLL-U")
  Da un lato la costruzione prevede che i tre elementi siano tutti adiacenti e non ci sia materiale
  nè tra N e 'dopo', nè tra 'dopo' e N.
  Questo possiamo esprimerlo nel campo **ADJACENCY**: se nel campo adiancency dell'elemento X compare
  l'ID Y, significa che X deve immediatamente precedere Y nella frase.
  Un altro aspetto spesso legato all'esistenza di altro materiale è la possibilità che gli elementi
  della costruzione presentino altre modificazioni.

  ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY
  ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------ | ------
  A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _
  B | dopo | dopo | ADP | _ | C | case | _ | A
  C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B

  Allo stesso modo possiamo imporre restrizioni sul tipo di altre dipendenze che l'elemento ha.
  Ad esempio in questo caso vogliamo filtrare casi del tipo "casa sua dopo casa mia" che non sono
  istanze della N dopo N che cerchiamo.
  Questo tipo di constraint va riportato nel campo **EXCLUSION**, la cui sintassi è:
  `KEYWORD:FIELD=VALUE`.
  Al momento l'unica keyword implementata è `CHILDREN`, per indicare che il tipo di relazioni che
  vogliamo escludere. Nel nostro caso, vogliamo che entrambi i nomi della costruzione non abbiano,
  ad esempio, aggettivi a modificarli: possiamo esprimerlo con il constraint `CHILDREN:DEPREL=amod`.

  ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION
  ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------ | ------ | ------
  A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _ | CHILDREN:DEPREL=amod
  B | dopo | dopo | ADP | _ | C | case | _ | A | _
  C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B | CHILDREN:DEPREL=amod

#### Restrizioni semantiche

#### Precisazioni sulla sintassi dei campi

## Morfologia

## Esempi
