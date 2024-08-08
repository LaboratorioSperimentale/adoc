import sys
from pathlib import Path

import cerberus
import yaml
from sty import fg
from pybtex.database import parse_file

CC_DB = yaml.safe_load(open("cc-database/cc-database.yaml", encoding="utf-8"))
CC_LIST = {x["Name"]:x["Type"] for x in CC_DB}
BIB = parse_file("bibliography/entries.bib", bib_format="bibtex")


class CXNValidator(cerberus.Validator):

	def _check_with_CClist_construction(self, field, value):
		if not value in CC_LIST:
			self._error(field, f"Value '{value}' not in list of comparative concepts")
		elif CC_LIST[value] not in ["cxn", "str"]:
			self._error(field, f"Value '{value}' has type '{CC_LIST[value]}' in list of comparative concepts, types 'str' or 'cxn' required")

	def _check_with_CClist_meaning(self, field, value):
		if not value in CC_LIST:
			self._error(field, f"Value '{value}' not in list of comparative concepts")
		elif CC_LIST[value] not in ["inf", "sem"]:
			self._error(field, f"Value '{value}' has type '{CC_LIST[value]}' in list of comparative concepts, types 'inf' or 'sem' required")

	def _check_with_conllc_path(self, field, value):
		p = Path("cxns_conllc").joinpath(value)
		if not p.exists():
			self._error(field, f"Value '{value}' is not a file in 'cxn_conllc folder'")

	def _check_with_conllu_path(self, field, value):
		p = Path("UD_examples").joinpath(value+".conllu")
		if not p.exists():
			self._error(field, f"Value '{value}' is not a file in 'UD_examples folder'")

		#TODO validate conllu file with example

	def _check_with_bibentry(self, field, value):

		if not value in BIB.entries:
			self._error(field, f"Value '{value}' is not a valid bibliographical identifier'")



if __name__ == "__main__":

	new_files = sys.argv[1:]

	v = CXNValidator(yaml.safe_load(open("validation/cxn_schema.yml", encoding="utf-8")))

	n_warnings = 0
	for file in new_files:
		with open(file, encoding="utf-8") as stream:
			try:
				cxn = yaml.safe_load(stream)

				validation_test = v.validate(cxn)

				if validation_test:
					output_str = fg.green + \
						f"[PASSED] CONSTRUCTION N. {Path(file).stem.split('_')[1]}: {cxn['name']}" + \
							fg.rs
				else:
					output_str = fg(255, 10, 10) + \
						f"[FAILED] CONSTRUCTION N. {Path(file).stem.split('_')[1]}: {cxn['name']}" + \
							fg.rs

				print(output_str)


				for field, value in v.errors.items():

					print(f"WARNING: {field}")
					for x in value:
						if len(x) > 0:
							if type(x) == str:
								print(f"\t{x}")
							else:
								for element in x:
									if type(element) == int:
										print(f"\titem-{element}: {' - '.join(x[element])}")
						else:
							print(f"\t{x}")
						n_warnings += 1
					print()
				print()

			except yaml.YAMLError as exc:
				print(exc)

	if n_warnings > 0:
		print(f"During check {n_warnings} warnings have been detected. Please check your files!")
	print()

