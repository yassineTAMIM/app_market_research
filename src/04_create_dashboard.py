"""
Dashboard - Consumer View
Creates visually stunning market intelligence dashboard
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import numpy as np

def load_data():
    """Load processed data"""
    app_kpis = pd.read_csv('data/processed/app_level_kpis.csv')
    daily_metrics = pd.read_csv('data/processed/daily_metrics.csv')
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    return app_kpis, daily_metrics

def create_dashboard():
    """Create a visually stunning dashboard"""
    print("Creating dashboard...")
    
    # Load data
    app_kpis, daily_metrics = load_data()
    reviews = pd.read_csv('data/processed/apps_reviews.csv')
    reviews['at'] = pd.to_datetime(reviews['at'])
    
    # Define modern color palette
    colors = {
        'primary': '#1f77b4',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#3498db',
        'purple': '#9b59b6',
        'teal': '#1abc9c',
        'dark': '#2c3e50'
    }
    
    # Create figure with custom spacing
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            '🎯 Sweet Spot Analysis', 
            '📊 Market Share by Reviews', 
            '⭐ Sentiment Distribution',
            '🏆 Top Performers', 
            '⚠️ Apps in Danger Zone', 
            '📈 Rating Evolution',
            '🚀 Market Growth Trajectory', 
            '💹 Recent Momentum', 
            '🔮 Trend Forecast'
        ),
        specs=[
            [{'type': 'scatter'}, {'type': 'pie'}, {'type': 'bar'}],
            [{'type': 'bar'}, {'type': 'bar'}, {'type': 'scatter'}],
            [{'type': 'scatter'}, {'type': 'indicator'}, {'type': 'scatter'}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.10,
        row_heights=[0.33, 0.33, 0.33]
    )
    
    # 1. SWEET SPOT: Quality vs Popularity (bubble chart)
    credible_apps = app_kpis[app_kpis['num_reviews'] >= 10]
    fig.add_trace(
        go.Scatter(
            x=credible_apps['num_reviews'],
            y=credible_apps['avg_rating'],
            mode='markers+text',
            text=credible_apps['title'].apply(lambda x: x.split(':')[0][:12]),
            textposition='top center',
            textfont=dict(size=9, color='white'),
            marker=dict(
                size=credible_apps['num_reviews']*1.2,
                color=credible_apps['pct_low_ratings'],
                colorscale=[[0, colors['success']], [0.5, colors['warning']], [1, colors['danger']]],
                showscale=True,
                colorbar=dict(title="Low %", x=0.31, len=0.3, y=0.85),
                line=dict(width=2, color='white'),
                opacity=0.9
            ),
            name='Apps',
            hovertemplate='<b>%{text}</b><br>Reviews: %{x}<br>Rating: %{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add quadrant lines
    median_reviews = credible_apps['num_reviews'].median()
    median_rating = 4.0
    fig.add_hline(y=median_rating, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    fig.add_vline(x=median_reviews, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
    
    # 2. MARKET SHARE PIE
    top_10_apps = app_kpis.nlargest(10, 'num_reviews')
    fig.add_trace(
        go.Pie(
            labels=top_10_apps['title'].apply(lambda x: x.split(':')[0][:15]),
            values=top_10_apps['num_reviews'],
            hole=0.4,
            marker=dict(
                colors=[colors['primary'], colors['info'], colors['teal'], colors['success'], 
                       colors['warning'], colors['danger'], colors['purple'], '#95a5a6', '#34495e', '#7f8c8d']
            ),
            textposition='inside',
            textfont=dict(size=10, color='white'),
            hovertemplate='<b>%{label}</b><br>Reviews: %{value}<br>Share: %{percent}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. SENTIMENT DISTRIBUTION (vertical bars)
    rating_counts = reviews['score'].value_counts().sort_index()
    sentiment_colors = [colors['danger'], colors['warning'], '#95a5a6', colors['success'], colors['success']]
    fig.add_trace(
        go.Bar(
            x=rating_counts.index,
            y=rating_counts.values,
            marker=dict(
                color=sentiment_colors,
                line=dict(color='white', width=2)
            ),
            text=rating_counts.values,
            textposition='outside',
            textfont=dict(size=14, color=colors['dark']),
            name='Reviews',
            hovertemplate='<b>%{x} ⭐</b><br>Count: %{y}<extra></extra>'
        ),
        row=1, col=3
    )
    
    # 4. TOP PERFORMERS (gradient bar)
    top_5 = app_kpis[app_kpis['num_reviews'] >= 20].nlargest(5, 'avg_rating').sort_values('avg_rating')
    fig.add_trace(
        go.Bar(
            y=top_5['title'].apply(lambda x: x.split(':')[0][:20]),
            x=top_5['avg_rating'],
            orientation='h',
            marker=dict(
                color=top_5['avg_rating'],
                colorscale=[[0, colors['warning']], [1, colors['success']]],
                line=dict(color='white', width=2)
            ),
            text=top_5['avg_rating'].apply(lambda x: f'{x:.2f}⭐'),
            textposition='inside',
            textfont=dict(size=12, color='white'),
            name='Rating',
            hovertemplate='<b>%{y}</b><br>Rating: %{x:.2f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 5. DANGER ZONE (red bars)
    danger_apps = app_kpis[app_kpis['num_reviews'] >= 10].nlargest(5, 'pct_low_ratings').sort_values('pct_low_ratings')
    fig.add_trace(
        go.Bar(
            y=danger_apps['title'].apply(lambda x: x.split(':')[0][:20]),
            x=danger_apps['pct_low_ratings'],
            orientation='h',
            marker=dict(
                color=colors['danger'],
                line=dict(color='white', width=2)
            ),
            text=danger_apps['pct_low_ratings'].apply(lambda x: f'{x:.1f}%'),
            textposition='inside',
            textfont=dict(size=12, color='white'),
            name='Low %',
            hovertemplate='<b>%{y}</b><br>Negative: %{x:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # 6. RATING EVOLUTION (last 180 days with smooth)
    recent_180 = daily_metrics.tail(180)
    fig.add_trace(
        go.Scatter(
            x=recent_180['date'],
            y=recent_180['daily_avg_rating'],
            mode='lines',
            line=dict(color=colors['info'], width=1, shape='spline'),
            fill='tozeroy',
            fillcolor=f'rgba(52, 152, 219, 0.2)',
            name='Rating',
            hovertemplate='%{x|%b %d}<br>Rating: %{y:.2f}<extra></extra>'
        ),
        row=2, col=3
    )
    
    # 7. MARKET GROWTH (area chart with MA)
    fig.add_trace(
        go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['daily_review_count'],
            mode='lines',
            line=dict(color=colors['teal'], width=1),
            fill='tozeroy',
            fillcolor=f'rgba(26, 188, 156, 0.3)',
            name='Daily',
            hovertemplate='%{x|%Y-%m-%d}<br>Reviews: %{y}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # Add 30-day MA
    daily_metrics['ma_30'] = daily_metrics['daily_review_count'].rolling(window=30, min_periods=1).mean()
    fig.add_trace(
        go.Scatter(
            x=daily_metrics['date'],
            y=daily_metrics['ma_30'],
            mode='lines',
            line=dict(color=colors['purple'], width=3),
            name='30-day MA',
            hovertemplate='%{x|%Y-%m-%d}<br>MA: %{y:.1f}<extra></extra>'
        ),
        row=3, col=1
    )
    
    # 8. MOMENTUM INDICATOR
    recent_30 = daily_metrics.tail(30)['daily_review_count'].mean()
    previous_30 = daily_metrics.tail(60).head(30)['daily_review_count'].mean()
    momentum = ((recent_30 - previous_30) / previous_30 * 100) if previous_30 > 0 else 0
    
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=recent_30,
            delta={'reference': previous_30, 'relative': True, 'valueformat': '.1%'},
            title={'text': "Daily Reviews<br>(30-day avg)", 'font': {'size': 14}},
            number={'font': {'size': 40}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ),
        row=3, col=2
    )
    
    # 9. TREND FORECAST (last 90 days with prediction)
    recent_90 = daily_metrics.tail(90).copy()
    recent_90_clean = recent_90.dropna(subset=['daily_avg_rating'])
    
    if len(recent_90_clean) > 10:
        # Actual data
        fig.add_trace(
            go.Scatter(
                x=recent_90_clean['date'],
                y=recent_90_clean['daily_avg_rating'],
                mode='markers',
                marker=dict(size=6, color=colors['purple'], line=dict(width=1, color='white')),
                name='Actual',
                hovertemplate='%{x|%b %d}<br>Rating: %{y:.2f}<extra></extra>'
            ),
            row=3, col=3
        )
        
        # Trend line
        x_numeric = np.arange(len(recent_90_clean))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, recent_90_clean['daily_avg_rating'])
        trend_line = slope * x_numeric + intercept
        
        fig.add_trace(
            go.Scatter(
                x=recent_90_clean['date'],
                y=trend_line,
                mode='lines',
                line=dict(color=colors['danger'], width=3, dash='dash'),
                name='Trend',
                hovertemplate='Trend: %{y:.2f}<extra></extra>'
            ),
            row=3, col=3
        )
    
    # LAYOUT STYLING
    fig.update_layout(
        height=1400,
        showlegend=False,
        title={
            'text': "🤖 AI Note-Taking Apps: Market Intelligence Dashboard<br><sub>Real-time Competitive Analysis & Market Insights</sub>",
            'font': {'size': 28, 'color': colors['dark'], 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        template='plotly_white',
        paper_bgcolor='#f8f9fa',
        plot_bgcolor='white',
        font=dict(family='Arial', size=11, color=colors['dark'])
    )
    
    # Update all subplot backgrounds
    for i in range(1, 10):
        row = (i-1)//3 + 1
        col = (i-1)%3 + 1
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#ecf0f1', row=row, col=col)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ecf0f1', row=row, col=col)
    
    # Specific axis updates
    fig.update_xaxes(title_text="Reviews", row=1, col=1)
    fig.update_yaxes(title_text="Avg Rating ⭐", range=[0, 5.5], row=1, col=1)
    
    fig.update_xaxes(title_text="Stars", row=1, col=3)
    fig.update_yaxes(title_text="Count", row=1, col=3)
    
    fig.update_xaxes(title_text="Rating", row=2, col=1)
    fig.update_xaxes(title_text="Negative %", row=2, col=2)
    fig.update_yaxes(title_text="", row=2, col=1)
    fig.update_yaxes(title_text="", row=2, col=2)
    
    fig.update_xaxes(title_text="Date", row=2, col=3)
    fig.update_yaxes(title_text="Rating", range=[1, 5], row=2, col=3)
    
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Reviews/Day", row=3, col=1)
    
    fig.update_xaxes(title_text="Date", row=3, col=3)
    fig.update_yaxes(title_text="Rating", range=[2, 5], row=3, col=3)
    
    # Save
    fig.write_html('data/processed/dashboard.html')
    print("✅ Dashboard saved to: data/processed/dashboard.html")
    
    # INSIGHTS
    print("\n" + "="*70)
    print("📊 MARKET INTELLIGENCE REPORT")
    print("="*70)
    
    print(f"\n📈 OVERVIEW")
    print(f"   Apps: {len(app_kpis)} | Reviews: {app_kpis['num_reviews'].sum():,} | Avg Rating: {app_kpis['avg_rating'].mean():.2f}⭐")
    
    sweet_spot = app_kpis[(app_kpis['num_reviews'] >= 20) & (app_kpis['avg_rating'] >= 4.2)]
    if len(sweet_spot) > 0:
        print(f"\n🎯 WINNERS ({len(sweet_spot)} apps):")
        for _, row in sweet_spot.nlargest(3, 'avg_rating').iterrows():
            print(f"   • {row['title'].split(':')[0][:30]}: {row['avg_rating']:.2f}⭐")
    
    struggling = app_kpis[(app_kpis['pct_low_ratings'] > 40) & (app_kpis['num_reviews'] >= 10)]
    if len(struggling) > 0:
        print(f"\n⚠️  AT RISK ({len(struggling)} apps):")
        for _, row in struggling.nlargest(2, 'pct_low_ratings').iterrows():
            print(f"   • {row['title'].split(':')[0][:30]}: {row['pct_low_ratings']:.0f}% negative")
    
    print(f"\n📊 MOMENTUM: {momentum:+.1f}% (last 30d vs previous 30d)")
    
    if len(recent_90_clean) > 10:
        trend = "📈 UP" if slope > 0 else "📉 DOWN"
        print(f"🔮 TREND: {trend} ({slope*1000:.2f} pts/day, R²={r_value**2:.2f})")
    
    print("\n" + "="*70)

def main():
    create_dashboard()
    print("\n🎨 Open dashboard.html in your browser for full interactive experience")

if __name__ == "__main__":
    main()