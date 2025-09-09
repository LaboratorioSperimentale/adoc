import sys
import os
import re

HEADER = ["ID", "UD.FORM", "LEMMA", "UPOS", "FEATS", "HEAD", "DEPREL", "REQUIRED",
        "WITHOUT", "SEM_FEATS", "SEM_ROLES", "ADJACENCY", "IDENTITY"]
HEADER_MAP = {field:pos for pos, field in enumerate(HEADER)}

# TODO: the function can now parse only one construction from each file
# refactor so that it can produce more than one construction
def parse_custom_conllu_cxn(conllu_string):

    lines = conllu_string.strip().split('\n')

    nodes_data = {}
    relations_data = []
    adjacency_data = []
    identity_data = set()
    children_deprel_constraints = []

    # header_map = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#'):
            # if line.startswith('# fields ='):
            #     headers = [h.strip() for h in line.replace('# fields =', '').split('\t')]
            #     header_map = {header: idx for idx, header in enumerate(headers)}
            continue

        # if line.startswith("# cxn_id ="):
            # continue
            #TODO: nuova costruzione

        # if not header_map:
            # print("Errore: Impossibile trovare la riga '# fields =' nel CoNLL-U fornito.")
            # return [], [], [], [], []

        parts = line.split('\t')

        if len(parts) < len(HEADER):
            print(f"Attenzione: La riga ha meno colonne rispetto all'header. Saltata: {line}")
            continue

        node_id = parts[HEADER_MAP['ID']]
        if "." in node_id:
            continue
        # node_props = {'name': node_id}
        node_props = {}

        # currently, OR cannot operate on form
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

        deprels = parts[HEADER_MAP['DEPREL']]
        if deprels != '_' and not deprels.startswith("root"):
            node_props['deprel'] = deprels.split(",")

        nodes_data[node_id] = node_props

        #! commented out for now to test
        # head_id = parts[header_map['HEAD']]
        # deprel_field = parts[header_map['DEPREL']]


        # if 'CHILDREN:DEPREL=' in deprel_field:
        #     parts_deprel = deprel_field.split('CHILDREN:DEPREL=')
        #     actual_deprel = parts_deprel[0].strip()
        #     child_deprel = parts_deprel[1].strip()

        #     children_deprel_constraints.append({
        #         'node': node_id,
        #         'deprel': child_deprel
        #     })

        #     deprel_to_use = actual_deprel
        # else:
        #     deprel_to_use = deprel_field

        # if head_id != '0' and deprel_to_use != '_':

        #     # TODO: handle multiple deprels
        #     for single_deprel in deprel_to_use.split(','):
        #         if single_deprel.strip():
        #             relations_data.append({
        #                 'source': head_id,
        #                 'target': node_id,
        #                 'deprel': single_deprel.strip()
        #             })


        adjacency_field = parts[HEADER_MAP['ADJACENCY']]
        if adjacency_field != '_':
            #! a node can only be adjacent to one other node, no need to split
            #! also, we can keep it in the properties of the node itself
            # for adj_node in adjacency_field.split(','):
                # if adj_node != '_':
                    # adjacency_data.append({'node1': adj_node.strip(), 'node2': node_id})
            node_props['adjacency'] = adjacency_field

        nodes_data[node_id] = node_props

        identity_field = parts[HEADER_MAP['IDENTITY']]
        if identity_field != '_':
            identity_constraints = identity_field.split(",")
            for constraint in identity_constraints:
                #! no way not to have '=' in this field
                # if '=' in identity_field:
                attr, other_node_id = constraint.split('=')

                attr_lower = attr.lower().replace('ud.', '')
                identity_data.add(
                    (
                        (min(node_id, other_node_id.strip()), max(node_id, other_node_id.strip())),
                        attr_lower
                    )
                )

            #! I don't get this
            # elif identity_field in nodes_data:
            #      identity_data.append({
            #         'node1': node_id,
            #         'node2': identity_field,
            #         'attr': 'form'
            #      })

    #! not sure why this is needed
    # final_nodes = list(nodes_data.values())

    # unique_relations = []
    # seen_rel = set()
    # for rel in relations_data:
    #     rel_tuple = (rel['source'], rel['deprel'], rel['target'])
    #     if rel_tuple not in seen_rel:
    #         unique_relations.append(rel)
    #         seen_rel.add(rel_tuple)

    # unique_identity = []
    # seen_id = set()
    # for ident in identity_data:
    #     id_tuple = (ident['node1'], ident['node2'], ident['attr'])
    #     if id_tuple not in seen_id:
    #         unique_identity.append(ident)
    #         seen_id.add(id_tuple)

    # unique_adjacency = []
    # seen_adj = set()
    # for adj in adjacency_data:
    #     adj_tuple = (adj['node1'], adj['node2'])
    #     if adj_tuple not in seen_adj:
    #         unique_adjacency.append(adj)
    #         seen_adj.add(adj_tuple)

    # return final_nodes, unique_relations, unique_identity, unique_adjacency, children_deprel_constraints
    return nodes_data, identity_data


def generate_grew_query_from_parsed(nodes_data, relations_data=None, identity_constraints=[], adjacency_constraints=None, children_deprel_constraints=None, pattern_name=""):

    query_lines = []

    # if pattern_name:
    #     query_lines.append(f"# {pattern_name}")

    query_lines.append("pattern {")

    # TODO: change quotes with regex-like syntax es. "fare" > /fare/i
    # TODO: E [upos="NOUN,PRON,VERB", VerbForm="Inf"]; > E [upos=NOUN|PRON|VERB]

    for node_name, node in nodes_data.items():
        # node_name = node['name']
        query_lines.append(f'{node_name}[];')

        if "form" in node:
            query_lines.append(f"{node_name}[form=/{node['form']}/i];")

        if "lemma" in node:
            lemma_str = [f'"{el}"' for el in node["lemma"]]
            query_lines.append(f"{node_name}[lemma={'|'.join(lemma_str)}];")

        if "upos" in node:
            query_lines.append(f"{node_name}[upos={'|'.join(node['upos'])}];")

        if "features" in node:
            for k, v in node["features"].items():
                query_lines.append(f"{node_name}[{k}={v}];")
        query_lines.append("")

        # attributes = []
        # for key, value in node.items():
        #     if key != 'name':
        #         if isinstance(value, str):

        #             is_regex_or_or = (value.startswith('/') and value.endswith('/')) or \
        #                              (value.startswith('/') and value.endswith('/i')) or \
        #                              ('|' in value)
        #             if is_regex_or_or:
        #                 attributes.append(f'{key}={value}')
        #             else:
        #                 attributes.append(f'{key}="{value}"')
        #         else:
        #             attributes.append(f'{key}={value}')
        # query_lines.append(f'  {node_name} [{", ".join(attributes)}];')

    # if relations_data:
    #     query_lines.append("")
    #     for rel in relations_data:
    #         source = rel['source']
    #         deprel = rel['deprel']
    #         target = rel['target']
    #         query_lines.append(f'  {source} -[{deprel}]-> {target};')

    for (nodes, field) in identity_constraints:
        node_a, node_b = nodes
        query_lines.append(f"{node_a}.{field} = {node_b}.{field};")
        # for constraint in identity_constraints:
        #     node1 = constraint['node1']
        #     node2 = constraint['node2']
        #     attr = constraint['attr']
        #     query_lines.append(f'  {node1}.{attr} = {node2}.{attr};')
        query_lines.append("")

    for node_name, node in nodes_data.items():
        if "adjacency" in node:
            query_lines.append(f"{node['adjacency']} < {node_name};")
    query_lines.append("")

    for node_name, node in nodes_data.items():
        if "head" in node and "deprel" in node:
            query_lines.append(f"{node['head']} -[{'|'.join(node['deprel'])}]-> {node_name};")
    query_lines.append("")
    # if adjacency_constraints:
    #     query_lines.append("")
    #     for adj in adjacency_constraints:
    #         query_lines.append(f'  {adj["node1"]} < {adj["node2"]};')

    # if children_deprel_constraints:
    #     query_lines.append("")
    #     for child_deprel_c in children_deprel_constraints:
    #         node = child_deprel_c['node']
    #         deprel = child_deprel_c['deprel']
    #         query_lines.append(f'  {node} [CHILDREN:DEPREL={deprel}];')

    query_lines.append("}")

    # ONLY FOR VISUALIZATION PURPOSES
    query_lines = [query_lines[0]]+[f"  {el}" for el in query_lines[1:-1]] + [query_lines[-1]]

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

    # nodes, relations, identity, adjacency, children_deprel = parse_custom_conllu_cxn(mio_input_conllu)
    nodes, identity_constraints = parse_custom_conllu_cxn(mio_input_conllu)
    print(nodes)
    print(identity_constraints)

    # name_match = re.search(r'# name = (.+)', mio_input_conllu)
    # pattern_name_per_query = name_match.group(1).strip() if name_match else "Pattern dal file"

    query_grew_generata = generate_grew_query_from_parsed(
        nodes_data=nodes,
        # relations_data=relations,
        identity_constraints=identity_constraints,
        # adjacency_constraints=adjacency,
        # children_deprel_constraints=children_deprel,
        # pattern_name=f"{pattern_name_per_query} (dal file)"
    )

    # print(query_grew_generata)
    # input()

    print(f"\n--- Query generata dal file '{file_da_testare}' ---")
    print(query_grew_generata)

    # output_filename = pattern_name_per_query.replace(" ", "_").replace("(", "").replace(")", "") + ".grew"
    with open(f"formalizzazioni/{os.path.basename(file_da_testare)}.gq","w",encoding="utf-8") as f:
        f.write(query_grew_generata)
    # print(f"\nQuery salvata in: {output_filename}")
