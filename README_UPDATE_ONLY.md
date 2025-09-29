# Update-Only Toolkit (Termux/Git) — Fresh Build
Toolkit ringan untuk **update repo ke GitHub** tanpa jalanin bot.

## File
- `set_git.sh` — set `user.name` & `user.email` (sekali saja)
- `update.sh` — pull --rebase -> add -> commit -> push (default branch `san`)
- `termux-update.sh` — shortcut: unzip patch -> panggil `update.sh`

## Cara Pakai (Termux)
1) Masuk ke repo:
   cd Oda-Music
2) Ekstrak toolkit:
   unzip /sdcard/Download/Oda-Music-update-only-tools-FRESH.zip -d .
   chmod +x set_git.sh update.sh termux-update.sh
3) Setup identitas (sekali):
   ./set_git.sh "UserLazy" "email@example.com"
4) Update cepat dari zip patch:
   ./termux-update.sh /sdcard/Download/Oda-Music-san-FINAL-with-README.zip
