# Ngebait eFootball — Blogger + GitHub Auto-Sync

## Apa ini?
Versi ini sengaja dibuat tanpa Node.js/SQLite/server berbayar.
- GitHub menyimpan JSON data.
- GitHub Actions menjalankan sinkronisasi otomatis.
- GitHub Pages menyajikan file JSON.
- Blogger menampilkan data memakai widget HTML/JavaScript.

## 1. Buat repository
Buat repository GitHub baru, misalnya `ngebait-efootball`.
Upload semua folder/file ZIP ini ke branch default (biasanya `main`).

## 2. Aktifkan GitHub Pages
Repository > Settings > Pages.
Pada "Build and deployment", pilih:
- Source: Deploy from a branch
- Branch: `main`
- Folder: `/ (root)`
Save.

Setelah aktif, URL data akan berbentuk:
https://USERNAME.github.io/ngebait-efootball/data/players.json

## 3. Aktifkan Actions
Masuk tab Actions dan jalankan workflow `Ngebait Auto Sync` secara manual sekali:
Actions > Ngebait Auto Sync > Run workflow.

Setelah itu workflow terjadwal akan mencoba berjalan setiap 2 jam.
GitHub menjalankan scheduled workflows memakai cron; jadwal default UTC. Menit 17 dipilih agar tidak tepat di pergantian jam.

## 4. Pasang di Blogger
Buka Blogger:
Tata Letak > Tambahkan Gadget > HTML/JavaScript.
Buka `blogger/ngebait-widget.html`, salin seluruh isinya.

Cari:
https://GITHUB_USERNAME.github.io/GITHUB_REPO/data/

Ganti menjadi URL GitHub Pages milikmu, misalnya:
https://namakamu.github.io/ngebait-efootball/data/

Simpan gadget.

Google juga menyediakan jalur Tema > Edit HTML jika ingin menanamkannya ke template.

## 5. Jika ingin menjadikan Ngebait satu halaman penuh
Kamu dapat memasukkan widget ke halaman Blogger atau template. Untuk tampilan penuh, lebih baik gunakan widget HTML/JavaScript di area utama template atau buat halaman statis khusus.

## Tentang auto-sync
Tanpa URL export PlayersDB, repo dimulai dengan snapshot kecil agar langsung tampil. Untuk database besar, isi secret/environment `PLAYERSDB_EXPORT_URL` dengan URL dataset JSON/JSONL/CSV yang memang kamu berhak akses.

Workflow juga mencoba membaca halaman berita resmi eFootball/KONAMI. Event yang terdeteksi dari halaman berita disimpan ke `events.json`. Ini bukan API resmi event terstruktur; tanggal mulai/selesai tidak ditebak.

## Penting
Jangan menaruh token/API key rahasia di Blogger. Jika nanti sumber data memerlukan token, simpan di GitHub Actions Secrets dan gunakan hanya di workflow.
