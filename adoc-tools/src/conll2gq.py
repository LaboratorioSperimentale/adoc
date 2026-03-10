def create_ud_node(node_info):
	ret = {}
	keys_map = {
		"UD.FORM": 'form',
		"LEMMA": 'lemma',
		"UPOS": 'upos'
	}

	for key, value in node_info.items():
		if key in keys_map and not value == "_":
			ret[keys_map[key]] = value

	return ret

def parse_custom_conllu_cxn(conllu_string):
	constructions = []
	current_conllu = []
	lines = conllu_string.strip().split('\n')

	for line in lines:
		if line.startswith("# cxn_id ="):
			if current_conllu:
				constructions.append(current_conllu)
			current_conllu = [line]
		else:
			current_conllu.append(line)

	if current_conllu:
		constructions.append(current_conllu)

	parsed_data = {}
	for construction in constructions:

		header = ""
		for cxn_string in construction:

			if cxn_string.startswith("# fields"):
				header = [x.strip() for x in cxn_string.split("=")[1].split()]
				continue
			elif cxn_string.startswith("#"):
				continue

			parts = line.split('\t')
			node_info = dict(zip(header, parts))

			node_id = node_info["ID"]
			parsed_data[node_id] = create_ud_node(node_info)

	return parsed_data

def convert(nodes_data,
			identity_constraints=[],
			children_deprel_constraints=None,
			pattern_name=""):
	query_lines = []
	query_lines.append(f"pattern {{")
	for node_name, node in nodes_data.items():
		query_lines.append(f'{node_name}[];')
		if "form" in node:
			query_lines.append(f"{node_name}[form=/{node['form']}/i];")
		if "lemma" in node:
			query_lines.append(f'{node_name}[lemma="{node['lemma']}"];')
		if "upos" in node:
			query_lines.append(f"{node_name}[upos={node['upos']}];")

	query_lines.append("}")
	query_lines = [query_lines[0]] + \
			[f"\t{el}" for el in query_lines[1:-1]] + \
			[query_lines[-1]]
	return "\n".join(query_lines)

if __name__ == "__main__":

	input = open("adoc-tools/test-cases/simple_constraints-3.conllc").read()
	output = open("adoc-tools/test-cases/simple_constraints-3.gq").read()

	ret = convert(parse_custom_conllu_cxn(input))

	for a, b in zip(ret.split("\n"), output.split("\n")):
		print(a, b)
		assert a.strip() == b.strip()