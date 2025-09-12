import spacy
import re

def parse_corpus(file_path):
   
    nlp = spacy.load("it_core_news_sm")
    
    nlp.max_length = 3000000  
    
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()

    raw_text = re.sub(r'<[^>]+>|#.*?\n', '', content).strip()
    
    if not raw_text:
        print("Errore: Impossibile leggere il testo dal file del corpus.")
        print("Il file potrebbe non contenere testo grezzo o avere un formato non supportato.")
        return

    doc = nlp(raw_text)
    
    print(f"\n--- Analisi del file: {file_path} ---")
    print("Risultati del Parsing con spaCy:")
    print("-" * 50)
    print("{:<15} {:<10} {:<10} {:<15} {:<10}".format("TOKEN", "POS", "LEMMA", "DEPENDENCY", "HEAD"))
    print("-" * 50)
    for token in doc:
        print("{:<15} {:<10} {:<10} {:<15} {:<10}".format(
            token.text,
            token.pos_,
            token.lemma_,
            token.dep_,
            token.head.text
        ))
    
    print("\n" + "="*50)
    print("Entità Nominali (NER):")
    for ent in doc.ents:
        print(f"{ent.text:<20} | {ent.label_:<10}")

parse_corpus('itwac.sample')