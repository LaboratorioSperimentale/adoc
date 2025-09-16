import grewpy
from grewpy import Corpus, Request

grewpy.set_config("ud") # ud or basic

treebank_path = "../corpora_parsed"
corpus = Corpus(treebank_path)
print(type(corpus))

n_sentencens = len(corpus)
sent_ids = corpus.get_sent_ids()

print(sent_ids)

req1 = Request("pattern { e:X-[nsubj]->Y }")
occurrences = corpus.search(req1)

for occurrence in occurrences:
    print(occurrence)
    input()


