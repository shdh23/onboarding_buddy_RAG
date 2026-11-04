"""
PR Rules Reviewer, Step 2: fetch the files changed in a pull request.

Later steps will match these files to folder rules and send their diffs
to Claude. For now we only list them, to prove the GitHub API call works.
"""
import os, re, sys
import requests

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


def main():
    # Step 2 only prints what we found, to verify the API call works.
    # Steps 3 onward replace this with rule matching and the Claude review.
    for f in changed_files():
        print(f["filename"], f["status"])


if __name__ == "__main__":
    main()