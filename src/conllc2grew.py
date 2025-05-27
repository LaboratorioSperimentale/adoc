# EMANUELE

# read conllc file
# write a .grw file with all the needed patterns (% is a comment in grew)

# two kinds of lines, (type1) r"^[A-Z]\t" or  (type2) r"^[A-Z]\.[0-9]\t"
# we only care for type1 lines

# CONSTRAINTS:
# ID => name of the node in the grew pattern.
# UD.FORM => either "_" or a constraint on the form. It can be a regex.
# LEMMA => either "_" or a constraint on the lemma. It can be a regex.
# UPOS => either "_" or a list of comma separated UPOS tags. This means that one of the values has to appear (OR)
# FEATS => either "_" or a list of pipe separated ud features. This meand that all the values have to appear (AND). Each feature if of the form [Name]=[Value]. Value can be a list of comma separated values (this means that one of the values has to appear (OR))
# HEAD => either "_" or one of the IDs
# DEPREL => either "_" or a comma separated list of UD dependency relations. "head" means that there is no constraint on that node
# WITHOUT => either "_" or CHILDREN:DEPREL=[dep] means that the node cannot have a children with this dep OR LEMMA=[lemma,*]  (more to add?)
# ADJACENCY => either "_" or ID and it means this.ID<ID
# LINEARITY => either "_" or ID and it means this.ID<<ID
# IDENTITY => either "_" or [column_name]=ID. It means that this.column == ID.column

def conllc2grew():
	pass

if __name__ == "__main__":

	conllc2grew()