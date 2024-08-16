import sys
from pathlib import Path

import cerberus
import yaml
from sty import fg, bg
from pybtex.database import parse_file


CC_DB = yaml.safe_load(open("cc-database/cc-database.yaml", encoding="utf-8"))
CC_LIST = {x["Id"]:x["Type"] for x in CC_DB}
BIB = parse_file("bibliography/entries.bib", bib_format="bibtex")

class CXNValidator(cerberus.Validator):

	def _check_with_CClist_construction(self, field, value):
		if value is not None:
			if value.startswith("cc"):
				cc, category, name_str = value.split(":")
				cc_id = f"{category}:{name_str}"
				if not category in ["cxn", "str"]:
					self._error(field, f"(W) Value '{cc_id}' has type '{CC_LIST[cc_id]}' in list of comparative concepts, types 'str' or 'cxn' required")

				if not cc_id in CC_LIST:
					self._error(field, f"Value '{cc_id}' not in list of comparative concepts")

			else:
				self._error(field, f"(W) Value '{value}' defined by author")
				# self._warnings.append((field, f"DOUBLE CHECK: Value '{value}' created by author"))


	def _check_with_CClist_meaning(self, field, value):

		if value is not None:
			if value.startswith("cc"):
				cc, category, name_str = value.split(":")
				cc_id = f"{category}:{name_str}"
				if not category in ["inf", "sem"]:
					self._error(field, f"(W) Value '{cc_id}' has type '{CC_LIST[cc_id]}' in list of comparative concepts, types 'inf' or 'sem' required")

				if not cc_id in CC_LIST:
					self._error(field, f"Value '{cc_id}' not in list of comparative concepts")

			else:
				self._error(field, f"(W) Value '{value}' defined by author")



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
			except yaml.YAMLError as exc:
				print(exc)


			print(f"Examining CXN ID. {Path(file).stem.split('_')[1]}: {cxn['name']}")

			validation_test = v.validate(cxn)

			if validation_test:
				output_str = fg.green + \
					f"[PASSED] CONSTRUCTION N. {Path(file).stem.split('_')[1]}: {cxn['name']}" + \
						fg.rs

			else:

				n_errors = 0
				n_warning = 0

				for field, value in v.errors.items():
					print(f"Issue with field {field}")
					for x in value:
						if len(x) > 0:
							if type(x) == str:
								if x.startswith("(W)"):
									n_warnings += 1
								else:
									n_errors += 1
								print(f"\t{x}")
							else:
								for element, err_string in x.items():
									err_string = err_string[0]
									if err_string.startswith("(W)"):
										n_warnings += 1
									else:
										n_errors += 1
									print(f"\t{err_string}")
						else:
							if x.startswith("(W)"):
								n_warnings += 1
							else:
								n_errors += 1
							print(f"\t{x}")
				print()

				if n_errors > 0:
					output_str = fg(255, 10, 10) + \
						f"[FAILED] CONSTRUCTION N. {Path(file).stem.split('_')[1]}: {cxn['name']}" + \
							fg.rs
				else:
					output_str = fg.blue + \
						f"[WARNING] CONSTRUCTION N. {Path(file).stem.split('_')[1]}: {cxn['name']}" + \
							fg.rs

			print(output_str)
			print()






	# if n_warnings > 0:
	# 	print(f"During check {n_warnings} warnings have been detected. Please check your files!")
	# print()

