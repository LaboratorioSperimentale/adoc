import sys
from datetime import datetime
from pathlib import Path
import json
import yaml
import networkx as nx
from pybtex.database import parse_file

BIB = parse_file("bibliography/entries.bib", bib_format="bibtex")

def build_graph(cxns_list):
	Constructicon = nx.DiGraph()

	edges_to_add = []

	for file in cxns_list:
		cxn_id = int(Path(file).stem.split("_")[1])

		with open(file, encoding="utf-8") as stream:
			try:
				cxn = yaml.safe_load(stream)


				# todo: add link to comparative concepts
				# todo: change reference
				# print(cxn)
				# input()

				Constructicon.add_nodes_from([(cxn_id, cxn)])

				hor_links = cxn["horizontal-links"]
				# print(hor_links)
				if hor_links is not None:
					for n in hor_links:
						edges_to_add.append((cxn_id, n))
						edges_to_add.append((n, cxn_id))

				ver_links = cxn["vertical-links"]
				# print(ver_links)
				if ver_links is not None:
					for n in ver_links:
						edges_to_add.append((n, cxn_id))
				# input()
			except yaml.YAMLError as exc:
				print(exc)

	Constructicon.add_edges_from(edges_to_add)

	now = datetime.now().strftime("%Y-%d-%m-%H%M%S")
	graph_filename = f"graph/Constructicon-{now}.json"

	print(json.dumps(nx.node_link_data(Constructicon, name="cxn-id"),
					ensure_ascii=True,
					indent=4),
					file=open(graph_filename, "w", encoding="utf-8"))

	return graph_filename


if __name__ == "__main__":

	files_list = sys.argv[1:]
	file_output = build_graph(files_list)
	print(file_output)
