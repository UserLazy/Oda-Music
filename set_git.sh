#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
NAME="${1:-UserLazy}"
EMAIL="${2:-you@example.com}"
git config --global user.name  "$NAME"
git config --global user.email "$EMAIL"
git config --global credential.helper "cache --timeout=7200"
echo "✅ Git global configured."
