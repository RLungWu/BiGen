# Liang 0428 Retrieval Demo

## Current Result

本次實踐完成了一個 isolated retrieval sanity check：給定單張 WSI 的 PLIP feature `TCGA-3C-AALI.pt`，我們成功從 historical knowledge bank 中 retrieve 出對應的 historical report texts。初步結果顯示，retrieved texts 有抓到 breast cancer、lymph node、Nottingham grade、DCIS 等大方向語意，但 case-specific precision 不穩定，例如 ground truth 是 infiltrating ductal carcinoma 且 sentinel lymph nodes negative，retrieval 卻常出現 lobular carcinoma、lymph node metastasis、extracapsular extension 等不一致內容。

因此，目前結果比較適合被解讀為：PLIP feature 與 historical knowledge bank 在 embedding space 中具有粗略病理相關性，但這還不是完整 BiGen model 的 retrieval behavior，也不能直接等同於論文中的完整 knowledge retrieval module。

## What We Did

目前完成的流程如下：

1. 準備一張 WSI 的 PLIP feature：

   ```text
   liang_0428/data/test_data/TCGA-3C-AALI.pt
   ```

2. 使用 historical knowledge bank：

   ```text
   liang_0428/data/memory_bank/memory_short.pt
   liang_0428/data/memory_bank/short_brca.json
   ```

3. 執行 original/BiGen-style retrieval core：

   ```bash
   bash liang_0428/scripts/run_demo.sh
   ```

   這會產生：

   ```text
   liang_0428/results/retrieval/TCGA-3C-AALI_original_retrieval.csv
   liang_0428/results/features/TCGA-3C-AALI_original_retrieved_features.pt
   ```

4. 加入 ground truth report：

   ```text
   liang_0428/data/ground_truth/TCGA-3C-AALI.txt
   ```

5. 將 retrieved knowledge 與 ground truth 放在一起檢視：

   ```bash
   python liang_0428/scripts/summarize_retrieval_with_ground_truth.py \
     --retrieval_csv liang_0428/results/retrieval/TCGA-3C-AALI_original_retrieval.csv \
     --ground_truth liang_0428/data/ground_truth/TCGA-3C-AALI.txt \
     --top_n 15 \
     --out_md liang_0428/results/evaluation/TCGA-3C-AALI_retrieval_vs_ground_truth.md
   ```

6. 做 rule-based semantic evaluation：

   ```bash
   python liang_0428/scripts/evaluate_retrieval_semantics.py \
     --retrieval_csv liang_0428/results/retrieval/TCGA-3C-AALI_original_retrieval.csv \
     --ground_truth liang_0428/data/ground_truth/TCGA-3C-AALI.txt \
     --out_csv liang_0428/results/evaluation/TCGA-3C-AALI_semantic_eval.csv \
     --out_md liang_0428/results/evaluation/TCGA-3C-AALI_semantic_eval.md
   ```

## Project Structure

```text
liang_0428/
  README.md
  data/
    ground_truth/
      TCGA-3C-AALI.txt
    memory_bank/
      memory_short.pt
      short_brca.json
    test_data/
      TCGA-3C-AALI.pt
  results/
    evaluation/
      TCGA-3C-AALI_retrieval_vs_ground_truth.md
      TCGA-3C-AALI_semantic_eval.csv
      TCGA-3C-AALI_semantic_eval.md
    features/
      TCGA-3C-AALI_original_retrieved_features.pt
    retrieval/
      TCGA-3C-AALI_original_retrieval.csv
      TCGA-3C-AALI_retrieval_legacy.csv
  scripts/
    demo_retrieval.py
    summarize_retrieval_with_ground_truth.py
    evaluate_retrieval_semantics.py
    compare_retrieval_csv.py
    run_demo.sh
    run_compare.sh
```

## File Roles

```text
scripts/demo_retrieval.py
```

執行 retrieval 的主腳本。它會讀入 PLIP feature、knowledge bank embedding、knowledge text JSON，然後輸出每個 WSI region retrieve 到的 top-k historical knowledge。

```text
scripts/summarize_retrieval_with_ground_truth.py
```

把 ground truth report 和 retrieved texts 整理成可讀的 Markdown，方便人工檢查語意是否相關。

```text
scripts/evaluate_retrieval_semantics.py
```

用 keyword/rule-based 方法檢查 retrieved texts 是否命中 ground truth concepts，例如 ductal carcinoma、grade II、DCIS、negative margins、negative lymph nodes 等。

```text
scripts/compare_retrieval_csv.py
```

用來比較兩份 retrieval CSV，例如未來如果有 original retrieval 和 weighted retrieval，可以比較 top-1 match、top-k overlap、Jaccard similarity。

## Current Interpretation

目前這份 demo 不是完整重現論文中的 BiGen inference。它比較準確的定位是：

```text
Isolated PLIP-to-knowledge retrieval analysis
```

也就是單獨檢查：

```text
一張 WSI 的 PLIP patch features 在 historical knowledge bank 中會 retrieve 到哪些 texts。
```

論文中的完整方法還包含 trained model encoder、attention-based patch sorting、top-v selection、UNI/PLIP feature fusion，以及 knowledge feature 回注入 report generation model。這些部分目前沒有完整執行。

## Next Steps

1. 先把目前結果整理成 qualitative observation。

   可以描述為：

   ```text
   The isolated retrieval retrieves broadly pathology-related historical knowledge, but it often mismatches important case-specific attributes such as tumor subtype and lymph node status.
   ```

2. 增加更多 WSI cases。

   目前只有 `TCGA-3C-AALI` 一張 WSI。下一步應該多放幾張 PLIP `.pt` 和對應 ground truth reports，檢查這個現象是不是穩定存在。

3. 將 semantic evaluation 做成 case-level summary。

   對每張 WSI 統計：

   ```text
   matched concepts
   conflicting concepts
   most frequent retrieved knowledge
   highest similarity retrieved knowledge
   ```

4. 若未來取得 trained BiGen checkpoint 和 attention/sorted patch outputs，再做 full-model retrieval analysis。

   這樣才能更接近論文原本流程，而不是只做 isolated retrieval。

## Problems And Bugs

1. 這不是完整 BiGen retrieval module。

   目前沒有 trained model 的 attention scores、sorted indices、top-v selected patches，因此無法完全重現論文中的 retrieval behavior。

2. Weighted top-k retrieval 暫時不適合公平比較。

   如果沒有 trained model 的 learned attention 或其他中間輸出，weighted top-k 只能做 heuristic similarity weighting。這可以實作，但不能宣稱是論文原本方法。

3. Rule-based semantic evaluation 只是粗略檢查。

   `evaluate_retrieval_semantics.py` 依賴 keyword patterns，因此可能有 false positives 或 false negatives。例如一句話同時出現 `negative` 和 `metastatic carcinoma` 時，需要小心判斷它到底是在說 lymph nodes negative 還是 metastasis positive。

4. Retrieval 結果存在明顯 case-specific mismatch。

   目前 `TCGA-3C-AALI` ground truth 是 ductal carcinoma、lymph nodes negative，但 frequently retrieved knowledge 中多次出現 lobular carcinoma、lymph node metastasis、extracapsular extension。這是目前最重要的觀察，也是後續需要處理的問題。

5. 環境問題。

   此 workspace 的 default `python` 可能沒有 PyTorch，但使用者本機/指定環境有 PyTorch 和 CUDA。因此實際 retrieval 建議在正確 conda environment 中執行，並使用：

   ```bash
   --device cuda
   ```
