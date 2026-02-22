# 🤖 AI Note-Taking Apps — Market Intelligence Pipeline

![Python](https://img.shields.io/badge/Python-3.13.2-blue?logo=python&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-1.11.6-FF694B?logo=dbt&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-0.9.2-FCD034?logo=duckdb&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-5.18.0-3F4F75?logo=plotly&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

End-to-end data pipeline that scrapes Google Play Store reviews for AI note-taking apps, transforms them into an analytics-ready star schema, and serves insights via an interactive dashboard.

---

## 📐 Architecture

```
Google Play API
      │
      ▼
01_ingest_data.py          ← Raw scraping (42 apps, 1,436 reviews)
      │
      ▼
02_transform_data.py       ← Cleaning, type casting, deduplication
      │
      ▼
load_to_duckdb.py          ← Idempotent loader into DuckDB raw schema
      │
      ▼
dbt build                  ← Star schema: staging → dimensions → fact
      │
      ▼
app_market.duckdb          ← Serving layer (Power BI / Metabase / DuckDB CLI)
```

---

## 📦 Stack

| Layer | Tool | Version |
|-------|------|---------|
| Scraping | `google-play-scraper` | 1.2.7 |
| Transformation | `pandas` | 2.2.0 |
| Analytics DB | `DuckDB` | 0.9.2 |
| Data Modeling | `dbt-core` + `dbt-duckdb` | 1.7.4 / 1.7.2 |
| Dashboard | `Plotly` | 5.18.0 |

---

## 🗂️ Project Structure

```
App_Market_Research/
├── src/
│   ├── 01_ingest_data.py            # Google Play scraper
│   ├── 02_transform_data.py         # Pandas cleaning pipeline
│   ├── 03_create_serving_layer.py   # KPI aggregations
│   └── 04_create_dashboard.py       # Plotly HTML dashboard
│
├── dbt/
│   ├── models/
│   │   ├── staging/                 # stg_apps, stg_reviews (views)
│   │   └── marts/                   # dim_*, fact_reviews (tables)
│   ├── snapshots/                   # SCD2 on developer names
│   └── tests/                       # 3 custom data quality tests
│
├── scripts/
│   └── load_to_duckdb.py            # CSV → DuckDB raw schema
│
├── data/
│   ├── raw/                         # Immutable scraped files
│   ├── processed/                   # Lab 1 clean CSVs
│   └── app_market.duckdb            # DuckDB analytical database
│
└── requirements.txt
```

---

## ⭐ Star Schema

```
                    dim_date
                       │
dim_categories ── dim_apps ── fact_reviews ── dim_developers (SCD2)
```

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| `fact_reviews` | Incremental | 1,436 | One row per review — rating, thumbs_up, FKs |
| `dim_apps` | Table | 42 | App metadata with surrogate key |
| `dim_developers` | Table (SCD2) | 42+ | Developer history via dbt snapshot |
| `dim_categories` | Table | ~10 | App genres |
| `dim_date` | Table | 3,287 | Date spine 2019–2027, YYYYMMDD key |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
conda activate dataApps
pip install -r requirements.txt
```

### 2. Run Lab 1 pipeline
```bash
python run_pipeline.py
```

### 3. Load into DuckDB
```bash
python scripts/load_to_duckdb.py
```

### 4. Run dbt pipeline
```bash
cd dbt
dbt snapshot --profiles-dir .    # SCD2 first
dbt build --profiles-dir .       # Build all models + run 37 tests
```

### 5. Verify
```bash
duckdb ../data/app_market.duckdb
SELECT COUNT(*) FROM fact_reviews;   -- 1436
```

---

## ✅ Data Quality

37 automated tests — **0 failures**.

| Test | Type | What it catches |
|------|------|-----------------|
| `not_null` / `unique` on all PKs & FKs | Generic | Missing or duplicate keys |
| `accepted_values` on booleans | Generic | Data type corruption |
| FK relationships (6 pairs) | Relationships | Referential integrity violations |
| `assert_no_orphan_reviews` | Custom SQL | Reviews linked to unknown apps |
| `assert_rating_distribution_sane` | Custom SQL | >95% same rating (scraping anomaly) |
| `assert_no_data_loss` | Custom SQL | Ghost rows from deleted upstream batches |

---

## 📊 Key Findings

| Category | App | Rating | Signal |
|----------|-----|--------|--------|
| 🏆 Top Performer | Smart Note — Notes | 4.68 ★ | Highest rated |
| 🏆 Top Performer | Samsung Notes | 4.66 ★ | Established leader |
| ⚠️ Danger Zone | OtterAI Transcribe | 2.48 ★ | 64% negative reviews |
| ⚠️ Danger Zone | Smart Notebook | 2.51 ★ | 61.5% negative reviews |

> 📈 Market growth: **+592%** review volume spike in late 2025 (24.23 reviews/day).  
> 📉 Rating trend: declining from 5.0 → ~3.5 — expectations outpacing product quality.

---

## 🔄 Adding a New Review Batch

```bash
# 1. Append new batch
python scripts/load_to_duckdb.py --new-reviews data/raw/batch2.jsonl

# 2. Rebuild (only processes new rows)
cd dbt && dbt build --profiles-dir .
```

The incremental model processes only rows where `_loaded_at > MAX(_loaded_at)` in the existing table.

---

## 📁 Data Lineage

```
raw.apps_catalog ──► stg_apps ──► dim_categories
                  │            ├─► dim_developers (via scd2_developers snapshot)
                  │            └─► dim_apps
                  │                    │
raw.apps_reviews ──► stg_reviews ──► fact_reviews ──► assert_no_orphan_reviews
                                   │               ├─► assert_rating_distribution_sane
                                   │               └─► assert_no_data_loss
                    dim_date ──────┘
```

---

*Lab 1 & Lab 2 — Data Engineering | Centrale Casablanca | February 2026*