import os
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# lettura dei file input

folderin = "data/db_esempi(NON-definitivo)"
folderout = "data/db_esempi"
os.makedirs(folderout, exist_ok=True)

# parser

def parse_with_udpipe(url, model, data):

    source, text = data["source"], data["text"]

    payload = urlencode(
        {
            "model": model,
            "tokenizer": "",
            "tagger": "",
            "parser": "",
            "data": text,
        }
    ).encode("utf-8")
    request = Request(url, data=payload, method="POST")

    try:
        with urlopen(request) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"UDPipe API HTTP error {exc.code}: {details}") from exc
    except URLError as exc:
        raise SystemExit(f"UDPipe API connection error: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"UDPipe API returned invalid JSON: {body[:200]}") from exc

    if "result" not in parsed:
        raise SystemExit(f"UDPipe API response missing 'result': {parsed}")

    return parsed["result"]

# scrittura dei file output

for fin in os.listdir(folderin):
    filepath = os.path.join(folderin, fin)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.readlines()
        source_in_header = content[0].strip("\n")
        text_in_header = content[1].strip("\n")
        sample_text = (text_in_header.rsplit("= ", 1)[1]).strip("\n")

        if __name__ == "__main__":
            DATA = {"source": source_in_header,
                    "text": sample_text}

            DEFAULT_MODEL = "italian-isdt-ud-2.17-251125"
            DEFAULT_URL = "https://lindat.mff.cuni.cz/services/udpipe/api/process"
            conllu = parse_with_udpipe(DEFAULT_URL, DEFAULT_MODEL, DATA)

            fout = f"{folderout}/{fin.strip(".txt")}.conllu"
            with open(fout, "w", encoding="utf-8") as f:
                
                for line in conllu.split("\n"):
                    if line.startswith("# new"):
                        continue
                    if line.startswith("# sent_id"):
                        f.write(f"{source_in_header}\n")
                    f.write(f"{line}\n")