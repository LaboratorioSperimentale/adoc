import sys
import os
import re
import pandas as pd
import subprocess  # Per eseguire il comando 'grew' come processo esterno
import tempfile    # Per creare e gestire file temporanei per le query

# --- CONFIGURAZIONE CRITICA ---
# Questi nomi non sono più i nomi dei corpora remoti, ma i NOMI delle sottocartelle
# che hai scaricato nella tua cartella 'corpora'.
grew_corpora = [
    'UD_Italian-ISDT', 'bUD_Italian-ISDT', 'UD_Italian-MarkIT', 
    'UD_Italian-Old', 'UD_Italian-PUD', 'UD_Italian-ParTUT', 
    'UD_Italian-ParlaMint', 'UD_Italian-PoSTWITA', 'UD_Italian-TWITTIRO', 
    'UD_Italian-VIT', 'UD_Italian-Valico'
]

# *** IL PERCORSO CHE PUNTIAMO: LA TUA CARTELLA 'corpora' ***
LOCAL_CORPUS_DIR = "corpora" 
# --- FINE CONFIGURAZIONE ---

# --- DICHIARAZIONI INIZIALI E FUNZIONI DI PARSING/QUERY (INVARIATE) ---

HEADER = ["ID", "UD.FORM", "LEMMA", "UPOS", "FEATS", "HEAD", "DEPREL", "REQUIRED",
          "WITHOUT", "SEM_FEATS", "SEM_ROLES", "ADJACENCY", "IDENTITY"]
HEADER_MAP = {field: pos for pos, field in enumerate(HEADER)}

def parse_custom_conllu_cxn(conllu_string):
    constructions = []
    current_conllu = []
    lines = conllu_string.strip().split('\n')
    for line in lines:
        if line.startswith("# cxn_id ="):
            if current_conllu:
                constructions.append("\n".join(current_conllu))
            current_conllu = [line]
        else:
            current_conllu.append(line)
    if current_conllu:
        constructions.append("\n".join(current_conllu))
    parsed_data = []
    for cxn_string in constructions:
        lines = cxn_string.strip().split('\n')
        nodes_data = {}
        identity_data = set()
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) < len(HEADER): continue
            node_id = parts[HEADER_MAP['ID']]
            if "." in node_id: continue
            node_props = {}
            form = parts[HEADER_MAP['UD.FORM']];
            if form != '_': node_props['form'] = form
            lemma = parts[HEADER_MAP['LEMMA']];
            if lemma != '_': node_props['lemma'] = lemma.split(",")
            upos = parts[HEADER_MAP['UPOS']];
            if upos != '_': node_props['upos'] = upos.split(",")
            feats_str = parts[HEADER_MAP['FEATS']];
            if feats_str != '_':
                node_props['features'] = {}
                for feat_pair in feats_str.split('|'):
                    if '=' in feat_pair:
                        k, v = feat_pair.split('=', 1)
                        node_props['features'][k] = v
            head = parts[HEADER_MAP['HEAD']];
            if head != '_': node_props['head'] = head
            if head == '0': node_props['head'] = "*"
            deprels = parts[HEADER_MAP['DEPREL']];
            if deprels != '_':
                if deprels.startswith('root') and len(deprels.split(":")) > 1:
                    node_props['deprel'] = [deprels.split(":")[1]]
                elif not deprels.startswith("root"):
                    node_props['deprel'] = deprels.split(",")
            adjacency_field = parts[HEADER_MAP['ADJACENCY']];
            if adjacency_field != '_': node_props['adjacency'] = adjacency_field
            nodes_data[node_id] = node_props
            identity_field = parts[HEADER_MAP['IDENTITY']];
            if identity_field != '_':
                identity_constraints = identity_field.split(",")
                for constraint in identity_constraints:
                    if '=' in constraint:
                        attr, other_node_id = constraint.split('=')
                        attr_lower = attr.lower().replace('ud.', '')
                        identity_data.add(((min(node_id, other_node_id.strip()), max(node_id, other_node_id.strip())), attr_lower))
        parsed_data.append((nodes_data, identity_data))
    return parsed_data

def generate_grew_query_from_parsed(nodes_data, identity_constraints=[], children_deprel_constraints=None, pattern_name=""):
    query_lines = []
    query_lines.append(f"pattern {{")
    for node_name, node in nodes_data.items():
        query_lines.append(f'{node_name}[];')
        if "form" in node: query_lines.append(f"{node_name}[form=/{node['form']}/i];")
        if "lemma" in node:
            lemma_str = [f'/{el.strip()}/i' for el in node["lemma"]]
            query_lines.append(f"{node_name}[lemma={ '|'.join(lemma_str) }];")
        if "upos" in node: query_lines.append(f"{node_name}[upos={'|'.join([x.strip() for x in node['upos']])}];")
        if "features" in node:
            for k, v in node["features"].items():
                query_lines.append(f"{node_name}[{k}={v}]|[!{k}]; ")
        query_lines.append("")
    for (nodes, field) in identity_constraints:
        if field in ['form', 'lemma', 'upos']:
            node_a, node_b = nodes
            query_lines.append(f"{node_a}.{field} = {node_b}.{field};")
        query_lines.append("")
    for node_name, node in nodes_data.items():
        if "adjacency" in node: query_lines.append(f"{node['adjacency']} < {node_name};")
    query_lines.append("")
    for node_name, node in nodes_data.items():
        if "head" in node and "deprel" in node: query_lines.append(f"{node['head']} -[{'|'.join([x.strip() for x in node['deprel']])}]-> {node_name};")
    query_lines.append("")
    query_lines.append("}")
    query_lines = [query_lines[0]] + [f"  {el}" for el in query_lines[1:-1]] + [query_lines[-1]]
    return "\n".join(query_lines)

# --- Esecuzione Principale ---

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Errore: Devi fornire il percorso del file .conllc come argomento.")
        sys.exit()

    file_da_testare = sys.argv[1]
    print(f"\n--- reading '{file_da_testare}' ---")

    try:
        with open(file_da_testare, "r", encoding="utf-8") as f:
            mio_input_conllu = f.read()
    except FileNotFoundError:
        print(f"Errore: Il file '{file_da_testare}' non è stato trovato. Controlla il percorso.")
        sys.exit()

    parsed_constructions = parse_custom_conllu_cxn(mio_input_conllu)
    
    if not parsed_constructions:
        print("Nessuna costruzione trovata nel file.")
        sys.exit()

    output_dir_queries = "formalizzazioni"
    os.makedirs(output_dir_queries, exist_ok=True)
    
    all_queries_grew_with_id = []
    base_filename, _ = os.path.splitext(os.path.basename(file_da_testare))
    
    match = re.search(r'\d+', base_filename)
    cxn_number = match.group(0) if match else "0"

    for i, (nodes, identity_constraints) in enumerate(parsed_constructions):
        query_grew_generata = generate_grew_query_from_parsed(
            nodes_data=nodes,
            identity_constraints=identity_constraints,
        )
        
        alphabet_suffix = chr(ord('a') + i)
        query_id = f"cxn={cxn_number}_{alphabet_suffix}"
        
        all_queries_grew_with_id.append({
            'id': query_id,
            'query': query_grew_generata,
            'header': f"#{query_id}\n{query_grew_generata}"
        })

    # ---
    ## 1. Esecuzione e Conteggio Corpus per Corpus (Bypass API - Comando di Sistema)
    # ---

    print("\n--- 1. Esecuzione e Conteggio (Bypass API con comando di sistema 'grew' e file locali) ---")
    
    results_list = []
    
    print(f"Userà i seguenti {len(grew_corpora)} cartelle locali: {', '.join(grew_corpora)}")
    
    for corpus_name in grew_corpora:
        corpus_path = f'{LOCAL_CORPUS_DIR}/{corpus_name}'
        print(f"  -> Processando cartella corpus: {corpus_path}...")

        if not os.path.isdir(corpus_path):
            print(f"  ❌ Errore: Cartella corpus non trovata a '{corpus_path}'. Salto.")
            continue

        for query_data in all_queries_grew_with_id:
            query_id = query_data['id']
            query_string = query_data['query']
            
            tmp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.gq') as tmp_file:
                    tmp_file.write(query_string)
                    tmp_file_path = tmp_file.name
                
                command = [
                    'grew', 'count', 
                    '-grs', tmp_file_path, 
                    
                    '-dir', corpus_path 
                ]
                
                process = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    check=True, 
                    encoding='utf-8'
                )
                
                output_line = process.stdout.strip()
                
                count_match = re.search(r'(\d+)', output_line)
                count_result = int(count_match.group(1)) if count_match else 0
                
                results_list.append({
                    'Query_ID': query_id,
                   
                    'Corpus': f'{corpus_name}@Local', 
                    'Count': count_result
                })
                
            except subprocess.CalledProcessError as e:
               
                error_message = e.stderr.strip().split('\n')[-1]
                print(f"  ❌ Errore Grew su {corpus_name} con {query_id}: {error_message}")
                results_list.append({
                    'Query_ID': query_id,
                    'Corpus': f'{corpus_name}@Local',
                    'Count': 0
                })
            except Exception as e:
                print(f"  ❌ Errore sconosciuto su {corpus_name} con {query_id}: {e}")
                results_list.append({
                    'Query_ID': query_id,
                    'Corpus': f'{corpus_name}@Local',
                    'Count': 0
                })
            finally:
               
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

    if not results_list:
        print("Nessun risultato valido è stato generato.")
        sys.exit()

    print("\n--- 2. Salvataggio dei risultati in CSV ---")
    
    output_results_dir = "risultati_query_corpora"
    os.makedirs(output_results_dir, exist_ok=True)
    output_csv_filename = f"{output_results_dir}/{base_filename}_conteggi.csv"

    try:
    
        results_df = pd.DataFrame(results_list)
        results_df_pivot = results_df.pivot(index='Query_ID', columns='Corpus', values='Count').fillna(0)
        results_df_pivot.to_csv(output_csv_filename, sep='\t')
        
        print(f"✅ Risultati di Conteggio salvati con successo in: '{output_csv_filename}'")
    
    except Exception as e:
        print(f"❌ Errore durante la creazione o il salvataggio del CSV: {e}")

    print("\n--- 3. Visualizzazione Grafica (Disabilitata) ---")
    print("La visualizzazione grafica richiede l'API grewpy, che è incompatibile con il tuo sistema.")
