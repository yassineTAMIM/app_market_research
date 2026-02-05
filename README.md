# Lab 1 Report: Python Data Pipeline
**Student:** Yassine TAMIM | **Date:** February 2026

---

## Part A: Environment Setup 

Created virtual environment with Python 3.10 and installed:
- `google-play-scraper` (API access)
- `pandas` (data manipulation)  
- `plotly` (visualization)
- `scipy` (statistical analysis)

**Time spent:** 30 minutes (mostly fighting with package compatibility issues)

---

## Part B: End-to-End Pipeline

### 1. Data Ingestion

**Approach:** Used `google-play-scraper` library to extract app metadata and reviews from Google Play Store.

**Challenges:**
- Initial `reviews_all()` function had a bug (kept failing with "'int' object has no attribute 'value'")
- Had to switch to standard `reviews()` function
- DateTime serialization issues required custom converter
- Rate limiting forced 1-second delays between requests

**Results:** 
- 42 apps extracted
- 1,436 reviews collected
- Date range: April 2019 - February 2026

**Key Learning:** Real-world APIs are messy. Even popular libraries have bugs.

---

### 2. Data Transformation

**Before coding, I inspected raw files and found 5+ issues:**

1. **Nested timestamps** - some as strings, some as objects, some as Python datetime
2. **Install counts as strings** - "1,000,000+" instead of integers
3. **Missing values everywhere** - nulls in developer names, content, ratings
4. **Price formatting** - "$4.99" with currency symbols
5. **Inconsistent data types** - genre sometimes string, sometimes list

**Transformation Strategy:**
```python
# Standardize dates
def parse_review_date(date_obj):
    # Handle all 3 formats: string, dict, datetime
    return pd.to_datetime(...).strftime('%Y-%m-%d %H:%M:%S')

# Clean numeric fields
def clean_installs(val):
    return int(str(val).replace('+', '').replace(',', ''))
```

**Results:**
- Apps: 42 → 42 clean records (no loss)
- Reviews: 1,436 → 1,436 clean records (all valid)
- Output: Two clean CSV files ready for analysis

---

### 3. Serving Layer

Created two analytics-ready datasets:

**App-Level KPIs:**
- Review count, avg rating, % low ratings (≤2★)
- First/last review dates
- 38 apps had reviews

**Daily Metrics:**
- Daily review volume and average rating
- 415 unique days tracked
- Reveals market growth patterns

**Insight:** Data is heavily skewed to 2025-2026. AI note-taking is a NEW market.

---

### 4. Dashboard

Built interactive HTML dashboard with 9 visualizations:

**Key Insights:**

🎯 **Sweet Spot Apps** (high volume + high rating):
- Plaud AI: 4.46★ with 50 reviews
- Smart Note: 4.68★ with 50 reviews  
- Samsung Notes: 4.66★ (established player holding strong)

⚠️ **Apps in Trouble:**
- OtterAI: 2.48★ avg, 64% negative reviews
- Smart Notebook: 2.51★ avg, 61% negative
- Goodnotes: 2.68★ avg, 54% negative

📊 **Market Trends:**
- Review volume spiked 500%+ in late 2025 (market explosion!)
- Rating trend: **DECLINING** (from 5.0 to 3.92 over time)
- User expectations rising or quality dropping?

**Business Takeaway:** AI note-taking is growing fast, but competition is brutal. Early movers like OtterAI are struggling. Newer, AI-native apps (Plaud, Turbo AI) are winning.

---

## Part C: Pipeline Pain Points

### What Breaks This Pipeline:

1. **No Schema Validation**
   - If Google changes API structure → silent failures
   - Example: field rename from 'score' to 'rating' breaks everything

2. **No Incremental Updates**  
   - Must re-scrape ALL data every time
   - 10-minute runtime for 1,436 reviews
   - What if we had 1 million?

3. **Hardcoded Everything**
   - App IDs in source code
   - File paths hardcoded
   - No configuration files

4. **Zero Observability**
   - No logging
   - No error tracking
   - Pipeline fails → you find out manually

5. **Can't Scale**
   - Pandas loads everything in memory
   - No parallelization
   - Single machine only

### Real Scenario Test: "What if Google changes the API tomorrow?"

My pipeline would:
1. Fail silently or produce garbage data
2. I wouldn't know until someone checks the dashboard
3. Would take hours to diagnose and fix
4. No way to roll back to last good state

**This is why we need proper data engineering tools.**

---

## Reflections

### What Worked:
- Pandas was fine for 1,436 rows (no need to overcomplicate)
- Running steps separately (ingest → transform → serve → dashboard) made debugging easier
- Dashboard immediately revealed data quality issues

### What I'd Do Differently:
1. **Schema validation upfront** (Pydantic or similar)
2. **Proper logging** (would've saved 2 hours of debugging)
3. **Config files** for app IDs and paths
4. **Unit tests** for transformation functions
5. **Design for 100x scale** from day 1

### Why This Lab Matters:
Now I viscerally understand why production pipelines need:
- Orchestration (Airflow) for scheduling/monitoring
- Data warehouses (BigQuery) for scale  
- Schema management (dbt) for transformations
- Quality frameworks (Great Expectations) for validation

