import os
import re

FEATURE_KEYS = {
    "UD.FORM": "form",
    "FORM": "form",    # cxns_from_examples.py's own generated .conllc uses "FORM", not "UD.FORM"
    "LEMMA": "lemma",
    "UPOS": "upos",
}
STRUCTURAL_KEYS = {
    "HEAD": "head",
    "DEPREL": "deprel",
    "IDENTITY": "identity",
    "ADJACENCY": "adjacency",
    "EXCLUSION": "exclusion",
}


_FEATS_KV_RE = re.compile(r"^\w+=[^=,|]+$")


def _split_feats(raw):
    """Split a FEATS cell into separate Grew clauses.

    Two conventions have to coexist here:
      - the plain-UD convention (what cxns_from_examples.py itself writes):
        "|" separates *different* keys, e.g. "Mood=Ind|Number=Sing" -- each
        key=value pair must become its own clause, or Grew reads the whole
        thing as one bogus disjunctive value of a single feature.
      - this project's own convention (see test-cases/features_disjunction):
        "," separates clauses, and "|" is left untouched *inside* a clause
        as Grew's own disjunction operator, e.g. "VerbForm=Fin|Pers=3, VerbForm=Inf".

    Disambiguation: only treat "|" as a key separator when there's no comma
    at all AND every pipe-segment is a clean, distinct "key=value" pair --
    that's unambiguously the plain-UD shape and never true of a real
    Grew-style disjunction clause (which repeats the same key across '|').
    Otherwise, fall back to the comma-split/pipe-untouched convention.
    """
    if "," not in raw:
        segments = [s.strip() for s in raw.split("|")]
        if len(segments) > 1 and all(_FEATS_KV_RE.match(s) for s in segments):
            keys = [s.split("=", 1)[0] for s in segments]
            if len(set(keys)) == len(keys):
                return segments
    return [chunk.strip() for chunk in raw.split(",") if chunk.strip()]


def create_ud_node(node_info):
    ret = {
        FEATURE_KEYS[k]: v
        for k, v in node_info.items()
        if k in FEATURE_KEYS and v != "_"
    }

    if "FEATS" in node_info and node_info["FEATS"] != "_":
        ret["feats"] = _split_feats(node_info["FEATS"])

    for k, ret_key in STRUCTURAL_KEYS.items():
        if k in node_info and node_info[k] != "_":
            ret[ret_key] = node_info[k].strip()

    return ret


def parse_custom_conllu_cxn(conllu_string):
    """Parse a .conllc file into an ordered list of constructions, each
    {"cxn_id": ..., "nodes": {ID: node_dict, ...}}. Node IDs are only unique
    *within* a construction, so constructions must stay separated -- a flat
    dict keyed by ID alone would silently collide across constructions that
    reuse the same letter IDs (which is most of them)."""
    constructions = []
    cxn_id, header, nodes = None, [], {}

    def flush():
        if cxn_id is not None and nodes:
            constructions.append({"cxn_id": cxn_id, "nodes": nodes})

    for raw_line in conllu_string.strip().split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# cxn_id"):
            flush()
            cxn_id, header, nodes = line.split("=", 1)[1].strip(), [], {}
        elif line.startswith("# name") or line.startswith("# cxn_name"):
            continue
        elif line.startswith("# fields"):
            # "# fields = ID UD.FORM LEMMA UPOS ..." (space-separated column list)
            header = [x.strip() for x in line.split("=", 1)[1].split()]
        elif line.startswith("# ID"):
            # cxns_from_examples.py's own dialect: "# ID\tFORM\tLEMMA\t..."
            # (tab-separated column names directly, no "fields =" prefix)
            header = [x.strip() for x in line.lstrip("#").strip().split("\t")]
        elif line.startswith("#"):
            continue
        else:
            parts = line.split("\t")
            if header and len(parts) == len(header):
                node_info = dict(zip(header, parts))
                nodes[node_info["ID"]] = create_ud_node(node_info)

    flush()
    return constructions


def _split_disjunction(raw):
    """Strip a leading '!' (negation) and split the rest on ',' (disjunction)."""
    negated = raw.startswith("!")
    v = raw[1:] if negated else raw
    return negated, [p.strip() for p in v.split(",") if p.strip()]


def _form_clause(value):
    if value.startswith("/"):
        return f"form={value}"
    negated, values = _split_disjunction(value)
    rhs = "|".join(f"/{v}/i" for v in values)
    return f"form{'<>' if negated else '='}{rhs}"


def _lemma_clause(value):
    if value.startswith("/"):
        return f"lemma={value}"
    negated, values = _split_disjunction(value)
    rhs = "|".join(f'"{v}"' for v in values)
    return f"lemma{'<>' if negated else '='}{rhs}"


def _upos_clause(value):
    negated, values = _split_disjunction(value)
    rhs = "|".join(values)
    return f"upos{'<>' if negated else '='}{rhs}"


def _edge_label(value):
    """DEPREL disjunction/negation follows the same convention as every
    other field per guida.md: ',' separates alternative values (e.g. the
    real "case,mark" / "obl, xcomp" seen in ItCon/constructions/conllc/),
    translated to Grew's own '|'; a leading '!' becomes Grew's edge-negation
    '^' (which applies to the whole disjunction, per grew.fr/doc/request)."""
    negated, values = _split_disjunction(value)
    label = "|".join(values)
    return f"^{label}" if negated else label


def convert(construction):
    cxn_id = construction["cxn_id"]
    nodes = construction["nodes"]

    node_lines, edge_lines, constraint_lines = [], [], []
    without_blocks = []
    fresh = [0]

    def fresh_name(prefix):
        fresh[0] += 1
        return f"_{prefix}{fresh[0]}"

    for name, node in nodes.items():
        clauses = []
        if "lemma" in node:
            clauses.append(_lemma_clause(node["lemma"]))
        if "upos" in node:
            clauses.append(_upos_clause(node["upos"]))
        if "form" in node:
            clauses.append(_form_clause(node["form"]))
        for f in node.get("feats", []):
            clauses.append(f)

        node_lines.append(f"  {name} [{', '.join(clauses)}];" if clauses else f"  {name} [];")

        head, deprel = node.get("head"), node.get("deprel")
        if head is not None:
            if head == "0":
                if deprel and deprel.startswith("root:"):
                    ext_rel = deprel.split(":", 1)[1]
                    edge_lines.append(f"  {name} -[{ext_rel}]-> {fresh_name('EXT')};")
                # plain "root" (or no deprel given): unconstrained external
                # attachment, nothing to add
            else:
                label = _edge_label(deprel) if deprel else ""
                edge_lines.append(f"  {head} -[{label}]-> {name};" if label else f"  {head} -> {name};")

        if "identity" in node:
            # "field_name:ID" per guida.md, e.g. "FORM:C"; a dotted field
            # ("FEATS.Number:C") coindexes a single morphosyntactic feature --
            # Grew exposes FEATS keys as direct node attributes, so this is
            # just the bare feature name on both sides (e.g. A.Number = C.Number).
            for constraint in node["identity"].split("|"):
                constraint = constraint.strip()
                if ":" not in constraint:
                    continue
                field, other = constraint.split(":", 1)
                field, other = field.strip(), other.strip()
                if "." in field:
                    _, grew_field = field.split(".", 1)
                else:
                    grew_field = FEATURE_KEYS.get(f"UD.{field}", field.lower())
                constraint_lines.append(f"  {name}.{grew_field} = {other}.{grew_field};")

        if "adjacency" in node:
            # Y << X for each Y listed on X's row -- guida.md: "X's ADJACENCY
            # containing Y means X immediately precedes Y", confirmed for
            # direction by its own worked N-dopo-N example, and now explicit
            # about the operator too: "in grew, A << B".
            for other in re.split(r"[|,]", node["adjacency"]):
                other = other.strip()
                if other:
                    constraint_lines.append(f"  {other} << {name};")

        if "exclusion" in node:
            for constraint in node["exclusion"].split("|"):
                m = re.match(r"CHILDREN:DEPREL=(.+)", constraint.strip())
                if m:
                    excl_node = fresh_name("EXCL")
                    without_blocks.append([f"  {name} -[{_edge_label(m.group(1))}]-> {excl_node};"])

    body = node_lines + edge_lines + constraint_lines
    out = ["pattern {"] + body + ["}"]
    for wb in without_blocks:
        out += ["without {"] + wb + ["}"]

    return "\n".join(out)


def convert_file(conllc_text):
    """Convert a whole .conllc file (possibly several constructions) into
    one Grew pattern per construction, joined by blank lines."""
    return "\n\n".join(convert(c) for c in parse_custom_conllu_cxn(conllc_text))


def convert_directory(conllc_dir, gq_dir):
    """Convert every .conllc file in conllc_dir into a matching .gq file in
    gq_dir (same basename), one construction per input file, as written by
    cxns_from_examples.py. Returns the number of .gq files written."""
    os.makedirs(gq_dir, exist_ok=True)
    for stale in os.listdir(gq_dir):
        if stale.endswith(".gq"):
            os.remove(os.path.join(gq_dir, stale))

    count = 0
    for fname in sorted(os.listdir(conllc_dir)):
        if not fname.endswith(".conllc"):
            continue
        name = fname[: -len(".conllc")]
        input_data = open(os.path.join(conllc_dir, fname), encoding="utf-8").read()
        result_gq = convert_file(input_data)
        with open(os.path.join(gq_dir, f"{name}.gq"), "w", encoding="utf-8") as f:
            f.write(result_gq + "\n")
        count += 1
    return count


def run_self_test(test_cases_dir):
    failures = 0
    for fname in sorted(os.listdir(test_cases_dir)):
        if not fname.endswith(".conllc"):
            continue
        name = fname[: -len(".conllc")]
        in_p = os.path.join(test_cases_dir, fname)
        out_p = os.path.join(test_cases_dir, f"{name}.gq")
        if not os.path.exists(out_p):
            continue

        input_data = open(in_p, encoding="utf-8").read()
        result_gq = convert_file(input_data)

        expected = open(out_p, encoding="utf-8").read()
        gen = [l.strip() for l in result_gq.split("\n") if l.strip()]
        exp = [l.strip() for l in expected.split("\n") if l.strip()]

        if gen == exp:
            print(f"PASS  {name}")
        else:
            failures += 1
            print(f"FAIL  {name}")
            print(f"  got:      {gen}")
            print(f"  expected: {exp}")

    if failures:
        raise SystemExit(f"{failures} test case(s) failed")
    print("all test cases passed")


if __name__ == "__main__":
    import sys

    base = os.path.dirname(os.path.abspath(__file__))

    if "--self-test" in sys.argv:
        run_self_test(os.path.join(base, "..", "test-cases"))
    else:
        conllc_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "..", "..", "data", "constructions", "conllc")
        gq_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, "..", "..", "data", "output", "gq")
        n = convert_directory(conllc_dir, gq_dir)
        print(f"wrote {n} Grew pattern file(s) to {gq_dir}")
