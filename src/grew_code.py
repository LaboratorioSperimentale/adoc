import sys
import os
import re
import subprocess

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
            if not line:
                continue

            if line.startswith('#'):
                continue

            parts = line.split('\t')

            if len(parts) < len(HEADER):
                print(f"Attenzione: La riga ha meno colonne rispetto all'header. Saltata: {line}")
                continue

            node_id = parts[HEADER_MAP['ID']]
            if "." in node_id:
                continue
            
            node_props = {}

            form = parts[HEADER_MAP['UD.FORM']]
            if form != '_':
                node_props['form'] = form

            lemma = parts[HEADER_MAP['LEMMA']]
            if lemma != '_':
                node_props['lemma'] = lemma.split(",")

            upos = parts[HEADER_MAP['UPOS']]
            if upos != '_':
                node_props['upos'] = upos.split(",")

            feats_str = parts[HEADER_MAP['FEATS']]
            if feats_str != '_':
                node_props['features'] = {}
                for feat_pair in feats_str.split('|'):
                    if '=' in feat_pair:
                        k, v = feat_pair.split('=', 1)
                        node_props['features'][k] = v

            head = parts[HEADER_MAP['HEAD']]
            if head != '_':
                node_props['head'] = head
            if head == '0':
                node_props['head'] = "*"

            deprels = parts[HEADER_MAP['DEPREL']]
            if deprels != '_':
                if deprels.startswith('root') and len(deprels.split(":")) > 1:
                    node_props['deprel'] = [deprels.split(":")[1]]
                elif not deprels.startswith("root"):
                    node_props['deprel'] = deprels.split(",")

            adjacency_field = parts[HEADER_MAP['ADJACENCY']]
            if adjacency_field != '_':
                node_props['adjacency'] = adjacency_field

            nodes_data[node_id] = node_props

            identity_field = parts[HEADER_MAP['IDENTITY']]
            if identity_field != '_':
                identity_constraints = identity_field.split(",")
                for constraint in identity_constraints:
                    if '=' in constraint:
                        attr, other_node_id = constraint.split('=')
                        attr_lower = attr.lower().replace('ud.', '')
                        identity_data.add(
                            (
                                (min(node_id, other_node_id.strip()), max(node_id, other_node_id.strip())),
                                attr_lower
                            )
                        )
        parsed_data.append((nodes_data, identity_data))

    return parsed_data

def generate_grew_query_from_parsed(nodes_data,
                                  identity_constraints=[],
                                  children_deprel_constraints=None,
                                  pattern_name=""):

    query_lines = []
    
    query_lines.append("pattern {")

    for node_name, node in nodes_data.items():
        query_lines.append(f'{node_name}[];')

        if "form" in node:
            query_lines.append(f"{node_name}[form=/{node['form']}/i];")

        if "lemma" in node:
            lemma_str = [f'/{el.strip()}/i' for el in node["lemma"]]
            query_lines.append(f"{node_name}[lemma={ '|'.join(lemma_str) }];")

        if "upos" in node:
            query_lines.append(f"{node_name}[upos={'|'.join([x.strip() for x in node['upos']])}];")

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
        if "adjacency" in node:
            query_lines.append(f"{node['adjacency']} < {node_name};")
    query_lines.append("")

    for node_name, node in nodes_data.items():
        if "head" in node and "deprel" in node:
            query_lines.append(f"{node['head']} -[{'|'.join([x.strip() for x in node['deprel']])}]-> {node_name};")
    query_lines.append("")

    query_lines.append("}")

    query_lines = [query_lines[0]] + [f"  {el}" for el in query_lines[1:-1]] + [query_lines[-1]]

    return "\n".join(query_lines)

if __name__ == "__main__":
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
    
    queries_to_run = []

    for i, (nodes, identity_constraints) in enumerate(parsed_constructions):
        print(f"\n--- Parsing Construction {i+1} ---")
        print("Nodi:", nodes)
        print("Vincoli di identità:", identity_constraints)

        query_grew_generata = generate_grew_query_from_parsed(
            nodes_data=nodes,
            identity_constraints=identity_constraints,
        )

        print(f"\n--- Query generata per la costruzione {i+1} ---")
        print(query_grew_generata)

        base_filename, _ = os.path.splitext(os.path.basename(file_da_testare))
        alphabet_suffix = chr(ord('a') + i)
        output_filename = f"{output_dir_queries}/{base_filename}_{alphabet_suffix}.gq"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(query_grew_generata)
        print(f"Query salvata in '{output_filename}'")
        queries_to_run.append(output_filename)

    print("\n--- Esecuzione delle query sui corpora ---")
    
    corpora_dir = "corpora"
   
    output_results_dir = "risultati_query_corpora"

    if not os.path.isdir(corpora_dir):
        print(f"Errore: La cartella dei corpora '{corpora_dir}' non è stata trovata. Impossibile eseguire le query.")
        sys.exit()
    
    os.makedirs(output_results_dir, exist_ok=True)

    for corpus_file in os.listdir(corpora_dir):
        if corpus_file.endswith(('.conllu', '.conllc')):
            corpus_base_name, _ = os.path.splitext(os.path.basename(corpus_file))
            corpus_path = os.path.join(corpora_dir, corpus_file)
            
            for query_file in queries_to_run:
                query_base_name = os.path.splitext(os.path.basename(query_file))[0]

                output_result_filename = f"{output_results_dir}/{query_base_name}_su_{corpus_base_name}.txt"
                
                print(f"- Esecuzione della query '{query_file}' su '{corpus_path}'...")
                
                try:
                    with open(output_result_filename, "w", encoding="utf-8") as outfile:
                       
                        subprocess.run(
                            ["grew", "-graph", corpus_path, "-query", query_file],
                            stdout=outfile, stderr=subprocess.PIPE, check=True
                        )
                    print(f"  Risultati salvati in '{output_result_filename}'")
                        
                except FileNotFoundError:
                    print("Errore: L'eseguibile di Grew non è stato trovato. Assicurati che sia installato e nel tuo PATH.")
                    break
                except subprocess.CalledProcessError as e:
                    print(f"  Errore durante l'esecuzione di Grew. Errore standard: {e.stderr.decode('utf-8')}")
