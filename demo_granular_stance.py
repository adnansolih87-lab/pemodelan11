"""
Demo script for granular stance analysis using Google Gemini API.

This script shows how to:
1. Load a dataset with posts and comments
2. Run granular stance analysis on the first 5 posts
3. Aggregate results and display summary
4. Save results to CSV
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

import pandas as pd

# Import custom modules
from load_data import load_dataset, prepare_post_comment_data
from stance_analysis_granular import (
    initialize_gemini,
    run_granular_stance_analysis,
    aggregate_stance_by_post
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run granular stance analysis demo."""
    
    print("=" * 80)
    print("DEMO: Granular Stance Analysis dengan Google Gemini API")
    print("=" * 80)
    
    # Step 1: Get API key
    print("\n[1/5] Mengambil Google Gemini API Key...")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: Environment variable 'GOOGLE_API_KEY' tidak ditemukan!")
        print("   Silakan set: export GOOGLE_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("✅ API Key ditemukan")
    
    # Step 2: Load data
    print("\n[2/5] Memuat dataset...")
    
    # Try different data sources
    data_path = None
    for path in ["sample_posts_comments.csv", "sample_data.csv"]:
        if Path(path).exists():
            data_path = path
            break
    
    if not data_path:
        print("❌ ERROR: Dataset tidak ditemukan!")
        print("   Coba: sample_posts_comments.csv atau sample_data.csv")
        sys.exit(1)
    
    try:
        df = load_dataset(data_path)
        print(f"✅ Dataset dimuat: {data_path} ({len(df)} baris)")
    except Exception as e:
        print(f"❌ ERROR: Gagal memuat dataset: {e}")
        sys.exit(1)
    
    # Step 3: Prepare post-comment structure
    print("\n[3/5] Mempersiapkan struktur data Post-Comment...")
    
    try:
        posts_df, comments_df = prepare_post_comment_data(df)
        print(f"✅ Data siap: {len(posts_df)} unggahan, {len(comments_df)} komentar")
        print(f"   Sample unggahan: '{posts_df.iloc[0]['full_text'][:80]}...'")
    except Exception as e:
        print(f"❌ ERROR: Gagal mempersiapkan data: {e}")
        sys.exit(1)
    
    # Step 4: Run granular stance analysis
    print("\n[4/5] Menjalankan analisis stance granular...")
    print("      (Menganalisis 5 unggahan pertama sebagai sample)\n")
    
    try:
        comments_with_stance = run_granular_stance_analysis(
            posts_df=posts_df,
            comments_df=comments_df,
            api_key=api_key,
            model_name="gemini-1.5-flash",
            sample_size=5,  # Demo: analyze first 5 posts
            batch_delay=2.0  # 2 second delay between API calls
        )
        
        print("\n✅ Analisis selesai!")
        print(f"   Kolom baru: {[col for col in comments_with_stance.columns if 'stance' in col.lower()]}")
        
    except Exception as e:
        print(f"❌ ERROR: Gagal menjalankan analisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 5: Display results
    print("\n[5/5] Menampilkan hasil analisis...\n")
    
    # Aggregated statistics
    print("=" * 80)
    print("STATISTIK KESELURUHAN")
    print("=" * 80)
    
    total_comments = len(comments_with_stance)
    mendukung_count = (comments_with_stance["stance_label"] == "Mendukung").sum()
    menolak_count = (comments_with_stance["stance_label"] == "Menolak").sum()
    netral_count = (comments_with_stance["stance_label"] == "Netral").sum()
    avg_weight = comments_with_stance["stance_weight"].mean()
    
    print(f"Total Komentar Dianalisis: {total_comments}")
    print(f"  🟩 Mendukung: {mendukung_count} ({mendukung_count/total_comments*100:.1f}%)")
    print(f"  🟥 Menolak:   {menolak_count} ({menolak_count/total_comments*100:.1f}%)")
    print(f"  ⬜ Netral:    {netral_count} ({netral_count/total_comments*100:.1f}%)")
    print(f"Rata-rata Bobot Keyakinan: {avg_weight:.2f}")
    
    # Sample of results
    print("\n" + "=" * 80)
    print("SAMPLE HASIL (5 KOMENTAR PERTAMA)")
    print("=" * 80 + "\n")
    
    for idx, (_, row) in enumerate(comments_with_stance.head(5).iterrows(), 1):
        print(f"📌 UNGGAHAN: \"{row['full_text'][:100]}...\"")
        print(f"   ↳ Komentar: \"{row['full_text_comments'][:100]}...\"")
        print(f"      - Stance: {row['stance_label']}")
        print(f"      - Bobot: {row['stance_weight']:.2f}")
        print(f"      - Alasan: {row.get('stance_reasoning', 'N/A')[:80]}...")
        print()
    
    # Per-post aggregation
    print("=" * 80)
    print("AGREGASI PER UNGGAHAN")
    print("=" * 80 + "\n")
    
    post_stats = aggregate_stance_by_post(comments_with_stance)
    
    for _, row in post_stats.iterrows():
        post_id = row["post_id"]
        post_text = posts_df[posts_df["post_id"] == post_id]["full_text"].iloc[0]
        
        print(f"📌 {post_id}: \"{post_text[:80]}...\"")
        print(f"   Distribusi Sikap:")
        print(f"     - Mendukung: {row['stance_mendukung_pct']:.1f}%")
        print(f"     - Menolak:   {row['stance_menolak_pct']:.1f}%")
        print(f"     - Netral:    {row['stance_netral_pct']:.1f}%")
        print(f"   Rata-rata Keyakinan: {row['avg_weight']:.2f}")
        print()
    
    # Save results
    print("=" * 80)
    print("MENYIMPAN HASIL")
    print("=" * 80 + "\n")
    
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    detailed_path = output_dir / f"stance_analysis_granular_{timestamp}.csv"
    comments_with_stance.to_csv(detailed_path, index=False)
    print(f"✅ Hasil detail disimpan: {detailed_path}")
    
    # Save aggregated results
    agg_path = output_dir / f"stance_aggregated_{timestamp}.csv"
    post_stats.to_csv(agg_path, index=False)
    print(f"✅ Hasil agregasi disimpan: {agg_path}")
    
    print("\n" + "=" * 80)
    print("✅ DEMO SELESAI!")
    print("=" * 80)
    print("\nLangkah selanjutnya:")
    print("1. Jalankan dashboard: streamlit run streamlit_granular_stance.py")
    print("2. Lihat hasil di dashboard dengan visualisasi interaktif")
    print("3. Filter dan explore data granular per unggahan")


if __name__ == "__main__":
    main()
