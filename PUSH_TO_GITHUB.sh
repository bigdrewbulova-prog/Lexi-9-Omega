#!/bin/bash
# Push this monorepo to github.com/Bigdrewbulova-prog/LEXI-9-OMEGA
set -euo pipefail

export PATH="/usr/local/bin:/usr/local/Cellar/gh/2.94.0/bin:$PATH"
REPO_NAME="${1:-LEXI-9-OMEGA}"
OWNER="Bigdrewbulova-prog"
VISIBILITY="${2:-private}"   # private | public

cd "$(dirname "$0")"

if ! gh auth status >/dev/null 2>&1; then
  echo "Not logged in. Starting GitHub login (browser)..."
  gh auth login -h github.com -p https -w
fi

LOGIN="$(gh api user --jq .login)"
echo "Authenticated as: $LOGIN"
if [[ "$LOGIN" != "$OWNER" ]]; then
  echo "WARNING: logged in as '$LOGIN', target owner is '$OWNER'."
  echo "Continue only if you intend to create the repo under $LOGIN or have access to $OWNER."
  read -r -p "Continue? [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] || exit 1
  OWNER="$LOGIN"
fi

if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  echo "Repo exists: https://github.com/$OWNER/$REPO_NAME"
else
  echo "Creating repo $OWNER/$REPO_NAME ($VISIBILITY)..."
  gh repo create "$OWNER/$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --description "LEXI-9-Omega stack: Drewskii.Engine, documentary, sims, hackathon"
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/$OWNER/$REPO_NAME.git"
else
  git remote add origin "https://github.com/$OWNER/$REPO_NAME.git"
fi

git push -u origin main
echo "Done: https://github.com/$OWNER/$REPO_NAME"
