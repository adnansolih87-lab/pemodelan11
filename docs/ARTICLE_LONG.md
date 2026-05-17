Deteksi Stance pada Komentar Postingan: Pendekatan Leksikon + Sinyal — Versi Lengkap untuk Tesis
=====================================================================================

Ringkasan Eksekutif
-------------------
Masalah stance detection pada komentar media sosial menuntut pendekatan yang sensitif terhadap nuansa lokal bahasa, slang, dan sinyal paralinguistik (seperti huruf kapital berlebih dan tanda baca berulang). Untuk kebutuhan tesis, saya mengusulkan pipeline hybrid yang menggabungkan leksikon bahasa Indonesia, ekstraksi sinyal intensitas, heuristic deteksi sarkasme sederhana, dan penggunaan konteks post-level untuk mengurangi bias over-prediksi kelas "Netral". Dokumen ini menjelaskan latar, metodologi, hasil awal, keterbatasan, dan panduan reproducibility yang cukup untuk lampiran tesis.

Latar Belakang
---------------
Stance detection adalah tugas klasifikasi teks yang menentukan apakah teks mendukung, menentang, atau netral terhadap suatu target. Dalam komentar, target sering tidak disebutkan eksplisit; komentar bisa berupa potongan reaktif, ironi, atau retoris—kasus yang mudah memicu kesalahan pada model statistik murni atau model pra-latih yang tidak disesuaikan dengan ragam lokal bahasa.

Mengapa pendekatan leksikon + sinyal?
-------------------------------------
- Explainability: Leksikon memudahkan penelusuran alasan keputusan dan membolehkan peneliti memberi bukti pada penguji tesis.
- Robustness untuk data kecil: tanpa dataset besar untuk fine-tuning, heuristik terstruktur memberikan baseline yang dapat diandalkan.
- Kecepatan: analisis berbasis aturan dapat dijalankan cepat pada CPU tanpa GPU.

Kontribusi Teknis
------------------
1. `ImprovedStanceAnalyzer`: modul utama yang memadukan skor leksikon, fitur intensitas, pengaruh modifier, deteksi negasi, dan override konteks.
2. `enhanced_preprocessing`: mempertahankan sinyal penting (caps, elongation, repeated punctuation) yang biasanya dihilangkan oleh pembersihan tekstual.
3. Toolkit reproducible: skrip eksperimen, generator laporan, notebook analisis, dan kumpulan artefak untuk lampiran tesis.
4. Panduan pengumpulan ground-truth: prosedur practical untuk menghasilkan dataset label berkualitas tinggi (dokumentasi, template CSV, dan protokol adjudication).

Metode
------
1) Preprocessing berorientasi sinyal
   - Ekstrak jumlah huruf kapital berurutan, kasus elongation ("gakkk"), penghitungan berulang tanda seru/tanya, dan skor emoji sederhana.
   - Jangan hilangkan sinyal tersebut — jadikan fitur tambahan yang memodulasi skor leksikon.

2) Leksikon & scoring
   - Leksikon menyimpan token/phrase → skor stance (positif/negatif) dan bobot kepercayaan.
   - Token multi-kata (n-gram) dihitung sebelum token unigrams.

3) Booster/Reducer & Negation
   - Booster seperti "banget", "sekali" menaikkan magnitudo skor; reducer seperti "agak" menurunkannya.
   - Negasi membalik polaritas dalam window lokal.

4) Sarkasme & pertanyaan retoris
   - Pola regex menandai frasa seperti "maaf ya ... tapi" atau kombinasi kata pemanis + kontradiksi.
   - Jika terdeteksi, skor ditimbang ulang untuk preferensi interpretasi kritis (negative) kecuali ada sinyal jelas sebaliknya.

5) Context override
   - Jika post lebih condong positif sementara komentar berisi perturbasi kritis ("tapi"/"tetapi"/"sayangnya"), tambahkan bobot interpretif untuk konsistensi pragmatic.

Eksperimen & Hasil Awal
------------------------
Eksperimen awal pada subset ground-truth (n kecil, 20–30 contoh) menunjukkan perbaikan F1 untuk kelas non-neutral dibandingkan baseline transformer default dengan threshold confidence tinggi. Penyesuaian threshold ke 0.45 dan penggunaan fitur intensitas mengurangi false-negative pada kelas dukungan/penolakan.

Analisis Error
--------------
- Sarkasme kompleks yang memerlukan world-knowledge masih menjadi titik lemah.
- Komentar yang hanya berisi emojis atau tag (tanpa kata) kadang salah klasifikasi karena dependensi pada konten multimodal.
- Leksikon perlu pemeliharaan berkala untuk menangkap slang baru.

Reproducibility & Lampiran Tesis
--------------------------------
Untuk setiap eksperimen, repo menyimpan:
- CSV prediksi per-run (`results/.../stance_results_*.csv`)
- Laporan metrik dan confusion matrix (`REPORT.md`, `detailed_metrics.csv`)
- Contoh kesalahan (`error_examples.csv`) untuk inspeksi manual
- Notebook komprehensif: `notebooks/thesis_results_analysis.ipynb`

Praktik Pengumpulan Ground-Truth (ringkasan)
---------------------------------------------
- Gunakan template CSV berisi `post_id`, `post_text`, `comment_id`, `comment_text`, `label_expected`, `labeler_id`, `notes`.
- Label 2 annotator per item; adjudicate pada discord/Sheet jika disagreement.
- Lakukan pilot 50–100 item untuk kalibrasi annotator.

Rencana untuk Pengembangan Lanjutan
-----------------------------------
1. Kumpulkan 500–1000 contoh berlabel (stratified by topic) untuk fine-tuning IndoBERT/indobertweet.
2. Jalankan per-topik evaluation dan presentasikan metric per-class dengan CI.
3. Eksperimen ensemble: improved lexicon + fine-tuned + LLM untuk tie-break.

Instruksi Praktis untuk Penguji/Tesis
------------------------------------
- Jalankan `scripts/run_stance_experiment.py` untuk men-generate prediksi dan `scripts/generate_report.py` untuk metrik.
- Untuk mengukur kualitas annotator, gunakan `scripts/compute_inter_annotator_kappa.py` (disertakan) untuk menghitung Cohen's kappa pairwise dan Fleiss' kappa multi-annotator.

Kesimpulan
----------
Pendekatan yang diajukan memberikan baseline reproducible dan explainable yang cocok untuk thesis submission. Pipeline ini menyeimbangkan kebutuhan akurasi, transparansi, dan keterjangkauan sumber daya. Dengan dataset ground-truth yang lebih besar, pipeline ini siap untuk dikombinasikan dengan model terlatih untuk mencapai performa publikasi.

Referensi Lampiran
------------------
- Kode: repository `pemodelan11`
- Notebook: `notebooks/thesis_results_analysis.ipynb`
- Panduan labeling: `docs/GROUND_TRUTH_LABELING_GUIDE.md`

