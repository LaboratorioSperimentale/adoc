import os

def create_ud_node(node_info):

    keys_map = {
        "UD.FORM": 'form',
        "LEMMA":   'lemma',
        "UPOS":    'upos'
    }

    ret = {
        keys_map[k]: v 
        for k, v in node_info.items() 
        if k in keys_map and v != "_"
    }
    
    if "FEATS" in node_info and node_info["FEATS"] != "_":
        ret['feats'] = [
            node_info["FEATS"].strip()
        ]
        
    return ret

def parse_custom_conllu_cxn(conllu_string):
    parsed_data = {}
    header = []
    
    for line in conllu_string.strip().split('\n'):
        line = line.strip()
        
        if not line or line.startswith(("# cxn_id", "# name")):
            continue
            
        if line.startswith("# fields"):
            header = [
                x.strip() 
                for x in line.split("=")[1].split()
            ]
        elif not line.startswith("#"):
            parts = line.split('\t')
            if len(parts) == len(header):
                node_info = dict(zip(header, parts))
                parsed_data[node_info["ID"]] = create_ud_node(node_info)
                
    return parsed_data

def convert(nodes_data):
    out = [
        "pattern {"
    ]
    
    for name, node in nodes_data.items():
        
        out.append(f"	{name}[];")
        
        values = {
            "lemma": f'"{node["lemma"]}"' if "lemma" in node and not node["lemma"].startswith("/") else node.get("lemma"),
            "upos":  node.get("upos"),
            "form":  f"/{node['form']}/i" if "form" in node else None
        }
 
        for key, val in values.items():
            if val:
                out.append(f"	{name}[{key}={val}];")
    
        if "feats" in node:
            for f in node["feats"]:
                out.append(f"	{name}[{f}];")
                
    out.append("}")
    return "\n".join(out)

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    
    target = "features_disjunction" 
    
    in_p  = os.path.join(base, "..", "test-cases", f"simple_constraints-1.conllc")
    out_p = os.path.join(base, "..", "test-cases", f"simple_constraints-1.gq")

    input_data = open(in_p, "r", encoding="utf-8").read()
    result_gq  = convert(parse_custom_conllu_cxn(input_data))
    
    output_data = open(out_p, "r", encoding="utf-8").read()
    gen = [l.strip() for l in result_gq.split("\n") if l.strip()]
    exp = [l.strip() for l in output_data.split("\n") if l.strip()]
    
    for a, b in zip(gen, exp):
        assert a == b

    print(f"✅ Conversione riuscita per: {target}")
    print("-" * 30)
    print(result_gq)