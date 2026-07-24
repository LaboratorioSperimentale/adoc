"""Runs every (name.conllc, name.gq) fixture pair in test-cases/ through
conll2gq.convert_file() and asserts the output matches exactly."""
import os
import sys

import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(TESTS_DIR, "..", "src")
TEST_CASES_DIR = os.path.join(TESTS_DIR, "..", "test-cases")

sys.path.insert(0, SRC_DIR)
from conll2gq import convert_file  # noqa: E402


def _fixture_names():
    return sorted(
        fname[: -len(".conllc")]
        for fname in os.listdir(TEST_CASES_DIR)
        if fname.endswith(".conllc")
        and os.path.exists(os.path.join(TEST_CASES_DIR, fname[: -len(".conllc")] + ".gq"))
    )


@pytest.mark.parametrize("name", _fixture_names())
def test_conllc_to_grew(name):
    conllc_path = os.path.join(TEST_CASES_DIR, f"{name}.conllc")
    gq_path = os.path.join(TEST_CASES_DIR, f"{name}.gq")

    result = convert_file(open(conllc_path, encoding="utf-8").read())
    expected = open(gq_path, encoding="utf-8").read()

    got_lines = [l.strip() for l in result.split("\n") if l.strip()]
    exp_lines = [l.strip() for l in expected.split("\n") if l.strip()]

    assert got_lines == exp_lines
