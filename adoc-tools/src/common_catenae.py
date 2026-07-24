"""
Extract catenae common to a small set of UD-parsed sentences, ranked by
a score that promotes both length and lexical specificity.

Vendored from Catenae/adoc/scripts/common_catenae.py (dependency-free port of
catenae.utils.catenae_utils: pos_admitted / rel_admitted / word_admitted /
recursive_catenae_extraction). See that repo for the original.
"""
import collections
import itertools
import re

from typing import Dict, Iterable, List, Sequence, Tuple


SENT_ID_RE = re.compile(r"^(cxn_\d+)_")
# Matches cxns_from_examples.py's own tag filter (CONTEXT, MORPHOLOGICAL, DROP)
# so both extraction algorithms in this file run over the exact same sentence
# groups.
DROPPED_TAGS = {"CONTEXT", "MORPHOLOGICAL", "DROP"}


ADMITTED_PUNCT = ".-' ’"  # includes the typographic apostrophe (') used in Italian, e.g. "c'e'"
POS_TO_EXCLUDE = ("PUNCT",)
RELS_TO_EXCLUDE = ("discourse", "fixed", "flat", "compound", "list", "parataxis", "orphan",
                   "goeswith", "reparandum", "punct", "dep")


def word_admitted(word: str) -> bool:
    # Unicode-aware: accepts accented letters (perché, città, ...), not just ASCII.
    return all(c.isalpha() or c in ADMITTED_PUNCT for c in word)


def pos_admitted(pos: str) -> bool:
    return pos not in POS_TO_EXCLUDE


def rel_admitted(rel: str) -> bool:
    return rel not in RELS_TO_EXCLUDE


def recursive_catenae_extraction(node, tree_children, min_len_catena, max_len_catena):
    """Children are combined incrementally with early pruning instead of via a
    full itertools.product, so wide/flat subtrees don't blow up combinatorially.
    """
    if node not in tree_children:
        return [[node]], [[node]]

    found_catenae = []
    partial = [[node]]

    for child in tree_children[node]:
        c, all_c = recursive_catenae_extraction(child, tree_children, min_len_catena, max_len_catena)
        found_catenae += all_c

        next_partial = []
        for p in partial:
            next_partial.append(p)  # option: exclude this child's subtree entirely
            for child_catena in c:
                if len(p) + len(child_catena) <= max_len_catena:
                    next_partial.append(sorted(p + child_catena))
        partial = next_partial

    combos = [c for c in partial if min_len_catena <= len(c) <= max_len_catena]
    return combos, combos + found_catenae


def _parse_conllu_sentence(lines: Sequence[str]):
    children = collections.defaultdict(list)
    tokens, postags, rels = {}, {}, {}
    excluded = set()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        fields = line.split("\t")
        position_str = fields[0]
        if "-" in position_str or "." in position_str:
            continue

        position, word, _, pos, _, _, head, rel = fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7]

        if not (pos_admitted(pos) and rel_admitted(rel)):
            continue
        if not head.lstrip("-").isdigit():
            continue

        position, head = int(position), int(head)

        if not word_admitted(word):
            excluded.add(position)

        children[head].append(position)
        tokens[position] = word
        postags[position] = "_" + pos
        rels[position] = "@" + rel

    return children, tokens, postags, rels, excluded


def catenae_variants_for_sentence(lines: Sequence[str], min_len: int = 1, max_len: int = 5) -> set:
    children, tokens, postags, rels, excluded = _parse_conllu_sentence(lines)

    if 0 not in children:
        return set()

    root = children[0][0]
    _, catenae = recursive_catenae_extraction(root, children, min_len, max_len)

    variants = set()
    for catena in catenae:
        if any(pos in excluded for pos in catena):
            continue

        layers = [(tokens[p], postags[p], rels[p]) for p in catena]

        for combo in itertools.product((0, 1, 2), repeat=len(catena)):
            rendered = tuple(layers[i][c] for i, c in enumerate(combo))
            lex_count = sum(1 for c in combo if c == 0)
            variants.add((rendered, lex_count))

    return variants


def read_grouped_sentences(filepath: str) -> Dict[str, List[List[str]]]:
    """Read a CoNLL-U file of the examples.conllu shape and group sentences by
    construction id (the "cxn_N" prefix of "# sent_id = cxn_N_example_i_j").

    Sentences whose "# tags = ..." line contains any of DROPPED_TAGS
    (comma-separated, case-insensitive) are excluded from their group.
    """
    groups: Dict[str, List[List[str]]] = collections.defaultdict(list)

    group_key = None
    tags: set = set()
    token_lines: List[str] = []

    def flush():
        if group_key is not None and token_lines and not (tags & DROPPED_TAGS):
            groups[group_key].append(token_lines[:])

    with open(filepath) as fin:
        for raw_line in fin:
            line = raw_line.strip()

            if line.startswith("# sent_id"):
                flush()
                group_key = None
                tags = set()
                token_lines = []

                sent_id = line.split("=", 1)[1].strip()
                match = SENT_ID_RE.match(sent_id)
                if match:
                    group_key = match.group(1)

            elif line.startswith("# tags"):
                tag_str = line.split("=", 1)[1].strip()
                tags = {t.strip().upper() for t in tag_str.split(",")}

            elif line.startswith("#") or not line:
                continue

            else:
                token_lines.append(line)

        flush()

    return dict(groups)


def common_catenae(sentences: Iterable[Sequence[str]], min_len: int = 1, max_len: int = 5,
                    length_weight: float = 1.0, specificity_weight: float = 1.0,
                    max_sentence_len: int = 150) -> List[Tuple[str, float]]:
    """Find catenae shared across all given sentences, ranked by length + lexical specificity.

    Returns:
        List of (catena_string, score) sorted by descending score.
    """
    sentences = list(sentences)
    too_long = [s for s in sentences if len(s) > max_sentence_len]
    if too_long:
        print(f"skipping group: {len(too_long)} sentence(s) exceed "
              f"max_sentence_len={max_sentence_len} (longest has {max(len(s) for s in too_long)} tokens)")
        return []

    sentence_sets = [catenae_variants_for_sentence(s, min_len, max_len) for s in sentences]
    if not sentence_sets:
        return []

    common = set.intersection(*sentence_sets)

    scored = []
    for rendered, lex_count in common:
        length = len(rendered)
        score = length_weight * length + specificity_weight * lex_count
        scored.append(("|".join(rendered), score))

    scored.sort(key=lambda x: -x[1])
    return scored
