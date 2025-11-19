import spacy
from spacy.tokens import Doc
import re
import os
import spacy_conll
<<<<<<< HEAD
import ftfy 

def _get_nlp_instance():
    """Inizializza l'istanza di spaCy con il modello italiano e il conll_formatter."""
=======
import tqdm

def _get_nlp_instance():
    def custom_tokenizer(text):
        tokens = text.split(" ")

        # your existing code to fill the list with tokens

        # replace this line:
        return Doc(nlp.vocab, tokens)

        # with this:
        # return Doc(nlp.vocab, tokens)

>>>>>>> 4d3e62325668bb318665d2186fc45a1105e2374c
    try:
        nlp = spacy.load("it_core_news_sm", exclude=["ner"])
        nlp.tokenizer = custom_tokenizer
        nlp.add_pipe("conll_formatter", last=True)
        nlp.max_length = 3000000
        return nlp
    except OSError:
        print("Il modello 'it_core_news_sm' non è installato.")
        print("Per installarlo, esegui: python -m spacy download it_core_news_sm")
        print("Potrebbe essere necessario installare anche la libreria ftfy: pip install ftfy")
        return None

<<<<<<< HEAD
=======
def _parse_structured_corpus(file_path, nlp, outfile):

    doc_id = None
    url = None

    with open(file_path, 'r', encoding='latin-1') as f:
        sentence_text = ""
        sentence_id = 1

        for line in f:
            line = line.strip()

            if line.startswith('<text'):

                match_id = re.search(r'id="([^"]+)"', line)
                doc_id = match_id.group(1) if match_id else None
                match_url = re.search(r'url="([^"]+)"', line)
                url = match_url.group(1) if match_url else None

                if doc_id:
                    outfile.write(f"# newdoc id = {doc_id}\n")
                if url:
                    outfile.write(f"# newdoc url = {url}\n")

            # elif line.startswith('<s>'):
            #     sentence_text = ""

            elif line.startswith('</s>'):
                if sentence_text:
                    final_text = sentence_text.strip()
                    docs = nlp.pipe([final_text])

                    for doc in docs:
                        outfile.write(f"# sent_id = {sentence_id}\n")
                        outfile.write(f"# text = {final_text}\n")
                        outfile.write(doc._.conll_str + "\n")

                    sentence_id += 1
                sentence_text = ""

            elif line and not line.startswith('<'):
                clean_line = re.sub(r'#.*|[\t].*', '', line).strip()
                if clean_line:
                    sentence_text += clean_line + " "

def _parse_unstructured_corpus(file_path, nlp, outfile):

    doc_id = None
    url = None
    text_buffer = ""
    sentence_id = 1

    with open(file_path, 'r', encoding='latin-1') as f:
        for line in f:
            line = line.strip()

            if line.startswith('<text'):
                if text_buffer:
                    doc = nlp(text_buffer.strip())

                    if doc_id:
                        outfile.write(f"# newdoc id = {doc_id}\n")
                    if url:
                        outfile.write(f"# newdoc url = {url}\n")

                    for sent in doc.sents:
                        outfile.write(f"# sent_id = {sentence_id}\n")
                        outfile.write(f"# text = {sent.text}\n")
                        outfile.write(sent._.conll_str + "\n")
                        sentence_id += 1
                    text_buffer = ""
                    doc_id = None
                    url = None
                    sentence_id = 1

                match_id = re.search(r'id="([^"]+)"', line)
                doc_id = match_id.group(1) if match_id else None
                match_url = re.search(r'url="([^"]+)"', line)
                url = match_url.group(1) if match_url else None

            elif not line.startswith('<') and not line.startswith('#') and line:
                clean_line = re.sub(r'#.*|[\t].*', '', line).strip()
                if clean_line:
                    text_buffer += clean_line + " "

        if text_buffer:
            doc = nlp(text_buffer.strip())
            if doc_id:
                outfile.write(f"# newdoc id = {doc_id}\n")
            if url:
                outfile.write(f"# newdoc url = {url}\n")
            for sent in doc.sents:
                outfile.write(f"# sent_id = {sentence_id}\n")
                outfile.write(f"# text = {sent.text}\n")
                outfile.write(sent._.conll_str + "\n")
                sentence_id += 1


>>>>>>> 4d3e62325668bb318665d2186fc45a1105e2374c
def main_parser(file_paths):

    nlp = _get_nlp_instance()
    if not nlp:
        return

    output_dir = "corpora_parsati_UD"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            output_file_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.conllu")

            print(f"Inizio il parsing di '{file_name}'...")

            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                if 'repubblica' in file_name.lower():
                    _parse_repubblica(nlp, outfile, file_path)
                elif 'itwac' in file_name.lower():
                    _parse_itwac(nlp, outfile, file_path)
                elif 'paisa' in file_name.lower():
                    _parse_paisa(nlp, outfile, file_path)
                else:
                    print(f"ATTENZIONE: Nessuna funzione di parsing trovata per il file '{file_name}'. Saltato.")

            print(f"Parsing completato. Il risultato è stato salvato in '{output_file_path}'")

        except FileNotFoundError:
            print(f"Errore: Il file '{file_path}' non è stato trovato.")
        except Exception as e:
            print(f"Si è verificato un errore inaspettato durante l'analisi di '{file_path}': {e}")

def _structured_corpus_generator(file_path):
    doc_id = None
    url = None
    
    with open(file_path, 'r', encoding='latin-1') as f:
        sentence_text = ""
        
        for line in f:
            line = line.strip()

            if line.startswith('<text'):
                match_id = re.search(r'id="([^"]+)"', line)
                doc_id = match_id.group(1) if match_id else None
                match_url = re.search(r'url="([^"]+)"', line)
                url = match_url.group(1) if match_url else None
            
            elif line.startswith('<s>'):
                sentence_text = ""
            
            elif line.startswith('</s>'):
                if sentence_text:
                    final_text = sentence_text.strip()
                    final_text = ftfy.fix_text(final_text) 
                    metadata = {"doc_id": doc_id, "url": url}
                    yield final_text, metadata
                sentence_text = ""
            
            elif line and not line.startswith('<'):
                clean_line = re.sub(r'#.*|[\t].*', '', line).strip()

                if clean_line:
                    sentence_text += clean_line + " "

def _parse_repubblica(nlp, outfile, file_path):
    sentence_data = list(_structured_corpus_generator(file_path))
    
    if not sentence_data:
        print(f"Attenzione: Nessun dato trovato nel file {file_path}")
        return

    texts = [text for text, meta in sentence_data]
    docs = nlp.pipe(texts)
    
    current_doc_id = None
    sentence_id = 1
    
    for doc, (text, metadata) in zip(docs, sentence_data):

        if metadata['doc_id'] != current_doc_id:
            sentence_id = 1
            current_doc_id = metadata['doc_id']
            
            if metadata['doc_id']: outfile.write(f"# newdoc id = {metadata['doc_id']}\n")
            if metadata['url']: outfile.write(f"# newdoc url = {metadata['url']}\n")

        outfile.write(f"# sent_id = {sentence_id}\n")
        outfile.write(f"# text = {text}\n")
        outfile.write(doc._.conll_str + "\n")
        
        sentence_id += 1

def _parse_itwac(nlp, outfile, file_path):
    _parse_repubblica(nlp, outfile, file_path) 

def _unstructured_corpus_generator(file_path):
    doc_id = None
    url = None
    text_buffer = ""
    
    with open(file_path, 'r', encoding='latin-1') as f:
        for line in f:
            line = line.strip()

            if line.startswith('<text'):
                if text_buffer:
                    final_text = text_buffer.strip()
                    final_text = ftfy.fix_text(final_text) 
                    metadata = {"doc_id": doc_id, "url": url}
                    yield final_text, metadata
              
                text_buffer = ""
                match_id = re.search(r'id="([^"]+)"', line)
                doc_id = match_id.group(1) if match_id else None
                match_url = re.search(r'url="([^"]+)"', line)
                url = match_url.group(1) if match_url else None

            elif not line.startswith('<') and not line.startswith('#') and line:
                clean_line = re.sub(r'#.*|[\t].*', '', line).strip()
                if clean_line:
                    text_buffer += clean_line + " "

        if text_buffer:
            final_text = text_buffer.strip()
            final_text = ftfy.fix_text(final_text) 
            metadata = {"doc_id": doc_id, "url": url}
            yield final_text, metadata

def _parse_paisa(nlp, outfile, file_path):
    document_data = list(_unstructured_corpus_generator(file_path))
    
    if not document_data:
        print(f"Attenzione: Nessun dato trovato nel file {file_path}")
        return

    texts = [text for text, meta in document_data]
    docs = nlp.pipe(texts)
    
    for doc, (text, metadata) in zip(docs, document_data):
        
        sentence_id = 1

        if metadata['doc_id']: outfile.write(f"# newdoc id = {metadata['doc_id']}\n")
        if metadata['url']: outfile.write(f"# newdoc url = {metadata['url']}\n")
        for sent in doc.sents:
            outfile.write(f"# sent_id = {sentence_id}\n")
            outfile.write(f"# text = {sent.text}\n")
            outfile.write(sent._.conll_str + "\n")
            sentence_id += 1

if __name__ == "__main__":
    main_parser(['repubblica.sample', 'paisa.sample', 'itwac.sample'])
