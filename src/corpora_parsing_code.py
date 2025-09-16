import spacy
import re
import os
import spacy_conll

def _get_nlp_instance():

    try:
        nlp = spacy.load("it_core_news_sm")
        nlp.add_pipe("conll_formatter", last=True)
        return nlp
    except OSError:
        print("Il modello di lingua italiana non è installato.")
        print("Per installarlo, esegui il comando nel terminale:")
        print("python -m spacy download it_core_news_sm")
        return None

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
            
            elif line.startswith('<s>'):
                sentence_text = ""
            
            elif line.startswith('</s>'):
                if sentence_text:
                    final_text = sentence_text.strip()
                    doc = nlp(final_text)
                    
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
                if 'paisa' in file_name.lower():
                    _parse_unstructured_corpus(file_path, nlp, outfile)
                else:
                    _parse_structured_corpus(file_path, nlp, outfile)
            
            print(f"Parsing completato. Il risultato è stato salvato in '{output_file_path}'")
        
        except FileNotFoundError:
            print(f"Errore: Il file '{file_path}' non è stato trovato.")
        except Exception as e:
            print(f"Si è verificato un errore inaspettato durante l'analisi di '{file_path}': {e}")
            
main_parser(['repubblica.sample', 'paisa.sample', 'itwac.sample'])

