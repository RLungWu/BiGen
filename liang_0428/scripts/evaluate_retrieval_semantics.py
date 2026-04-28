import argparse
import csv
import os
import re
from collections import Counter, defaultdict


CATEGORIES = {
    "tumor_type_ductal": {
        "positive": [r"\bductal\b", r"\binfiltrating ductal\b", r"\binvasive ductal\b"],
        "conflict": [r"\blobular\b"],
    },
    "tumor_type_lobular": {
        "positive": [r"\blobular\b"],
        "conflict": [r"\bductal\b"],
    },
    "grade_ii": {
        "positive": [r"\bgrade ii\b", r"\bgrade 2\b", r"\bnottingham grade ii\b", r"\bnottingham grade 2\b"],
        "conflict": [r"\bgrade iii\b", r"\bgrade 3\b", r"\bgrade i\b", r"\bgrade 1\b"],
    },
    "dcis": {
        "positive": [r"\bdcis\b", r"\bductal carcinoma in situ\b", r"\bcarcinoma in situ\b"],
        "conflict": [],
    },
    "no_angiolymphatic_invasion": {
        "positive": [
            r"\bno angiolymphatic invasion\b",
            r"\bangiolymphatic invasion is (not|absent)\b",
            r"\blymphovascular invasion is (not|absent)\b",
            r"\bno lymphovascular invasion\b",
        ],
        "conflict": [r"\bangiolymphatic invasion\b", r"\blymphovascular invasion\b", r"\bvascular invasion\b"],
    },
    "negative_margins": {
        "positive": [
            r"\bmargins? (are )?negative\b",
            r"\bnegative (for tumor )?margins?\b",
            r"\bmargin-free\b",
            r"\btumou?r-free margin\b",
        ],
        "conflict": [r"\bpositive margin\b", r"\binvolved margin\b", r"\bmargin involvement\b"],
    },
    "negative_lymph_nodes": {
        "positive": [
            r"\blymph nodes? (are )?negative\b",
            r"\bnegative for metastatic carcinoma\b",
            r"\bnegative for metastasis\b",
            r"\bno lymph node metastasis\b",
            r"\bno nodal metastasis\b",
        ],
        "conflict": [
            r"\blymph node metast",
            r"\bnodal metast",
            r"\bmetastatic carcinoma (in|involving|to|within)\b",
            r"\bextranodal extension\b",
            r"\bextracapsular extension\b",
            r"\bpositive lymph nodes?\b",
        ],
    },
    "right_side": {
        "positive": [r"\bright\b", r"\bright-sided\b"],
        "conflict": [r"\bleft\b"],
    },
}


GROUND_TRUTH_EXPECTED = {
    "tumor_type_ductal",
    "grade_ii",
    "dcis",
    "no_angiolymphatic_invasion",
    "negative_margins",
    "negative_lymph_nodes",
    "right_side",
}


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def has_any(patterns, text):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def classify_text(text):
    normalized = normalize(text)
    matched = []
    conflicts = []
    for category, patterns in CATEGORIES.items():
        has_positive = has_any(patterns["positive"], normalized)
        has_conflict = has_any(patterns["conflict"], normalized)
        if has_positive:
            matched.append(category)
        if has_conflict and not (
            has_positive
            and category
            in {"negative_lymph_nodes", "negative_margins", "no_angiolymphatic_invasion"}
        ):
            conflicts.append(category)
    return matched, conflicts


def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text


def load_retrieval(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["region"] = int(row["region"])
            row["rank"] = int(row["rank"])
            row["knowledge_index"] = int(row["knowledge_index"])
            row["similarity"] = float(row["similarity"])
            rows.append(row)
    return rows


def summarize_unique(rows):
    by_index = {}
    counts = Counter()
    similarities = defaultdict(list)
    for row in rows:
        idx = row["knowledge_index"]
        by_index[idx] = row["text"]
        counts[idx] += 1
        similarities[idx].append(row["similarity"])

    unique_rows = []
    for idx, text in by_index.items():
        matched, conflicts = classify_text(text)
        unique_rows.append(
            {
                "knowledge_index": idx,
                "count": counts[idx],
                "mean_similarity": sum(similarities[idx]) / len(similarities[idx]),
                "max_similarity": max(similarities[idx]),
                "matched_gt_categories": ";".join(
                    category for category in matched if category in GROUND_TRUTH_EXPECTED
                ),
                "conflicting_categories": ";".join(
                    category for category in conflicts if category in GROUND_TRUTH_EXPECTED
                ),
                "other_matched_categories": ";".join(
                    category for category in matched if category not in GROUND_TRUTH_EXPECTED
                ),
                "text": text,
            }
        )
    unique_rows.sort(key=lambda row: (-row["count"], -row["max_similarity"]))
    return unique_rows


def write_unique_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fieldnames = [
        "knowledge_index",
        "count",
        "mean_similarity",
        "max_similarity",
        "matched_gt_categories",
        "conflicting_categories",
        "other_matched_categories",
        "text",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            formatted = dict(row)
            formatted["mean_similarity"] = f"{row['mean_similarity']:.6f}"
            formatted["max_similarity"] = f"{row['max_similarity']:.6f}"
            writer.writerow(formatted)


def write_report(ground_truth, gt_matches, unique_rows, path, top_n):
    category_hits = Counter()
    category_conflicts = Counter()
    weighted_hits = Counter()
    weighted_conflicts = Counter()

    for row in unique_rows:
        for category in row["matched_gt_categories"].split(";"):
            if category:
                category_hits[category] += 1
                weighted_hits[category] += row["count"]
        for category in row["conflicting_categories"].split(";"):
            if category:
                category_conflicts[category] += 1
                weighted_conflicts[category] += row["count"]

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Semantic Retrieval Evaluation\n\n")
        f.write("## Ground Truth\n\n")
        f.write(ground_truth.strip())
        f.write("\n\n## Ground Truth Concepts Detected\n\n")
        for category in sorted(GROUND_TRUTH_EXPECTED):
            status = "yes" if category in gt_matches else "no"
            f.write(f"- `{category}`: {status}\n")

        f.write("\n## Retrieved Knowledge Concept Coverage\n\n")
        f.write("| concept | unique matching texts | retrieval occurrences | unique conflicting texts | conflicting occurrences |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for category in sorted(GROUND_TRUTH_EXPECTED):
            f.write(
                f"| `{category}` | {category_hits[category]} | {weighted_hits[category]} | "
                f"{category_conflicts[category]} | {weighted_conflicts[category]} |\n"
            )

        f.write("\n## Top Retrieved Knowledge With Labels\n\n")
        for row in unique_rows[:top_n]:
            f.write(
                f"- index `{row['knowledge_index']}` | count `{row['count']}` | "
                f"mean sim `{row['mean_similarity']:.6f}` | max sim `{row['max_similarity']:.6f}`\n"
            )
            f.write(f"  - matched GT: `{row['matched_gt_categories'] or 'none'}`\n")
            f.write(f"  - conflicts: `{row['conflicting_categories'] or 'none'}`\n")
            f.write(f"  - text: {row['text']}\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Keyword-based semantic check between ground truth and retrieved knowledge."
    )
    parser.add_argument("--retrieval_csv", required=True)
    parser.add_argument("--ground_truth", required=True)
    parser.add_argument("--out_csv", required=True)
    parser.add_argument("--out_md", required=True)
    parser.add_argument("--top_n", type=int, default=20)
    return parser.parse_args()


def main():
    args = parse_args()
    ground_truth = load_ground_truth(args.ground_truth)
    rows = load_retrieval(args.retrieval_csv)
    gt_matches, _ = classify_text(ground_truth)
    unique_rows = summarize_unique(rows)
    write_unique_csv(unique_rows, args.out_csv)
    write_report(ground_truth, set(gt_matches), unique_rows, args.out_md, args.top_n)

    matched_rows = sum(1 for row in unique_rows if row["matched_gt_categories"])
    conflict_rows = sum(1 for row in unique_rows if row["conflicting_categories"])
    print(f"Retrieved rows: {len(rows)}")
    print(f"Unique retrieved knowledge: {len(unique_rows)}")
    print(f"Unique knowledge with at least one GT concept match: {matched_rows}")
    print(f"Unique knowledge with at least one conflict signal: {conflict_rows}")
    print(f"Saved CSV: {args.out_csv}")
    print(f"Saved report: {args.out_md}")


if __name__ == "__main__":
    main()
