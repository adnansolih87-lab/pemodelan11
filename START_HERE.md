# 🚀 NEXT STEPS - Immediate Action Items

**Everything is ready. Follow these steps to get started.**

---

## ⏱️ Time Estimates

| Step | Time | Complexity |
|------|------|-----------|
| Setup | 5 min | ⭐ Easy |
| Test | 10-15 min | ⭐ Easy |
| Explore | 10 min | ⭐⭐ Medium |
| Customize | 30+ min | ⭐⭐⭐ Advanced |

---

## 🎯 Step 1: Setup (5 minutes)

### 1.1 Install Dependencies
```bash
pip install -r requirements.txt
```

If there are any issues with specific packages:
```bash
pip install --upgrade google-generativeai
```

### 1.2 Get Google Gemini API Key
1. Visit: https://aistudio.google.com
2. Click **"Get API Key"** button
3. Select **"Create API Key in new project"**
4. Copy the API key to clipboard

### 1.3 Set Environment Variable
**Linux/Mac:**
```bash
export GOOGLE_API_KEY="paste-your-key-here-from-step-1.2"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=paste-your-key-here-from-step-1.2
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY = "paste-your-key-here-from-step-1.2"
```

### 1.4 Verify Setup
```bash
python -c "import google.generativeai; print('✅ Setup Complete!')"
```

---

## 🧪 Step 2: Test with Demo (10-15 minutes)

Run the demo script to analyze first 5 posts:

```bash
python demo_granular_stance.py
```

**Expected Output:**
```
====== DEMO: Granular Stance Analysis dengan Google Gemini API ======

[1/5] Mengambil Google Gemini API Key...
✅ API Key ditemukan

[2/5] Memuat dataset...
✅ Dataset dimuat: sample_posts_comments.csv (2500 baris)

[3/5] Mempersiapkan struktur data Post-Comment...
✅ Data siap: 50 unggahan, 2500 komentar

[4/5] Menjalankan analisis stance granular...
(Menganalisis 5 unggahan pertama sebagai sample)

✅ Analisis selesai!

[5/5] Menampilkan hasil analisis...

📌 UNGGAHAN: "Kebijakan luar negeri harus lebih terbuka..."
   Distribusi Sikap: 🟩 20% | 🟥 70% | ⬜ 10%
   
   ↳ Komentar: "Setuju, ini langkah yang tepat"
      - Stance: Mendukung
      - Bobot: 0.95
      - Alasan: Komentar mengekspresikan persetujuan eksplisit

✅ Hasil detail disimpan: results/stance_analysis_granular_20260515_*.csv
✅ Hasil agregasi disimpan: results/stance_aggregated_20260515_*.csv

====== ✅ DEMO SELESAI! ======
```

**Files Generated:**
- `results/stance_analysis_granular_*.csv` - Detailed results per comment
- `results/stance_aggregated_*.csv` - Summary per post

---

## 🎨 Step 3: Explore Dashboard (10 minutes)

Launch the interactive Streamlit dashboard:

```bash
streamlit run streamlit_granular_stance.py
```

**Browser opens automatically to:** `http://localhost:8501`

**Dashboard Walkthrough:**

### 3.1 Load Data
- Left sidebar: Select **"Sample Data"** (default)
- Click **"▶️ Jalankan Analisis Stance"** button
- Watch progress bar as analysis runs

### 3.2 View Summary Statistics
- Top section shows overall metrics:
  - Total Posts, Total Comments (filtered)
  - Average Confidence Score
  - Distribution charts

### 3.3 Explore Per-Post Details
- Scroll down to **"📑 Detail Per Unggahan"**
- Click 🔽 arrow to expand each post accordion
- See:
  - 📊 Stance distribution pie chart
  - 💬 Comments table with color-coded stances
  - 🔍 Option to view full details per comment

### 3.4 Use Filters
- Left sidebar under **"🔍 Filter Hasil Analisis":**
  - **Filter Sikap:** Select specific stance(s)
  - **Bobot Keyakinan Minimum:** Drag slider to filter by confidence
  - **Filter Topik:** Choose specific topics (if available)
- Results update in real-time!

---

## 🔧 Step 4: Next Actions (After Step 3)

### Choose One Path:

#### Path A: Scale Analysis 📈
```python
# Edit demo_granular_stance.py, change sample_size:
sample_size=50  # Analyze first 50 posts instead of 5
```
Then run: `python demo_granular_stance.py`

#### Path B: Customize for Your Domain 🎯
1. Open `stance_analysis_granular.py`
2. Find `create_stance_prompt()` function
3. Modify instructions for your specific domain
4. Example: Add specific policy context, different categories

#### Path C: Integrate with Existing Pipeline 🔗
```python
# Use in your own scripts:
from stance_analysis_granular import run_granular_stance_analysis
from load_data import load_dataset, prepare_post_comment_data

df = load_dataset("your_data.csv")
posts_df, comments_df = prepare_post_comment_data(df)

results = run_granular_stance_analysis(
    posts_df=posts_df,
    comments_df=comments_df,
    api_key=os.getenv("GOOGLE_API_KEY"),
    sample_size=100
)
```

#### Path D: Generate Reports 📊
After running analysis, check `results/` folder:
```bash
ls -la results/stance_analysis_*.csv
```

Load in Excel/Sheets for further analysis or pivot tables.

---

## 📖 Documentation Guide

| What You Want | Read This |
|---------------|-----------|
| "I want to understand everything" | `IMPLEMENTATION_SUMMARY.md` |
| "Give me quick setup" | `IMPLEMENTATION_CHECKLIST.md` (Top 3 steps) |
| "How do I solve XYZ problem?" | `GRANULAR_STANCE_GUIDE.md` (Troubleshooting) |
| "Show me code examples" | `demo_granular_stance.py` |
| "I want to use the dashboard" | Explore `streamlit_granular_stance.py` running |

---

## ⚠️ Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| "Google API Key tidak ditemukan" | Run: `export GOOGLE_API_KEY="your-key"` then try again |
| "ModuleNotFoundError: google" | Run: `pip install google-generativeai` |
| "Analysis takes too long" | Reduce `sample_size` from 50 to 5 in demo |
| "Rate limit errors" | Increase `batch_delay` in code (default: 2.0 sec) |
| "Output is mostly 'Netral'" | Check API logs, or adjust prompt in `create_stance_prompt()` |

---

## ✨ Pro Tips

1. **First Run:** Always test with `sample_size=5` to verify setup works
2. **Save Results:** CSV files are automatically saved to `results/` folder
3. **Batch Processing:** Analyze different time periods separately for comparison
4. **Custom Prompts:** Edit prompt in `create_stance_prompt()` for domain-specific logic
5. **Dashboard**: Use filters to focus on specific patterns (e.g., high-confidence negative stances)

---

## 🎯 Your Task Checklist

- [ ] **Step 1:** Setup (pip install, API key, env var)
- [ ] **Step 2:** Run `python demo_granular_stance.py` (verify it works)
- [ ] **Step 3:** Run `streamlit run streamlit_granular_stance.py` (explore UI)
- [ ] **Step 4:** Choose Path A/B/C/D based on your needs
- [ ] **Step 5:** Document findings, save results to `results/` folder

---

## 📞 When You Get Stuck

1. **Re-read:** Check if issue is mentioned in `GRANULAR_STANCE_GUIDE.md` Troubleshooting
2. **Verify:** Confirm API key is correct: `echo $GOOGLE_API_KEY`
3. **Test:** Run a simple test: `python -c "import google.generativeai"`
4. **Logs:** Run with debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
5. **Check Files:** Ensure all created files exist: `ls *.py | grep stance`

---

## 🚀 Accelerated Path (If in hurry)

**Total time: 20 minutes**

```bash
# 1. Setup (3 min)
pip install -r requirements.txt
export GOOGLE_API_KEY="your-key"

# 2. Verify (2 min)
python -c "import google.generativeai; print('✅')"

# 3. Test (10 min)
python demo_granular_stance.py

# 4. Explore Dashboard (5 min)
streamlit run streamlit_granular_stance.py
# (then just click buttons and explore!)
```

Done! Results in `results/` folder, dashboard at `localhost:8501`

---

## 🎓 What You'll Learn

By completing these steps, you will understand:

1. ✅ How Google Gemini API works with few-shot prompting
2. ✅ How to extract granular stance analysis (not just aggregates)
3. ✅ How to build professional dashboards with Streamlit
4. ✅ How to process hierarchical data (Post → Comments → Analysis)
5. ✅ How to implement color-coding and filters for UX
6. ✅ Best practices for batch processing with APIs

---

## 💡 Future Learning

After mastering this, explore:
- Multi-language support (extending to English, Arabic, etc.)
- Different LLM models (GPT-4, Claude, local LLMs)
- Real-time streaming analysis
- Database integration (PostgreSQL, MongoDB)
- Advanced visualizations (network graphs, trend analysis)

---

**Status:** ✅ Ready to Go!  
**Start Time:** Now!  
**Estimated Completion:** 30-45 minutes

---

**Good luck! You've got this! 🎉**

Once you complete Step 3 and see the dashboard working, you'll have a professional,
production-ready stance analysis system that goes way beyond just showing numbers.

👉 **Start with:** `python demo_granular_stance.py`
