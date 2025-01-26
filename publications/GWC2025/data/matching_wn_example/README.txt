1. Query in grew-match (https://universal.grew.fr/):


	pattern { X [lemma="fare"];
		Y [upos = "NOUN", Number=Sing];
       		X-[obj]->Y;
		X << Y}

	without { Y -[det]-> S}



	We searched the following Treebanks:

	UD_Italian-ISDT@2.15
	UD_Italian-MarkIT@2.15
	UD_Italian-ParTUT@2.15
	UD_Italian-ParlaMint@2.15
	UD_Italian-PUD@2.15
	UD_Italian-PoSTWITA@2.15
	UD_Italian-TWITTIRO@2.15
	UD_Italian-VIT@2.15


	Result: 426 occurrences


2. Classification of the occurrences (matching_wn.py):

	cxn 71
	not_cxn 355



3. Evaluation after manual checking on the occurrences (contained in the file filtered_results.txt, column manual_check)
	
	true positives = 53
	true negatives = 353
	false positives = 17
	false negatives = 2

	Metrics:
	Accuracy		0,955399061
	FalsePositiveRate	0,045945946
	Precision		0,76056338
	Recall			0,964285714


