
def parse_token(cols):
	header = ["id", "form", "lemma", "upos", "feats", "head", "deprel", "required", "without", "sem_feats", "sem_roles", "adjacency", "identity"]

	ret = {}
	for x, y in zip(header, cols):
		if x in ["id", "feats"]:
			ret[x]=y
		elif x in ["form", "lemma", "upos"]:
			ret[x] = y.split(",")
		elif x in ["required"]:
			ret[x]=bool(int(y))
		else:
			ret[x]=y

	return ret



# TODO: handle more than one construction
def parse(construction):

	ret = { "metadata": [],
			"tokens": []
		}

	for line in construction:
		line = line.strip()
		if len(line):
			if line.startswith("#"):
				ret["metadata"].append(line[1:].split("="))
			else:
				new_token = parse_token(line.split("\t"))
				ret["tokens"].append(new_token)

	return ret


if __name__ == "__main__":
	with open("/Users/ludovica/Documents/projects/adoc/cxns_conllc/cxn_68.conllc") as fin:
		print(parse(fin.readlines()))