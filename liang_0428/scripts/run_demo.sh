python liang_0428/scripts/demo_retrieval.py \
  --plip_pt liang_0428/data/test_data/TCGA-3C-AALI.pt \
  --bank_pt liang_0428/data/memory_bank/memory_short.pt \
  --bank_json liang_0428/data/memory_bank/short_brca.json \
  --device cuda \
  --m 10 \
  --k 3 \
  --out_csv liang_0428/results/retrieval/TCGA-3C-AALI_original_retrieval.csv \
  --out_features_pt liang_0428/results/features/TCGA-3C-AALI_original_retrieved_features.pt
