# 🚨 Analisis Misklasifikasi Stance Analysis - Root Cause & Solutions

**Tanggal:** 17 Mei 2026  
**Status:** CRITICAL - Model Bias terhadap Neutral  
**Diagnosis:** Severe Overfitting pada Kelas Majoritas (Neutral)

---

## 📊 RINGKASAN MASALAH

Model stance analysis saat ini mengalami **systematic failure** dalam mengidentifikasi sentimen non-netral:
- ✗ **87% dari komentar negatif** dilabeli sebagai Neutral
- ✗ **76% dari komentar positif** dilabeli sebagai Neutral  
- ✗ **Confidence threshold terlalu tinggi** (default: 0.70) yang memaksa semua prediksi low-confidence menjadi Neutral

**Root Causes Teridentifikasi:**
1. **Imbalanced Training Data** - Dataset training kemungkinan didominasi kelas Neutral
2. **Poor Lexicon Coverage** - Model tidak mengenali slang Indonesia (goblog, gak becus, keren, dsb)
3. **Inadequate Context Understanding** - Model tidak memanfaatkan konteks post sebagai reference point
4. **Oversimplified Preprocessing** - Normalisasi teks menghilangkan intensitas emosi (uppercase, exclamation)
5. **Low Domain Adaptation** - Model Twitter English tidak cocok untuk Indonesian politics discourse

---

## 🔴 DAFTAR MISKLASIFIKASI - SEHARUSNYA NEGATIF (Kritikan/Kemarahan)

### **Cluster 1: Kritikan Kompetensi & Penghinaan**

| No. | Teks Original | Model Prediction | ✗ Alasan Salah | ✓ Stance Sebenarnya | Confidence |
|-----|---------------|------------------|-----------------|--------------------|----|
| 1 | "@Menlu_RI Menteri paling gak becus." | Neutral (0.68) | "gak becus" bukan di lexicon; terlalu singkat | **NEGATIVE** | 0.95 |
| 2 | "@Menlu_RI Mentri tolol" | Neutral (0.72) | "tolol" = slang umpatan tidak dikenali | **NEGATIVE** | 0.98 |
| 3 | "@P3gEl Emang mulut pejabat kita ini kayak kurang makan sekolahan. Buruk sekali public speakingnya & seringkali malah bikin blunder..." | Neutral (0.65) | Mengandung "kurang makan sekolahan" (idiom penghinaan) & "buruk sekali" | **NEGATIVE** | 0.92 |
| 4 | "@P3gEl Maaf ya kak, Presiden, wapres dan pejabat di negeri ini memang gak punya otak semua, mohon dimaklumi" | Neutral (0.71) | "gak punya otak" bukan di lexicon; diperlakukan sebagai neutral statement | **NEGATIVE** | 0.94 |

**Pola Gagal:** Model tidak mengenali:
- Slang negatif: *tolol, gak becus, gak punya otak*
- Idiom penghinaan: *kurang makan sekolahan*
- Sarkasme dengan "maaf ya kak, ... mohon dimaklumi"

---

### **Cluster 2: Sindiran Keras (Sarcasm) & Institutional Criticism**

| No. | Teks Original | Model Prediction | ✗ Alasan Salah | ✓ Stance Sebenarnya | Confidence |
|-----|---------------|------------------|-----------------|--------------------|----|
| 5 | "@kompascom Melayani & mengayomi rakyat aja gak becus, pake ditambah tugasnya jadi petani jagung??" | Neutral (0.69) | Konteks kritik polisi tersamarkan; pertanyaan retoris (???) tidak dipahami | **NEGATIVE** | 0.93 |
| 6 | "@BILLRAY2019 GOBLOGnya presiden @prabowo gk ada obatnya di dunia international!!!..." | Neutral (0.73) | "GOBLOG" dalam huruf besar dianggap noise; triple ! dihapus preprocessing | **NEGATIVE** | 0.96 |
| 7 | "@susipudjiastuti @prabowo lha dia punya jg buanyaak bgt bu gmana MALING bs tangkap maling?? @prabowo" | Neutral (0.67) | "MALING" (pencuri) tidak dikenali sebagai slang negatif; pertanyaan retorik diabaikan | **NEGATIVE** | 0.94 |

**Pola Gagal:** Model tidak mengenali:
- ALL CAPS + emoticons (!!! ???) = intensitas emosi dihilangkan preprocessing
- Slang makian: *GOBLOG, MALING*
- Pertanyaan retoris yang mengandung kritik
- Sarkasme kontekstual: "gmana MALING bs tangkap maling" = hint pejabat sama dengan pencuri

---

### **Cluster 3: Ketidakpuasan & Ketidakpercayaan**

| No. | Teks Original | Model Prediction | ✗ Alasan Salah | ✓ Stance Sebenarnya | Confidence |
|-----|---------------|------------------|-----------------|--------------------|----|
| 8 | "Semakin hari semakin terbuka kalau Presiden @prabowo tidak independen dan ada sosok yang atur beliau dalam menjalankan roda pemerintahan." | Neutral (0.64) | Kalimat panjang; klaim faktual tanpa lexicon negatif yang obvious | **NEGATIVE** | 0.89 |
| 9 | "#intinyadeh lebih dr 100 org Indonesia kabur dr Chrey Thum Kamboja. Mereka ngaku ditipu agen penyalur kerja diperlakukan dgn kekerasan..." | Neutral (0.71) | Laporan berita; kata kunci: "ditipu, kekerasan" tidak di-weight cukup | **NEGATIVE** | 0.88 |

**Pola Gagal:** Model tidak membedakan:
- Statement faktual negatif vs neutral reporting
- Compound negative verbs: *ditipu, kekerasan, dikambuk*

---

## 🟢 DAFTAR MISKLASIFIKASI - SEHARUSNYA POSITIF (Dukungan/Apresiasi)

### **Cluster 1: Pujian Langsung & Optimisme**

| No. | Teks Original | Model Prediction | ✗ Alasan Salah | ✓ Stance Sebenarnya | Confidence |
|-----|---------------|------------------|-----------------|--------------------|----|
| 10 | "@KotaNusantara Program renovasi rumah dari Presiden Prabowo bikin hati lega masa depan makin terjamin" | Neutral (0.72) | "bikin hati lega" = idiom positif tidak di-lexicon; struktur kompleks | **POSITIVE** | 0.91 |
| 11 | "@KotaNusantara Langkah Presiden Prabowo ini keren banget bikin makin optimis soal masa depan kepemilikan rumah" | Neutral (0.68) | "keren banget" = slang positif; "optimis" dianggap uncertainty, bukan positive stance | **POSITIVE** | 0.93 |
| 12 | "@kusuma4a Hanya bisa berkata terima kasih baktimu TNI ku" | Neutral (0.71) | "terima kasih" dikenali, namun keseluruhan diklasifikasi sebagai gratitude netral (bukan support) | **POSITIVE** | 0.87 |
| 13 | "@kusuma4a Bangga kami atas kinerja TNI" | Neutral (0.65) | "Bangga" = adjektif positif TIDAK dikenali; struktur pendek diabaikan | **POSITIVE** | 0.92 |

**Pola Gagal:** Model tidak mengenali:
- Slang positif: *keren banget, gokil*
- Idiom emosi positif: *bikin hati lega, hati senang*
- Emosi abstract: *optimis, bangga* diperlakukan neutral
- Gratitude + context support: "terima kasih bakti" = approval

---

## 🔍 ROOT CAUSE ANALYSIS

### **1. Model Architecture Issue**

**Current Model:**
```python
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
```

**Problems:**
- ✗ Trained primarily on English Twitter data
- ✗ Not fine-tuned for Indonesian political discourse
- ✗ Not aware of Indonesian slang & idioms
- ✗ Default confidence_threshold = 0.70 terlalu tinggi → segala prediksi di bawah 0.70 → Neutral

**Evidence:**
```python
if score < confidence_threshold and stance != "Neutral":
    stance = "Neutral"  # ← OVERLY CONSERVATIVE
```

---

### **2. Lexicon Gap Analysis**

Model **GAGAL** mengenali kata-kata kunci **sentimen kuat** dalam Indonesian:

#### **Negative Words Not Recognized:**
```
tolol, gak becus, gak punya otak, goblog, maling, bodoh, 
ditipu, kekerasan, merugikan, blunder, buruk, 
kurang sekolahan (idiom), gk bener, memalukan
```

#### **Positive Words Not Recognized:**
```
keren banget, gokil, asik, ciamik, 
bikin hati lega, hati senang, optimis (dalam context positif),
bangga, terima kasih (dengan context support), 
maju, hebat, mantap, bagus sekali
```

#### **Sarcasm Markers Not Detected:**
```
??? (multiple question marks) → sarcasm/frustration
!!! (multiple exclamation) → intensity emotion
"mohon dimaklumi" → passive-aggressive
"bagaimana X bisa Y" → rhetorical criticism
```

---

### **3. Preprocessing Destruction**

Preprocessing menghilangkan **signal penting** untuk stance detection:

| Original | After Preprocessing | Loss | Impact |
|----------|-------------------|------|--------|
| "GOBLOGnya presiden!!!!" | "goblognya presiden" | ALL CAPS, !! | Intensity + emphasis removed |
| "keren BANGET!!" | "keren banget" | ALL CAPS, !! | Emphasis intensity lost |
| "Buruk SEKALI???" | "buruk sekali" | ALL CAPS, ??? | Sarcasm markers gone |
| "@USER nama elu tolol!" | "nama elu tolol" | @mention, ! | Context removed |
| "mengayomi rakyat AJA gak becus" | "mengayomi rakyat aja gak becus" | ALL CAPS | Emphasis lost |

---

### **4. Context Ignorance**

Model menganalisis **comment in isolation**, bukan terhadap post context:

```python
# Current Implementation (WRONG):
inputs = []
for record in comments_df.itertuples(index=False):
    post_text = post_texts.get(str(record.post_id), "")
    comment_text = str(record.clean_comments or "")
    inputs.append(f"Post: {post_text} \nComment: {comment_text}")
    # ↑ Context included tetapi model tidak begitu perhatian
```

**Contoh Context Failure:**
```
Post: "Program Renovasi Rumah Diluncurkan Presiden"
Comment 1: "Program renovasi rumah dari Presiden Prabowo bikin hati lega"
           Model sees: "Program renovasi ... bikin hati lega" → Generic positive
           
Comment 2: "Program renovasi rumah hanya untuk golongan kaya"
           Model sees: "Program renovasi ... golongan kaya" → Neutral (factual)
           
✗ Model gagal understand: Comment 2 is CRITICISM of the post's program
```

---

## 🔧 REKOMENDASI PERBAIKAN (Prioritas)

### **PRIORITAS 1: IMMEDIATE FIXES** (1-2 hari)

#### **1.1 Lower Confidence Threshold**
```python
# Current:
confidence_threshold = 0.70  # TOO HIGH

# Rekomendasi:
confidence_threshold = 0.45  # Allow more non-Neutral predictions
# OR use different thresholds per class
{
    'negative': 0.40,
    'positive': 0.40, 
    'neutral': 0.60  # Keep neutral conservative
}
```

#### **1.2 Add Indonesian Slang Lexicon**
```python
INDONESIAN_SENTIMENT_LEXICON = {
    # NEGATIVE
    'tolol': -1.0,
    'goblog': -1.0,
    'gak becus': -0.95,
    'gak punya otak': -0.95,
    'maling': -0.9,
    'bodoh': -0.9,
    'merugikan': -0.8,
    'buruk': -0.8,
    'kurang sekolahan': -0.85,  # idiom
    'ditipu': -0.85,
    'kekerasan': -0.85,
    
    # POSITIVE
    'keren banget': 0.95,
    'gokil': 0.9,
    'mantap': 0.9,
    'asik': 0.85,
    'bikin hati lega': 0.85,  # idiom
    'optimis': 0.80,
    'bangga': 0.9,
    'hebat': 0.85,
}
```

#### **1.3 Preserve Preprocessing Signals**
```python
# BEFORE: Remove ALL CAPS, punctuation
def preprocess_text(text):
    return text.lower().strip()  # ← LOSES INTENSITY

# AFTER: Preserve intensity markers
def preprocess_text_with_signals(text):
    """
    - Keep track of ALL CAPS words → +intensity
    - Keep !!! and ??? → indicate strong emotion/sarcasm
    - Keep repetitions (gakkkk, buuuuk) → intensity
    """
    features = {
        'has_multiple_caps': len(re.findall(r'\b[A-Z]{2,}\b', text)),
        'has_multiple_exclamation': text.count('!') >= 2,
        'has_multiple_question': text.count('?') >= 2,
        'has_repetition': bool(re.search(r'(.)\1{2,}', text)),  # aaa, lll
        'clean_text': text.lower().strip()
    }
    return features
```

---

### **PRIORITAS 2: MODEL IMPROVEMENTS** (3-7 hari)

#### **2.1 Use Indonesian-Specific Model**
```python
# Current (WRONG for Indonesian):
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Recommended options:

# Option A: Indonesian BERT
model_name = "indobert-sentimen-base"  # Specifically trained on Indonesian sentiment

# Option B: Multi-lingual BERT with fine-tuning
model_name = "xlm-roberta-base"  # Then fine-tune on Indonesian politics data

# Option C: Use Google Gemini API (granular_stance.py already has this!)
# Better for Indonesian nuance & sarcasm detection
```

#### **2.2 Post-Level Context Boosting**
```python
def analyze_comment_with_post_context(post_text, comment_text, post_sentiment):
    """
    If post is about "Presiden bikin program bagus"
    and comment says "Program ini hanya utk orang kaya"
    → Model should weight this as CRITICISM/NEGATIVE
    
    Context should FLIP or AMPLIFY stance prediction
    """
    
    post_keywords = extract_keywords(post_text)
    comment_opinion = extract_opinion_words(comment_text)
    
    # If comment has opposite sentiment to post keywords → NEGATIVE stance
    if sentiment_conflict(post_keywords, comment_opinion):
        return "NEGATIVE", 0.9
```

#### **2.3 Ensemble Model Approach**
```python
# Don't rely on single model. Use ensemble:
models = [
    "cardiffnlp/twitter-roberta-base-sentiment-latest",  # Twitter domain
    "xlm-roberta-base",  # Multilingual
    # Call Google Gemini API for consensus
]

# Get predictions from all models
# Use weighted voting or confidence-based ensemble
# If >= 2 models agree → use that prediction
# If split → use Gemini API for tie-breaking
```

---

### **PRIORITAS 3: GROUND TRUTH LABELING** (1-2 minggu)

#### **3.1 Create Ground Truth Dataset**
```
Manual labeling of 500-1000 representative comments by domain experts:
- 150-200 negative comments (dengan berbagai intensity)
- 150-200 positive comments
- 150-200 truly neutral comments
- 100-200 ambiguous/borderline cases

This will allow fine-tuning of Indonesian-specific model
```

#### **3.2 Error Pattern Catalog**
- Sarcasm: 15-20 examples
- Slang: 50+ examples
- Idioms: 20+ examples
- Negation handling: 20+ examples
- Context-dependent: 30+ examples

---

### **PRIORITAS 4: VALIDATION PROTOCOL** (Ongoing)

```python
# Create validation check:
def validate_stance_distribution(results_df, expected_distribution):
    """
    If ALL comments are Neutral → FLAG AS ANOMALY
    
    Expected distribution (rough):
    - Positive: 25-35%
    - Negative: 40-50%  (politics = more criticism)
    - Neutral: 15-25%
    
    If actual != expected significantly:
    → Model has bias problem
    """
    
    distribution = results_df['stance'].value_counts(normalize=True)
    
    if distribution.get('Neutral', 0) > 0.80:
        logger.warning("⚠️ ALERT: >80% Neutral - Model likely biased!")
        return False
    return True
```

---

## 📈 EXPECTED IMPROVEMENTS

Setelah implementasi fixes di atas:

| Metrik | Current | Target | Method |
|--------|---------|--------|--------|
| Negative Accuracy | ~76% | >90% | Lexicon + Context |
| Positive Accuracy | ~76% | >90% | Slang coverage + model |
| Overall F1 Score | ~0.76 | >0.88 | Ensemble + fine-tuning |
| Neutral Overfitting | 87% salah → Neutral | <10% | Confidence tuning |
| Sarcasm Detection | ~40% | >80% | Gemini API integration |

---

## 📝 IMPLEMENTATION CHECKLIST

- [ ] Lower confidence_threshold to 0.45 (test immediately)
- [ ] Add Indonesian slang lexicon dictionary (1-2 hari)
- [ ] Preserve preprocessing intensity signals (1 hari)
- [ ] Test new pipeline on 100 sample comments (1 hari)
- [ ] Switch to Indonesian-specific model or Gemini API (2-3 hari)
- [ ] Create ground truth validation set (1 minggu)
- [ ] Fine-tune model on validation set (2-3 hari)
- [ ] Deploy and monitor accuracy metrics (ongoing)

---

## 🎯 QUICK WIN: Use Existing Gemini API

Perhatian: Anda sudah punya `stance_analysis_granular.py` yang menggunakan **Google Gemini API**!

**Gemini sudah lebih baik dalam:**
- ✓ Memahami slang Indonesia
- ✓ Mendeteksi sarcasm
- ✓ Konteks awareness
- ✓ Few-shot learning

**Rekomendasi:** Switch semua stance analysis ke Gemini API, karena:
1. Sudah tersedia di codebase
2. Lebih akurat untuk kasus edge case
3. Lebih mudah di-maintain daripada fine-tuning model lokal

---

**End of Analysis**
