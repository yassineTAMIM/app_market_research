"""
Dashboard - Consumer View
Creates simple visualizations from processed data
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_data():
    """Load processed data"""
    app_kpis = pd.read_csv('data/processed/app_level_kpis.csv')
    daily_metrics = pd.read_csv('data/processed/daily_metrics.csv')
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    return app_kpis, daily_metrics

def create_dashboard():
    """Create a simple dashboard with key visualizations"""
    print("Creating dashboard...")
    
    # Load data
    app_kpis, daily_metrics = load_data()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Top 10 Apps by Average Rating',
            'Top 10 Apps by Review Volume',
            'Daily Review Volume Over Time',
            'Daily Average Rating Trend'
        ),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'scatter'}, {'type': 'scatter'}]]
    )
    
    # 1. Top apps by rating
    top_rated = app_kpis.nlargest(10, 'avg_rating').sort_values('avg_rating')
    fig.add_trace(
        go.Bar(
            x=top_rated['avg_rating'],
            y=top_rated['title'],
            orientation='h',
            marker_color='lightblue',
            name='Avg Rating'
        ),
        row=1, col=1
    )
    
    # 2. Top apps by review count
    top_reviewed = app_kpis.nlargest(10, 'num_reviews').sort_values('num_reviews')
    fig.add_trace(
        go.Bar(
            x=top_reviewed['num_reviews'],
            y=top_reviewed['title'],
            orientation='h',
            marker_color='lightgreen',
            name='Review Count'
        ),
        row=1, col=2
    )
    
    # 3. Daily review volume
    fig.add_trace(
        go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['daily_review_count'],
            mode='lines+markers',
            marker_color='orange',
            name='Daily Reviews'
        ),
        row=2, col=1
    )
    
    # 4. Daily rating trend
    fig.add_trace(
        go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['daily_avg_rating'],
            mode='lines+markers',
            marker_color='purple',
            name='Daily Avg Rating'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="AI Note-Taking Apps Dashboard",
        title_font_size=20
    )
    
    fig.update_xaxes(title_text="Average Rating", row=1, col=1)
    fig.update_xaxes(title_text="Number of Reviews", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=2)
    
    fig.update_yaxes(title_text="App", row=1, col=1)
    fig.update_yaxes(title_text="App", row=1, col=2)
    fig.update_yaxes(title_text="Review Count", row=2, col=1)
    fig.update_yaxes(title_text="Average Rating", row=2, col=2, range=[1, 5])
    
    # Save as HTML
    fig.write_html('data/processed/dashboard.html')
    print("Dashboard saved to: data/processed/dashboard.html")
    
    # Display summary statistics
    print("\n=== DASHBOARD INSIGHTS ===")
    print(f"\nTotal Apps Analyzed: {len(app_kpis)}")
    print(f"Total Reviews: {app_kpis['num_reviews'].sum()}")
    print(f"Overall Average Rating: {app_kpis['avg_rating'].mean():.2f}")
    
    print("\n--- Best Performing Apps (by rating) ---")
    print(app_kpis.nlargest(5, 'avg_rating')[['title', 'avg_rating', 'num_reviews']])
    
    print("\n--- Most Reviewed Apps ---")
    print(app_kpis.nlargest(5, 'num_reviews')[['title', 'num_reviews', 'avg_rating']])
    
    print("\n--- Apps with Highest % of Low Ratings ---")
    print(app_kpis.nlargest(5, 'pct_low_ratings')[['title', 'pct_low_ratings', 'avg_rating']])
    
    # Rating trend analysis
    if len(daily_metrics) > 1:
        first_week_avg = daily_metrics.head(7)['daily_avg_rating'].mean()
        last_week_avg = daily_metrics.tail(7)['daily_avg_rating'].mean()
        trend = "improving" if last_week_avg > first_week_avg else "declining"
        print(f"\n--- Rating Trend ---")
        print(f"First week average: {first_week_avg:.2f}")
        print(f"Last week average: {last_week_avg:.2f}")
        print(f"Overall trend: {trend}")

def main():
    create_dashboard()
    print("\nOpen 'data/processed/dashboard.html' in your browser to view the dashboard")

if __name__ == "__main__":
    main()
