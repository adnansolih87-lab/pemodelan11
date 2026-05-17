Deteksi Stance pada Komentar Postingan: Pendekatan Leksikon + Sinyal (Untuk Tesis)
=======================================================================

Abstrak
-------
Deteksi stance (pro/kontra/netral) pada komentar sosial media sangat penting untuk analisis opini publik dan riset sosial. Penelitian ini mengusulkan pipeline praktis untuk teks berbahasa Indonesia yang menggabungkan leksikon domain-spesifik, preservasi sinyal intensitas (mis. ALL CAPS, tanda seru berulang, repetisi), dan konteks post-level. Metode ini menunjukkan peningkatan F1 pada kelas non-neutral pada eksperimen awal, dibandingkan konfigurasi baseline yang memiliki bias ke kelas "Netral".

Pendahuluan
----------
Stance detection pada komentar berbeda dengan sentiment analysis umum karena fokusnya pada posisi (mendukung atau menentang topik tertentu) bukan sekadar emosi. Komentar di media sosial sering memuat slang, idiom, sarkasme, dan pertanyaan retoris yang menyulitkan model pra-latih bahasa umum. Di konteks bahasa Indonesia, gap ini semakin nyata: kata-kata seperti "goblog", "gak becus", atau frasa "bikin hati lega" membawa sinyal sentiment/stance kuat namun sering tidak dikenali oleh model yang dilatih pada korpus bahasa Inggris.

Kontribusi
----------
1. Mengembangkan `ImprovedStanceAnalyzer` yang menggabungkan: leksikon bahasa Indonesia (slang + idiom), preprocessing yang mempertahankan sinyal intensitas, deteksi sarkasme sederhana, dan penanganan negasi.
2. Menyediakan skrip reproduksi eksperimen dan notebook analisis untuk tesis sehingga hasil dapat diulang dan diverifikasi.
3. Menyajikan panduan praktis untuk membangun dataset ground-truth berkualitas (labeling protocol) untuk fine-tuning model.

Metodologi
----------
Arsitektur pipeline terbagi menjadi beberapa komponen:

- Preprocessing terawasi sinyal: ekstraksi ALL CAPS, penghitungan tanda seru/pertanyaan berganda, dan deteksi repetisi karakter (mis. "gakkk"). Sinyal ini tidak dihilangkan namun dipakai sebagai fitur penguat.
- Leksikon Bahasa Indonesia: kamus kata-kata negatif/positif berisi slang, idiom, dan frase komposit (mis. "gak punya otak", "keren banget"). Leksikon ini memberi skor dasar untuk setiap teks.
- Penguat intensitas dan penanganan negasi: booster ("banget", "sangat") meningkatkan skor; reducer ("agak", "mungkin") menguranginya; negasi ("tidak", "gak") mengubah polaritas lokal bila diperlukan.
- Deteksi pola sarkasme & pertanyaan retoris: regex terspesialisasi mendeteksi pola "maaf ya ... tapi" atau "gmana ... bs" yang mengindikasikan kritik terselubung.
- Context override: jika komentar menunjukkan kontradiksi terhadap posted content (mis. post positif—komentar berisi "tapi" + klaim negatif), sistem memberi bobot lebih pada interpretasi kritik.

Implementasi & Reproduksibilitas
--------------------------------
Semua kode dan skrip eksperimen tersedia di repo:
- `improved_stance_analyzer.py` — inti analyzer
- `indonesian_stance_lexicon.py` — leksikon dan pola
- `enhanced_preprocessing.py` — ekstraksi sinyal
- `scripts/run_stance_experiment.py` — menjalankan pipeline dan mengekspor hasil
- `notebooks/thesis_results_analysis.ipynb` — notebook analisis dan visualisasi

Untuk eksperimen cepat (offline), jalankan improved analyzer saja:

```bash
python3 scripts/run_stance_experiment.py --posts posts.csv --comments comments.csv --outdir results/final_experiment --skip_transformer
```

Evaluasi
--------
Pada subset ground-truth awal (n=23) pipeline improved memberikan metrik:
- Positive — Precision: 0.889, Recall: 1.000, F1: 0.941
- Negative — Precision: 1.000, Recall: 0.800, F1: 0.889
- Neutral  — Precision: 0.667, Recall: 0.800, F1: 0.727

Analisis kesalahan memperlihatkan dua pola utama: (1) komentar yang padat konteks atau terpotong (ellipsis) yang membuat deteksi kata kunci sulit, dan (2) ambiguitas sarkastik yang memerlukan pemahaman pragmatik lebih dalam. Artefak evaluasi (confusion matrix, contoh error) tersimpan di `results/gt_experiment/`.

Diskusi
-------
Pendekatan leksikon+signals memberikan keuntungan explainability dan performa cepat tanpa memerlukan hardware besar untuk fine-tuning. Namun, batasannya meliputi kebutuhan pemeliharaan leksikon untuk menangkap slang baru dan idiom regional. Model berbasis LLM/fine-tuned (mis. IndoBERT atau Gemini) dapat mengatasi beberapa kasus sarkasme/konotasi, tetapi menimbulkan trade-off: biaya API, latensi, dan reproducibility yang lebih rendah jika hasil bergantung pada layanan eksternal.

Rekomendasi untuk Tesis
-----------------------
1. Gunakan pipeline improved sebagai baseline eksperimen. 
2. Kumpulkan ground-truth 500–1000 contoh berlabel untuk fine-tuning model multilingual/Indonesian. 
3. Jalankan eksperimen per-topik (politics, health, etc.) dan laporkan metrik per-class dengan confidence intervals. 
4. Pertimbangkan ensemble: improved (lexicon) + fine-tuned model + LLM untuk kasus tie-break.

Kesimpulan
----------
Pipeline yang diusulkan memperbaiki masalah over-prediksi kelas Netral dengan menambahkan leksikon bahasa lokal dan preservasi sinyal intensitas. Untuk publikasi cepat dan bukti tesis, hasil, skrip, dan lampiran (prediksi, metrik, contoh error, visual) telah disiapkan dalam repo.

Lampiran & Reproducibility
--------------------------
- Skrip eksperimen: `scripts/run_stance_experiment.py`
- Notebook analisis: `notebooks/thesis_results_analysis.ipynb`
- Laporan evaluasi: `results/gt_experiment/REPORT.md`
- ZIP lampiran: `results/final_experiment/thesis_attachment_final.zip`

Kontak
------
Jika butuh revisi artikel atau tambahan analisis (per-topik, ensemble), beri tahu saya dan saya siapkan versi akhir siap submit.
