import argparse
import csv
import json
import os

import torch
import torch.nn.functional as F


def load_tensor(path):
    tensor = torch.load(path, map_location="cpu")
    if isinstance(tensor, dict):
        for key in ("features", "feature", "embeddings", "embedding"):
            if key in tensor:
                tensor = tensor[key]
                break
    tensor = torch.as_tensor(tensor).float()
    if tensor.dim() == 3 and tensor.size(0) == 1:
        tensor = tensor.squeeze(0)
    return tensor


def load_knowledge_text(path):
    if path is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def lookup_text(metadata, index):
    if metadata is None:
        return ""
    keys = [index, str(index)]
    if isinstance(metadata, list):
        if 0 <= index < len(metadata):
            value = metadata[index]
        else:
            return ""
    elif isinstance(metadata, dict):
        value = None
        for key in keys:
            if key in metadata:
                value = metadata[key]
                break
        if value is None:
            return ""
    else:
        return ""

    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "caption", "report", "sentence", "annotation"):
            if key in value:
                return str(value[key])
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def retrieve(plip_features, knowledge_bank, region_size, top_k, top_regions=None):
    if plip_features.size(-1) != knowledge_bank.size(-1):
        raise ValueError(
            "Feature dimension mismatch: "
            f"PLIP has {plip_features.size(-1)}, knowledge bank has {knowledge_bank.size(-1)}"
        )

    if top_regions is not None:
        plip_features = plip_features[:top_regions]

    n = plip_features.size(0)
    num_regions = (n + region_size - 1) // region_size
    padding = region_size * num_regions - n
    padded = F.pad(plip_features, (0, 0, 0, padding), value=0)
    groups = padded.view(num_regions, region_size, plip_features.size(-1))
    region_features = groups.mean(dim=1)

    similarities = F.cosine_similarity(
        region_features.unsqueeze(1),
        knowledge_bank.unsqueeze(0),
        dim=2,
    )
    scores, indices = similarities.topk(top_k, dim=1, largest=True, sorted=True)
    return scores, indices


def write_csv(rows, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["region", "rank", "knowledge_index", "similarity", "text"],
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inspect BiGen knowledge retrieval without a trained checkpoint."
    )
    parser.add_argument("--plip_pt", required=True, help="Path to one PLIP WSI feature .pt file.")
    parser.add_argument("--bank_pt", required=True, help="Path to knowledge_bank .pt file.")
    parser.add_argument("--bank_json", default=None, help="Optional JSON metadata for knowledge text.")
    parser.add_argument("--m", type=int, default=10, help="Region size used by BiGen retrieval.")
    parser.add_argument("--k", type=int, default=3, help="Top-k knowledge entries per region.")
    parser.add_argument(
        "--top_regions",
        type=int,
        default=None,
        help="Optional number of PLIP patches to keep before grouping. "
        "Use this to approximate BiGen's top-v selected patches when no checkpoint is available.",
    )
    parser.add_argument("--max_print_regions", type=int, default=10)
    parser.add_argument("--out_csv", default=None, help="Optional path to save retrieval results.")
    return parser.parse_args()


def main():
    args = parse_args()
    plip_features = load_tensor(args.plip_pt)
    knowledge_bank = load_tensor(args.bank_pt)
    metadata = load_knowledge_text(args.bank_json)

    scores, indices = retrieve(
        plip_features=plip_features,
        knowledge_bank=knowledge_bank,
        region_size=args.m,
        top_k=args.k,
        top_regions=args.top_regions,
    )

    print(f"PLIP feature shape: {tuple(plip_features.shape)}")
    print(f"Knowledge bank shape: {tuple(knowledge_bank.shape)}")
    print(f"Regions: {scores.size(0)}, top-k per region: {scores.size(1)}")
    print()

    rows = []
    for region in range(scores.size(0)):
        for rank in range(scores.size(1)):
            knowledge_index = int(indices[region, rank].item())
            similarity = float(scores[region, rank].item())
            text = lookup_text(metadata, knowledge_index)
            rows.append(
                {
                    "region": region,
                    "rank": rank + 1,
                    "knowledge_index": knowledge_index,
                    "similarity": f"{similarity:.6f}",
                    "text": text,
                }
            )

    for row in rows[: args.max_print_regions * args.k]:
        text = row["text"]
        if len(text) > 220:
            text = text[:217] + "..."
        print(
            f"region={row['region']:03d} rank={row['rank']} "
            f"idx={row['knowledge_index']} sim={row['similarity']} {text}"
        )

    if args.out_csv:
        write_csv(rows, args.out_csv)
        print()
        print(f"Saved CSV: {args.out_csv}")


if __name__ == "__main__":
    main()
