"""
Granular Stance Analysis using Google Gemini API.

Performs hierarchical stance classification:
- Post (Unggahan Utama) as context
- Comments (Komentar) as analysis units
- Output: stance label + confidence weight per comment
"""

import pandas as pd
import json
import re
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import time
import logging

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StanceResult:
    """Stance analysis result for a single comment."""
    post_id: str
    comment_id: str
    full_text: str
    full_text_comments: str
    stance_label: str  # "Mendukung", "Menolak", "Netral"
    stance_weight: float  # 0.0 - 1.0
    reasoning: str  # Brief explanation


def initialize_gemini(api_key: str) -> bool:
    """Initialize Google Gemini API."""
    if genai is None:
        logger.error("google-generativeai package not installed. Install with: pip install google-generativeai")
        return False
    
    try:
        genai.configure(api_key=api_key)
        logger.info("Google Gemini API initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {e}")
        return False


def create_stance_prompt(post_text: str, comments: List[str]) -> str:
    """Create structured few-shot prompt for granular stance analysis."""
    
    prompt = f"""Anda adalah analis sentimen dan sikap ahli yang berbahasa Indonesia. 

TUGAS: Lakukan Stance Analysis (Analisis Sikap) secara GRANULAR pada komentar terhadap unggahan utama.

KONTEKS UNGGAHAN UTAMA:
"{post_text}"

KOMENTAR-KOMENTAR YANG HARUS DIANALISIS:
{json.dumps(comments, ensure_ascii=False, indent=2)}

INSTRUKSI:
1. Analisis MASING-MASING komentar terhadap unggahan utama di atas
2. Klasifikasikan sikap ke dalam tiga kategori: "Mendukung", "Menolak", atau "Netral"
3. Berikan bobot keyakinan (confidence score) dari 0.0 hingga 1.0
4. Jelaskan alasan singkat (1 kalimat) mengapa klasifikasi tersebut dipilih

FORMAT OUTPUT (WAJIB):
Berikan output dalam bentuk JSON array seperti ini:
[
  {{
    "comment_index": 0,
    "comment_text": "[teks komentar]",
    "stance": "Mendukung|Menolak|Netral",
    "weight": 0.xx,
    "reasoning": "[Alasan singkat 1 kalimat]"
  }},
  ...
]

PEDOMAN KLASIFIKASI:
- MENDUKUNG: Komentar mengekspresikan persetujuan, dukungan, atau sentimen positif terhadap unggahan
- MENOLAK: Komentar mengekspresikan ketidaksetujuan, penolakan, atau sentimen negatif terhadap unggahan
- NETRAL: Komentar bersifat informatif, pertanyaan, atau tidak jelas mendukung/menolak

OUTPUT HANYA JSON ARRAY TANPA TEKS TAMBAHAN."""
    
    return prompt


def analyze_batch_with_gemini(
    post_id: str,
    post_text: str,
    comment_records: List[Dict],
    model_name: str = "gemini-1.5-flash",
    retry_attempts: int = 3,
    delay_seconds: float = 1.0
) -> List[StanceResult]:
    """
    Analyze a batch of comments for a single post using Gemini API.
    
    Args:
        post_id: Unique post identifier
        post_text: Full text of the main post
        comment_records: List of dicts with keys: comment_id, full_text_comments
        model_name: Gemini model to use
        retry_attempts: Number of retry attempts for API calls
        delay_seconds: Delay between retries
    
    Returns:
        List of StanceResult objects
    """
    if genai is None:
        raise RuntimeError("Google Generative AI not initialized. Install: pip install google-generativeai")
    
    if not comment_records:
        return []
    
    # Extract comment texts
    comments = [rec.get("full_text_comments", "") for rec in comment_records]
    
    # Create prompt
    prompt = create_stance_prompt(post_text, comments)
    
    # Call Gemini API with retry logic
    results = []
    attempt = 0
    
    while attempt < retry_attempts:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for consistency
                    max_output_tokens=2048
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if not json_match:
                logger.warning(f"Could not find JSON in response for post {post_id}. Attempt {attempt + 1}/{retry_attempts}")
                attempt += 1
                if attempt < retry_attempts:
                    time.sleep(delay_seconds)
                continue
            
            parsed_results = json.loads(json_match.group())
            
            # Convert parsed results to StanceResult objects
            for idx, record in enumerate(parsed_results):
                comment_record = comment_records[idx]
                stance_result = StanceResult(
                    post_id=str(post_id),
                    comment_id=str(comment_record.get("comment_id", f"comment_{idx}")),
                    full_text=post_text,
                    full_text_comments=comment_record.get("full_text_comments", ""),
                    stance_label=record.get("stance", "Netral"),
                    stance_weight=float(record.get("weight", 0.5)),
                    reasoning=record.get("reasoning", "")
                )
                results.append(stance_result)
            
            logger.info(f"Successfully analyzed {len(results)} comments for post {post_id}")
            return results
        
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing error for post {post_id}: {e}. Attempt {attempt + 1}/{retry_attempts}")
            attempt += 1
            if attempt < retry_attempts:
                time.sleep(delay_seconds)
        
        except Exception as e:
            logger.error(f"API error for post {post_id}: {e}. Attempt {attempt + 1}/{retry_attempts}")
            attempt += 1
            if attempt < retry_attempts:
                time.sleep(delay_seconds)
    
    logger.error(f"Failed to analyze comments for post {post_id} after {retry_attempts} attempts")
    return []


def run_granular_stance_analysis(
    posts_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    api_key: Optional[str] = None,
    model_name: str = "gemini-1.5-flash",
    sample_size: Optional[int] = None,
    batch_delay: float = 1.0
) -> pd.DataFrame:
    """
    Perform granular stance analysis using Google Gemini API.
    
    Args:
        posts_df: DataFrame with columns: post_id, full_text
        comments_df: DataFrame with columns: post_id, comment_id, full_text_comments
        api_key: Google Gemini API key (if not already initialized)
        model_name: Model to use (default: gemini-1.5-flash)
        sample_size: If set, only analyze first N posts (for testing)
        batch_delay: Delay in seconds between batch API calls
    
    Returns:
        DataFrame with added columns: stance_label, stance_weight, stance_reasoning
    """
    
    # Initialize API if key provided
    if api_key:
        if not initialize_gemini(api_key):
            raise RuntimeError("Failed to initialize Gemini API")
    
    if genai is None:
        raise RuntimeError("Google Generative AI not initialized")
    
    # Copy comments dataframe
    result_df = comments_df.copy()
    result_df["stance_label"] = "Netral"
    result_df["stance_weight"] = 0.5
    result_df["stance_reasoning"] = ""
    
    # Create post lookup
    post_texts = posts_df.set_index("post_id")["full_text"].to_dict()
    
    # Group comments by post
    grouped = comments_df.groupby("post_id")
    posts_to_analyze = list(grouped.groups.keys())
    
    if sample_size:
        posts_to_analyze = posts_to_analyze[:sample_size]
    
    logger.info(f"Starting granular stance analysis for {len(posts_to_analyze)} posts")
    
    # Process each post
    for post_idx, post_id in enumerate(posts_to_analyze):
        post_text = post_texts.get(post_id, "")
        if not post_text:
            logger.warning(f"Post text not found for post_id: {post_id}")
            continue
        
        # Get comments for this post
        post_comments = grouped.get_group(post_id)
        comment_records = [
            {
                "comment_id": row["comment_id"],
                "full_text_comments": row["full_text_comments"]
            }
            for _, row in post_comments.iterrows()
        ]
        
        # Analyze comments
        stance_results = analyze_batch_with_gemini(
            post_id=post_id,
            post_text=post_text,
            comment_records=comment_records,
            model_name=model_name,
            retry_attempts=3,
            delay_seconds=1.0
        )
        
        # Map results back to dataframe
        for stance_result in stance_results:
            mask = (result_df["post_id"] == stance_result.post_id) & \
                   (result_df["comment_id"] == stance_result.comment_id)
            result_df.loc[mask, "stance_label"] = stance_result.stance_label
            result_df.loc[mask, "stance_weight"] = stance_result.stance_weight
            result_df.loc[mask, "stance_reasoning"] = stance_result.reasoning
        
        # Progress logging
        logger.info(f"Processed {post_idx + 1}/{len(posts_to_analyze)} posts")
        
        # Delay between batch calls
        if post_idx < len(posts_to_analyze) - 1:
            time.sleep(batch_delay)
    
    return result_df


def aggregate_stance_by_post(comments_with_stance: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate stance analysis results by post.
    
    Returns DataFrame with columns:
    - post_id
    - stance_mendukung_pct: Percentage of "Mendukung" comments
    - stance_menolak_pct: Percentage of "Menolak" comments
    - stance_netral_pct: Percentage of "Netral" comments
    - avg_weight: Average confidence weight
    """
    
    if comments_with_stance.empty:
        return pd.DataFrame()
    
    # Normalize stance labels
    comments_with_stance_copy = comments_with_stance.copy()
    comments_with_stance_copy["stance_label_normalized"] = comments_with_stance_copy["stance_label"].str.lower().str.strip()
    
    # Group by post_id and stance
    grouped = comments_with_stance_copy.groupby("post_id").agg({
        "stance_label_normalized": lambda x: (x == "mendukung").sum() / len(x) * 100 if len(x) > 0 else 0,
    }).reset_index()
    grouped.rename(columns={"stance_label_normalized": "stance_mendukung_pct"}, inplace=True)
    
    # Add other stance percentages
    for post_id in grouped["post_id"].unique():
        mask = comments_with_stance_copy["post_id"] == post_id
        stances = comments_with_stance_copy.loc[mask, "stance_label_normalized"]
        total = len(stances)
        
        grouped.loc[grouped["post_id"] == post_id, "stance_menolak_pct"] = (stances == "menolak").sum() / total * 100 if total > 0 else 0
        grouped.loc[grouped["post_id"] == post_id, "stance_netral_pct"] = (stances == "netral").sum() / total * 100 if total > 0 else 0
        grouped.loc[grouped["post_id"] == post_id, "avg_weight"] = comments_with_stance_copy.loc[mask, "stance_weight"].mean()
    
    return grouped


if __name__ == "__main__":
    print("Stance Analysis Granular module loaded successfully.")
    print("Usage: from stance_analysis_granular import run_granular_stance_analysis")
