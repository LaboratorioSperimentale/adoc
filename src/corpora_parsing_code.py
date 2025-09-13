import spacy
import re
import os

def parse_and_save_conllc(file_path):
   
    try:
        nlp = spacy.load("it_core_news_sm")
    except OSError:
        print("Il modello di lingua italiana non è installato.")
        print("Per installarlo, esegui il comando nel terminale:")
        print("python -m spacy download it_core_news_sm")
        return

    nlp.max_length = 5000000
    
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()

    raw_text = re.sub(r'<[^>]+>|#.*?\n', '', content).strip()
    
    if not raw_text:
        print(f"Errore: Nessun testo grezzo trovato in {file_path}")
        return

    doc = nlp(raw_text)

    output_dir = "corpora_parsati_UD"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_name = os.path.basename(file_path)
    
    output_file_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.conllc")
    
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        sentence_id = 0
        for sent in doc.sents:
            outfile.write(f"# sent_id = {sentence_id}\n")
            outfile.write("# text = " + sent.text + "\n")
            
            for token in sent:
                
                outfile.write(
                    f"{token.i+1}\t"           
                    f"{token.text}\t"          
                    f"{token.lemma_}\t"        
                    f"{token.pos_}\t"          
                    f"{token.dep_}\t"          
                    f"{token.head.i+1}\n"      
                )
            outfile.write("\n")  
            sentence_id += 1
    
    print(f"Analisi completata. Il risultato è stato salvato in '{output_file_path}'")

parse_and_save_conllc('repubblica.sample')
parse_and_save_conllc('paisa.sample')
parse_and_save_conllc('itwac.sample')
