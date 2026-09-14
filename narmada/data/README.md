# Narmada Basin — Utilizable Flow Dataset

This folder is the **single source of truth** for the year-by-year Utilizable
Flow Statement. Once data lives here, it can be modelled and monitored without
any external connection (NotebookLM, Drive, etc.).

## File: `utilizable_flow_statement.csv`

One row per water year (June–May). Columns:

| Column | Meaning |
|---|---|
| `water_year` | e.g. `1994-95` |
| `assessment_date` | Date up to which utilisation is counted (usually 1 November) |
| `util_major_MCM` | Utilisation by **major** schemes up to assessment date |
| `util_medium_MCM` | Utilisation by **medium** schemes up to assessment date |
| `util_minor_MCM` | Utilisation by **minor** schemes up to assessment date |
| `util_total_MCM` | Sum of major + medium + minor |
| `ssp_rbph_outflow_MCM` | Outflow from SSP **River Bed Power House** |
| `ssp_spillage_MCM` | Outflow from SSP **spillway** |
| `ssp_canal_head_MCM` | Outflow at SSP canal head (if tracked separately) |
| `ssp_outflow_total_MCM` | Total SSP outflow (RBPH + spillage + canal head) |
| `live_storage_1nov_MCM` | Live storage in reservoirs on assessment date (if used) |
| `utilizable_flow_total_MCM` | **Total assessed utilizable flow** for the year |
| `remarks` | Notes, source reference, any caveats |

**Units:** template uses MCM (million cubic metres). If the source statements
use MAF / TMC / Mm³, tell me and I will relabel/convert consistently.

## How the gap gets filled
1. Data is exported/pasted from the source (NotebookLM notebook
   `F_Sardar_sarovar_reservoir_regulation_committee`).
2. It is structured into `utilizable_flow_statement.csv` here.
3. Model + monitoring page are built off this file only.
