"""
Data Acquisition and Ingestion
Extracts AI note-taking apps and reviews from Google Play Store
"""
import json
from google_play_scraper import app, Sort, reviews, search
from datetime import datetime
import time

def get_ai_note_apps():
    """Search for AI note-taking applications"""
    print("Searching for AI note-taking apps...")
    
    # Search terms for AI note-taking apps
    search_terms = ["AI note", "AI notes", "note taking AI", "smart notes"]
    app_ids = set()
    
    for term in search_terms:
        try:
            results = search(term, n_hits=20)
            for result in results:
                app_ids.add(result['appId'])
        except Exception as e:
            print(f"Error searching for '{term}': {e}")
            continue
    
    return list(app_ids)

def extract_app_metadata(app_id):
    """Extract metadata for a single app"""
    try:
        result = app(app_id, lang='en', country='us')
        return {
            'appId': result.get('appId'),
            'title': result.get('title'),
            'developer': result.get('developer'),
            'score': result.get('score'),
            'ratings': result.get('ratings'),
            'installs': result.get('installs'),
            'genre': result.get('genre'),
            'price': result.get('price'),
            'description': result.get('description'),
            'updated': str(result.get('updated')) if result.get('updated') else None,
            'version': result.get('version')
        }
    except Exception as e:
        print(f"Error extracting metadata for {app_id}: {e}")
        return None

def convert_datetime_to_string(obj):
    """Convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_datetime_to_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    return obj

def extract_app_reviews(app_id, count=50):
    """Extract reviews for a single app"""
    try:
        print(f"Extracting reviews for {app_id}...")
        
        result, _ = reviews(
            app_id,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=count
        )
        
        # Convert datetime objects to strings
        clean_reviews = []
        for review in result:
            clean_review = convert_datetime_to_string(review)
            clean_reviews.append(clean_review)
        
        return clean_reviews
        
    except Exception as e:
        print(f"Error extracting reviews for {app_id}: {e}")
        return []

def main():
    # Step 1: Get list of AI note-taking apps
    app_ids = get_ai_note_apps()
    print(f"Processing {len(app_ids)} apps")
    
    # Step 2: Extract metadata for each app
    apps_metadata = []
    for app_id in app_ids:
        print(f"Extracting metadata for {app_id}...")
        metadata = extract_app_metadata(app_id)
        if metadata:
            apps_metadata.append(metadata)
        time.sleep(0.5)  # Rate limiting
    
    # Step 3: Save apps metadata
    with open('data/raw/apps_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(apps_metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(apps_metadata)} apps to apps_catalog.json")
    
    # Step 4: Extract reviews for each app
    all_reviews = []
    for app_id in app_ids:
        reviews_list = extract_app_reviews(app_id, count=50)
        for review in reviews_list:
            review['app_id'] = app_id
            all_reviews.append(review)
        time.sleep(1)  # Rate limiting
    
    # Step 5: Save reviews
    with open('data/raw/apps_reviews.jsonl', 'w', encoding='utf-8') as f:
        for review in all_reviews:
            f.write(json.dumps(review, ensure_ascii=False) + '\n')
    print(f"Saved {len(all_reviews)} reviews to apps_reviews.jsonl")
    
    print(f"\nIngestion complete!")
    print(f"Apps: {len(apps_metadata)}")
    print(f"Reviews: {len(all_reviews)}")

if __name__ == "__main__":
    main()