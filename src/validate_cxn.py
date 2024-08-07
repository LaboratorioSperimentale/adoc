import glob
import warnings
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

#		exec(f"python3 tools/validate.py --lang it --level 2 --no-space-after ../UD_examples/VIT-8523.conllu")

v = CXNValidator(yaml.safe_load(open("validation/cxn_schema.yml")))

for file in glob.glob("cxns/*"):
	with open(file, encoding="utf-8") as stream:
		try:
			print("CONSTRUCTION N.", Path(file).stem.split("_")[1])
			cxn = yaml.safe_load(stream)
			print(v.validate(cxn))

			for field, value in v.errors.items():
				s = field+"\n"
				for x in value:
					s+=f"\t{x}\n"

				warnings.warn(s)

			# input()
		except yaml.YAMLError as exc:
			print(exc)