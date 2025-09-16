import spacy
import re
import os
import spacy_conll

def parse_and_save_conllu(file_path):

    try:
        nlp = spacy.load("it_core_news_sm")
        nlp.add_pipe("conll_formatter", last=True)
    except OSError:
        print("Il modello di lingua italiana non è installato.")
        print("Per installarlo, esegui il comando nel terminale:")
        print("python -m spacy download it_core_news_sm")
        return

    nlp.max_length = 10000000

    output_dir = "corpora_parsed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.basename(file_path)
    output_file_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.conllu")

    doc_id = None
    url = None

    try:
        with open(file_path, 'r', encoding='latin-1') as f, open(output_file_path, 'w', encoding='utf-8') as outfile:
            sentence_text = ""
            sentence_id = 1

            for line in f:
                line = line.strip()

                if line.startswith('<text'):

                    match_id = re.search(r'id="([^"]+)"', line)
                    if match_id:
                        doc_id = match_id.group(1)

                    match_url = re.search(r'url="([^"]+)"', line)
                    if match_url:
                        url = match_url.group(1)

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

    except FileNotFoundError:
        print(f"Errore: Il file '{file_path}' non è stato trovato.")
        return
    except Exception as e:
        print(f"Si è verificato un errore inaspettato durante l'analisi del file: {e}")
        return

    print(f"Analisi completata. Il risultato è stato salvato in '{output_file_path}'")


if __name__ == "__main__":
    import sys
    parse_and_save_conllu(sys.argv[1])
    # parse_and_save_conllu('paisa.sample')
    # parse_and_save_conllu('itwac.sample')
