"""One-shot: captures screenshots (if missing), creates a PUBLIC GitHub repo, pushes everything,
sets the REQRES_API_KEY secret, creates the Issues and the Project board.

Prereqs (one time): Git, GitHub CLI (https://cli.github.com) and `gh auth login`.
Usage: python scripts/publish.py [repo-name]        (default repo name: saucedemo-qa-assignment)
"""
import getpass
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def run(*cmd, check=True, capture=False):
    r = subprocess.run(cmd, check=check, text=True, capture_output=capture)
    return r.stdout.strip() if capture else None


def need(tool, hint):
    if not shutil.which(tool):
        sys.exit(f"'{tool}' not found. {hint}")


need("git", "Install Git from https://git-scm.com")
need("gh", "Install GitHub CLI from https://cli.github.com, then run: gh auth login")
if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
    sys.exit("Not logged in. Run: gh auth login")

repo_name = sys.argv[1] if len(sys.argv) > 1 else "saucedemo-qa-assignment"
owner = run("gh", "api", "user", "--jq", ".login", capture=True)
slug = f"{owner}/{repo_name}"
print(f"Publishing to https://github.com/{slug}")

# 1. screenshots
if len(list((ROOT / "docs" / "screenshots").glob("BUG-*.png"))) < 6:
    print("\n[1/6] Capturing screenshots from saucedemo.com ...")
    run(sys.executable, "scripts/capture_screenshots.py")
else:
    print("\n[1/6] Screenshots already present, skipping.")

# 2. fill placeholders
print("[2/6] Filling in your GitHub username and repo name ...")
for p in [ROOT / "README.md"]:
    p.write_text(p.read_text(encoding="utf-8").replace("__OWNER__", owner).replace("__REPO__", repo_name),
                 encoding="utf-8")

# 3. git + repo
print("[3/6] Creating the repo and pushing ...")
if not (ROOT / ".git").exists():
    run("git", "init", "-q")
run("git", "add", "-A")
run("git", "commit", "-q", "-m", "QA assignment: test plan, bugs, Selenium + API automation, CI", check=False)
run("git", "branch", "-M", "main")
run("gh", "repo", "create", slug, "--public", "--source", ".", "--remote", "origin", "--push")

# 4. secret
print("[4/6] ReqRes API key secret ...")
key = os.getenv("REQRES_API_KEY") or getpass.getpass("Paste your ReqRes API key (Enter to skip): ").strip()
if key:
    run("gh", "secret", "set", "REQRES_API_KEY", "--repo", slug, "--body", key)
    print("  secret set.")
else:
    print("  skipped - API tests will be skipped in CI until you add REQRES_API_KEY.")

# 5. project scope + labels
print("[5/6] Creating labels and Project board ...")
run("gh", "auth", "refresh", "-s", "project")  # may open a browser once
run("gh", "label", "create", "bug", "--repo", slug, "--color", "d73a4a", "--force", capture=True)
for s in ("critical", "major", "minor"):
    run("gh", "label", "create", f"severity: {s}", "--repo", slug, "--force", capture=True)
num = run("gh", "project", "create", "--owner", owner, "--title", "SauceDemo QA Board",
          "--format", "json", "--jq", ".number", capture=True)
run("gh", "project", "link", num, "--owner", owner, "--repo", slug)

# 6. issues
print("[6/6] Creating issues ...")
for f in sorted((ROOT / "docs" / "bug-reports").glob("BUG-*.md")):
    text = f.read_text(encoding="utf-8").replace("__OWNER__", owner).replace("__REPO__", repo_name)
    lines = text.splitlines()
    title = f"{f.stem}: " + re.sub(r"^# BUG-\d+: ", "", lines[0])
    sev = re.search(r"\| Severity \| (\w+)", text).group(1).lower()
    body = ROOT / "artifacts" / f"{f.stem}.body.md"
    body.parent.mkdir(exist_ok=True)
    body.write_text("\n".join(lines[1:]), encoding="utf-8")
    url = run("gh", "issue", "create", "--repo", slug, "--title", title, "--body-file", str(body),
              "--label", "bug", "--label", f"severity: {sev}", capture=True)
    run("gh", "project", "item-add", num, "--owner", owner, "--url", url, capture=True)
    print("  ", url)

print(f"\nDone.\n  Repo:    https://github.com/{slug}\n  Actions: https://github.com/{slug}/actions"
      f"\n  Project: https://github.com/users/{owner}/projects/{num}")
