#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BRANCH="${1:-san}"
MSG="${2:-chore: update Oda-Music repo auto-push}"

if ! git config --get user.name >/dev/null 2>&1; then
  if [[ -n "${GIT_USER_NAME:-}" ]]; then git config user.name  "$GIT_USER_NAME"; fi
fi
if ! git config --get user.email >/dev/null 2>&1; then
  if [[ -n "${GIT_USER_EMAIL:-}" ]]; then git config user.email "$GIT_USER_EMAIL"; fi
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "❌ Remote 'origin' belum diset. Pakai: git remote add origin <URL-REPO>"
  exit 1
fi

echo "ℹ️  Branch: $BRANCH"
git fetch origin "$BRANCH" || true

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
else
  if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    git checkout -b "$BRANCH" "origin/$BRANCH"
  else
    git checkout -b "$BRANCH"
  fi
fi

echo "⬇️  Pull (rebase) ..."
git pull --rebase origin "$BRANCH" || {
  echo "❌ Konflik rebase. Perbaiki lalu: git rebase --continue"
  exit 1
}

if [ -f .gitmodules ]; then
  git submodule sync --recursive
  git submodule update --init --recursive
fi

git add -A
if git diff --cached --quiet; then
  echo "✅ Tidak ada perubahan."
  exit 0
fi
git commit -m "$MSG"
git push origin "$BRANCH"
echo "✅ Push selesai."
