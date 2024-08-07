import sys
import glob
import cerberus
import yaml
from pathlib import Path

CC_DB = yaml.safe_load(open("cc-database/cc-database.yaml"))
CC_LIST = {x["Name"]:x["Type"] for x in CC_DB}


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

v = CXNValidator(yaml.safe_load(open("validation/cxn_schema.yml")))

n_warnings = 0
for file in glob.glob("cxns/*"):
	with open(file, encoding="utf-8") as stream:
		try:
			cxn = yaml.safe_load(stream)

			validation_test = v.validate(cxn)
			label = "PASSED" if validation_test else "FAILED"

			print("CONSTRUCTION N.", Path(file).stem.split("_")[1], "-", label)


			for field, value in v.errors.items():

				print(f"WARNING: {field}")
				for x in value:
					print(f"\t{x}")
					n_warnings += 1
				print()
			print()

		except yaml.YAMLError as exc:
			print(exc)

if n_warnings > 0:
	print(f"During check {n_warnings} warnings have been detected. Please check your files!")
	sys.exit(1)