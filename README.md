# Oda-Music — Updated (2025-09-29)

Template bot musik Telegram (voice chat) yang telah dimigrasikan ke **Pyrogram v2**, **PyTgCalls v3**, dan **yt-dlp**. Repo ini dilengkapi tooling modern (ruff, black, pre-commit), CI GitHub Actions, serta opsi deploy (Termux/Local, Docker, Heroku, Railway).

## ✨ Fitur Utama
- Kompatibel **Pyrogram v2** & **PyTgCalls v3**
- Menggunakan **yt-dlp** (pengganti youtube_dl)
- Tooling dev: **ruff**, **black**, **pre-commit**, **.editorconfig**
- CI: **GitHub Actions** (lint & format check)
- Deploy siap pakai: **Termux/Local**, **Docker Compose**, **Heroku**, **Railway**
- Skrip utilitas: `update.sh` (auto pull → lint/format → commit → push), `set_git.sh`

## 🧰 Prasyarat
- Python 3.11+
- FFmpeg
- Telegram API_ID / API_HASH, BOT_TOKEN
- (Opsional) STRING_SESSION untuk fitur tertentu

## ⚙️ Konfigurasi
1. Salin konfigurasi contoh:
   ```bash
   cp .env.example .env
   ```
2. Isi nilai pada `.env`:
   ```dotenv
   API_ID=123456
   API_HASH=abcdef123456
   BOT_TOKEN=123456:abcdef-ghijk
   OWNER_ID=987654321
   STRING_SESSION=
   DATABASE_URL=sqlite:///data/database.sqlite3
   LOG_LEVEL=INFO
   ```

## 🏃 Menjalankan Secara Lokal / Termux
```bash
# (opsional) venv
python -m venv venv && source venv/bin/activate

# install requirements
pip install -r requirements.new.txt  # atau gabungkan ke requirements.txt

# jalankan bot
python -m oda
```

### Termux quick push (branch default: `san`)
```bash
chmod +x set_git.sh update.sh
./set_git.sh "YourName" "email@example.com"
./update.sh           # auto pull --rebase → lint/format → commit → push ke 'san'
```

## 🐳 Docker
### Docker Compose
```bash
docker compose up -d
```
Pastikan environment (`API_ID`, `API_HASH`, `BOT_TOKEN`, dll) sudah tersedia di environment host atau file `.env`.

## ☁️ Heroku
Menggunakan container stack.
```bash
heroku stack:set container
git push heroku san:main
```
Buildpacks/FFmpeg sudah di-handle via `Dockerfile`/`heroku.yml`.

## 🚆 Railway
```bash
railway up
```
Konfigurasi berada di `railway.json` (Nixpacks: python311 + ffmpeg).

## 🛠 Tooling Dev
- **Ruff** (lint & import sort), **Black** (format)
- **Pre-commit**:
  ```bash
  pip install pre-commit ruff black
  pre-commit install
  pre-commit run --all-files
  ```

## 🔁 Skrip Otomatis
- `set_git.sh` — set `user.name`, `user.email`, dan credential helper (cache 2 jam)
- `update.sh` — auto pull → submodule sync → (ruff/black) → sync `requirements.new.txt` → pre-commit → commit → push  
  Argumen opsional:
  ```bash
  ./update.sh <branch> "<commit message>"
  # contoh:
  ./update.sh master "chore: migrate modules & bump deps"
  ```

## 📄 Changelog
Lihat `CHANGELOG.md` untuk daftar perubahan.

## ⚠️ Catatan
- Termux bukan VPS: proses berhenti jika app mati/dibunuh. Untuk 24/7 gunakan Heroku/Railway/VPS/Docker pada server.
- Jika terjadi error/traceback setelah update, buat issue/PR beserta log-nya.

---

Made with ❤️ to keep your Telegram music bot up-to-date.
