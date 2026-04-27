import os
import csv
import yaml
import textwrap
import rapidfuzz
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Export construction database CSV to YAML and CoNLL-C files.")
    parser.add_argument("input_csv", help="Input CSV file (e.g. export.csv)")
    parser.add_argument("--cc-database", default="cc-database/cc-database.yaml", metavar="FILE",
                        help="Comparative concepts database YAML file (default: cc-database.yaml)")
    parser.add_argument("--yml-out", default="data/db_yaml", metavar="DIR",
                        help="Output folder for YAML files (default: db_yaml)")
    parser.add_argument("--conllc-out", default="data/db_conllc(NON-definitivo)", metavar="DIR",
                        help="Output folder for CoNLL-C files (default: db_conllc(NON-definitivo))")
    parser.add_argument("--examples-out", default="data/db_esempi(NON-definitivo)", metavar="DIR",
                        help="Output folder for unparsed example TXT files (default: db_esempi(NON-definitivo))")
    return parser.parse_args()


def load_cc_maps(file_ccdatabase):
    with open(file_ccdatabase, "r", encoding="utf-8-sig", newline="") as f:
        ccdb = yaml.safe_load(f)

    map_functional = {}
    map_formal = {}

    for element in ccdb:
        eid = element["Id"]
        names = [eid[4:]] + [a.replace(" ", "-") for a in element.get("Alias", [])]
        if element["Type"] in ["sem", "inf"]:
            map_functional[eid] = names
        elif element["Type"] in ["cxn", "str"]:
            map_formal[eid] = names

    return map_formal, map_functional


def match_tags(tags_str, cc_map):
    results = []
    for tag in tags_str.split(", "):
        current = tag.replace(" ", "-")
        min_distance = float("inf")
        best_match = None
        for cc_id, aliases in cc_map.items():
            for alias in aliases:
                distance = rapidfuzz.distance.Levenshtein.distance(current, alias)
                if distance < min_distance:
                    min_distance = distance
                    best_match = cc_id
        if min_distance < 3:
            results.append(f"{current} >> cc:{best_match}")
        else:
            results.append(current)
    return results


def write_conllc(row, conllcfolderout):
    cxn_id = row["Construction ID"].replace("\n", " ")
    name = row["Form"].replace("\n", " ") if row["Name"] == "" else row["Name"].replace("\n", " ")

    conllc_template = {
        "cxn_id": cxn_id,
        "name": name,
        "function": row["Function"].replace("\n", " "),
        "horizontal_links": row["Horizontal links"].replace("\n", " "),
        "vertical_links": row["Vertical links"].replace("\n", " "),
        "fields": "ID UD.FORM LEMMA UPOS FEATS HEAD DEPREL REQUIRED WITHOUT SEM_FEATS SEM_ROLES ADJACENCY IDENTITY",
    }

    fout = os.path.join(conllcfolderout, f"cxn_{cxn_id}.conllc")
    with open(fout, "w", encoding="utf-8") as f:
        f.writelines(f"# {key} = {value} \n" for key, value in conllc_template.items())

    return f"cxn_{cxn_id}.conllc"


def write_examples(row, txtfolderout):
    cxn_id = row["Construction ID"].replace("\n", " ")
    example_files = []

    for n in range(1, 6):
        text_key = f"Examples {n}"
        source_key = f"Source {n}"
        if row.get(text_key, "") != "":
            filename = f"cxn_{cxn_id}_example_{n}.txt"
            foutdir = os.path.join(txtfolderout, filename)
            with open(foutdir, "w", encoding="utf-8") as f:
                f.write("# source = " + row[source_key].replace("\n", " "))
                f.write("\n# text = " + row[text_key].replace("\n", " "))
            example_files.append(filename)

    return example_files


def write_yaml(yaml_template, ymlfolderout):
    cxn_id = yaml_template["cxn-id"]
    fout = os.path.join(ymlfolderout, f"cxn_{cxn_id}.yml")
    width = 60

    with open(fout, "w", encoding="utf-8") as f:
        for key, value in yaml_template.items():
            if key in ["examples", "formal-tags", "functional-tags"]:
                value = "\n\t".join(f"- {item}" for item in value)
                f.write(f"{key}: \n\t{value}\n")
            elif key in ["form", "function", "restrictions", "coll-preferences", "complexity-level-tags", "category-tags", "note"]:
                f.write(f"{key}: |\n")
                for element in value:
                    f.write(f"\t-")
                    if element == "":
                        f.write("\n")
                    wrapped = textwrap.wrap(str(element), width=width)
                    for line in wrapped:
                        f.write(f"  {line}\n")
            else:
                wrapped = textwrap.wrap(str(value), width=width)
                f.write(f"{key}: |\n")
                for line in wrapped:
                    f.write(f"  {line}\n")
            f.write("\n")


def process_row(row, map_formal, map_functional, ymlfolderout, conllcfolderout, txtfolderout):
    cxn_id = row["Construction ID"].replace("\n", " ")
    name = row["Form"].replace("\n", " ") if row["Name"] == "" else row["Name"].replace("\n", " ")

    conllc_filename = write_conllc(row, conllcfolderout)
    example_files = write_examples(row, txtfolderout)

    yaml_template = {
        "cxn-id": cxn_id,
        "name": name,
        "cxn-machine-readable-formalization": conllc_filename,
        "form": [row["Form"].replace("\n", " "), row["Explain 2"].replace("\n", " ")],
        "function": [row["Function"].replace("\n", " "), row["Definition"].replace("\n", " "), row["Explain 1"].replace("\n", " ")],
        "restrictions": [row["Restrictions"].replace("\n", " "), row["Explain 3"].replace("\n", " ")],
        "coll-preferences": [row["Collocational preferences"].replace("\n", " "), row["Explain 4"].replace("\n", " ")],
        "usage": row["Usage"].replace("\n", " "),
        "formal-tags": match_tags(row["Formal Tags"], map_formal),
        "functional-tags": match_tags(row["Functional Tags"], map_functional),
        "complexity-level-tags": [row["Complexity level tags"].replace("\n", " "), row["Complexity level"].replace("\n", " ")],
        "category-tags": [row["Category tags"].replace("\n", " "), row["Category"].replace("\n", " ")],
        "schematicity-level": row["Schematicity Level"].replace("\n", " "),
        "cefr-level": "",
        "horizontal-links": row["Horizontal links"].replace("\n", " "),
        "vertical-links": row["Vertical links"].replace("\n", " "),
        "examples": example_files,
        "note": [row["Notes"].replace("\n", " "), f"USAGE: {row["Explain 5"].replace("\n", " ")}"],
        "references": "",
        "collector": row["Data Collector"].replace("\n", " "),
    }

    write_yaml(yaml_template, ymlfolderout)


def main():
    args = parse_args()

    os.makedirs(args.yml_out, exist_ok=True)
    os.makedirs(args.conllc_out, exist_ok=True)
    os.makedirs(args.examples_out, exist_ok=True)

    map_formal, map_functional = load_cc_maps(args.cc_database)

    with open(args.input_csv, "r", encoding="utf-8-sig", newline="") as csvfin:
        csvreader = csv.DictReader(csvfin, delimiter=",")
        for row in csvreader:
            process_row(row, map_formal, map_functional, args.yml_out, args.conllc_out, args.examples_out)


if __name__ == "__main__":
    main()
