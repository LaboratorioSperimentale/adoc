"""
Merged catena-extraction pipeline for construction examples.

This unifies what used to be two independent algorithms:

  - candidate discovery / node filtering: PUNCT-only (matches the old
    "algorithm A" -- no broader relation blocklist, so e.g. a `parataxis`-
    attached clause isn't severed from the tree, see cxn_21).
  - cross-sentence matching: structural signature (deprel-labeled tree
    shape, order-independent) -- matches the old "algorithm B", vendored
    from conllc_extraction.py / common_catenae.py. This is what correctly
    unifies e.g. proclitic/enclitic clitic placement as the same construction.
  - scoring: BOTH a background log-likelihood score (how distinctive this
    catena is versus the rest of the corpus -- old "algorithm A") and a
    length+lexicalization score (old "algorithm B") are computed for every
    matched candidate and shown side by side.
  - post-match growth: the winning match is greedily expanded outward as
    far as every example sentence still agrees (old "algorithm A").

Three outputs, same as before:
  1. catenae_ranking.txt   -- human-readable ranking, both scores, base + expanded forms
  2. catenae_ranking_rank1.conllu -- rank-1 candidate, expanded, as CoNLL-U
  3. one .conllc file per construction -- rank-1 candidate, expanded, as CoNLL-C
     (letter IDs, FEATS intersection), written into PATH_OUTPUT_CONLLC_DIR
"""
from collections import defaultdict
import networkx as nx
import re
import math
import os
from conllu import parse

from common_catenae import recursive_catenae_extraction
from conllc_extraction import catena_signature, canonical_order, _best_instance_combo

# --- 1. CONFIGURAZIONE PERCORSI E LIMITI ---

PATH_CONLLU = "../../data/examples/examples.conllu"
PATH_CARTELLA_YAML = "../../data/constructions/yaml"

PATH_OUTPUT_TXT = "../../data/output/catenae_ranking.txt"
PATH_OUTPUT_CONLLU = "../../data/output/catenae_ranking_rank1.conllu"
PATH_OUTPUT_CONLLC_DIR = "../../data/constructions/conllc"

MIN_LEN = 1   # min/max catena length (nodes), for the structural (signature-based) extraction
MAX_LEN = 6
TOP_N = 5     # quante catenae rankate per cxn nel file TXT
LOWERCASE_FORM = True


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


# --- 3. LETTURA DEL CORPUS + COSTRUZIONE GRAFI/INFO (PUNCT-only filter) ---

with open(PATH_CONLLU, "r", encoding="utf-8") as f:
    sentences = parse(f.read())

cxn_groups = defaultdict(list)
for sent in sentences:
    if sent.metadata.get("tags") in ["CONTEXT", "MORPHOLOGICAL", "DROP"]: continue
    sent_id = sent.metadata.get("sent_id", "")
    match = re.search(r'(cxn_\d+)', sent_id)
    if match: cxn_groups[match.group(1)].append(sent)

cxn_groups = {c_id: s for c_id, s in cxn_groups.items() if len(s) > 1}


def build_sentence_data(sent):
    """Build (G, info, children) for one sentence, excluding only PUNCT nodes
    -- no broader relation blocklist, so a node stays reachable from the
    sentence root regardless of its deprel (e.g. parataxis)."""
    punct_ids = {t["id"] for t in sent if not isinstance(t["id"], tuple) and t["upos"] == "PUNCT"}

    G = nx.DiGraph()
    info = {}
    for t in sent:
        if isinstance(t["id"], tuple): continue
        tid = t["id"]
        if tid in punct_ids: continue
        form = t["form"].lower() if (LOWERCASE_FORM and t["form"]) else t["form"]
        feats_dict = t["feats"] or {}
        feats_str = "|".join(f"{k}={v}" for k, v in sorted(feats_dict.items())) or "_"
        G.add_node(tid, form=form, lemma=t["lemma"], upos=t["upos"], feats=feats_dict)
        info[tid] = {"form": form, "lemma": t["lemma"], "upos": t["upos"],
                     "feats": feats_str, "head": t["head"], "deprel": t["deprel"]}

    children = defaultdict(list)
    for t in sent:
        if isinstance(t["id"], tuple): continue
        tid = t["id"]
        if tid in punct_ids: continue
        head = t["head"]
        if head == 0:
            children[0].append(tid)
        elif head is not None and head not in punct_ids and head in info:
            G.add_edge(head, tid, deprel=t["deprel"])
            children[head].append(tid)

    return G, info, dict(children)


def catenae_by_signature(children, info, min_len, max_len):
    """All catenae in a sentence, grouped by their order-independent structural signature."""
    if 0 not in children:
        return {}
    root = children[0][0]
    _, catenae = recursive_catenae_extraction(root, children, min_len, max_len)

    by_sig = defaultdict(list)
    for c in catenae:
        c_sorted = sorted(c)
        sig = catena_signature(c_sorted, info)
        by_sig[sig].append(c_sorted)
    return dict(by_sig)


# --- 4. RICOSTRUZIONE STRUTTURA / ESPANSIONE GREEDY (invariate rispetto alla versione precedente) ---

def ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences):
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

        struttura[i]["padre_idx"] = padre_idx_comune if consistente else None
        struttura[i]["deprel"] = deprel_comune if consistente else None

    for i in range(n):
        forms = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['form'] for g_idx in range(total_sentences)]
        lemmas = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['lemma'] for g_idx in range(total_sentences)]
        upos_list = [graphs[g_idx].nodes[istanze_correnti[g_idx][i]]['upos'] for g_idx in range(total_sentences)]

        if len(set(forms)) == 1: struttura[i]["label"] = f"FORM:{forms[0]}"
        elif len(set(lemmas)) == 1: struttura[i]["label"] = f"LEMMA:{lemmas[0]}"
        elif len(set(upos_list)) == 1: struttura[i]["label"] = f"UPOS:{upos_list[0]}"
        else: struttura[i]["label"] = "ANY"

    return struttura


def trova_espansione_greedy(struttura_posizioni, istanze_correnti, graphs, total_sentences):
    n_posizioni = len(struttura_posizioni)
    migliore = None

    for pos_i in range(n_posizioni):
        for direzione in ("parent", "child"):
            opzioni_per_istanza = []
            fallito = False

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
                    break
                opzioni_per_istanza.append(opzioni)

            if fallito: continue

            deprel_sets = [set(d for (_, d) in opz) for opz in opzioni_per_istanza]
            deprel_comuni = set.intersection(*deprel_sets)
            if not deprel_comuni: continue

            for deprel in deprel_comuni:
                nodi_scelti = []
                for g_idx, opz in enumerate(opzioni_per_istanza):
                    nodo_id = next(n_id for (n_id, d) in opz if d == deprel)
                    nodi_scelti.append((g_idx, nodo_id))

                forms = [graphs[g_idx].nodes[n_id]['form'] for g_idx, n_id in nodi_scelti]
                lemmas = [graphs[g_idx].nodes[n_id]['lemma'] for g_idx, n_id in nodi_scelti]
                upos_list = [graphs[g_idx].nodes[n_id]['upos'] for g_idx, n_id in nodi_scelti]

                if len(set(forms)) == 1: label, spec = f"FORM:{forms[0]}", 3
                elif len(set(lemmas)) == 1: label, spec = f"LEMMA:{lemmas[0]}", 2
                elif len(set(upos_list)) == 1: label, spec = f"UPOS:{upos_list[0]}", 1
                else: label, spec = "ANY", 0

                candidato = (spec, pos_i, direzione, deprel, label, nodi_scelti)
                if migliore is None or candidato[0] > migliore[0]:
                    migliore = candidato

    if migliore is None: return False, None, None

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


def espandi_greedy_al_massimo(istanze_correnti, graphs, total_sentences):
    struttura_posizioni = ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences)
    while True:
        trovata, nuova_struttura, nuove_istanze = trova_espansione_greedy(
            struttura_posizioni, istanze_correnti, graphs, total_sentences
        )
        if not trovata: break
        struttura_posizioni, istanze_correnti = nuova_struttura, nuove_istanze
    return struttura_posizioni, istanze_correnti


def calcola_ordine_lineare(istanze_correnti, n_nodi_totali, total_sentences):
    mappatura_posizioni_per_frase = []
    for g_idx in range(total_sentences):
        nodi_con_indice_orig = [(istanze_correnti[g_idx][pos_i], pos_i) for pos_i in range(n_nodi_totali)]
        nodi_con_indice_orig.sort(key=lambda x: x[0])
        mappatura_posizioni_per_frase.append(tuple(coppia[1] for coppia in nodi_con_indice_orig))

    conteggio_ordini = defaultdict(int)
    for ord_seq in mappatura_posizioni_per_frase:
        conteggio_ordini[ord_seq] += 1
    return max(conteggio_ordini, key=conteggio_ordini.get)


def calcola_stabilita(struttura_posizioni, istanze_correnti, n_nodi_totali, total_sentences):
    """Per position, whether every sentence places it on the same side
    (before/after) of its structural parent. A position whose side flips
    across examples -- e.g. a clitic that's proclitic in one sentence and
    enclitic in another, like "farsi le ossa" vs "mi sono fatto le ossa" --
    comes back False, flagged downstream as MISC=LinearOrder=Variable
    instead of silently picking one side. Root positions (no parent) are
    always stable."""
    stabile = [True] * n_nodi_totali
    for i in range(n_nodi_totali):
        padre_idx = struttura_posizioni[i]["padre_idx"]
        if padre_idx is None:
            continue
        lati = set()
        for g_idx in range(total_sentences):
            nodo_i = istanze_correnti[g_idx][i]
            nodo_padre = istanze_correnti[g_idx][padre_idx]
            lati.add(nodo_i < nodo_padre)
        if len(lati) > 1:
            stabile[i] = False
    return stabile


def serializza_parsabile(struttura_posizioni, ordine_lineare_ottimale):
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


def esporta_catena(cxn_id, cxn_name, struttura, ordine, istanze, graphs, total_sentences):
    """Export the expanded, matched catena as both a CoNLL-U block (numeric
    IDs) and a CoNLL-C block (letter IDs, FEATS intersection)."""
    vecchio_idx_a_nuovo_id = {vecchio_idx: i + 1 for i, vecchio_idx in enumerate(ordine)}
    lettere = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stabile = calcola_stabilita(struttura, istanze, len(struttura), total_sentences)

    conllu_rows, conllc_rows = [], []
    tokens_text, tokens_form = [], []

    for i, vecchio_idx in enumerate(ordine):
        nuovo_id = i + 1
        info_pos = struttura[vecchio_idx]

        forms = [graphs[g].nodes[istanze[g][vecchio_idx]]['form'] for g in range(total_sentences)]
        lemmas = [graphs[g].nodes[istanze[g][vecchio_idx]]['lemma'] for g in range(total_sentences)]
        upos_list = [graphs[g].nodes[istanze[g][vecchio_idx]]['upos'] for g in range(total_sentences)]
        feats_list = [graphs[g].nodes[istanze[g][vecchio_idx]]['feats'] for g in range(total_sentences)]

        form_val = forms[0] if len(set(forms)) == 1 else "_"
        lemma_val = lemmas[0] if len(set(lemmas)) == 1 else "_"
        upos_val = upos_list[0] if len(set(upos_list)) == 1 else "_"

        common_feats = dict(feats_list[0]) if feats_list else {}
        for fd in feats_list[1:]:
            common_feats = {k: v for k, v in common_feats.items() if fd.get(k) == v}
        feats_val = "|".join(f"{k}={v}" for k, v in sorted(common_feats.items())) or "_"

        tokens_text.append(form_val)
        tokens_form.append(form_val if form_val != "_" else lemma_val if lemma_val != "_" else upos_val)

        if info_pos["padre_idx"] is None:
            head_num, deprel_val, head_letter = 0, "root", "0"
        else:
            head_num = vecchio_idx_a_nuovo_id[info_pos["padre_idx"]]
            deprel_val = info_pos["deprel"] or "_"
            head_letter = lettere[head_num - 1] if head_num - 1 < len(lettere) else f"N{head_num}"

        orig_id = lettere[i] if i < len(lettere) else f"N{i + 1}"
        misc_val = "_" if stabile[vecchio_idx] else "LinearOrder=Variable"

        conllu_rows.append(f"{nuovo_id}\t{form_val}\t{lemma_val}\t{upos_val}\t_\t_\t{head_num}\t{deprel_val}\t_\tOrigID={orig_id}"
                            + ("" if misc_val == "_" else f"|{misc_val}"))
        conllc_rows.append(f"{orig_id}\t{form_val}\t{lemma_val}\t{upos_val}\t{feats_val}\t{head_letter}\t{deprel_val}\t{misc_val}")

    conllu_block = "\n".join(
        [f"# sent_id = {cxn_id}", f"# text = {' '.join(tokens_text)}", f"# form = {' '.join(tokens_form)}"]
        + conllu_rows
    )
    conllc_header = [f"# cxn_id = {cxn_id}"]
    if cxn_name:
        conllc_header.append(f"# cxn_name = {cxn_name}")
    conllc_header.append("# " + "\t".join(["ID", "FORM", "LEMMA", "UPOS", "FEATS", "HEAD", "DEPREL", "MISC"]))
    conllc_block = "\n".join(conllc_header + conllc_rows)

    return conllu_block, conllc_block


def matches_spec(struttura_base, candidate_catena, candidate_info):
    """Whether a background catena instance (sharing the same signature)
    also matches the exact FORM/LEMMA/UPOS constraints resolved for the
    target group's matched catena, slot for slot (canonical order)."""
    order = canonical_order(candidate_catena, candidate_info)
    if len(order) != len(struttura_base):
        return False
    for i, pos in enumerate(struttura_base):
        label = pos["label"]
        node = order[i]
        if label.startswith("FORM:"):
            if candidate_info[node]["form"] != label[5:]: return False
        elif label.startswith("LEMMA:"):
            if candidate_info[node]["lemma"] != label[6:]: return False
        elif label.startswith("UPOS:"):
            if candidate_info[node]["upos"] != label[5:]: return False
    return True


# --- 5. COSTRUZIONE DATI PER GRUPPO + POOL GLOBALE (per lo score di background) ---

group_sentence_data = {}    # cxn_id -> list of (G, info, by_sig)
global_sig_pool = defaultdict(list)   # signature -> list of (cxn_id, info, [catena, ...])
total_global_sentences = 0

for c_id, sents in cxn_groups.items():
    data = []
    for sent in sents:
        G, info, children = build_sentence_data(sent)
        by_sig = catenae_by_signature(children, info, MIN_LEN, MAX_LEN)
        data.append((G, info, by_sig))
        for sig, catenae_list in by_sig.items():
            global_sig_pool[sig].append((c_id, info, catenae_list))
        total_global_sentences += 1
    group_sentence_data[c_id] = data


# --- 6. MATCHING PER COSTRUZIONE + DOPPIO SCORE + ESPANSIONE + SALVATAGGIO ---

os.makedirs(os.path.dirname(PATH_OUTPUT_TXT), exist_ok=True)
os.makedirs(PATH_OUTPUT_CONLLC_DIR, exist_ok=True)
for stale in os.listdir(PATH_OUTPUT_CONLLC_DIR):
    if stale.endswith(".conllc"):
        os.remove(os.path.join(PATH_OUTPUT_CONLLC_DIR, stale))

with open(PATH_OUTPUT_TXT, "w", encoding="utf-8") as out_txt, \
     open(PATH_OUTPUT_CONLLU, "w", encoding="utf-8") as out_conllu:

    for cxn_id, data in group_sentence_data.items():
        total_sentences = len(data)
        graphs = [d[0] for d in data]
        infos = [d[1] for d in data]
        by_sig_list = [d[2] for d in data]

        signature_sets = [set(bs) for bs in by_sig_list]
        common_signatures = set.intersection(*signature_sets) if signature_sets else set()
        if not common_signatures:
            continue

        candidates = []
        for sig in common_signatures:
            per_sentence_candidates = [by_sig_list[i][sig] for i in range(total_sentences)]
            instances = _best_instance_combo(per_sentence_candidates, infos)
            istanze_correnti = {i: tuple(canonical_order(catena, info))
                                 for i, (catena, info) in enumerate(instances)}

            struttura_base = ricostruisci_struttura_da_grafi(istanze_correnti, graphs, total_sentences)
            length = len(struttura_base)
            n_lex = sum(1 for p in struttura_base if p["label"].startswith("FORM:"))
            score_lex = length + n_lex

            bg_sentences = 0
            for (bg_cxn_id, bg_info, bg_catenae) in global_sig_pool.get(sig, []):
                if bg_cxn_id == cxn_id: continue
                if any(matches_spec(struttura_base, c, bg_info) for c in bg_catenae):
                    bg_sentences += 1
            total_bg_sentences = total_global_sentences - total_sentences
            p_bg = (bg_sentences + 1) / (total_bg_sentences + 1)
            score_bg = total_sentences * math.log(1.0 / p_bg, 2)

            candidates.append({
                "istanze": istanze_correnti,
                "struttura_base": struttura_base,
                "score_bg": score_bg,
                "score_lex": score_lex,
                "size": length,
                "n_lex": n_lex,
            })

        if not candidates:
            continue

        candidates.sort(key=lambda c: (-c["score_bg"], -c["score_lex"]))

        out_txt.write(f"# cxn_id = {cxn_id}\n")
        out_txt.write(f"# cxn_name = {cxn_names.get(cxn_id, '_')}\n")
        out_txt.write(f"# n_frasi = {total_sentences}\n\n")

        viste = set()
        rank = 0

        for cand in candidates:
            if rank >= TOP_N: break

            ordine_base = calcola_ordine_lineare(cand["istanze"], cand["size"], total_sentences)
            catena_base_parsabile = serializza_parsabile(cand["struttura_base"], ordine_base)

            struttura_espansa, istanze_espanse = espandi_greedy_al_massimo(
                cand["istanze"], graphs, total_sentences
            )
            ordine_espanso = calcola_ordine_lineare(istanze_espanse, len(struttura_espansa), total_sentences)
            catena_espansa_parsabile = serializza_parsabile(struttura_espansa, ordine_espanso)

            chiave_dedup = (catena_base_parsabile, catena_espansa_parsabile)
            if chiave_dedup in viste: continue
            viste.add(chiave_dedup)
            rank += 1

            out_txt.write(f"  [{rank}] score_bg = {cand['score_bg']:.2f}  score_lex = {cand['score_lex']}  "
                          f"(size={cand['size']}, lexicalized={cand['n_lex']})\n")
            out_txt.write(f"      base:    {catena_base_parsabile}\n")
            out_txt.write(f"      espansa: {catena_espansa_parsabile}\n\n")

            if rank == 1:
                conllu_block, conllc_block = esporta_catena(
                    cxn_id, cxn_names.get(cxn_id), struttura_espansa, ordine_espanso,
                    istanze_espanse, graphs, total_sentences
                )
                out_conllu.write(conllu_block + "\n\n")
                conllc_path = os.path.join(PATH_OUTPUT_CONLLC_DIR, f"{cxn_id}.conllc")
                with open(conllc_path, "w", encoding="utf-8") as out_conllc:
                    out_conllc.write(conllc_block + "\n")

        out_txt.write("\n")

print(f"Fatto!\n1. File con tutte le catene (TXT): {PATH_OUTPUT_TXT}\n"
      f"2. File Rank 1 espanso (CoNLL-U): {PATH_OUTPUT_CONLLU}\n"
      f"3. File CoNLL-C rank 1 espanso (uno per costruzione): {PATH_OUTPUT_CONLLC_DIR}/")
