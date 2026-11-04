"""Unit tests for the reviewer's pure functions.

These run before the review step in CI, so a bug in line numbering or
rule resolution fails the build instead of posting wrong comments.
"""
import os
import sys

# review.py reads these at import time; give it dummy values for tests
os.environ.update(REPO="x", PR_NUMBER="1", HEAD_SHA="x", GITHUB_TOKEN="x")
sys.path.insert(0, ".github/scripts")
import review


def test_annotate_numbers_added_and_context_lines():
    patch = "@@ -10,3 +10,4 @@\n ctx\n-old\n+new1\n+new2\n ctx2"
    text, valid = review.annotate(patch)
    assert valid == {10, 11, 12, 13}     # removed line takes no number
    assert "L11   +new1" in text


def test_annotate_multiple_hunks_reset_counter():
    patch = "@@ -1,1 +1,1 @@\n+a\n@@ -50,1 +50,2 @@\n ctx\n+b"
    _, valid = review.annotate(patch)
    assert valid == {1, 50, 51}          # second hunk restarts at 50


def test_annotate_ignores_no_newline_marker():
    patch = "@@ -1,1 +1,1 @@\n+a\n\\ No newline at end of file"
    _, valid = review.annotate(patch)
    assert valid == {1}


def test_rules_inherit_from_root():
    # Relies on the real rule files in the repo (Step 3)
    assert review.rules_for("backend/retrieval/retriever.py") == (
        ".review-rules.md",
        "backend/retrieval/.review-rules.md",
    )


def test_rules_root_only_for_other_folders():
    assert review.rules_for("frontend/src/App.jsx") == (".review-rules.md",)

# --- Step 7: dedup ---------------------------------------------------------

def test_finding_key_ignores_line_number():
    # Same file + same rule on a shifted line is the same issue
    a = {"path": "a.py", "rule_id": "RET-1", "line": 14}
    b = {"path": "a.py", "rule_id": "RET-1", "line": 20}
    assert review.finding_key(a) == review.finding_key(b)


def test_existing_keys_only_counts_bot_comments(monkeypatch):
    fake_comments = [
        {"path": "a.py", "body": f"**[warning] RET-1**: hardcoded\n{review.MARKER}"},  # bot
        {"path": "a.py", "body": "**[warning] GEN-1**: a human typed this"},           # human
    ]
    monkeypatch.setattr(review, "gh_paginated", lambda url: fake_comments)
    assert review.existing_keys() == {("a.py", "RET-1")}