"""Build the static site and capture metadata for the checked-out source."""

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "dist"


def git(*args):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True
    ).strip()


def main():
    state = {
        "mode": "deployment",
        "branch": os.environ.get("BUILD_BRANCH")
        or git("branch", "--show-current")
        or "detached HEAD",
        "head": git("rev-parse", "HEAD"),
        "subject": git("log", "-1", "--format=%s"),
        "dirty": bool(git("status", "--porcelain")),
    }
    if os.environ.get("GITHUB_ACTIONS") == "true" and state["dirty"]:
        raise SystemExit("CI build must use a clean checkout")

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    marker = '<meta name="git-state-url" content="/api/git" />'
    if html.count(marker) != 1:
        raise SystemExit("Expected one git-state-url meta tag in index.html")
    html = html.replace(
        marker, '<meta name="git-state-url" content="./git-state.json" />'
    )

    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "index.html").write_text(html, encoding="utf-8")
    shutil.copyfile(ROOT / "app.js", OUTPUT / "app.js")
    (OUTPUT / "git-state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Built dist/ from {state['branch']} at {state['head']}")
    if state["dirty"]:
        print("Local preview includes uncommitted changes.")


if __name__ == "__main__":
    main()
