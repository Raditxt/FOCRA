# Focra 🎯

> AI-powered distraction coach untuk mahasiswa dan self-learner.

Focra membantu kamu memahami pola distraksimu sendiri — bukan cuma timer biasa, tapi sistem yang aktif menganalisis perilaku belajarmu dan memberikan coaching personal berdasarkan data nyata.

## Latar Belakang

Pasca-pandemi, produktivitas belajar mandiri menurun drastis karena distraksi digital yang makin parah. Data:

- **Microsoft Work Trend Index 2023** — 58% pekerja merasa fokus menurun
- **RescueTime & Toggl 2023–2025** — rata-rata hanya 3–4 jam produktif dari 8 jam kerja

Kebanyakan app hanya menyediakan timer. Focra mengambil pendekatan berbeda: **behavioral distraction intelligence** — sistem yang belajar dari pola distraksimu dan memberi intervensi yang relevan secara personal.

## Fitur

- **Timer sesi dengan hitung mundur live** — sisa waktu tampil real-time menit & detik
- **Alarm otomatis** — notifikasi audio saat sesi selesai
- **Pencatatan distraksi** — log jenis gangguan selama sesi berlangsung
- **Focus score otomatis** — sistem menilai kualitas fokusmu berdasarkan data perilaku, bukan self-report
- **Dashboard insight** — statistik sesi, distribusi distraksi, trend focus score
- **AI Coach (Gemini)** — analisis pola distraksi + rekomendasi spesifik, gratis

## Focus Score — Cara Sistem Menilai

Focus score (0–10) dihitung otomatis saat sesi selesai, berdasarkan dua faktor perilaku:

| Faktor | Bobot | Penjelasan |
|--------|-------|------------|
| Completion rate | 40% | Seberapa dekat durasi aktual dengan target |
| Distraction rate | 60% | Jumlah distraksi per jam — semakin sedikit, semakin tinggi |

Hasilnya lebih objektif dibanding rating manual karena berbasis perilaku nyata.

## Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Frontend | Streamlit |
| Database | SQLite |
| AI Engine | Google Gemini (`gemini-2.0-flash`) — free tier |
| Visualisasi | Plotly |
| Deployment | Streamlit Cloud |

## Quickstart

```bash
# Clone & masuk folder
git clone https://github.com/username/focra.git
cd focra

# Virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Setup API key
cp .env.example .env
# Edit .env → isi GEMINI_API_KEY

# Jalankan
streamlit run main.py
```

Buka `http://localhost:8501`.

## Cara Dapat API Key Gemini (Gratis)

1. Buka [Google AI Studio](https://aistudio.google.com/)
2. Login dengan akun Google
3. Klik **Get API key** → **Create API key**
4. Copy key yang dimulai `AIzaSy...`
5. Paste ke `.env` sebagai `GEMINI_API_KEY=...`

Free tier: 15 request per menit, 1.500 request per hari — cukup untuk penggunaan personal.

## Struktur Project