import sys
import os
import re
import collections
# import pandas as pd


import grewpy
from grewpy import Corpus, Request, CorpusDraft

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

	grewpy.set_config("ud") # ud or basic

	treebank_path = "corpora_parsed"
	corpus = Corpus(treebank_path)
	# draft = CorpusDraft(treebank_path)

	output_dir_queries = "formalizzazioni_gq"
	os.makedirs(output_dir_queries, exist_ok=True)

	output_dir_examples = "examples_grew"
	os.makedirs(output_dir_examples, exist_ok=True)

	if len(sys.argv) < 2:
		print("Errore: Devi fornire il percorso del file .conllc come argomento.")
		sys.exit()

	files_da_testare = sys.argv[1:]
	print(f"\n--- reading '{files_da_testare}' ---")

	for file in files_da_testare:
		base_filename, _ = os.path.splitext(os.path.basename(file))

		match = re.search(r'\d+', base_filename)
		cxn_id = match.group(0) if match else "0"
		try:
			with open(file, "r", encoding="utf-8") as f:
				mio_input_conllu = f.read()
		except FileNotFoundError:
			print(f"Errore: Il file '{file}' non è stato trovato. Controlla il percorso.")
			sys.exit()

		parsed_constructions = parse_custom_conllu_cxn(mio_input_conllu)
		gq_constructions = []
		for cxn in parsed_constructions:
			nodes, identity_constraints = cxn
			query_grew_generata = generate_grew_query_from_parsed(
				nodes_data=nodes,
				identity_constraints=identity_constraints,
			)
			gq_constructions.append(query_grew_generata)

		with open(f"{output_dir_queries}/{cxn_id}.gq", "w") as fout, \
		open(f"{output_dir_examples}/{cxn_id}.conllu", "w") as fout_examples:
			sentences = {}
			tot_occurrences = collections.defaultdict(list)

			for query in gq_constructions:
				print(query, file=fout)

				req = Request(query)
				occurrences = corpus.search(req)

				for occurrence in occurrences:
					sent_id = occurrence['sent_id']
					sentences[sent_id] = corpus[sent_id]
					tot_occurrences[sent_id].append(occurrence["matching"])

			# for sentence_id, sentence in sentences.items():
			# 	print(sentence.to_conll())
			draft = CorpusDraft("\n".join([sentence.to_conll() for _, sentence in sentences.items()]))
			print(draft)

			for sent_id in tot_occurrences:
				for occurrence in tot_occurrences[sent_id]:
					# print(occurrence.items())
					# input()
					for node_id, node_num in occurrence["nodes"].items():
						if "Cxn" in draft[sent_id][node_num]:
							draft[sent_id][node_num].update({"Cxn": f"{draft[sent_id][node_num]['Cxn']},{cxn_id}.{node_id}"})
						else:
							draft[sent_id][node_num].update({"Cxn": f"{cxn_id}.{node_id}"})

			corpus2 = Corpus(draft)
			print(corpus2.to_conll(), file=fout_examples)

			print("\n#####\n", file=fout)