import argparse
import csv
import os
from collections import Counter, defaultdict


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


def top_by_frequency(rows, limit):
    counts = Counter(row["knowledge_index"] for row in rows)
    similarities = defaultdict(list)
    texts = {}
    for row in rows:
        idx = row["knowledge_index"]
        similarities[idx].append(row["similarity"])
        texts[idx] = row["text"]

    output = []
    for idx, count in counts.most_common(limit):
        sims = similarities[idx]
        output.append(
            {
                "knowledge_index": idx,
                "count": count,
                "mean_similarity": sum(sims) / len(sims),
                "max_similarity": max(sims),
                "text": texts[idx],
            }
        )
    return output


def top_by_similarity(rows, limit):
    best = {}
    for row in rows:
        idx = row["knowledge_index"]
        if idx not in best or row["similarity"] > best[idx]["max_similarity"]:
            best[idx] = {
                "knowledge_index": idx,
                "count": 0,
                "mean_similarity": 0.0,
                "max_similarity": row["similarity"],
                "text": row["text"],
            }

    counts = Counter(row["knowledge_index"] for row in rows)
    similarities = defaultdict(list)
    for row in rows:
        similarities[row["knowledge_index"]].append(row["similarity"])

    for idx, item in best.items():
        sims = similarities[idx]
        item["count"] = counts[idx]
        item["mean_similarity"] = sum(sims) / len(sims)

    return sorted(best.values(), key=lambda item: item["max_similarity"], reverse=True)[:limit]


def write_markdown(ground_truth, frequent, similar, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Retrieval vs Ground Truth\n\n")
        f.write("## Ground Truth Report\n\n")
        f.write(ground_truth)
        f.write("\n\n## Most Frequently Retrieved Knowledge\n\n")
        for item in frequent:
            f.write(
                f"- index `{item['knowledge_index']}` | count `{item['count']}` | "
                f"mean sim `{item['mean_similarity']:.6f}` | max sim `{item['max_similarity']:.6f}`\n"
            )
            f.write(f"  {item['text']}\n")
        f.write("\n## Highest Similarity Retrieved Knowledge\n\n")
        for item in similar:
            f.write(
                f"- index `{item['knowledge_index']}` | count `{item['count']}` | "
                f"mean sim `{item['mean_similarity']:.6f}` | max sim `{item['max_similarity']:.6f}`\n"
            )
            f.write(f"  {item['text']}\n")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize retrieved historical knowledge beside one ground truth report."
    )
    parser.add_argument("--retrieval_csv", required=True)
    parser.add_argument("--ground_truth", required=True)
    parser.add_argument("--top_n", type=int, default=15)
    parser.add_argument("--out_md", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    ground_truth = load_ground_truth(args.ground_truth)
    rows = load_retrieval(args.retrieval_csv)
    frequent = top_by_frequency(rows, args.top_n)
    similar = top_by_similarity(rows, args.top_n)
    write_markdown(ground_truth, frequent, similar, args.out_md)

    print(f"Retrieval rows: {len(rows)}")
    print(f"Unique knowledge indices: {len(set(row['knowledge_index'] for row in rows))}")
    print(f"Saved summary: {args.out_md}")


if __name__ == "__main__":
    main()
