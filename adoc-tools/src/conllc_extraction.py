"""
Derive CoNLL-C-style construction skeletons (UD-compatible columns only --
ID, FORM, LEMMA, UPOS, FEATS, HEAD, DEPREL -- no IDENTITY/ADJACENCY/EXCLUSION/
SEM_FEATS/SEM_ROLES/REQUIRED, which need human judgement) from grouped example
sentences.

Vendored from Catenae/adoc/scripts/conllc_from_examples.py. Unlike the
subgraph/background-frequency ranking in cxns_from_examples.py, this does NOT
collapse a catena to a flat rendered string. It keeps the actual head/deprel
skeleton of each catena, so that slots can be aligned across sentences and
each column is filled in only where it is genuinely invariant across every
example -- exactly the "restriction or no restriction" logic CoNLL-C is built
on. Alignment is done via a structural signature (deprel-labeled tree shape)
rather than exact node position, so e.g. Italian clitics that are proclitic in
one example and enclitic in another still match up.
"""
import collections
import functools
import string

from typing import Dict, List, Optional, Sequence, Tuple

from common_catenae import pos_admitted, rel_admitted, word_admitted, recursive_catenae_extraction


def parse_sentence(lines: Sequence[str]) -> Tuple[Dict[int, List[int]], Dict[int, dict], set]:
    """Full per-position CoNLL-U record for a sentence, plus the admitted
    children map used for catena extraction.

    Returns:
        children: head position -> list of admitted child positions (0 = sentence root)
        info: position -> {form, lemma, upos, feats, head, deprel}
        excluded: positions whose FORM fails word_admitted (e.g. stray symbols)
    """
    children = collections.defaultdict(list)
    info: Dict[int, dict] = {}
    excluded = set()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split("\t")
        position_str = fields[0]
        if "-" in position_str or "." in position_str:
            continue

        position, form, lemma, upos, _, feats, head, deprel = (
            fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7]
        )

        if not (pos_admitted(upos) and rel_admitted(deprel)):
            continue
        if not head.lstrip("-").isdigit():
            continue

        position, head = int(position), int(head)

        if not word_admitted(form):
            excluded.add(position)

        children[head].append(position)
        info[position] = {
            "form": form, "lemma": lemma, "upos": upos,
            "feats": feats, "head": head, "deprel": deprel,
        }

    return children, info, excluded


def catenae_for_sentence(lines: Sequence[str], min_len: int = 1,
                          max_len: int = 6) -> Tuple[List[List[int]], Dict[int, dict]]:
    """All valid catenae (as sorted position lists) for a sentence, plus its info map."""
    children, info, excluded = parse_sentence(lines)
    if 0 not in children:
        return [], info

    root = children[0][0]
    _, catenae = recursive_catenae_extraction(root, children, min_len, max_len)

    valid = [sorted(c) for c in catenae if not any(p in excluded for p in c)]
    return valid, info


def _catena_tree(catena: List[int], info: Dict[int, dict]) -> Tuple[int, Dict[int, List[int]]]:
    """Children map (local head position -> child positions within the
    catena) and the position of the catena's local root (the one node whose
    real head sits outside the catena)."""
    catena_set = set(catena)
    children: Dict[int, List[int]] = collections.defaultdict(list)
    root = None
    for p in catena:
        head = info[p]["head"]
        if head in catena_set:
            children[head].append(p)
        else:
            root = p
    return root, children


def _canonical_subtree_signature(node: int, children: Dict[int, List[int]],
                                  info: Dict[int, dict]) -> tuple:
    child_sigs = [(info[c]["deprel"], _canonical_subtree_signature(c, children, info))
                  for c in children.get(node, [])]
    child_sigs.sort()
    return tuple(child_sigs)


def catena_signature(catena: List[int], info: Dict[int, dict]) -> tuple:
    """Structural skeleton of a catena, independent of both lexical content
    and linear word order: the shape of its internal dependency tree
    (deprel-labeled, canonically sorted at every level of siblings).

    The catena's local root's external attachment is deliberately NOT part of
    the signature: a construction can recur as the sentence root in one
    example and embedded (e.g. as a ccomp) in another while still being the
    same construction internally -- CoNLL-C's own "root" (unconstrained) vs
    "root:X" (constrained) DEPREL notation exists precisely to leave this open.
    """
    root, children = _catena_tree(catena, info)
    return _canonical_subtree_signature(root, children, info)


def canonical_order(catena: List[int], info: Dict[int, dict]) -> List[int]:
    """Deterministic traversal of a catena's internal tree -- root first,
    then children sorted by (deprel, subtree signature) at every level --
    used to assign stable slot IDs across instances that share a signature,
    regardless of each instance's original word order."""
    root, children = _catena_tree(catena, info)

    order: List[int] = []

    def visit(node: int) -> None:
        order.append(node)
        kids = sorted(
            children.get(node, []),
            key=lambda c: (info[c]["deprel"], _canonical_subtree_signature(c, children, info)),
        )
        for c in kids:
            visit(c)

    visit(root)
    return order


def candidate_catenae_by_signature(lines: Sequence[str], min_len: int = 1,
                                    max_len: int = 6) -> Tuple[Dict[tuple, List[List[int]]], Dict[int, dict]]:
    """All catena instances per distinct signature found in a sentence."""
    catenae, info = catenae_for_sentence(lines, min_len, max_len)

    by_sig: Dict[tuple, List[List[int]]] = collections.defaultdict(list)
    for catena in sorted(catenae):
        sig = catena_signature(catena, info)
        by_sig[sig].append(catena)

    return dict(by_sig), info


def _feats_dict(feats_str: str) -> dict:
    if feats_str in ("_", ""):
        return {}
    return dict(pair.split("=", 1) for pair in feats_str.split("|"))


def _letter_ids(n: int) -> List[str]:
    letters = list(string.ascii_uppercase)
    if n <= len(letters):
        return letters[:n]
    out = []
    i = 0
    while len(out) < n:
        out.append(letters[i % 26] * (1 + i // 26))
        i += 1
    return out


def _output_order(instances: List[Tuple[List[int], Dict[int, dict]]],
                   struct_orders: List[List[int]],
                   parent_of: List[Optional[int]]) -> Tuple[List[int], List[bool]]:
    """Reconstruct a linear slot order to render the table in, preferring
    each instance's actual word order and falling back to a majority vote
    only where instances disagree."""
    n = len(struct_orders[0])
    stable = [True] * n

    def before(u: int, v: int) -> Tuple[bool, bool]:
        votes = [order[u] < order[v] for order in struct_orders]
        if all(votes):
            return True, True
        if not any(votes):
            return False, True
        n_true = sum(votes)
        return n_true >= (len(votes) - n_true), False

    def cmp(u: int, v: int) -> int:
        is_before, unanimous = before(u, v)
        if not unanimous:
            stable[u] = False
            stable[v] = False
        return -1 if is_before else 1

    side: List[Optional[bool]] = [None] * n
    for slot in range(n):
        p = parent_of[slot]
        if p is not None:
            is_before, unanimous = before(slot, p)
            side[slot] = is_before
            if not unanimous:
                stable[slot] = False

    children_of: Dict[Optional[int], List[int]] = collections.defaultdict(list)
    for slot in range(n):
        children_of[parent_of[slot]].append(slot)

    root = next(slot for slot in range(n) if parent_of[slot] is None)

    def render(slot: int) -> List[int]:
        kids = children_of.get(slot, [])
        left = sorted((k for k in kids if side[k] is True), key=functools.cmp_to_key(cmp))
        right = sorted((k for k in kids if side[k] is False), key=functools.cmp_to_key(cmp))
        out: List[int] = []
        for k in left:
            out.extend(render(k))
        out.append(slot)
        for k in right:
            out.extend(render(k))
        return out

    return render(root), stable


def build_conllc_table(instances: List[Tuple[List[int], Dict[int, dict]]]) -> List[dict]:
    """Given the representative (catena, info) pair from every sentence in a
    group -- all sharing the same order-independent signature -- build the
    CoNLL-C row list: FORM/LEMMA/UPOS filled in only where invariant across
    all sentences, FEATS as the intersection of shared key=value pairs,
    HEAD/DEPREL from the (guaranteed consistent) internal tree shape."""
    struct_orders = [canonical_order(catena, info) for catena, info in instances]
    n = len(struct_orders[0])
    ids = _letter_ids(n)

    slot_of = [{p: i for i, p in enumerate(order)} for order in struct_orders]
    catena_sets = [set(catena) for catena, _ in instances]

    node0_list, info0 = struct_orders[0], instances[0][1]
    parent_of: List[Optional[int]] = []
    for slot in range(n):
        head0 = info0[node0_list[slot]]["head"]
        parent_of.append(slot_of[0][head0] if head0 in catena_sets[0] else None)

    output_order, stable = _output_order(instances, struct_orders, parent_of)
    id_of_slot = {slot: ids[i] for i, slot in enumerate(output_order)}

    rows = [None] * n
    for slot in range(n):
        nodes = [order[slot] for order in struct_orders]
        forms = {info[node]["form"] for node, (_, info) in zip(nodes, instances)}
        lemmas = {info[node]["lemma"] for node, (_, info) in zip(nodes, instances)}
        upostags = {info[node]["upos"] for node, (_, info) in zip(nodes, instances)}
        feats_sets = [_feats_dict(info[node]["feats"]) for node, (_, info) in zip(nodes, instances)]

        common_feats = dict(feats_sets[0]) if feats_sets else {}
        for fd in feats_sets[1:]:
            common_feats = {k: v for k, v in common_feats.items() if fd.get(k) == v}

        node0, (_, info_first) = nodes[0], instances[0]
        head0 = info_first[node0]["head"]

        if parent_of[slot] is None:
            external_deprels = {info[node]["deprel"] for node, (_, info) in zip(nodes, instances)}
            head_id = "0"
            if len(external_deprels) == 1 and next(iter(external_deprels)) != "root":
                deprel_out = f"root:{next(iter(external_deprels))}"
            else:
                deprel_out = "root"
        else:
            head_id = id_of_slot[parent_of[slot]]
            deprel_out = info_first[node0]["deprel"]

        misc = "_" if stable[slot] else "LinearOrder=Variable"

        rows[slot] = {
            "id": id_of_slot[slot],
            "form": next(iter(forms)) if len(forms) == 1 else "_",
            "lemma": next(iter(lemmas)) if len(lemmas) == 1 else "_",
            "upos": next(iter(upostags)) if len(upostags) == 1 else "_",
            "feats": "|".join(f"{k}={v}" for k, v in sorted(common_feats.items())) or "_",
            "head": head_id,
            "deprel": deprel_out,
            "misc": misc,
        }

    return [rows[slot] for slot in output_order]


def _best_instance_combo(per_sentence_candidates: List[List[List[int]]],
                          infos: List[Dict[int, dict]], max_combos: int = 512
                          ) -> List[Tuple[List[int], Dict[int, dict]]]:
    """When a signature has more than one candidate catena in some sentence
    (ambiguous sibling deprels), try combinations and keep the one that
    maximizes cross-sentence lexical agreement."""
    if all(len(c) == 1 for c in per_sentence_candidates):
        return [(c[0], info) for c, info in zip(per_sentence_candidates, infos)]

    n_combos = 1
    for c in per_sentence_candidates:
        n_combos *= len(c)

    if n_combos > max_combos:
        return [(c[0], info) for c, info in zip(per_sentence_candidates, infos)]

    import itertools as _it

    best_combo, best_score = None, (-1, -1, -1)
    for combo in _it.product(*per_sentence_candidates):
        instances = list(zip(combo, infos))
        table = build_conllc_table(instances)
        score = (sum(1 for r in table if r["form"] != "_"),
                  sum(1 for r in table if r["lemma"] != "_"),
                  sum(1 for r in table if r["upos"] != "_"))
        if score > best_score:
            best_score, best_combo = score, instances

    return best_combo


def common_construction(sentences: Sequence[Sequence[str]], min_len: int = 1, max_len: int = 6,
                         max_sentence_len: int = 150) -> List[Tuple[float, List[dict]]]:
    """Find catena skeletons common to every sentence in the group, ranked by
    length + lexical specificity (number of slots with a fixed FORM).

    Returns each match as a (score, table) pair, best first, so callers can
    report the score alongside the table (e.g. in the TXT ranking) instead of
    only getting the winning table back.
    """
    sentences = list(sentences)

    non_empty = []
    for s in sentences:
        _, info, _ = parse_sentence(s)
        if info:
            non_empty.append(s)
        else:
            print(f"skipping stub sentence with no admitted tokens: {' '.join(l.split(chr(9))[1] for l in s)!r}")
    sentences = non_empty
    if not sentences:
        return []

    too_long = [s for s in sentences if len(s) > max_sentence_len]
    if too_long:
        print(f"skipping group: {len(too_long)} sentence(s) exceed "
              f"max_sentence_len={max_sentence_len} (longest has {max(len(s) for s in too_long)} tokens)")
        return []

    per_sentence = [candidate_catenae_by_signature(s, min_len, max_len) for s in sentences]
    if not per_sentence:
        return []

    infos = [info for _, info in per_sentence]
    signature_sets = [set(by_sig) for by_sig, _ in per_sentence]
    common_signatures = set.intersection(*signature_sets)

    scored = []
    for sig in common_signatures:
        per_sentence_candidates = [by_sig[sig] for by_sig, _ in per_sentence]
        instances = _best_instance_combo(per_sentence_candidates, infos)
        table = build_conllc_table(instances)

        length = len(table)
        n_lexicalized = sum(1 for row in table if row["form"] != "_")
        score = length + n_lexicalized

        scored.append((score, table))

    scored.sort(key=lambda x: -x[0])
    return scored


def format_conllc_block(cxn_id: str, table: List[dict], cxn_name: str = None) -> str:
    lines = [f"# cxn_id = {cxn_id}"]
    if cxn_name:
        lines.append(f"# cxn_name = {cxn_name}")
    lines.append("# " + "\t".join(["ID", "FORM", "LEMMA", "UPOS", "FEATS", "HEAD", "DEPREL", "MISC"]))
    for row in table:
        lines.append("\t".join([row["id"], row["form"], row["lemma"], row["upos"],
                                 row["feats"], row["head"], row["deprel"], row["misc"]]))
    return "\n".join(lines)
