"""
Serving Layer
Creates analytics-ready aggregated datasets
"""
import pandas as pd

def create_app_level_kpis():
    """Create app-level aggregated metrics"""
    print("Creating app-level KPIs...")
    
    # Load clean data
    reviews = pd.read_csv('data/processed/apps_reviews.csv')
    reviews['at'] = pd.to_datetime(reviews['at'])
    
    # Calculate metrics per app
    app_kpis = reviews.groupby('app_id').agg({
        'reviewId': 'count',  # Number of reviews
        'score': 'mean',  # Average rating
        'at': ['min', 'max']  # First and last review dates
    }).reset_index()
    
    # Flatten column names
    app_kpis.columns = ['app_id', 'num_reviews', 'avg_rating', 'first_review_date', 'last_review_date']
    
    # Calculate % of low ratings (score <= 2)
    low_ratings = reviews[reviews['score'] <= 2].groupby('app_id').size().reset_index(name='low_rating_count')
    app_kpis = app_kpis.merge(low_ratings, on='app_id', how='left')
    app_kpis['low_rating_count'] = app_kpis['low_rating_count'].fillna(0)
    app_kpis['pct_low_ratings'] = (app_kpis['low_rating_count'] / app_kpis['num_reviews'] * 100).round(2)
    
    # Add app names
    apps = pd.read_csv('data/processed/apps_catalog.csv')
    app_kpis = app_kpis.merge(apps[['appId', 'title']], left_on='app_id', right_on='appId', how='left')
    
    # Select final columns
    app_kpis = app_kpis[[
        'app_id', 'title', 'num_reviews', 'avg_rating', 
        'pct_low_ratings', 'first_review_date', 'last_review_date'
    ]]
    
    # Round average rating
    app_kpis['avg_rating'] = app_kpis['avg_rating'].round(2)
    
    app_kpis.to_csv('data/processed/app_level_kpis.csv', index=False)
    print(f"Saved app-level KPIs: {len(app_kpis)} apps")
    
    return app_kpis

def create_daily_metrics():
    """Create daily time series metrics"""
    print("Creating daily metrics...")
    
    # Load clean data
    reviews = pd.read_csv('data/processed/apps_reviews.csv')
    reviews['at'] = pd.to_datetime(reviews['at'])
    reviews['date'] = reviews['at'].dt.date
    
    # Calculate daily metrics
    daily_metrics = reviews.groupby('date').agg({
        'reviewId': 'count',  # Daily number of reviews
        'score': 'mean'  # Daily average rating
    }).reset_index()
    
    daily_metrics.columns = ['date', 'daily_review_count', 'daily_avg_rating']
    daily_metrics['daily_avg_rating'] = daily_metrics['daily_avg_rating'].round(2)
    
    # Sort by date
    daily_metrics = daily_metrics.sort_values('date')
    
    daily_metrics.to_csv('data/processed/daily_metrics.csv', index=False)
    print(f"Saved daily metrics: {len(daily_metrics)} days")
    
    return daily_metrics

def main():
    # Create serving layer outputs
    app_kpis = create_app_level_kpis()
    daily_metrics = create_daily_metrics()
    
    print("\nServing layer complete!")
    print(f"App-level KPIs: data/processed/app_level_kpis.csv")
    print(f"Daily metrics: data/processed/daily_metrics.csv")
    
    # Display sample data
    print("\n--- Sample App KPIs ---")
    print(app_kpis.head())
    print("\n--- Sample Daily Metrics ---")
    print(daily_metrics.head())

if __name__ == "__main__":
    main()
