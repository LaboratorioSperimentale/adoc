import os
import csv
import yaml
import textwrap
import rapidfuzz

fin = "export.csv"
ymlfolderout = "cxn_yml"

os.makedirs(ymlfolderout, exist_ok=True)

file_ccdatabase = "cc-database.yaml"

CCDB = yaml.safe_load(open(file_ccdatabase, "r", encoding = "utf-8-sig", newline = ""))

map_functional = {}
map_formal = {}

for element in CCDB:
    if element["Type"] in ["sem", "inf"]:
        map_functional[element["Id"]] = [element["Id"][4:]]
        aliases = element.get("Alias", [])
        for alias in aliases:
            map_functional[element["Id"]].append(alias.replace(" ", "-"))
    
    elif element["Type"] in ["cxn", "str"]:
        map_formal[element["Id"]] = [element["Id"][4:]]
        aliases = element.get("Alias", [])
        for alias in aliases:
            map_formal[element["Id"]].append(alias.replace(" ", "-"))

with open(fin, "r", encoding = "utf-8-sig", newline = "",) as csvfin:
    csvreader = csv.DictReader(csvfin, delimiter = ",")
    for row in csvreader:
        
        yaml_template = {
            "cxn-id": "",
            "name": "",
            "cxn-machine-readable-formalization": "",
            "form": "",
            "definition": "", 
            "restrictions": "",
            "coll-preferences": "",
            "usage": "",
            "formal-tags": "",
            "functional-tags": "",
            "complexity-level-tags": "",
            "category-tags": "",
            "schematicity-level": "",
            "cefr-level": "",
            "horizontal-links": "",
            "vertical-links": "",
            "examples": "",
            "note": "",
            "references": "",
            "collector": "",
            "to-be-kept": "",
        }

# mapping tra i key-value pairings di yaml_template e i key-value pairings tra ogni riga e l'header del csv

        yaml_template["cxn-id"] = row["Construction ID"].replace("\n", " ")

        if row["Name"] == "":
            yaml_template["name"] = row["Form"].replace("\n", " ")
        else:
            yaml_template["name"] = row["Name"].replace("\n", " ")
        
# creazione del file conllc

        conllcfolderout = "cxn_conllc"
        os.makedirs(conllcfolderout, exist_ok=True)
        fout = f"{conllcfolderout}/cxn_{row["Construction ID"]}.conllc"

        conllc_template = {
            "cxn_id": "",
            "name": "",
            "function": "",
            "horizontal_links": "",
            "vertical_links": "",
            "fields" : "ID UD.FORM LEMMA UPOS FEATS HEAD DEPREL REQUIRED WITHOUT SEM_FEATS SEM_ROLES ADJACENCY IDENTITY"
        }

        conllc_template["cxn_id"] = row["Construction ID"].replace("\n", " ")
        if row["Name"] == "":
            conllc_template["name"] = row["Form"].replace("\n", " ")
        else:
            conllc_template["name"] = row["Name"].replace("\n", " ")
        conllc_template["function"] = row["Function"].replace("\n", " ")

        with open(fout, "w", encoding = "utf-8") as conllcfout:
            conllcfout.writelines(f"# {key} = {value} \n" for key, value in conllc_template.items())

# ripresa del mapping

        yaml_template["cxn-machine-readable-formalization"] = f"cxn_{row["Construction ID"]}.conllc"

        yaml_template["form"] = row["Form"].replace("\n", " ")

        yaml_template["definition"] = row["Function"].replace("\n", " ")

        # yaml_template["restrictions"] # NON ESISTE, VUOTO
        # yaml_template["coll-preferences"] # NON ESISTE, VUOTO
        # yaml_template["usage"] # NON ESISTE, VUOTO

# ricerca di formal-tags e functional tags tra i comparative concepts

        yaml_template["formal-tags"] = row["Formal Tags"].split(", ")
        for i, el in enumerate(yaml_template["formal-tags"]):
            current_tag = el.replace(" ", "-")
            
            min_distance = float("inf")
            best_match = None
            for cc_tag in map_formal:
                # print("Evaluating:", current_tag, "against", cc_tag)
                for alias in map_formal[cc_tag]:
                    # print("Comparing with alias:", alias)
                    distance = rapidfuzz.distance.Levenshtein.distance(current_tag, alias)
                    # print("Distance:", distance)
                    if distance < min_distance:
                        min_distance = distance
                        best_match = cc_tag
            if min_distance < 3:  # Soglia di distanza per considerare una corrispondenza valida
                yaml_template["formal-tags"][i] = f"{current_tag} >> cc:{best_match}"
            else:
                yaml_template["formal-tags"][i] = f"{current_tag}"
            
        yaml_template["functional-tags"] = row["Functional Tags"].split(", ") # cercare nei CC
        for i, el in enumerate(yaml_template["functional-tags"]):
            current_tag = el.replace(" ", "-")
            
            min_distance = float("inf")
            best_match = None
            for cc_tag in map_functional:
                # print("Evaluating:", current_tag, "against", cc_tag)
                for alias in map_functional[cc_tag]:
                    # print("Comparing with alias:", alias)
                    distance = rapidfuzz.distance.Levenshtein.distance(current_tag, alias)
                    # print("Distance:", distance)
                    if distance < min_distance:
                        min_distance = distance
                        best_match = cc_tag
            if min_distance < 3:  # Soglia di distanza per considerare una corrispondenza valida
                yaml_template["functional-tags"][i] = f"{current_tag} >> cc:{best_match}"
            else:
                yaml_template["functional-tags"][i] = f"{current_tag}"
        # for i, el in enumerate(yaml_template["functional-tags"]):
        #     yaml_template["functional-tags"][i] = el.replace(" ", "-")

# ripresa del mapping

        # yaml_template["complexity-level-tags"] # NON ESISTE, VUOTO
        # yaml_template["category-tags"] # NON ESISTE, VUOTO

        yaml_template["schematicity-level"] = row["Schematicity Level"].replace("\n", " ")

        # yaml_template["cefr-level"] # NON ESISTE, VUOTO
        # yaml_template["horizontal-links"] # NON ESISTE, VUOTO
        # yaml_template["vertical-links"] # NON ESISTE, VUOTO

# creazione dei file txt per gli esempi

        txtfolderout = "cxn_examples_unparsed"
        os.makedirs(txtfolderout, exist_ok=True)

        if row["Examples 1"] != "":
            fout_1 = f"cxn_{row["Construction ID"]}_example_1.txt"
            foutdir = f"{txtfolderout}/{fout_1}"
            with open(foutdir, "w", encoding = "utf-8") as txtfout:
                txtfout.write("# source = "+row["Source 1"].replace("\n", " "))
                txtfout.write("\n# text = "+row["Examples 1"].replace("\n", " "))

        if row["Examples 2"] != "":
            fout_2 = f"cxn_{row["Construction ID"]}_example_2.txt"
            foutdir = f"{txtfolderout}/{fout_2}"
            with open(foutdir, "w", encoding = "utf-8") as txtfout:
                txtfout.write("# source = "+row["Source 2"].replace("\n", " "))
                txtfout.write("\n# text = "+row["Examples 2"].replace("\n", " "))

        if row["Examples 3"] != "":
            fout_3 = f"cxn_{row["Construction ID"]}_example_3.txt"
            foutdir = f"{txtfolderout}/{fout_3}"
            with open(foutdir, "w", encoding = "utf-8") as txtfout:
                txtfout.write("# source = "+row["Source 3"].replace("\n", " "))
                txtfout.write("\n# text = "+row["Examples 3"].replace("\n", " "))
        
        if row["Examples 4"] != "": 
            fout_4 = f"cxn_{row["Construction ID"]}_example_4.txt"
            foutdir = f"{txtfolderout}/{fout_4}"
            with open(foutdir, "w", encoding = "utf-8") as txtfout:
                txtfout.write("# source = "+row["Source 4"].replace("\n", " "))
                txtfout.write("\n# text = "+row["Examples 4"].replace("\n", " "))

        if row["Examples 5"] != "":    
            fout_5 = f"cxn_{row["Construction ID"]}_example_5.txt"
            foutdir = f"{txtfolderout}/{fout_5}"
            with open(foutdir, "w", encoding = "utf-8") as txtfout:
                txtfout.write("# source = "+row["Source 5"].replace("\n", " "))
                txtfout.write("\n# text = "+row["Examples 5"].replace("\n", " "))

# ripresa del mapping

        # yaml_template["examples"] = f"\n\t- {fout_1}\n\t- {fout_2}\n\t- {fout_3}\n\t- {fout_4}\n\t- {fout_5}"
        yaml_template["examples"] = [fout_1, fout_2, fout_3, fout_4, fout_5]

        yaml_template["note"] = row["Notes"].replace("\n", " ")

        # yaml_template["references"] # NON ESISTE, VUOTO
        
        yaml_template["collector"] = row["Data Collector"].replace("\n", " ")

        yaml_template["to-be-kept"] = row["Francesca"].replace("\n", " ")      

# creazione del file yaml

        width = 60
        fout = f"{ymlfolderout}/cxn_{row["Construction ID"]}.yml"
        with open(fout, "w", encoding = "utf-8") as ymlfout:
            
            for key, value in yaml_template.items():
                if key in ["examples", "formal-tags", "functional-tags"]:
                    value = "\n\t".join(f"- {example}" for example in value)
                    ymlfout.write(f"{key}: \n\t{value}\n")
                else:
                    wrapped = textwrap.wrap(str(value), width=width)
                    
                    ymlfout.write(f"{key}: |\n")
                    for line in wrapped:
                        ymlfout.write(f"  {line}\n")
                ymlfout.write("\n")