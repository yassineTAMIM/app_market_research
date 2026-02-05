"""
Data Transformation
Converts raw JSON/JSONL data into clean, structured CSV files
"""
import json
import pandas as pd
from datetime import datetime
import re

def load_raw_data():
    """Load raw JSON and JSONL files"""
    print("Loading raw data...")
    
    # Load apps catalog
    with open('data/raw/apps_catalog.json', 'r', encoding='utf-8') as f:
        apps_data = json.load(f)
    
    # Load reviews
    reviews_data = []
    with open('data/raw/apps_reviews.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            reviews_data.append(json.loads(line))
    
    return apps_data, reviews_data

def clean_installs(installs_str):
    """Convert install string to numeric value"""
    if pd.isna(installs_str) or installs_str is None:
        return 0
    
    # Remove '+' and ',' and convert to int
    try:
        cleaned = str(installs_str).replace('+', '').replace(',', '')
        return int(cleaned)
    except:
        return 0

def clean_price(price_value):
    """Convert price to numeric value"""
    if pd.isna(price_value) or price_value is None:
        return 0.0
    
    if price_value == 0:
        return 0.0
    
    # If it's a string, remove currency symbols
    try:
        if isinstance(price_value, str):
            cleaned = re.sub(r'[^\d.]', '', price_value)
            return float(cleaned) if cleaned else 0.0
        return float(price_value)
    except:
        return 0.0

def transform_apps(apps_data):
    """
    Transform apps catalog data
    Issues identified:
    1. Nested structures that need flattening
    2. Inconsistent data types (installs as string)
    3. Missing values in optional fields
    4. Price with currency symbols
    5. Genre can be list or string
    """
    print("Transforming apps catalog...")
    
    df = pd.DataFrame(apps_data)
    
    # Select and rename columns
    df_clean = pd.DataFrame({
        'appId': df['appId'],
        'title': df['title'],
        'developer': df['developer'],
        'score': pd.to_numeric(df['score'], errors='coerce'),
        'ratings': pd.to_numeric(df['ratings'], errors='coerce'),
        'installs': df['installs'].apply(clean_installs),
        'genre': df['genre'].apply(lambda x: x if isinstance(x, str) else str(x)),
        'price': df['price'].apply(clean_price)
    })
    
    # Handle missing values
    df_clean['score'] = df_clean['score'].fillna(0.0)
    df_clean['ratings'] = df_clean['ratings'].fillna(0)
    df_clean['developer'] = df_clean['developer'].fillna('Unknown')
    df_clean['genre'] = df_clean['genre'].fillna('Unknown')
    
    # Remove duplicates based on appId
    df_clean = df_clean.drop_duplicates(subset=['appId'], keep='first')
    
    print(f"Transformed {len(df_clean)} apps")
    return df_clean

def parse_review_date(date_obj):
    """Parse review date to ISO format"""
    try:
        if isinstance(date_obj, str):
            return pd.to_datetime(date_obj).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(date_obj, dict) and '$date' in date_obj:
            timestamp = date_obj['$date']
            return pd.to_datetime(timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
        else:
            return pd.to_datetime(date_obj).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def transform_reviews(reviews_data, apps_df):
    """
    Transform reviews data
    Issues identified:
    1. Nested 'at' timestamp structure
    2. Missing or null values in content
    3. Inconsistent score types
    4. ReviewId might be missing
    5. Need to join with apps for app_name
    """
    print("Transforming reviews...")
    
    df = pd.DataFrame(reviews_data)
    
    # Create mapping from appId to title
    app_name_map = dict(zip(apps_df['appId'], apps_df['title']))
    
    # Transform to required structure
    df_clean = pd.DataFrame({
        'app_id': df['app_id'],
        'app_name': df['app_id'].map(app_name_map).fillna('Unknown'),
        'reviewId': df['reviewId'],
        'userName': df['userName'].fillna('Anonymous'),
        'score': pd.to_numeric(df['score'], errors='coerce'),
        'content': df['content'].fillna(''),
        'thumbsUpCount': pd.to_numeric(df['thumbsUpCount'], errors='coerce'),
        'at': df['at'].apply(parse_review_date)
    })
    
    # Handle missing values
    df_clean['score'] = df_clean['score'].fillna(0)
    df_clean['thumbsUpCount'] = df_clean['thumbsUpCount'].fillna(0)
    
    # Remove reviews without valid dates
    df_clean = df_clean[df_clean['at'].notna()]
    
    # Remove duplicate reviews
    df_clean = df_clean.drop_duplicates(subset=['reviewId'], keep='first')
    
    # Ensure score is between 1 and 5
    df_clean = df_clean[(df_clean['score'] >= 1) & (df_clean['score'] <= 5)]
    
    print(f"Transformed {len(df_clean)} reviews")
    return df_clean

def main():
    # Load raw data
    apps_data, reviews_data = load_raw_data()
    
    # Transform apps
    apps_clean = transform_apps(apps_data)
    apps_clean.to_csv('data/processed/apps_catalog.csv', index=False)
    print(f"Saved clean apps catalog: {len(apps_clean)} rows")
    
    # Transform reviews
    reviews_clean = transform_reviews(reviews_data, apps_clean)
    reviews_clean.to_csv('data/processed/apps_reviews.csv', index=False)
    print(f"Saved clean reviews: {len(reviews_clean)} rows")
    
    print("\nTransformation complete!")
    print(f"Apps: data/processed/apps_catalog.csv")
    print(f"Reviews: data/processed/apps_reviews.csv")

if __name__ == "__main__":
    main()
