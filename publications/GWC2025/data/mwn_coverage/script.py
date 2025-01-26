import collections
import nltk
from nltk.corpus import wordnet as wn

hyper = lambda s: s.hypernyms()

freqs = {}

tot_nouns = collections.defaultdict(lambda: set())
tot_verbs = collections.defaultdict(lambda: set())

with open("lemmi_UD") as fin:
	for line in fin:
		freq, lemma, pos = line.strip().split()
		freq = int(freq)
		freqs[lemma] = freq
		wn_pos = wn.VERB if pos == "VERB" else wn.NOUN
		synsets = list(wn.synsets(lemma, lang="ita", pos=wn_pos))

		if len(synsets) == 0:
			print(f"{lemma}\t{pos}\t{freq}\t0\t0")
		else:
			d = collections.defaultdict(int)
			for synset in synsets:
				lexname = synset.lexname()
				d[lexname] += 1
				if pos == "NOUN":
					tot_nouns[lexname].add(lemma)
				else:
					tot_verbs[lexname].add(lemma)
				# print(f"\t{synset.name()}\t{synset.lexname()}")

			d = [f"{x} - {y}" for x, y in d.items()]
			d_str = '\t'.join(d)
			print(f"{lemma}\t{pos}\t{freq}\t{len(synsets)}\t{len(d)}\t{d_str}")


with open("nouns.out", "w") as fout:

	print("# LEMMA LEVEL", file=fout)

	header = "\t"+'\t'.join(tot_nouns)
	print(header, file=fout)

	for cat1 in tot_nouns:
		s = f"{cat1}"
		for cat2 in tot_nouns:
			x = len(tot_nouns[cat1]&tot_nouns[cat2])
			s+=f"\t{x}"
		print(s, file=fout)


	print("# TOKEN LEVEL", file=fout)
	header = "\t"+'\t'.join(tot_nouns)
	print(header, file=fout)

	for cat1 in tot_nouns:
		s = f"{cat1}"
		for cat2 in tot_nouns:
			x = sum(freqs[el] for el in tot_nouns[cat1]&tot_nouns[cat2])
			s+=f"\t{x}"
		print(s, file=fout)




with open("verbs.out", "w") as fout:

	header = "\t"+'\t'.join(tot_verbs)
	print(header, file=fout)

	for cat1 in tot_verbs:
		s = f"{cat1}"
		for cat2 in tot_verbs:
			x = len(tot_verbs[cat1]&tot_verbs[cat2])
			s+=f"\t{x}"
		print(s, file=fout)


	print("# TOKEN LEVEL", file=fout)
	header = "\t"+'\t'.join(tot_verbs)
	print(header, file=fout)

	for cat1 in tot_verbs:
		s = f"{cat1}"
		for cat2 in tot_verbs:
			x = sum(freqs[el] for el in tot_verbs[cat1]&tot_verbs[cat2])
			s+=f"\t{x}"
		print(s, file=fout)
