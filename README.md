# Focra 🎯

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> **AI-powered distraction coach untuk mahasiswa dan self-learner.**

Focra membantu kamu memahami pola distraksimu sendiri — bukan cuma timer biasa, tapi sistem yang aktif menganalisis perilaku belajarmu dan memberikan coaching personal berdasarkan data nyata.

---

## 📌 Preview
![Main Interface Placeholder](https://via.placeholder.com/800x450.png?text=Tambahkan+Screenshot+UI+Streamlit+Disini)
*Dashboard statistik dengan visualisasi Plotly dan analisis AI Coach.*

---

## 📖 Latar Belakang

Pasca-pandemi, produktivitas belajar mandiri menurun drastis karena distraksi digital. Berdasarkan **Microsoft Work Trend Index 2023**, sekitar 58% orang merasa fokusnya menurun, dan rata-rata hanya 3–4 jam produktif dari 8 jam kerja (RescueTime & Toggl, 2023–2025).

Kebanyakan aplikasi hanya menyediakan timer pasif. Focra mengambil pendekatan **Behavioral Distraction Intelligence** — sistem yang belajar dari pola gangguanmu untuk memberikan intervensi yang relevan secara personal menggunakan AI lokal.

---

## ✨ Fitur Utama

- **Live Countdown Timer** — Sisa waktu sesi tampil real-time menit & detik
- **Smart Alarm** — Notifikasi audio otomatis saat sesi berakhir
- **Active Distraction Logging** — Catat jenis gangguan beserta menit ke-berapa terjadi
- **Objective Focus Score** — Penilaian otomatis berbasis perilaku, bukan self-report
- **Pre-session Context** — Catat level energi dan lokasi belajar sebelum sesi dimulai
- **AI Coach (Local, via Ollama)** — Analisis pola distraksi dan rekomendasi strategi belajar yang spesifik, berjalan 100% offline
- **Visual Insight** — Grafik distribusi distraksi dan insight peak distraction minute

---

## 📉 Focus Score — Logika Penilaian

Sistem memberikan skor (0–10) secara objektif dengan rumus:

$$Score = (0.4 \times \text{Completion Rate}) + (0.6 \times \text{Distraction Factor})$$

| Faktor | Bobot | Penjelasan |
| :--- | :--- | :--- |
| **Completion Rate** | 40% | Rasio durasi aktual dibanding target awal |
| **Distraction Factor** | 60% | Jumlah distraksi per jam — semakin sedikit, skor semakin tinggi |

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
| :--- | :--- |
| Frontend | Streamlit |
| Database | SQLite (local) |
| AI Engine | Ollama (`llama3.1:8b`) — offline, gratis, tanpa API key |
| Visualisasi | Plotly |
| Environment | Python 3.9+ |

---

## 🚀 Quickstart

### 1. Install Ollama dan download model

Ollama diperlukan untuk menjalankan AI Coach secara lokal.

```bash
# Mac/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download di https://ollama.com/download
```

Setelah install, download model:

```bash
ollama pull llama3.1:8b
```

### 2. Persiapan environment

```bash
# Clone & masuk folder
git clone https://github.com/Raditxt/FOCRA.git
cd focra

# Buat & aktifkan virtual environment
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install library
pip install -r requirements.txt
```

### 3. Jalankan aplikasi

Pastikan Ollama sudah berjalan di background, lalu:

```bash
streamlit run main.py
```

Akses di browser: `http://localhost:8501`

> **Catatan:** Tidak perlu API key apapun. AI Coach berjalan sepenuhnya offline di mesin kamu.

---

## 📂 Struktur Proyek

```text
focra/
├── main.py                          # Entry point (onboarding, sesi, timer, alarm)
├── requirements.txt
├── app/
│   ├── pages/
│   │   └── dashboard.py             # Visualisasi data & AI Coach
│   └── components/
│       └── distraction_logger.py    # Form log distraksi + elapsed_minutes
├── core/
│   ├── session.py                   # CRUD SQLite, focus score, daily context
│   └── analyzer.py                  # Agregasi behavioral data untuk coaching
├── ai/
│   ├── prompts.py                   # System prompt & template coaching
│   └── coach.py                     # Ollama API wrapper
├── data/
│   └── focra.db                     # SQLite (auto-generated, tidak di-commit)
└── config/
    └── settings.py                  # Konfigurasi global (model, path DB)
```

---

## 🗄️ Database Schema

Focra menyimpan 4 tabel untuk behavioral analysis:

| Tabel | Fungsi |
| :--- | :--- |
| `users` | Identitas user (unique by name) |
| `sessions` | Data sesi belajar + focus score |
| `distractions` | Log distraksi + `elapsed_minutes` (menit ke-berapa terjadi) |
| `daily_context` | Kondisi sebelum sesi: energy level + lokasi belajar |

---

## 🗺️ Roadmap

- [x] Database SQLite dengan behavioral schema
- [x] Timer live countdown + alarm audio
- [x] Pencatatan distraksi dengan timestamp menit
- [x] Pre-session context (energy level + lokasi)
- [x] Focus score otomatis berbasis perilaku
- [x] Dashboard visualisasi Plotly
- [x] AI Coach lokal via Ollama (offline, gratis)
- [x] Prompt engineering coaching personal
- [ ] Deploy ke Streamlit Cloud
- [ ] Ekspor data sesi ke CSV
- [ ] Trend focus score mingguan
- [ ] Gamifikasi (streak & level fokus)

---

## 📄 Lisensi

Distribusi di bawah lisensi **MIT**. Lihat `LICENSE` untuk informasi lebih lanjut.

---

*Dibuat untuk membantu kamu belajar lebih dalam, bukan lebih lama.*