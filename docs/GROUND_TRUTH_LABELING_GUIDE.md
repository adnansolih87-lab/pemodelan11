Panduan Singkat Pengumpulan Ground-Truth (Template untuk Tesis)
=============================================================

Tujuan
------
Menyediakan panduan singkat dan template untuk mengumpulkan ground-truth komentar berlabel (Positive/Negative/Neutral) yang bisa digunakan untuk fine-tuning dan validasi model stance.

Format File
-----------
Gunakan CSV dengan kolom:
- `post_id`: ID unik post
- `post_text`: teks post (opsional tapi sangat membantu)
- `comment_id`: ID unik komentar
- `comment_text`: teks komentar
- `label_expected`: salah satu `Positive`, `Negative`, `Neutral`
- `labeler_id`: ID pemberi label
- `notes`: alasan/komentar annotator (opsional)

3 Langkah Cepat
----------------
1) Siapkan template dan sampel
   - Salin `data/ground_truth_template.csv` sebagai starting point.
   - Ambil sampel stratified per-topik dan per-lengkap/pendek komentar. Target awal 500 contoh.

2) Proses labeling terkontrol
   - Gunakan Google Sheets / Airtable / Label Studio.
   - Setiap komentar dilabeli minimal 2 annotator independen.
   - Jika ada disagreement, adjudicator (labeler senior) memilih label akhir atau memfasilitasi diskusi.
   - Catat `labeler_id` dan `notes` untuk setiap entri.

3) Validasi kualitas
   - Hitung inter-annotator agreement (Cohen's kappa / Fleiss' kappa).
   - Jika kappa < 0.6, perbaiki pedoman labeling dan ulangi labeling pada batch sample.
   - Setelah adjudication, simpan `ground_truth_final.csv` berisi `comment_text`, `expected_label`, dan `post_text`.

Contoh Kasus Labeling
---------------------
- "Menteri paling gak becus." → `Negative` (kritik langsung; kata "gak becus" adalah indikasi negatif kuat).
- "Langkah ini keren banget, mantap!" → `Positive` (pujian eksplisit).
- "Presiden membuat keputusan ini setelah konsultasi menyeluruh." → `Neutral` (faktual, tidak ada dukungan/penolakan).
- "Maaf ya, tapi ini jelas tidak masuk akal" → `Negative` (frasa "maaf ya" + "tapi" = sarkasme/penguatan kritik).

Tips Praktis
------------
- Beri contoh banyak untuk annotator, termasuk kasus ambiguous dan bagaimana menanganinya.
- Gunakan small pilot (50–100 entri) untuk mengkalibrasi annotator.
- Simpan raw files dan versi akhir untuk reproducibility.

Output yang Diharapkan
---------------------
- `ground_truth_final.csv` — CSV final untuk fine-tuning dan evaluasi.
- Laporan kualitas labeling (kappa, jumlah disagreement, contoh adjudicated).

Jika ingin, saya bisa:
- Menyusun Google Sheets template (file CSV + link instruksi) untuk dishare ke annotator.
- Membuat script otomatis untuk menghitung Cohen's/Fleiss' kappa dari hasil labeling.
