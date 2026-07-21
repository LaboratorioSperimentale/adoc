from collections import defaultdict
import networkx as nx
import re
import math
import os
import itertools

# --- 1. CONFIGURAZIONE PERCORSI E LIMITI ---

PATH_CONLLU = "../validated/examples.conllu"
PATH_CARTELLA_YAML = "../../../data/db_yaml"
PATH_OUTPUT_TXT = "catenae_ranking.txt"

MIN_NODI = 2 # min nodi della catena
MAX_NODI = 4 # max nodi della catena
TOP_N = 5                 # quante catenae rankate per cxn
LOWERCASE_FORM = True
DEBUG_ESPANSIONE = False  


# --- 2. DIZIONARIO DI SUPPORTO PER I NOMI DELLE CXN ---
cxn_names = {}

if os.path.exists(PATH_CARTELLA_YAML):
    for filename in os.listdir(PATH_CARTELLA_YAML):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            match = re.search(r'(cxn_\d+)', filename)
            if match:
                c_id = match.group(1)
                filepath = os.path.join(PATH_CARTELLA_YAML, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as yf:
                        content = yf.read()
                        name_match = re.search(r'^name:\s*(?:\|)?\s*\n(.*?)(?=\n\w+:|\Z)', content, re.DOTALL | re.MULTILINE)
                        if name_match:
                            raw_name = name_match.group(1)
                            lines = [line.strip() for line in raw_name.split("\n") if line.strip()]
                            clean_name = " ".join(lines).strip('"\'')
                            cxn_names[c_id] = clean_name
                        else:
                            inline_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
                            cxn_names[c_id] = inline_match.group(1).strip('"\'') if inline_match else "_"
                except Exception as e:
                    print(f"# Errore nella lettura di {filename}: {e}")
else:
    print(f"# ATTENZIONE: La cartella {PATH_CARTELLA_YAML} non esiste localmente.")

# --- 3. LETTURA E FILTRAGGIO DEL CORPUS ---
from conllu import parse

with open(PATH_CONLLU, "r", encoding="utf-8") as f:
    sentences = parse(f.read())

cxn_groups = defaultdict(list)
for sent in sentences:
    if sent.metadata.get("tags") in ["CONTEXT", "MORPHOLOGICAL", "DROP"]: continue
    sent_id = sent.metadata.get("sent_id", "")
    match = re.search(r'(cxn_\d+)', sent_id)
    if match: cxn_groups[match.group(1)].append(sent)

cxn_groups = {c_id: sents for c_id, sents in cxn_groups.items() if len(sents) > 1}

# --- 4. LOGICA GENERAZIONE E COMPOSIZIONE CATENE ANNOTATE ---
def genera_varianti_nodo(node_data):
    upos = node_data["upos"] or "_"
    lemma = node_data["lemma"] or "_"
    form = node_data["form"] or "_"
    return [f"FORM:{form}", f"LEMMA:{lemma}", f"UPOS:{upos}", "ANY"]


def crea_template_sottografo(subG, nodi_ordinati):
    struttura = []
    for i in range(1, len(nodi_ordinati)):
        u = nodi_ordinati[i]
        trovato = False
        for j in range(i):
            prec = nodi_ordinati[j]
            if subG.has_edge(prec, u):
                struttura.append((j, i, subG[prec][u]['deprel'], "->"))
                trovato = True
                break
            elif subG.has_edge(u, prec):
                struttura.append((j, i, subG[u][prec]['deprel'], "<-"))
                trovato = True
                break
        if not trovato:
            struttura.append((None, i, None, "??"))
    return struttura


def serializza_da_template(struttura, etichette):
    """Serializzazione 'interna' con frecce, usata solo per costruire la chiave
    di raggruppamento delle catenae (non finisce mai nell'output finale)."""
    parts = [etichette[0]]
    for (_, i, deprel, direz) in struttura:
        if direz == "->":
            parts.append(f"──({deprel})──> {etichette[i]}")
        elif direz == "<-":
            parts.append(f"<──({deprel})── {etichette[i]}")
        else:
            parts.append(f"?? {etichette[i]}")
    return " ".join(parts)


def estrai_catenae_tracciate(G):
    catene_mappa = defaultdict(list)
    underlying_graph = G.to_undirected()
    vicini_cache = {n: set(underlying_graph.neighbors(n)) for n in underlying_graph.nodes()}

    sottografi_validi = set()
    for u, v in underlying_graph.edges():
        sottografi_validi.add(frozenset([u, v]))

    correnti = list(sottografi_validi)
    for _ in range(3, MAX_NODI + 1):
        prossimi = set()
        for sg in correnti:
            vicini = set()
            for n in sg:
                vicini.update(vicini_cache[n])
            vicini -= sg

            for v in vicini:
                nuovo_sg = frozenset(list(sg) + [v])
                prossimi.add(nuovo_sg)

        sottografi_validi.update(prossimi)
        correnti = list(prossimi)

    sottografi_validi = [sg for sg in sottografi_validi if MIN_NODI <= len(sg) <= MAX_NODI]

    for nodes_set in sottografi_validi:
        nodi_ordinati = sorted(list(nodes_set))
        subG = G.subgraph(nodi_ordinati)

        struttura = crea_template_sottografo(subG, nodi_ordinati)
        varianti_per_nodo = [genera_varianti_nodo(G.nodes[n]) for n in nodi_ordinati]

        for combo_varianti in itertools.product(*varianti_per_nodo):
            stringa_chiave = serializza_da_template(struttura, combo_varianti)
            catene_mappa[stringa_chiave].append(nodi_ordinati)

    return catene_mappa


def trova_espansione_greedy(struttura_posizioni, istanze_correnti, graphs, total_sentences, debug=False):
    n_posizioni = len(struttura_posizioni)
    migliore = None  

    for pos_i in range(n_posizioni):
        for direzione in ("parent", "child"):
            opzioni_per_istanza = []
            fallito = False
            g_idx_mancante = None

            for g_idx in range(total_sentences):
                node_tuple = istanze_correnti[g_idx]
                G_inst = graphs[g_idx]
                nodo_corrente = node_tuple[pos_i]
                set_correnti = set(node_tuple)

                if direzione == "parent":
                    opzioni = [(p, G_inst[p][nodo_corrente]['deprel'])
                               for p in G_inst.predecessors(nodo_corrente)
                               if p not in set_correnti]
                else:
                    opzioni = [(c, G_inst[nodo_corrente][c]['deprel'])
                               for c in G_inst.successors(nodo_corrente)
                               if c not in set_correnti]

                if not opzioni:
                    fallito = True
                    g_idx_mancante = g_idx
                    break
                opzioni_per_istanza.append(opzioni)

            if fallito:
                if debug:
                    print(f"    [debug] pos={pos_i} dir={direzione}: nessun nodo disponibile "
                          f"nella frase idx={g_idx_mancante} -> posizione scartata")
                continue

            deprel_sets = [set(d for (_, d) in opz) for opz in opzioni_per_istanza]
            deprel_comuni = set.intersection(*deprel_sets)
            if not deprel_comuni:
                if debug:
                    print(f"    [debug] pos={pos_i} dir={direzione}: nodi presenti in tutte le frasi "
                          f"ma nessun deprel comune (deprel per frase: {deprel_sets}) -> posizione scartata")
                continue

            for deprel in deprel_comuni:
                nodi_scelti = []
                for g_idx, opz in enumerate(opzioni_per_istanza):
                    nodo_id = next(n_id for (n_id, d) in opz if d == deprel)
                    nodi_scelti.append((g_idx, nodo_id))

                forms = [graphs[g_idx].nodes[n_id]['form'] for g_idx, n_id in nodi_scelti]
                lemmas = [graphs[g_idx].nodes[n_id]['lemma'] for g_idx, n_id in nodi_scelti]
                upos_list = [graphs[g_idx].nodes[n_id]['upos'] for g_idx, n_id in nodi_scelti]

                if len(set(forms)) == 1:
                    label, spec = f"FORM:{forms[0]}", 3
                elif len(set(lemmas)) == 1:
                    label, spec = f"LEMMA:{lemmas[0]}", 2
                elif len(set(upos_list)) == 1:
                    label, spec = f"UPOS:{upos_list[0]}", 1
                else:
                    label, spec = "ANY", 0

                if debug:
                    print(f"    [debug] pos={pos_i} dir={direzione} deprel={deprel}: "
                          f"candidato valido, label={label} (forms={forms})")

                candidato = (spec, pos_i, direzione, deprel, label, nodi_scelti)
                if migliore is None or candidato[0] > migliore[0]:
                    migliore = candidato

    if migliore is None:
        return False, None, None

    spec, pos_i, direzione, deprel, label, nodi_scelti = migliore
    nuova_posizione_idx = n_posizioni
    nuova_struttura = [dict(p) for p in struttura_posizioni]

    if direzione == "parent":
        nuova_struttura.append({"label": label, "padre_idx": None, "deprel": None})
        nuova_struttura[pos_i]["padre_idx"] = nuova_posizione_idx
        nuova_struttura[pos_i]["deprel"] = deprel
    else:
        nuova_struttura.append({"label": label, "padre_idx": pos_i, "deprel": deprel})

    nuove_istanze = {}
    for g_idx, node_tuple in istanze_correnti.items():
        nodo_nuovo = next(n_id for gi, n_id in nodi_scelti if gi == g_idx)
        nuove_istanze[g_idx] = node_tuple + (nodo_nuovo,)

    return True, nuova_struttura, nuove_istanze


def ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences, debug=False):
    n = len(istanze_correnti[0])
    struttura = [{"label": None, "padre_idx": None, "deprel": None} for _ in range(n)]

    for i in range(n):
        padre_idx_comune, deprel_comune = None, None
        prima_istanza = True
        consistente = True

        for g_idx in range(total_sentences):
            node_tuple = istanze_correnti[g_idx]
            G_inst = graphs[g_idx]
            nodo_i = node_tuple[i]

            padre_trovato, deprel_trovato = None, None
            for j in range(n):
                if j == i: continue
                nodo_j = node_tuple[j]
                if G_inst.has_edge(nodo_j, nodo_i):
                    padre_trovato, deprel_trovato = j, G_inst[nodo_j][nodo_i]['deprel']
                    break

            if prima_istanza:
                padre_idx_comune, deprel_comune = padre_trovato, deprel_trovato
                prima_istanza = False
            elif padre_trovato != padre_idx_comune or deprel_trovato != deprel_comune:
                consistente = False
                if debug:
                    print(f"    [debug] posizione {i}: relazione non coerente tra le frasi "
                          f"(frase 0 -> padre_idx={padre_idx_comune}, deprel={deprel_comune}; "
                          f"frase {g_idx} -> padre_idx={padre_trovato}, deprel={deprel_trovato})")

        struttura[i]["padre_idx"] = padre_idx_comune if consistente else None
        struttura[i]["deprel"] = deprel_comune if consistente else None

    for i in range(n):
        forms = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['form'] for g_idx in range(total_sentences)]
        lemmas = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['lemma'] for g_idx in range(total_sentences)]
        upos_list = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['upos'] for g_idx in range(total_sentences)]

        if len(set(forms)) == 1:
            struttura[i]["label"] = f"FORM:{forms[0]}"
        elif len(set(lemmas)) == 1:
            struttura[i]["label"] = f"LEMMA:{lemmas[0]}"
        elif len(set(upos_list)) == 1:
            struttura[i]["label"] = f"UPOS:{upos_list[0]}"
        else:
            struttura[i]["label"] = "ANY"

    return struttura


def calcola_ordine_lineare(istanze_correnti, n_nodi_totali, total_sentences):
    """Trova, tra le frasi che condividono la catena, l'ordine lineare
    (in base alla posizione reale nella frase) più frequente."""
    mappatura_posizioni_per_frase = []
    for g_idx in range(total_sentences):
        nodi_con_indice_orig = [(istanze_correnti[g_idx][pos_i], pos_i) for pos_i in range(n_nodi_totali)]
        nodi_con_indice_orig.sort(key=lambda x: x[0])
        mappatura_posizioni_per_frase.append(tuple(coppia[1] for coppia in nodi_con_indice_orig))

    conteggio_ordini = defaultdict(int)
    for ord_seq in mappatura_posizioni_per_frase:
        conteggio_ordini[ord_seq] += 1
    return max(conteggio_ordini, key=conteggio_ordini.get)


def serializza_parsabile(struttura_posizioni, ordine_lineare_ottimale):
    """Serializza la catena in un formato univoco:

        id:LABEL_@deprel_head_id   (nodo con padre dentro la catena)
        id:LABEL_@root             (nodo che è la radice della catena)

    dove:
    - id è la posizione progressiva (1, 2, 3, ...) secondo l'ordine lineare
      reale della frase (non l'ordine dell'albero).
    - LABEL è FORM:xxx / LEMMA:xxx / UPOS:xxx (gerarchia dal più al meno
      specifico, a seconda di cosa risulta uniforme tra le frasi), oppure
      '_' se nessuno dei tre è uniforme.
    - deprel/head_id sono SEMPRE presenti (tranne per la radice, che ha solo
      '@root'): non serve nessun segnaposto come '~', perché la relazione
      strutturale di ogni nodo è sempre esplicita, qualunque sia la sua label.

    I token sono separati da uno spazio; ogni token è internamente parsabile
    con una regex tipo: r'(\\d+):((?:FORM|LEMMA|UPOS):[^_]+|_)_@(\\w+(?::\\w+)?)(?:_(\\d+))?'
    """
    vecchio_idx_a_pos = {vecchio_idx: i + 1 for i, vecchio_idx in enumerate(ordine_lineare_ottimale)}

    tokens = []
    for i, vecchio_idx in enumerate(ordine_lineare_ottimale):
        pos_id = i + 1
        info = struttura_posizioni[vecchio_idx]
        lbl = info["label"] if info["label"] != "ANY" else "_"

        if info["padre_idx"] is None:
            tokens.append(f"{pos_id}:{lbl}_@root")
        else:
            head_pos = vecchio_idx_a_pos[info["padre_idx"]]
            tokens.append(f"{pos_id}:{lbl}_@{info['deprel']}_{head_pos}")

    return " ".join(tokens)


def espandi_greedy_al_massimo(istanze_correnti, graphs, total_sentences, debug=False):
    """Ricostruisce la struttura di partenza ed esegue l'espansione greedy
    finché possibile. Ritorna (struttura_finale, istanze_finali)."""
    struttura_posizioni = ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences, debug=debug)
    while True:
        trovata, nuova_struttura, nuove_istanze = trova_espansione_greedy(
            struttura_posizioni, istanze_correnti, graphs, total_sentences, debug=debug
        )
        if not trovata:
            break
        struttura_posizioni, istanze_correnti = nuova_struttura, nuove_istanze
    return struttura_posizioni, istanze_correnti


# --- 5. ESTRAZIONE STATISTICA DEL BACKGROUND ---
cxn_graphs = defaultdict(list)
global_catenae_counts = defaultdict(int)
total_global_catenae = 0
frase_mappe_cache = {}

for c_id, sents in cxn_groups.items():
    for sent in sents:
        G = nx.DiGraph()
        punct_ids = {t["id"] for t in sent if not isinstance(t["id"], tuple) and t["upos"] == "PUNCT"}

        for t in sent:
            if isinstance(t["id"], tuple): continue
            if t["id"] in punct_ids: continue
            form_val = t["form"].lower() if (LOWERCASE_FORM and t["form"]) else t["form"]
            G.add_node(t["id"], form=form_val, lemma=t["lemma"], upos=t["upos"], feats=t["feats"] or {})

        for t in sent:
            if isinstance(t["id"], tuple): continue
            if t["id"] in punct_ids: continue
            if t["head"] is not None and t["head"] != 0 and t["head"] not in punct_ids:
                G.add_edge(t["head"], t["id"], deprel=t["deprel"])

        cxn_graphs[c_id].append(G)
        frase_mappa = estrai_catenae_tracciate(G)
        idx_frase = len(cxn_graphs[c_id]) - 1
        frase_mappe_cache[(c_id, idx_frase)] = frase_mappa

        for cat in frase_mappa.keys(): global_catenae_counts[cat] += 1
        total_global_catenae += len(frase_mappa)


# --- 6. RANKING PER CXN + ESPANSIONE GREEDY (NIENTE CONLL-C) ---
with open(PATH_OUTPUT_TXT, "w", encoding="utf-8") as out:
    for cxn_id, graphs in cxn_graphs.items():
        total_sentences = len(graphs)

        catene_nelle_frasi = defaultdict(set)
        catena_to_nodes_across_graphs = defaultdict(list)

        for idx, G in enumerate(graphs):
            frase_mappa = frase_mappe_cache[(cxn_id, idx)]
            for cat, list_of_node_tuples in frase_mappa.items():
                catene_nelle_frasi[cat].add(idx)
                # Salviamo solo la prima istanza trovata per questa frase specifica
                catena_to_nodes_across_graphs[cat].append((idx, list_of_node_tuples[0]))

        # Una catena è considerata condivisa SOLO se compare in tutte le frasi (esattamente total_sentences)
        condivise = {
            cat: len(frasi_set) 
            for cat, frasi_set in catene_nelle_frasi.items() 
            if len(frasi_set) == total_sentences
        }
        
        if not condivise:
            continue

        # Pulizia di sicurezza: teniamo solo i nodi delle catene effettivamente condivise
        catena_to_nodes_across_graphs = {
            cat: nodes 
            for cat, nodes in catena_to_nodes_across_graphs.items() 
            if cat in condivise
        }

        candidate_catenae = []
        for cat, f_target in condivise.items():
            f_bg = global_catenae_counts[cat] - f_target
            total_bg = total_global_catenae - len(condivise)
            p_target = f_target / total_sentences
            p_bg = (f_bg + 1) / (total_bg + 1)
            score = f_target * math.log(p_target / p_bg, 2)

            n_nodi = len(catena_to_nodes_across_graphs[cat][0][1])

            lexical_specificity = (cat.count("FORM:") * 3 +
                                   cat.count("LEMMA:") * 2 +
                                   cat.count("UPOS:") * 1)

            candidate_catenae.append({
                "string": cat,
                "score": score,
                "size": n_nodi,
                "specificity": lexical_specificity
            })

        if not candidate_catenae:
            continue

        candidate_catenae = sorted(candidate_catenae, key=lambda x: (-x["score"], -x["specificity"], -x["size"]))

        out.write(f"# cxn_id = {cxn_id}\n")
        out.write(f"# cxn_name = {cxn_names.get(cxn_id, '_')}\n")
        out.write(f"# n_frasi = {total_sentences}\n\n")

        if DEBUG_ESPANSIONE:
            print(f"[debug] {cxn_id}: scansione candidate per trovare {TOP_N} catenae distinte")

        viste = set()   # dedup sulla stringa finale renderizzata (base + espansa)
        rank = 0

        for cand in candidate_catenae:
            if rank >= TOP_N:
                break

            cat_string = cand["string"]

            istanze_correnti = {}
            for g_idx, node_list in catena_to_nodes_across_graphs[cat_string]:
                istanze_correnti[g_idx] = tuple(node_list)

            struttura_base = ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences)
            ordine_base = calcola_ordine_lineare(istanze_correnti, len(struttura_base), total_sentences)
            catena_base_parsabile = serializza_parsabile(struttura_base, ordine_base)

            struttura_espansa, istanze_espanse = espandi_greedy_al_massimo(
                istanze_correnti, graphs, total_sentences, debug=DEBUG_ESPANSIONE
            )
            ordine_espanso = calcola_ordine_lineare(istanze_espanse, len(struttura_espansa), total_sentences)
            catena_espansa_parsabile = serializza_parsabile(struttura_espansa, ordine_espanso)

            chiave_dedup = (catena_base_parsabile, catena_espansa_parsabile)
            if chiave_dedup in viste:
                continue
            viste.add(chiave_dedup)
            rank += 1

            out.write(f"  [{rank}] score = {cand['score']:.2f}  "
                      f"(size={cand['size']}, specificity={cand['specificity']})\n")
            out.write(f"      base:    {catena_base_parsabile}\n")
            out.write(f"      espansa: {catena_espansa_parsabile}\n\n")

        out.write("\n")

print(f"Fatto. Output scritto in: {PATH_OUTPUT_TXT}")