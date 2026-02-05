# Lab 1: Python-only Data Pipeline

This project implements an end-to-end data pipeline for analyzing AI note-taking mobile apps from Google Play Store.

## Project Structure

```
App Market Research/
├── data/
│   ├── raw/              # Raw data from Google Play Store
│   └── processed/        # Cleaned and aggregated data
├── src/
│   ├── 01_ingest_data.py         # Data acquisition from Play Store
│   ├── 02_transform_data.py      # Data cleaning and transformation
│   ├── 03_create_serving_layer.py # Analytics aggregations
│   └── 04_create_dashboard.py    # Visualization dashboard
├── requirements.txt      # Python dependencies
├── run_pipeline.py      # Main pipeline runner
└── README.md           # This file
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Using conda (recommended)
conda create -n dataApps python=3.10
conda activate dataApps

# OR using venv
python -m venv dataApps
source dataApps/bin/activate  # On Windows: dataApps\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `google-play-scraper`: Extract data from Google Play Store
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations

### 3. Verify Setup

Check that you're in the correct virtual environment:
```bash
python --version  # Should show Python 3.7+
pip list          # Should show installed packages
```

## Running the Pipeline

### Option 1: Run Complete Pipeline

Execute all steps in sequence:

```bash
python run_pipeline.py
```

### Option 2: Run Individual Steps

Run each step separately:

```bash
# Step 1: Data Ingestion (takes 5-10 minutes)
python src/01_ingest_data.py

# Step 2: Data Transformation
python src/02_transform_data.py

# Step 3: Serving Layer
python src/03_create_serving_layer.py

# Step 4: Dashboard
python src/04_create_dashboard.py
```

## Pipeline Stages

### Stage 1: Data Ingestion
- Searches Google Play Store for AI note-taking apps
- Extracts app metadata (title, developer, ratings, etc.)
- Extracts user reviews (50 reviews per app)
- Saves raw data as JSON/JSONL in `data/raw/`

**Output:**
- `data/raw/apps_catalog.json` - App metadata
- `data/raw/apps_reviews.jsonl` - User reviews

### Stage 2: Data Transformation
Addresses 5+ data quality issues:
1. **Nested structures** - Flattens JSON hierarchies
2. **Inconsistent data types** - Converts installs to integers
3. **Missing values** - Fills with appropriate defaults
4. **Price formatting** - Removes currency symbols
5. **Date parsing** - Standardizes timestamp formats

**Output:**
- `data/processed/apps_catalog.csv` - Clean app data
- `data/processed/apps_reviews.csv` - Clean review data

### Stage 3: Serving Layer
Creates analytics-ready aggregations:

**App-Level KPIs** (`app_level_kpis.csv`):
- Number of reviews
- Average rating
- % of low ratings (≤2 stars)
- First and last review dates

**Daily Metrics** (`daily_metrics.csv`):
- Daily review count
- Daily average rating

### Stage 4: Dashboard
Creates interactive HTML dashboard with:
- Top 10 apps by rating
- Top 10 apps by review volume
- Daily review volume trends
- Daily rating trends

**Output:**
- `data/processed/dashboard.html` - Open in browser to view

## Expected Outputs

After running the complete pipeline, you should have:

```
data/
├── raw/
│   ├── apps_catalog.json      # ~10-20 apps
│   └── apps_reviews.jsonl     # ~500-1000 reviews
└── processed/
    ├── apps_catalog.csv       # Clean app data
    ├── apps_reviews.csv       # Clean reviews
    ├── app_level_kpis.csv     # App aggregations
    ├── daily_metrics.csv      # Time series data
    └── dashboard.html         # Interactive dashboard
```

## Viewing Results

1. **Dashboard**: Open `data/processed/dashboard.html` in your browser
2. **CSV Files**: Open with Excel, Google Sheets, or any text editor
3. **Summary Statistics**: Printed to console after each step

## Dashboard Insights

The dashboard answers these questions:
- **Which apps perform best?** Top 10 by average rating
- **Which apps have most engagement?** Top 10 by review volume
- **Are ratings improving?** Daily rating trend over time
- **Is review volume stable?** Daily review count trend

## Troubleshooting

### Rate Limiting Errors
If you see rate limiting errors from Google Play Store:
- The script includes delays (0.5-1 second between requests)
- Reduce the number of apps/reviews in `01_ingest_data.py`
- Wait a few minutes and try again

### No Data Found
If the scraper finds no apps:
- Check your internet connection
- The search terms may need adjustment
- Google Play Store structure may have changed

### Import Errors
Make sure you're in the project root directory when running scripts:
```bash
cd "App Market Research"
python run_pipeline.py
```

## Data Quality Issues Addressed

The transformation script handles:

1. **Missing values**: Filled with appropriate defaults (0, "Unknown", etc.)
2. **Data type inconsistencies**: Converts strings to numbers where needed
3. **Nested structures**: Flattens complex JSON objects
4. **Invalid ratings**: Filters scores outside 1-5 range
5. **Duplicate records**: Removes duplicates based on IDs
6. **Date formatting**: Standardizes all timestamps to ISO format
7. **Price formatting**: Removes currency symbols and converts to float
8. **Install counts**: Converts "1,000+" format to integers

## Notes

- **First run takes longer**: Data ingestion from Google Play Store takes 5-10 minutes
- **Limited to 10 apps**: To speed up development; increase in `01_ingest_data.py` line 78
- **50 reviews per app**: Increase the `count` parameter for more reviews
- **Reproducible**: Re-running the pipeline generates fresh data

## Next Steps (Not Implemented in This Lab)

The lab document mentions stress testing scenarios:
- New data batches
- Schema drift handling
- Dirty data handling
- Updated metadata
- Sentiment analysis logic

These are intentionally not implemented to demonstrate pipeline fragility and set up for future labs using proper data engineering tools.

## Questions or Issues?

If the pipeline fails:
1. Check that you're in the correct virtual environment
2. Verify all dependencies are installed
3. Ensure you're running from the project root directory
4. Check error messages for specific issues
5. Try running individual steps to isolate problems

## Summary

This pipeline demonstrates:
✓ Data acquisition from external APIs
✓ Handling semi-structured data (JSON/JSONL)
✓ Data quality issues and transformations
✓ Creating analytics-ready aggregations
✓ Building a consumer-facing dashboard
✓ Pain points of handcrafted pipelines
