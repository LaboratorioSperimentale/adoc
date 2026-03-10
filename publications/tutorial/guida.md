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
  Il campo form può essere espresso tramite espressione regolare (prefissando la stringa con r).
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
  A | _ | _ | NOUN | Number=Sing | 0 | root:obl | FORM=C
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

Spesso importanti restrizioni sulla produttività della costruzione provengono dal campo semantico
legato ad uno slot.
Sebbene UD non preveda annotazione di questo tipo, in CoNLL-C due campi (**SEM_FEATS** e **SEM_ROLES**)
sono dedicati a specificare restrizioni di questo tipo.

- Per le features semantiche (**SEM_FEATS**), è possibile specificare la classe ontologica per nomi e
  verbi (`OntoClass`), l'Aktionsart per i verbi (`Aktionsart`) e la classe da ontologie dedicate per
  aggettivi e avverbi (`AdjClass` e `AdvClass`).
  Se quindi ad esempio vogliamo formalizzare una sottocostruzione della costruzione precedente,
  restringendo la produttività ai nomi di tempo (ora dopo ora, giorno dopo giorno, ma escludendo
  settore dopo settore), possiamo esprimerlo così

  ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION | SEM_FEATS
  ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------ | ------ | ------ | ------
  A | _ | _ | NOUN | Number=Sing | 0 | root | FORM=C | _ | CHILDREN:DEPREL=amod | time
  B | dopo | dopo | ADP | _ | C | case | _ | A | _ | _
  C | _ | _ | NOUN | Number=Sing | A | nmod | FORM=A | B | CHILDREN:DEPREL=amod | time

- Similmente, possiamo annotae il ruolo semantico realizzato dagli elementi della costruzione,
  seguendo la tassonomia prevista da [Unified Verb Index](https://uvi.colorado.edu/references_page#ThematicRoleHierarchy)

#### Precisazioni sulla sintassi dei campi

Se pensiamo in termini di restrizioni, per poter esprimere al meglio le restrizioni possibili sugli
slot, abbiamo bisogno di introdurre alcune operazioni sui possibili valori:

- **disgiunzione**: se pensiamo alla costruzione "che X!", non possiamo esprimere la parte del discorso
  da attribuire a X con una sola etichetta. Vogliamo infatti rappresentare costrutti diversi, che
  includono sia aggettivi (Che bello!) sia nomi (Che noia!)
  Per esprimere la disgiunzione tra due valori ("ADJ" oppure "NOUN") possiamo in generale usare
  la virgola.

  ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION
  ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------ | ------ | ------
  A | che | che | DET | _ | B | det | _ | _ | _
  B | _ | _ | ADJ,NOUN | _ | 0 | root | _ | _ | _

  La disgiunzione può avvenire:
  - nel campo **LEMMA** (e.g., "che,qual")
  - per ogni feature morfosintattica (e.g. VerbForm=Fin,Part)
  - per la relazione di dipendenza *tranne root* (e.g., "det,amod")
  - per i semantic roles e le semantic features

- **negazione**: allo stesso modo, potremmo voler restringere la produttività escludendo un valore
  piuttosto che elencando i valori possibili (per esempio: lo slot può essere riempito da qualsiasi
  categoria tranne che un nome proprio). In questo caso usiamo il punto esclamativo per segnalarlo
  ("!PROPN")

  La negazione può avvenire:
  - nel campo **LEMMA** (e.g., "!che")
  - per ogni feature morfosintattica (e.g. VerbForm=!Fin)
  - per la relazione di dipendenza *tranne root* (e.g., "!det")
  - per i semantic roles e le semantic features

- **congiunzione**: nel caso delle features e dei filtri che vogliamo applicare (**EXCLUSION**),
  potremmo voler esprimere più di un constraint. Ad esempio un certo elemento deve essere un nome di
  genere femminile e numero singolare.
  In continuità con il formato CoNLL-U, questo viene espresso dal simbolo pipe (|, ad esempio
  Gender=Fem|Number=Sing).

Un altro aspetto da considerare è l'**opzionalità**. Nella costruzione sopra ("che bello!") potremmo
voler includere il punto esclamativo come opzionale. Per questo il campo **REQUIRED** può contenere
i valori 0 o 1.

## Morfologia

Le costruzioni che vogliamo rappresentare ovviamente non agiscono necessariamente a livello della
frase. Potrebbero interessare anche livelli inferiori, come ad esempio il livello morfologico,
o superiori, come il livello testuale.

Il formato CoNLL-C può essere utilizzato per costruzioni al livello morfologico.
In questo caso dobbiamo rappresentare gli elementi a livello morfologico (sotto il livello di
parola) che costituiscono la costruzione.

Prendiamo in considerazione il caso della costruzione "X-issimo", che genera i superlativi degli
aggettivi.
Possiamo modellare la costruzione nel seguente modo:

ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | IDENTITY | ADJACENCY | EXCLUSION
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------ | ------ | ------
A | r".*issim[oaie]" | _ | ADJ | Degree=Sup | 0 | root | _ | _ | _
A-1 | _ | _ | ADJ | _ | A | root/m | _ | _ | _
A-2 | _ | -issmo | BMORPH | _ | A-1 | der/m | _ | _ | _

Gli elementi morfologici sono caratterizzati da:

- ID composto da due componenti: lettera che identifica la parola a cui si riferiscono e un numero
  progressivo
- Come parte del discorso, gli elementi che esistono come lessemi liberi mantengono la loro parte
  del discorso, mentre le forme legate (affissi, affissoidi, forme combinatorie) sono annotate come
  BMORPH
- per le dipendenze, al livello di morfema introduciamo le seguenti relazioni:
  - root/m: la radice all'interno della costruzione morfologica. Nella derivazione corrisponde allo stemma, nella composizione corrisponde alla testa del composto.
  - der/m: la relazione che lega l'affisso derivazionale allo stemma
  - case/m: la relazione che lega il complemento alla testa nei composti subordinant (e.g., capostazione)
  - mod/m: la relazione che lega l'attributo alla testa nei composti attributivi (e.g., altopiano)
  - conj/m: la relazione che lega il secondo costituente al primo nei composti coordinanti (e.g., cartongesso)

## Variazione formale in CoNLL-C

Può capitare che i vincoli illustrati fin qui non bastino a rappresentare in modo soddisfacente la
costruzione in modo compatibile con Universal Dependencies, spesso a causa di variazioni
ortografiche o idiosincrasie del formato.

Ad esempio, la costruzione "semiX" o "similX" può essere istanziata sia in modo univerbato, sia con
la presenza di "-", sia tramite modificazione.

In questi casi, il file `conllc` può contenere più di una struttura.

## Esempi in CoNLL-Uc

Una volta che la formalizzazione è finita, possiamo utilizzarla per annotare istanze della
costruzione nei corpora a nostra disposizione, in particolare allineando i nostri elementi con
l'annotazione UD.

Come abbiamo visto, il formato CoNLL-U si compone di 10 colonne. A queste aggiungiamo un'ulteriore
colonna con la nostra annotazione.

Consideriamo il seguente esempio CoNLL-U:
```
# sent_id = 3214_it_postwita
# source = http://hdl.handle.net/11234/1-5502 UD_Italian-PoSTWITA/it_postwita-ud-train 3214
# text = Pensa se alla fine di tutto sto casino viene fuori che Borghezio è l'unico onesto
```

ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | -------
1 | Pensa | pensare | VERB | V | Mood=Imp\|Number=Sing\|Person=2\|Tense=Pres\|VerbForm=Fin | 0 | root | _ | _
2 | se | se | SCONJ | CS | _ | 10 | mark | _ | _
3-4 | alla | _ | _ | _ | _ | _ | _ | _ | _
3 | a | a | ADP | E | _ | 5 | case | _ | _
4 | la | il | DET | RD | Definite=Def\|Gender=Fem\|Number=Sing\|PronType=Art | 5 | det | _ | _
5 | fine | fine | NOUN | S | Gender=Fem\|Number=Sing | 10 | obl | _ | _
6 | di | di | ADP | E | _ | 9 | case | _ | _
7 | tutto | tutto | DET | DI | PronType=Ind | 9 | det:predet | _ | _
8 | sto | questo | DET | DD | PronType=Dem | 9 | det | _ | _
9 | casino | casino | NOUN | S | Gender=Masc\|Number=Sing | 5 | nmod | _ | _
10 | viene | venire | VERB | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 1 | ccomp | _ | CXN=167:A
11 | fuori | fuori | ADV | B | _ | 10 | advmod | _ | CXN=167:B
12 | che | che | SCONJ | CS | _ | 17 | mark | _ | CXN=167:C
13 | Borghezio | Borghezio | PROPN | SP | _ | 17 | nsubj | _ | _
14 | è | essere | AUX | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 17 | cop | _ | _
15 | l' | il | DET | RD | Definite=Def\|Number=Sing\|PronType=Art | 17 | det | _ | SpaceAfter=No
16 | unico | unico | ADJ | A | Gender=Masc\|Number=Sing | 17 | amod | _ | _
17 | onesto | onesto | ADJ | A | Gender=Masc\|Number=Sing | 10 | ccomp | _ | _

Avendo a disposizione una formalizzazione CoNLL-C per la costruzione "viene fuori che X" come di seguito:

ID | FORM | LEMMA | UPOS | FEATS | HEAD | DEPREL | REQUIRED | EXCLUSION | SEM_FEATS | SEM_ROLES | ADJACENCY | IDENTITY
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | -------- | -------- | --------
A | _ | venire | VERB | Number=Sing\|Person=3 | 0 | root | 1 | CHILDREN:DEPREL=nsubj | _ | _ | _ | _
B | fuori | fuori | ADV | _ | A | advmod | 1 | _ | _ | _ | _ | _
C | che | che | SCONJ | _ | D | mark | 1 | _ | _ | _ | _ | _
D | _ | _ | VERB,NOUN,ADJ | VerbForm=Fin | A | csubj,ccomp | 1 | _ | _ | Eventuality | _ | _

Possiamo procedere ad annotare la frase aggiungendo gli elementi necessari:

ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC | CONSTRUCTION
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | -------
1 | Pensa | pensare | VERB | V | Mood=Imp\|Number=Sing\|Person=2\|Tense=Pres\|VerbForm=Fin | 0 | root | _ | _ | _
2 | se | se | SCONJ | CS | _ | 10 | mark | _ | _ | _
3-4 | alla | _ | _ | _ | _ | _ | _ | _ | _ | _
3 | a | a | ADP | E | _ | 5 | case | _ | _ | _
4 | la | il | DET | RD | Definite=Def\|Gender=Fem\|Number=Sing\|PronType=Art | 5 | det | _ | _ | _
5 | fine | fine | NOUN | S | Gender=Fem\|Number=Sing | 10 | obl | _ | _ | _
6 | di | di | ADP | E | _ | 9 | case | _ | _ | _
7 | tutto | tutto | DET | DI | PronType=Ind | 9 | det:predet | _ | _ | _
8 | sto | questo | DET | DD | PronType=Dem | 9 | det | _ | _ | _
9 | casino | casino | NOUN | S | Gender=Masc\|Number=Sing | 5 | nmod | _ | _ | _
10 | viene | venire | VERB | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 1 | ccomp | _ | _ | 167:A
11 | fuori | fuori | ADV | B | _ | 10 | advmod | _ | _ | 167:B
12 | che | che | SCONJ | CS | _ | 17 | mark | _ | _ | 167:C
13 | Borghezio | Borghezio | PROPN | SP | _ | 17 | nsubj | _ | _ | _
14 | è | essere | AUX | V | Mood=Ind\|Number=Sing\|Person=3\|Tense=Pres\|VerbForm=Fin | 17 | cop | _ | _ | _
15 | l' | il | DET | RD | Definite=Def\|Number=Sing\|PronType=Art | 17 | det | _ | SpaceAfter=No | _
16 | unico | unico | ADJ | A | Gender=Masc\|Number=Sing | 17 | amod | _ | _ | _
17 | onesto | onesto | ADJ | A | Gender=Masc\|Number=Sing | 10 | ccomp | _ | | 167:D

Su una stessa frase e anche su uno stesso elemento possono essere presenti annotazioni di più costruzioni.
Quando questo accade, sono legate da pipe (|).

Nel caso delle costruzioni morfologiche, gli elementi al di sotto del livello di parola vanno aggiunti
all'esempio.

```
# sent_id = VIT-8523
# source = http://hdl.handle.net/11234/1-5502 UD_Italian-VIT/it_vit-ud-train VIT-8523
# text = Pochi, i cittadini di buona volontà, e seminascosti da un ingente presidio di poliziotti e di militari.
```

ID | FORM | LEMMA | UPOS | XPOS | FEATS | HEAD | DEPREL | DEPS | MISC | CONSTRUCTION
------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | -------
1 | Pochi | poco | PRON | PI | Gender=Masc\|Number=Plur\|PronType=Ind | 0 | root | _ | SpaceAfter=No | _
2 | , | , | PUNCT | FF | _ | 1 | punct | _ | _ | _
3 | i | il | DET | RD | Definite=Def\|Gender=Masc\|Number=Plur\|PronType=Art | 4 | det | _ | _ | _
4 | cittadini | cittadino | NOUN | S | Gender=Masc\|Number=Plur | 1 | appos | _ | _ | _
5 | di | di | ADP | E | _ | 7 | case | _ | _ | _
6 | buona | buono | ADJ | A | Gender=Fem\|Number=Sing | 7 | amod | _ | _ | _
7 | volontà | volontà | NOUN | S | Gender=Fem | 4 | nmod | _ | SpaceAfter=No | _
8 | , | , | PUNCT | FF | _ | 10 | punct | _ | _ | _
9 | e | e | CCONJ | CC | _ | 10 | cc | _ | _ | _
10 | seminascosti | seminascosto | ADJ | A | Gender=Masc\|Number=Plur | 1 | conj | _  | _ | 169a:A
10.1 | semi | semi | BMORPH | _ | _ | 10.2 | der/m | _ | _ | 169a:A.1
10.2 | nascosti | nascosto | ADJ | A | Gender=Masc\|Number=Plur | 10 | root/m | _ | _ | 169a:A.2
11 | da | da | ADP | E | _ | 14 | case | _ | _ | _
12 | un | uno | DET | RI | Definite=Ind\|Gender=Masc\|Number=Sing\|PronType=Art | 14 | det | _ | _ | _
13 | ingente | ingente | ADJ | A | Number=Sing | 14 | amod | _ | _ | _
14 | presidio | presidio | NOUN | S | Gender=Masc\|Number=Sing | 10 | obl | _ | _ | _
15 | di | di | ADP | E | _ | 16 | case | _ | _ | _
16 | poliziotti | poliziotto | NOUN | S | Gender=Masc\|Number=Plur | 14 | nmod | _ | _ | _
17 | e | e | CCONJ | CC | _ | 19 | cc | _ | _ | _
18 | di | di | ADP | E | _ | 19 | case | _ | _ | _
19 | militari | militare | NOUN | S | Gender=Masc\|Number=Plur | 16 | conj | _ | SpaceAfter=No | _
20 | . | . | PUNCT | FS | _ | 1 | punct | _ | _ | _

## E quindi come si fa?

A regime ci saranno degli step automatici nel processo e l'annotazione sarà mediata da un'interfaccia.
Per adesso, seguiamo questi step:

1. Creiamo il file `.yaml` per la nostra costruzione a partire dal template. Assegnamo un ID a caso.
   L'unico requisito è che non sia già stato scelto.
2. Compiliamo lo yaml per quanto possibile, e creiamo il corrispondente file `.conllc`
3. Proviamo a cercare alcuni esempi della costruzione che vogliamo formalizzare su grew match,
   su tutti i corpora italiani
4. Se non riusciamo a trovare esempi (i corpora sono relativamente piccoli),
   cerchiamo qualcosa di simile in lingue affini (es. altre lingue romanze o in generale lingue che
   parliamo e dove riusciamo a trovare una struttura simile)
5. Scegliamo la rappresentazione sintattica che ci sembra più fedele a ciò che vogliamo rappresentare
   e partiamo da quella per costruire il file CoNLL-C (può essere utile anche excel per compilare meglio
   il formato tabulare)
6. Cerchiamo degli esempi preferibilmente già nei corpora UD (tramite grew match).
   1. Se ne troviamo, salviamo l'esempio in un file dedicato e aggiungiamo l'annotazione degli elementi
   2. Se non troviamo nessun esempio già in UD, cerchiamolo in altre risorse. Possiamo parsarlo in UD
      usando strumenti come ad esempio [udpipe](https://lindat.mff.cuni.cz/services/udpipe/) o al minimo
      tokenizzarlo mettendo ogni token su una riga diversa. L'annotazione fornita da UDPipe probabilmente
      non sarà perfetta ma dovrebbe essere semplice da modificare. A quel punto possiamo aggiungere
      l'esempio in un file dedicato ed aggiungere l'annotazione relativa alla nostra costruzione.
7. Controlliamo che gli esempi già presenti per altre costruzioni non contengano anche esempi della nostra
   costruzione. In caso positivo, aggiungiamo l'annotazione del caso.