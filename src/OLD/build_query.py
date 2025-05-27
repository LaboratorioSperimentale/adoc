FIELDS = ["id", "form", "lemma", "upos", "feats", "head", "deprel", "required", "without", "sem_feats", "sem_roles", "adjacency", "identity"]

def read_cxn(list_of_conllc_lines):

	for item in list_of_conllc_lines:
		item = dict(zip(FIELDS, item))
		print(item)



if __name__ == "__main__":
	file_input = "cxns_conllc/cxn_104.conllc"

	with open(file_input) as fin:
		cxns = []
		cxn = []
		for line in fin:

			if line.startswith("#"):
				continue
			if len(line.strip()) == 0:
				cxns.append(cxn)
				cxn = []
				continue

			line = line.strip().split("\t")
			cxn.append(line)

	for cxn in cxns:
		read_cxn(cxn)

