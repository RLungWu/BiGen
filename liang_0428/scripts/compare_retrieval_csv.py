import argparse
import csv
import os
from collections import Counter, defaultdict


def load_by_region(path):
    rows_by_region = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["region"] = int(row["region"])
            row["rank"] = int(row["rank"])
            row["knowledge_index"] = int(row["knowledge_index"])
            row["similarity"] = float(row["similarity"])
            rows_by_region[row["region"]].append(row)

    for rows in rows_by_region.values():
        rows.sort(key=lambda row: row["rank"])
    return dict(rows_by_region)


def write_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "region",
                "baseline_top1",
                "candidate_top1",
                "top1_match",
                "topk_overlap",
                "topk_jaccard",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Compare two retrieval CSV files.")
    parser.add_argument("--baseline_csv", required=True, help="Original/BiGen-style retrieval CSV.")
    parser.add_argument("--candidate_csv", required=True, help="New retrieval CSV to compare.")
    parser.add_argument("--out_csv", default=None, help="Optional per-region comparison CSV.")
    return parser.parse_args()


def main():
    args = parse_args()
    baseline = load_by_region(args.baseline_csv)
    candidate = load_by_region(args.candidate_csv)
    regions = sorted(set(baseline) & set(candidate))

    if not regions:
        raise ValueError("No shared regions found between the two CSV files.")

    comparison_rows = []
    top1_matches = 0
    overlap_sum = 0
    jaccard_sum = 0.0

    for region in regions:
        base_indices = [row["knowledge_index"] for row in baseline[region]]
        cand_indices = [row["knowledge_index"] for row in candidate[region]]
        base_set = set(base_indices)
        cand_set = set(cand_indices)
        overlap = len(base_set & cand_set)
        union = len(base_set | cand_set)
        jaccard = overlap / union if union else 0.0
        top1_match = base_indices[0] == cand_indices[0]

        top1_matches += int(top1_match)
        overlap_sum += overlap
        jaccard_sum += jaccard
        comparison_rows.append(
            {
                "region": region,
                "baseline_top1": base_indices[0],
                "candidate_top1": cand_indices[0],
                "top1_match": int(top1_match),
                "topk_overlap": overlap,
                "topk_jaccard": f"{jaccard:.6f}",
            }
        )

    base_all = [row["knowledge_index"] for rows in baseline.values() for row in rows]
    cand_all = [row["knowledge_index"] for rows in candidate.values() for row in rows]
    base_unique = set(base_all)
    cand_unique = set(cand_all)
    global_overlap = len(base_unique & cand_unique)
    global_union = len(base_unique | cand_unique)
    global_jaccard = global_overlap / global_union if global_union else 0.0

    print(f"Shared regions: {len(regions)}")
    print(f"Top-1 match rate: {top1_matches / len(regions):.4f}")
    print(f"Mean top-k overlap count: {overlap_sum / len(regions):.4f}")
    print(f"Mean top-k Jaccard: {jaccard_sum / len(regions):.4f}")
    print(f"Global unique knowledge Jaccard: {global_jaccard:.4f}")
    print()
    print("Baseline most common:")
    for idx, count in Counter(base_all).most_common(5):
        print(f"  {idx}: {count}")
    print("Candidate most common:")
    for idx, count in Counter(cand_all).most_common(5):
        print(f"  {idx}: {count}")

    if args.out_csv:
        write_csv(comparison_rows, args.out_csv)
        print()
        print(f"Saved comparison CSV: {args.out_csv}")


if __name__ == "__main__":
    main()
