#!/usr/bin/env bash
# Creates one GitHub Issue per bug report in docs/bug-reports/, creates a Project board,
# links it to the repo and adds every issue to it.
#
# Prereqs: GitHub CLI (https://cli.github.com), `gh auth login`, and the project scope:
#   gh auth refresh -s project
# Run AFTER pushing docs/screenshots/BUG-00X.png to the main branch, so inline images resolve.
#
# Usage: scripts/create_issues.sh <owner>/<repo>
set -euo pipefail

REPO="${1:?usage: $0 <owner>/<repo>}"
OWNER="${REPO%%/*}"
NAME="${REPO##*/}"

gh label create bug --repo "$REPO" --color d73a4a --force >/dev/null
for s in critical major minor; do
  gh label create "severity: $s" --repo "$REPO" --force >/dev/null
done

PROJECT_NUM=$(gh project create --owner "$OWNER" --title "SauceDemo QA Board" --format json --jq '.number')
gh project link "$PROJECT_NUM" --owner "$OWNER" --repo "$REPO"
echo "Created project #$PROJECT_NUM"

for f in docs/bug-reports/BUG-*.md; do
  id=$(basename "$f" .md)
  title="$id: $(head -1 "$f" | sed -E 's/^# BUG-[0-9]+: //')"
  sev=$(grep -m1 '^| Severity' "$f" | awk -F'|' '{gsub(/ /,"",$3); print tolower($3)}')
  body=$(mktemp)
  tail -n +2 "$f" | sed "s#__OWNER__#$OWNER#g; s#__REPO__#$NAME#g" > "$body"
  url=$(gh issue create --repo "$REPO" --title "$title" --body-file "$body" \
        --label bug --label "severity: $sev")
  gh project item-add "$PROJECT_NUM" --owner "$OWNER" --url "$url" >/dev/null
  echo "Created $url"
done

echo "Open the board and check the Status columns (Todo / In Progress / Done)."
echo "Move at least one card to 'In Progress' or 'Done' if you want the board to look worked."
