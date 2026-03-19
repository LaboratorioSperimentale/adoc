import os
import csv
import yaml

# fin = "toy_database_pulito.csv"
fin = "data/export.csv"
output_folder = "data/db_yaml"

os.makedirs(output_folder, exist_ok=True)

with open(fin, "r", encoding = "utf-8-sig", newline = "",) as csvfin:
    csvreader = csv.DictReader(csvfin, delimiter = ",")
    for row in csvreader:
        print(row)
        # input()
        fout = f"{output_folder}/{row["Construction ID"]}.yml"
        with open(fout, "w", encoding = "utf-8") as ymlfout:
            yaml.dump(row, ymlfout, allow_unicode = True)
            
            