"""
scripts/load_to_duckdb.py
─────────────────────────
Reads your ALREADY-EXISTING processed CSVs from data/processed/
and loads them into DuckDB so dbt can use them as source tables.

Run this ONCE (and again whenever you have a new batch of data).

Usage (from repo root):
    python scripts/load_to_duckdb.py

For an incremental batch (new reviews CSV):
    python scripts/load_to_duckdb.py --new-reviews data/raw/batch2.jsonl
"""

import duckdb
import pandas as pd
import json
import os
import sys
import argparse
from datetime import datetime

DB_PATH = "data/app_market.duckdb"


def get_con():
    os.makedirs("data", exist_ok=True)
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    return con


def load_apps(con):
    """Load data/processed/apps_catalog.csv → raw.apps_catalog"""
    path = "data/processed/apps_catalog.csv"
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return

    df = pd.read_csv(path)
    df["_loaded_at"] = datetime.utcnow().isoformat()
    df["_source_file"] = "apps_catalog.csv"

    con.execute("DROP TABLE IF EXISTS raw.apps_catalog")
    con.register("_apps", df)
    con.execute("CREATE TABLE raw.apps_catalog AS SELECT * FROM _apps")
    print(f"  [OK] raw.apps_catalog — {len(df)} rows")


def load_reviews(con, extra_file=None):
    """
    Load data/processed/apps_reviews.csv → raw.apps_reviews
    If extra_file is given (new batch), APPEND it without replacing existing data.
    """
    path = "data/processed/apps_reviews.csv"
    if not os.path.exists(path):
        print(f"  [SKIP] {path} not found")
        return

    # ── Initial load ──────────────────────────────────────────────────────────
    table_exists = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='raw' AND table_name='apps_reviews'"
    ).fetchone()[0]

    if not table_exists:
        df = pd.read_csv(path)
        df["_loaded_at"] = datetime.utcnow().isoformat()
        df["_source_file"] = "apps_reviews.csv"
        con.register("_reviews", df)
        con.execute("CREATE TABLE raw.apps_reviews AS SELECT * FROM _reviews")
        print(f"  [OK] raw.apps_reviews created — {len(df)} rows")
    else:
        # Check if already loaded
        already = con.execute(
            "SELECT COUNT(*) FROM raw.apps_reviews WHERE _source_file='apps_reviews.csv'"
        ).fetchone()[0]
        if already:
            print(f"  [SKIP] apps_reviews.csv already loaded ({already} rows present)")
        else:
            df = pd.read_csv(path)
            df["_loaded_at"] = datetime.utcnow().isoformat()
            df["_source_file"] = "apps_reviews.csv"
            con.register("_reviews", df)
            con.execute("INSERT INTO raw.apps_reviews SELECT * FROM _reviews")
            print(f"  [OK] raw.apps_reviews appended — {len(df)} rows")

    # ── Incremental batch ─────────────────────────────────────────────────────
    if extra_file:
        if not os.path.exists(extra_file):
            print(f"  [ERROR] batch file not found: {extra_file}")
            return

        fname = os.path.basename(extra_file)

        # Guard: don't load the same file twice
        already = con.execute(
            "SELECT COUNT(*) FROM raw.apps_reviews WHERE _source_file=?", [fname]
        ).fetchone()[0]
        if already:
            print(f"  [SKIP] {fname} already loaded ({already} rows present)")
            return

        # Read JSONL or CSV
        if extra_file.endswith(".jsonl"):
            records = [json.loads(l) for l in open(extra_file, encoding="utf-8") if l.strip()]
            df = pd.DataFrame(records)
        else:
            df = pd.read_csv(extra_file)

        # Normalize column names to match the base table
        ALIASES = {
            "reviewId": ["review_id", "id"],
            "score":    ["rating", "stars"],
            "content":  ["review_text", "text", "body"],
            "thumbsUpCount": ["thumbs_up_count", "helpful"],
            "at":       ["review_date", "created_at", "date"],
            "userName": ["user_name", "author"],
            "app_id":   ["appId", "application_id"],
        }
        for canonical, aliases in ALIASES.items():
            for alias in aliases:
                if alias in df.columns and canonical not in df.columns:
                    df = df.rename(columns={alias: canonical})
                    print(f"    schema drift: renamed '{alias}' → '{canonical}'")

        df["_loaded_at"] = datetime.utcnow().isoformat()
        df["_source_file"] = fname

        # Add missing columns as NULL so INSERT doesn't fail
        existing_cols = [
            r[0] for r in con.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='raw' AND table_name='apps_reviews'"
            ).fetchall()
        ]
        for col in existing_cols:
            if col not in df.columns:
                df[col] = None

        con.register("_batch", df)
        con.execute("INSERT INTO raw.apps_reviews SELECT * FROM _batch")
        print(f"  [OK] Batch appended — {len(df)} rows from {fname}")


def print_summary(con):
    apps = con.execute("SELECT COUNT(*) FROM raw.apps_catalog").fetchone()[0]
    reviews = con.execute("SELECT COUNT(*) FROM raw.apps_reviews").fetchone()[0]
    batches = con.execute(
        "SELECT _source_file, COUNT(*) as n FROM raw.apps_reviews GROUP BY 1"
    ).fetchall()
    print(f"\n  raw.apps_catalog  : {apps} rows")
    print(f"  raw.apps_reviews  : {reviews} rows total")
    for fname, n in batches:
        print(f"    └─ {fname}: {n}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-reviews", help="Path to a new batch file (CSV or JSONL) to append")
    args = parser.parse_args()

    # Must run from repo root
    if not os.path.exists("data/processed"):
        print("ERROR: Run this script from the repo root (where data/ lives)")
        sys.exit(1)

    print("Loading data into DuckDB...")
    con = get_con()
    load_apps(con)
    load_reviews(con, extra_file=args.new_reviews)
    print_summary(con)
    con.close()
    print(f"\nDone. Database: {DB_PATH}")


if __name__ == "__main__":
    main()