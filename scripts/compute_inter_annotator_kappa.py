#!/usr/bin/env python3
"""Compute pairwise Cohen's kappa and Fleiss' kappa from labeling CSV.

Expected input CSV format (rows per annotation):
- comment_id: unique id per item
- label_expected or label: label value (Positive/Negative/Neutral)
- labeler_id: annotator id (string or int)

The script will pivot annotations into an item x annotator matrix and compute:
- Pairwise Cohen's kappa for each annotator pair
- Average pairwise Cohen's kappa
- Fleiss' kappa for all items (handles variable number of annotators per item)

Outputs: prints to stdout and writes `results/kappa_report.txt` and `results/kappa_details.csv`.
"""
import argparse
import csv
import math
import os
from collections import defaultdict, Counter

try:
    import pandas as pd
    from sklearn.metrics import cohen_kappa_score
except Exception:
    pd = None
    def cohen_kappa_score(a,b):
        # fallback simple implementation for identical labels length
        if len(a)!=len(b):
            raise ValueError("Label arrays must have same length for Cohen's kappa fallback")
        # compute observed agreement
        n=len(a)
        agree=sum(1 for x,y in zip(a,b) if x==y)/n
        labels=sorted(set(a)|set(b))
        p_a={lab:sum(1 for x in a if x==lab)/n for lab in labels}
        p_b={lab:sum(1 for x in b if x==lab)/n for lab in labels}
        exp=sum(p_a[l]*p_b[l] for l in labels)
        if (1-exp)==0:
            return 0.0
        return (agree-exp)/(1-exp)


def fleiss_kappa(subjects_counts):
    """Compute Fleiss' kappa.
    subjects_counts: list of dicts mapping category -> count for each subject
    returns kappa float
    """
    n_subjects=len(subjects_counts)
    if n_subjects==0:
        return float('nan')
    categories=sorted({c for s in subjects_counts for c in s.keys()})
    n_categories=len(categories)
    # m = number of ratings per subject (may vary; Fleiss assumes fixed m)
    # We will handle variable m by weighting; here we only compute when m constant across subjects
    counts_per_subject=[sum(s.values()) for s in subjects_counts]
    if len(set(counts_per_subject))!=1:
        # fallback: compute approximate Fleiss with varying m by using mean m
        m=sum(counts_per_subject)/len(counts_per_subject)
    else:
        m=counts_per_subject[0]
    # p_j: proportion of all assignments to category j
    total_annotations=sum(counts_per_subject)
    p_j={cat: sum(s.get(cat,0) for s in subjects_counts)/total_annotations for cat in categories}
    # P_i: extent of agreement for subject i
    P_i=[]
    for s in subjects_counts:
        sum_sq=0
        for cat in categories:
            n_ij=s.get(cat,0)
            sum_sq += n_ij*(n_ij-1)
        if m*(m-1)==0:
            P_i.append(0.0)
        else:
            P_i.append(sum_sq/(m*(m-1)))
    P_bar=sum(P_i)/n_subjects
    P_e=sum(v*v for v in p_j.values())
    if (1-P_e)==0:
        return 0.0
    kappa=(P_bar - P_e)/(1-P_e)
    return kappa


def load_annotations(path):
    # Support both pandas or csv fallback
    anns=[]
    if pd is not None:
        df=pd.read_csv(path, dtype=str)
        # normalize column names
        cols={c.lower():c for c in df.columns}
        label_col=None
        for name in ['label_expected','label','label_value']:
            if name in cols:
                label_col=cols[name]
                break
        if 'comment_id' not in cols:
            raise ValueError('CSV must contain comment_id column')
        if 'labeler_id' not in cols:
            raise ValueError('CSV must contain labeler_id column')
        for _,row in df.iterrows():
            label=row[label_col] if label_col is not None else ''
            anns.append((str(row[cols['comment_id']]), str(row[cols['labeler_id']]), str(label)))
    else:
        with open(path, newline='') as f:
            r=csv.DictReader(f)
            lowcols={c.lower():c for c in r.fieldnames}
            if 'comment_id' not in lowcols:
                raise ValueError('CSV must contain comment_id column')
            if 'labeler_id' not in lowcols:
                raise ValueError('CSV must contain labeler_id column')
            label_col=None
            for name in ['label_expected','label','label_value']:
                if name in lowcols:
                    label_col=lowcols[name]
                    break
            for row in r:
                label=row[label_col] if label_col is not None else ''
                anns.append((row[lowcols['comment_id']], row[lowcols['labeler_id']], label))
    return anns


def pivot_annotations(anns):
    # anns: list of (item, annotator, label)
    items=defaultdict(dict)
    annotators=set()
    for item,ann,lab in anns:
        items[item][ann]=lab
        annotators.add(ann)
    annotators=sorted(annotators)
    return items, annotators


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--labels', required=True, help='CSV file with annotations (one row per annotation)')
    parser.add_argument('--outdir', default='results', help='Output folder')
    args=parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    anns=load_annotations(args.labels)
    items, annotators = pivot_annotations(anns)
    # build per-item lists for pairwise comparisions
    # compute pairwise Cohen's kappa for annotator pairs (only on common items)
    pairwise_results=[]
    for i in range(len(annotators)):
        for j in range(i+1,len(annotators)):
            a=annotators[i]; b=annotators[j]
            labels_a=[]; labels_b=[]
            for item,annmap in items.items():
                if a in annmap and b in annmap:
                    labels_a.append(annmap[a])
                    labels_b.append(annmap[b])
            if len(labels_a)==0:
                score=float('nan')
            else:
                score=cohen_kappa_score(labels_a, labels_b)
            pairwise_results.append((a,b, len(labels_a), score))
    # average pairwise (weighted by number of common items)
    total_pairs=0; weighted_sum=0.0; total_common=0
    for a,b,n_common,score in pairwise_results:
        if not math.isnan(score):
            weighted_sum += score * n_common
            total_common += n_common
            total_pairs += 1
    avg_pairwise = (weighted_sum/total_common) if total_common>0 else float('nan')

    # Fleiss' kappa: need subject counts per category
    categories=sorted({lab for _,_,lab in anns if lab!=''})
    subjects_counts=[]
    for item,annmap in items.items():
        c=Counter()
        for ann,lab in annmap.items():
            c[lab]+=1
        subjects_counts.append(c)
    fleiss = fleiss_kappa(subjects_counts)

    # write outputs
    report_path=os.path.join(args.outdir,'kappa_report.txt')
    with open(report_path,'w') as f:
        f.write('Inter-annotator agreement report\n')
        f.write('===============================\n')
        f.write(f"Input labels: {args.labels}\n")
        f.write(f"Annotators found: {', '.join(annotators)}\n")
        f.write('\nPairwise Cohen kappa (annotatorA, annotatorB, n_common_items, kappa)\n')
        for a,b,n_common,score in pairwise_results:
            f.write(f"{a}, {b}, {n_common}, {score}\n")
        f.write(f"\nAverage pairwise (item-weighted): {avg_pairwise}\n")
        f.write(f"Fleiss' kappa: {fleiss}\n")
    # also save details CSV
    details_path=os.path.join(args.outdir,'kappa_details.csv')
    with open(details_path,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['annotator_a','annotator_b','n_common_items','kappa'])
        for a,b,n_common,score in pairwise_results:
            w.writerow([a,b,n_common,score])
        w.writerow([])
        w.writerow(['average_pairwise', avg_pairwise])
        w.writerow(['fleiss_kappa', fleiss])
    print('Wrote report to', report_path)
    print('Wrote details to', details_path)

if __name__=='__main__':
    main()
