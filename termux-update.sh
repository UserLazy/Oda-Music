#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ZIPFILE="${1:-}"
BRANCH="${2:-san}"
MSG="${3:-chore: update Oda-Music repo auto-push}"
if [ -z "$ZIPFILE" ]; then
  echo "❌ Pemakaian: ./termux-update.sh <path/zipfile> [branch] [commit msg]"
  exit 1
fi
if [ ! -d .git ]; then
  echo "❌ Jalankan di folder repo git."
  exit 1
fi
unzip -o "$ZIPFILE" -d .
chmod +x update.sh || true
./update.sh "$BRANCH" "$MSG"
