"""
PR Rules Reviewer, Step 2: fetch the files changed in a pull request.

Later steps will match these files to folder rules and send their diffs
to Claude. For now we only list them, to prove the GitHub API call works.
"""
import os, re, sys
import requests
from pathlib import Path
from collections import defaultdict

# Name of the rules file the bot looks for in each folder.
RULE_FILE = ".review-rules.md"

# --- Inputs ---------------------------------------------------------------
# The GitHub Actions workflow passes these in as environment variables.
REPO = os.environ["REPO"]            # "owner/repo", e.g. shdh23/onboarding_buddy_RAG
PR = os.environ["PR_NUMBER"]         # pull request number, e.g. "1"
HEAD_SHA = os.environ["HEAD_SHA"]    # latest commit on the PR; used in Step 6 to attach comments

# Base URL for all GitHub REST API calls on this repo.
API = f"https://api.github.com/repos/{REPO}"

# Headers sent with every request:
# - Authorization: GITHUB_TOKEN is created automatically for each workflow run.
#   Its permissions come from the workflow's `permissions:` block.
# - Accept: tells GitHub we want the standard JSON API format.
GH = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
      "Accept": "application/vnd.github+json"}

# Files we never review: lockfiles, minified bundles, images, PDFs.
# They are generated or binary, so reviewing them wastes tokens and finds nothing useful.
SKIP = re.compile(r"(package-lock\.json|\.lock$|\.min\.js$|\.(png|jpg|svg|ico|pdf)$)")


def gh_paginated(url):
    """GET a GitHub list endpoint and return every item across all pages.

    GitHub returns at most 100 items per page. A large PR can change more
    than 100 files, so we keep requesting pages until one comes back empty.
    """
    items, page = [], 1
    while True:
        r = requests.get(url, headers=GH,
                         params={"per_page": 100, "page": page},
                         timeout=30)          # don't hang forever if GitHub is slow
        r.raise_for_status()                  # fail loudly on 401/403/404 instead of silently continuing
        batch = r.json()
        if not batch:                         # an empty page means we've seen everything
            return items
        items += batch
        page += 1


def changed_files():
    """Return the PR's changed files that are worth reviewing.

    Each item from GitHub is a dict with keys like:
      filename  -> "backend/retrieval/reranker.py"
      status    -> "added" | "modified" | "removed" | "renamed"
      patch     -> the unified diff for this file (missing for binary or huge files)
    """
    files = gh_paginated(f"{API}/pulls/{PR}/files")
    return [f for f in files
            if f.get("patch")                     # no patch means binary or too large; nothing to review
            and f["status"] != "removed"          # deleted files can't violate rules
            and not SKIP.search(f["filename"])]   # drop generated and binary files

def rules_for(path):
    """Return every rule file that applies to `path`, ordered root first.

    Walks from the file's folder up to the repo root, collecting any
    .review-rules.md found along the way. Example for
    "backend/retrieval/reranker.py":
        checks backend/retrieval/.review-rules.md  -> found
        checks backend/.review-rules.md            -> not found (yet)
        checks ./.review-rules.md                  -> found
    returns (".review-rules.md", "backend/retrieval/.review-rules.md")

    Root comes first and the most specific rules come last, so the model
    reads general rules before folder-specific ones.
    The result is a tuple, not a list, so it can be used as a dict key
    when grouping files.
    """
    found, d = [], Path(path).parent
    while True:
        rf = d / RULE_FILE
        if rf.is_file():          # the file exists on disk (the checkout step put the repo here)
            found.append(str(rf))
        if d == Path("."):        # reached the repo root; stop climbing
            break
        d = d.parent              # move up one folder
    return tuple(reversed(found))

def main():
    # Map each unique rule set to the files it covers, e.g.
    # (".review-rules.md", "backend/retrieval/.review-rules.md") -> [retriever.py, reranker.py]
    # Files that share a rule set will be reviewed together in one Claude call (Step 5).
    groups = defaultdict(list)

    for f in changed_files():
        rp = rules_for(f["filename"])
        if not rp:
            # No rule file anywhere above this file, so there is nothing to enforce.
            # (Won't happen once the root file exists, but keeps the bot safe without one.)
            continue
        groups[rp].append(f)

    # Step 3 only prints the mapping so we can verify it.
    for rp, files in groups.items():
        print("RULES:", list(rp))
        for f in files:
            print("   ", f["filename"])


if __name__ == "__main__":
    main()