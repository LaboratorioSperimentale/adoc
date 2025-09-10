import sys
import os
import re

HEADER = ["ID", "UD.FORM", "LEMMA", "UPOS", "FEATS", "HEAD", "DEPREL", "REQUIRED",
        "WITHOUT", "SEM_FEATS", "SEM_ROLES", "ADJACENCY", "IDENTITY"]
HEADER_MAP = {field:pos for pos, field in enumerate(HEADER)}

# TODO: the function can now parse only one construction from each file
def parse_custom_conllu_cxn(conllu_string):

    lines = conllu_string.strip().split('\n')

    nodes_data = {}
    identity_data = set()
    # children_deprel_constraints = []

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
        if head == '0':
            node_props['head'] = "*"


        deprels = parts[HEADER_MAP['DEPREL']]
        if deprels != '_':
            if deprels.startswith('root') and len(deprels.split(":")) > 1:
                node_props['deprel'] = [deprels.split(":")[1]]
            elif not deprels.startswith("root"):
                node_props['deprel'] = deprels.split(",")

        nodes_data[node_id] = node_props

        # TODO: add
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

    return nodes_data, identity_data


def generate_grew_query_from_parsed(nodes_data,
                                    identity_constraints=[],
                                    children_deprel_constraints=None,
                                    pattern_name=""):

    query_lines = []
    # if pattern_name:
    #     query_lines.append(f"# {pattern_name}")

    query_lines.append("pattern {")

    # TODO: change quotes with regex-like syntax es. "fare" > /fare/i
    # TODO: E [upos="NOUN,PRON,VERB", VerbForm="Inf"]; > E [upos=NOUN|PRON|VERB]

    for node_name, node in nodes_data.items():
        query_lines.append(f'{node_name}[];')

        if "form" in node:
            query_lines.append(f"{node_name}[form=/{node['form']}/i];")

        if "lemma" in node:
            lemma_str = [f'"{el.strip()}"' for el in node["lemma"]]
            query_lines.append(f"{node_name}[lemma={'|'.join(lemma_str)}];")

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

    nodes, identity_constraints = parse_custom_conllu_cxn(mio_input_conllu)
    print(nodes)
    print(identity_constraints)

    query_grew_generata = generate_grew_query_from_parsed(
        nodes_data=nodes,
        identity_constraints=identity_constraints,
    )

    print(f"\n--- Query generata dal file '{file_da_testare}' ---")
    print(query_grew_generata)

    with open(f"formalizzazioni/{os.path.basename(file_da_testare)}.gq","w",encoding="utf-8") as f:
        f.write(query_grew_generata)
