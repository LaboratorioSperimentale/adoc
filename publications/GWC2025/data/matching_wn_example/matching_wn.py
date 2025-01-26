import os
import csv
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.corpus import wordnet as wn
import pandas as pd

#set the relevant OMW topic (the tag in SEMFEAT's OntoClass) and the pos
match = "noun.feeling"
wn_pos = wn.NOUN

#import the datasets with the occurrences extracted in grew-match (pivot is the open slot we need to constrain), and merge them to a single df
path = "./dataset"

dataframes = []
for file in os.listdir(path):
    if file.endswith(".tsv"):  
        file_path = os.path.join(path, file)
        df_1 = pd.read_csv(file_path, sep='\t', quoting=csv.QUOTE_NONE, encoding ="utf-8")
        dataframes.append(df_1)
df = pd.concat(dataframes, ignore_index=True)

lemmalist = df['pivot'].tolist()
idlist = df['sent_id'].tolist()

#change name to duplicate ids (e.g., num to num_2)
dup = {}
idlist2 = []
for el in idlist:
    if el in dup:
        dup[el] += 1
        idlist2.append(f"{el}_{dup[el]}")
    else:
        dup[el] = 0
        idlist2.append(el)
        

#create a dictionary where keys are sent_ids, and values are lists of possible senses (synsets) of the pivot lemma
id_to_syn = dict()

for i in range(len(lemmalist)):
    if len(list(wn.synsets(str(lemmalist[i]), lang="ita", pos=wn_pos))) > 0:
        synsets = list(wn.synsets(str(lemmalist[i]), lang="ita", pos=wn_pos))
        id_to_syn[idlist2[i]] = synsets
        
    else:
        id_to_syn[idlist2[i]] = list()

#create a dictionary where keys are sent_ids, and values are lists of OMW topics for each possible sense of the pivot lemma
id_to_lex = dict()

for j in id_to_syn.keys():
    syns = id_to_syn[j]
    lex = []
    if len(syns)> 0:
        for synset in syns:
            lexname = synset.lexname()
            lex.append(lexname)
    else:
        lex.append('')
    id_to_lex[j] = lex

#create list with the annotation of constructs and false positives for each occurrence
matching = []

for k in id_to_lex.keys():
    lexlist = id_to_lex[k]
    if match in lexlist:
        matching.append('cxn')
    else:
        matching.append('not_cxn')
        
#create and save annotated dataset      
df['matching'] = matching
df.to_csv('filtered_results.txt', sep = "\t", encoding = "utf-8", index=False)
    

