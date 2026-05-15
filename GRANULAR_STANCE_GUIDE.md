# Granular Stance Analysis dengan Google Gemini API

Panduan lengkap untuk mengimplementasikan ekstraksi stance granular dan dashboard interaktif.

## 📋 Daftar Isi

1. [Overview](#overview)
2. [Instalasi & Setup](#instalasi--setup)
3. [Penggunaan](#penggunaan)
4. [Struktur Output](#struktur-output)
5. [Desain Dashboard](#desain-dashboard)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Sistem ini memungkinkan Anda untuk melakukan **analisis sikap (stance analysis) granular** pada data media sosial dengan struktur hierarki:

```
Unggahan Utama (Post)
├── Komentar 1 → Sikap: Mendukung | Bobot: 0.95
├── Komentar 2 → Sikap: Menolak | Bobot: 0.88
└── Komentar 3 → Sikap: Netral | Bobot: 0.70
```

### Fitur Utama

✅ **Analisis Granular Per Komentar**
- Bukan hanya agregasi angka, tetapi penjabaran detail per baris
- Setiap komentar dianalisis terhadap konteks unggahan utama

✅ **Google Gemini API Integration**
- Model LLM yang powerful untuk pemahaman nuansa bahasa Indonesia
- Confidence scoring untuk setiap klasifikasi

✅ **Dashboard Interaktif Streamlit**
- Accordion/Expander untuk navigasi hierarki
- Color-coding untuk visualisasi sikap
- Filter panel untuk eksplorasi data
- Mini-summary statistics per unggahan

---

## Instalasi & Setup

### 1. Install Dependencies

```bash
# Upgrade pip terlebih dahulu
pip install --upgrade pip

# Install dari requirements.txt
pip install -r requirements.txt
```

Jika terjadi error dengan package tertentu, install secara manual:

```bash
# Google Generative AI
pip install google-generativeai>=0.3.0

# Streamlit (jika belum ada)
pip install streamlit>=1.28.0

# Data processing
pip install pandas numpy

# Visualization
pip install plotly
```

### 2. Setup Google Gemini API

#### Langkah A: Dapatkan API Key

1. Kunjungi [Google AI Studio](https://aistudio.google.com)
2. Klik **"Get API Key"** di bagian kiri
3. Pilih **"Create API Key in new project"**
4. Copy API key yang dihasilkan

#### Langkah B: Set Environment Variable

**Di Linux/Mac:**
```bash
export GOOGLE_API_KEY="paste-your-api-key-here"
```

**Di Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=paste-your-api-key-here
```

**Di Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "paste-your-api-key-here"
```

#### Langkah C: Verifikasi Setup

```bash
python -c "import os; print('API Key:', os.getenv('GOOGLE_API_KEY')[:10] + '...' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
```

---

## Penggunaan

### Option 1: Demo Script (Rekomendasi untuk Testing)

Jalankan demo untuk melihat hasil dengan 5 unggahan pertama:

```bash
python demo_granular_stance.py
```

**Output yang diharapkan:**
- ✅ Dataset dimuat
- ✅ Analisis dijalankan
- ✅ Hasil ditampilkan di terminal
- ✅ File CSV disimpan ke folder `results/`

### Option 2: Dashboard Streamlit (Rekomendasi untuk Eksplorasi)

Jalankan dashboard interaktif:

```bash
streamlit run streamlit_granular_stance.py
```

Akses di browser: `http://localhost:8501`

**Navigasi Dashboard:**
1. **Sidebar Kiri:**
   - Pilih sumber data (Upload atau Sample)
   - Jalankan analisis stance
   - Filter hasil berdasarkan stance, bobot, topik

2. **Area Utama:**
   - Statistik keseluruhan dengan visualisasi
   - Accordion per unggahan (expandable)
   - Mini-summary distribusi sikap
   - Tabel komentar dengan color-coding
   - Detail lengkap per komentar

### Option 3: Manual Python Script

Buat script custom untuk analisis khusus:

```python
from load_data import load_dataset, prepare_post_comment_data
from stance_analysis_granular import run_granular_stance_analysis
import os

# Setup
api_key = os.getenv("GOOGLE_API_KEY")
df = load_dataset("your_dataset.csv")
posts_df, comments_df = prepare_post_comment_data(df)

# Run analysis
comments_with_stance = run_granular_stance_analysis(
    posts_df=posts_df,
    comments_df=comments_df,
    api_key=api_key,
    sample_size=10  # Analyze first 10 posts
)

# Save results
comments_with_stance.to_csv("results/stance_results.csv", index=False)
print("✅ Analisis selesai!")
```

---

## Struktur Output

### Kolom Output DataFrame

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `post_id` | str | ID unik unggahan |
| `comment_id` | str | ID unik komentar |
| `full_text` | str | Teks lengkap unggahan |
| `full_text_comments` | str | Teks lengkap komentar |
| `stance_label` | str | Klasifikasi: "Mendukung", "Menolak", "Netral" |
| `stance_weight` | float | Bobot keyakinan (0.0 - 1.0) |
| `stance_reasoning` | str | Penjelasan singkat alasan klasifikasi |

### Contoh Output CSV

```csv
post_id,comment_id,full_text,full_text_comments,stance_label,stance_weight,stance_reasoning
1,101,"Kebijakan luar negeri harus lebih terbuka","Setuju, ini langkah yang tepat",Mendukung,0.95,"Komentar mengekspresikan persetujuan eksplisit terhadap kebijakan."
1,102,"Kebijakan luar negeri harus lebih terbuka","Justru merugikan posisi diplomasi kita",Menolak,0.88,"Komentar mengkritik dampak negatif kebijakan terhadap diplomasi."
1,103,"Kebijakan luar negeri harus lebih terbuka","Kita lihat saja perkembangannya",Netral,0.70,"Komentar bersifat informatif dan terbuka, tidak jelas mendukung atau menolak."
```

---

## Desain Dashboard

### Layout Utama

```
┌─────────────────────────────────────────┐
│  📊 Analisis Sikap Granular - Dashboard │
├─────────────────────────────────────────┤
│ SIDEBAR (Kiri)      │ MAIN AREA (Kanan) │
│ • Upload/Sample     │ • Statistik Keseluruhan
│ • Jalankan Analisis │ • Chart Distribusi
│ • Filter:           │ • Per-Post Accordion
│   - Stance          │   - Mini Summary
│   - Confidence      │   - Distribusi Pie Chart
│   - Topic           │   - Comments Table
│                     │   - Detail Expandable
└─────────────────────────────────────────┘
```

### Color-Coding

| Status | Warna | Kode Hex |
|--------|-------|----------|
| 🟩 Mendukung | Hijau Muda | #90EE90 |
| 🟥 Menolak | Merah Muda | #FFB6C1 |
| ⬜ Netral | Abu-abu Terang | #D3D3D3 |

### Filter Panel

**1. Filter Stance:**
- Checkbox untuk "Mendukung", "Menolak", "Netral"
- Default: Semua dipilih

**2. Slider Confidence Score:**
- Range: 0.0 - 1.0
- Increment: 0.1
- Gunakan untuk menyaring hanya prediksi yang sangat confident

**3. Filter Topik:**
- Dropdown untuk topik (dari Topic Modeling)
- Memerlukan kolom `topic_id` di dataset

---

## Troubleshooting

### Error: "Google API Key tidak ditemukan"

**Solusi:**
```bash
# Verifikasi API key sudah di-set
echo $GOOGLE_API_KEY

# Jika kosong, set ulang
export GOOGLE_API_KEY="your-actual-api-key"
```

### Error: "google-generativeai package not installed"

**Solusi:**
```bash
pip install --upgrade google-generativeai
```

### Error: "ModuleNotFoundError: No module named 'load_data'"

**Solusi:**
```bash
# Pastikan Anda berada di direktori workspace
cd /workspaces/pemodelan7

# Jalankan script dari sana
python demo_granular_stance.py
```

### API Rate Limiting / Timeout

**Solusi:**
- Kurangi `sample_size` (analisis lebih sedikit posts)
- Tingkatkan `batch_delay` (delay lebih lama antar API calls)
- Gunakan model yang lebih cepat: `gemini-1.5-flash` (sudah default)

### Output hanya berisi "Netral" atau angka

**Solusi:**
- Model mungkin memiliki timeout atau error parsing
- Cek logs dengan level DEBUG:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
- Verifikasi format prompt di `create_stance_prompt()`
- Pastikan API key valid dan account memiliki quota

---

## Advanced Usage

### Custom Prompt Engineering

Edit `create_stance_prompt()` di `stance_analysis_granular.py` untuk:
- Menambah konteks domain (e.g., kebijakan spesifik)
- Mengubah definisi "Mendukung/Menolak"
- Menambah categories (e.g., "Sangat Mendukung", "Sedikit Menolak")

### Menggunakan Model Berbeda

```python
# Di demo atau script, ganti model_name:
comments_with_stance = run_granular_stance_analysis(
    posts_df=posts_df,
    comments_df=comments_df,
    api_key=api_key,
    model_name="gemini-2.0-flash"  # atau model lain
)
```

### Analisis Batch Besar

Untuk dataset besar, gunakan `chunking`:

```python
# Analisis per batch
batch_size = 50
total_posts = len(posts_df)

results = []
for i in range(0, total_posts, batch_size):
    batch_posts = posts_df.iloc[i:i+batch_size]
    batch_comments = comments_df[comments_df["post_id"].isin(batch_posts["post_id"])]
    
    batch_result = run_granular_stance_analysis(
        posts_df=batch_posts,
        comments_df=batch_comments,
        api_key=api_key,
        sample_size=None  # Analisis semua dalam batch
    )
    results.append(batch_result)

final_result = pd.concat(results, ignore_index=True)
```

---

## Performance Tips

1. **Gunakan `sample_size`** saat testing (jangan analisis seluruh dataset)
2. **Tingkatkan `batch_delay`** jika sering kena rate limit
3. **Gunakan `gemini-1.5-flash`** untuk kecepatan (bukan `-pro`)
4. **Cache hasil** di file CSV agar tidak perlu re-analyze

---

## File Reference

| File | Deskripsi |
|------|-----------|
| `stance_analysis_granular.py` | Module utama untuk analisis stance granular |
| `streamlit_granular_stance.py` | Dashboard Streamlit interaktif |
| `demo_granular_stance.py` | Script demo untuk testing |
| `load_data.py` | Utilitas untuk load dan prepare data |
| `requirements.txt` | Python dependencies (updated) |

---

## Kontak & Support

Jika mengalami masalah:
1. Cek error message dan traceback
2. Lihat section [Troubleshooting](#troubleshooting)
3. Verifikasi API key dan connectivity
4. Cek logs dengan `logging` module

---

**Last Updated:** May 15, 2026  
**Version:** 1.0 - Initial Release  
**Status:** Production Ready ✅
