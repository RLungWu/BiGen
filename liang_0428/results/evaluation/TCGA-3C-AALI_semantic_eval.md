# Semantic Retrieval Evaluation

## Ground Truth

The pathological report shows that a right-sided local excision was performed for a mass measuring 1.3 x 1.3 x 1.2 cm. The mass was diagnosed as infiltrating ductal carcinoma, Nottingham grade II (out of III). There is also ductal carcinoma in situ, comprising less than 5% of the tumor volume. No angiolymphatic invasion is present. Biopsy site changes were observed. All surgical resection margins are negative for tumor, with a minimum tumor-free margin of 0.7 cm at the inferior margin. 

In addition, the report states that multiple right axillary sentinel lymph nodes were examined and found to be negative for metastatic carcinoma. Lymph node No. 1 showed the presence of blue dye, while lymph node No. 2 did not. An immunohistochemical stain confirmed the initial impression. Faxitron imaging was done and showed no abnormalities.

## Ground Truth Concepts Detected

- `dcis`: yes
- `grade_ii`: yes
- `negative_lymph_nodes`: yes
- `negative_margins`: yes
- `no_angiolymphatic_invasion`: yes
- `right_side`: yes
- `tumor_type_ductal`: yes

## Retrieved Knowledge Concept Coverage

| concept | unique matching texts | retrieval occurrences | unique conflicting texts | conflicting occurrences |
|---|---:|---:|---:|---:|
| `dcis` | 6 | 47 | 0 | 0 |
| `grade_ii` | 5 | 86 | 5 | 354 |
| `negative_lymph_nodes` | 2 | 64 | 6 | 426 |
| `negative_margins` | 1 | 3 | 0 | 0 |
| `no_angiolymphatic_invasion` | 1 | 13 | 3 | 51 |
| `right_side` | 12 | 79 | 14 | 187 |
| `tumor_type_ductal` | 7 | 47 | 15 | 495 |

## Top Retrieved Knowledge With Labels

- index `6352` | count `314` | mean sim `0.311876` | max sim `0.330063`
  - matched GT: `none`
  - conflicts: `tumor_type_ductal;grade_ii`
  - text: The invasive lobular carcinoma measures 3.8 cm and is classified as grade I-L.
- index `7876` | count `131` | mean sim `0.302608` | max sim `0.314044`
  - matched GT: `none`
  - conflicts: `negative_lymph_nodes`
  - text: The lymph node metastases show extensive extracapsular extension and architectural replacement.
- index `7292` | count `119` | mean sim `0.302119` | max sim `0.317635`
  - matched GT: `none`
  - conflicts: `negative_lymph_nodes`
  - text: - Metastatic Carcinoma in 20 out of 24 lymph nodes with extranodal extension.
- index `5108` | count `94` | mean sim `0.306335` | max sim `0.330053`
  - matched GT: `none`
  - conflicts: `negative_lymph_nodes`
  - text: - Metastatic carcinoma involving two of twelve lymph nodes (2/12).
- index `6702` | count `63` | mean sim `0.300417` | max sim `0.309641`
  - matched GT: `grade_ii`
  - conflicts: `tumor_type_ductal;right_side`
  - text: - Invasive lobular carcinoma, Nottingham grade 2, in the left breast.
- index `1449` | count `61` | mean sim `0.303931` | max sim `0.317066`
  - matched GT: `negative_lymph_nodes`
  - conflicts: `none`
  - text: Twenty-six lymph nodes are negative for metastatic carcinoma.
- index `4909` | count `49` | mean sim `0.298715` | max sim `0.311905`
  - matched GT: `none`
  - conflicts: `none`
  - text: The remaining breast tissue shows lipomatous atrophy.
- index `2455` | count `45` | mean sim `0.306984` | max sim `0.327828`
  - matched GT: `none`
  - conflicts: `none`
  - text: This portion of adipose tissue contains 20 lymph nodes ranging in size from 0.2 to 3.5 cm.
- index `6206` | count `39` | mean sim `0.301884` | max sim `0.310048`
  - matched GT: `none`
  - conflicts: `negative_lymph_nodes`
  - text: The largest metastatic focus measures 1 cm with extracapsular extension.
- index `637` | count `38` | mean sim `0.300250` | max sim `0.307092`
  - matched GT: `none`
  - conflicts: `no_angiolymphatic_invasion;negative_lymph_nodes`
  - text: The report also provides information on various factors such as tumor type, Nottingham Grade, angiolymphatic invasion, surgical margins involvement, lymph node metastasis, and TNM stage.
- index `7653` | count `33` | mean sim `0.300028` | max sim `0.306126`
  - matched GT: `none`
  - conflicts: `none`
  - text: - Distant metastasis: Present.
- index `2040` | count `32` | mean sim `0.303618` | max sim `0.314595`
  - matched GT: `none`
  - conflicts: `none`
  - text: Additional specimens submitted include fragments of adipose tissue, skin, and skin tag.
- index `2362` | count `32` | mean sim `0.294806` | max sim `0.302469`
  - matched GT: `none`
  - conflicts: `none`
  - text: - Fibrosis.
- index `7681` | count `28` | mean sim `0.296710` | max sim `0.305187`
  - matched GT: `right_side`
  - conflicts: `tumor_type_ductal`
  - text: 8. Invasive lobular carcinoma found in the lower outer quadrant of the right breast with a size of 1.5 cm in the largest dimension.
- index `7654` | count `22` | mean sim `0.293255` | max sim `0.303458`
  - matched GT: `right_side`
  - conflicts: `right_side`
  - text: - Residual tumor dimension: 6 cm in the right breast and 5 cm in the left breast.
- index `1954` | count `21` | mean sim `0.300744` | max sim `0.307541`
  - matched GT: `none`
  - conflicts: `none`
  - text: - Multifocal fat necrosis.
- index `5349` | count `19` | mean sim `0.293215` | max sim `0.298543`
  - matched GT: `none`
  - conflicts: `none`
  - text: - Sarcomatous: Positive.
- index `7288` | count `19` | mean sim `0.293154` | max sim `0.298257`
  - matched GT: `none`
  - conflicts: `tumor_type_ductal;grade_ii`
  - text: - Invasive Lobular Carcinoma, Nottingham grade 3, measuring 3.3 cm in size and involving the nipple dermis.
- index `3892` | count `17` | mean sim `0.292622` | max sim `0.300641`
  - matched GT: `none`
  - conflicts: `right_side`
  - text: - The re-excision of the posterior margin of the left breast shows skeletal muscle and fibroadipose tissue, with no carcinoma identified.
- index `3749` | count `17` | mean sim `0.289513` | max sim `0.298933`
  - matched GT: `none`
  - conflicts: `none`
  - text: [name redacted].
