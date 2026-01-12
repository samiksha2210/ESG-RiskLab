import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class ESGVisualizations:
    """Create professional visualizations for ESG analysis"""
    
    @staticmethod
    def create_risk_quadrant(companies_data: pd.DataFrame):
        """
        Create the famous quadrant matrix:
        X-axis: Stock Performance, Y-axis: Greenwashing Risk
        """
        fig = go.Figure()
        
        # Generate sample stock returns if not present
        if 'stock_return' not in companies_data.columns:
            companies_data['stock_return'] = np.random.uniform(-0.2, 0.3, len(companies_data))
        
        # Color by risk level
        color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        companies_data['color'] = companies_data['risk_level'].map(color_map)
        
        # Create scatter plot
        fig.add_trace(go.Scatter(
            x=companies_data['stock_return'],
            y=companies_data['greenwashing_score'],
            mode='markers+text',
            marker=dict(size=15, color=companies_data['color'], line=dict(color='white', width=2)),
            text=companies_data['ticker'],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Stock Return: %{x:.1%}<br>Risk Score: %{y:.2f}<br><extra></extra>'
        ))
        
        # Add quadrant lines
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        annotations = [
            dict(x=0.15, y=0.8, text="Lying Leaders", showarrow=False, font=dict(size=12, color='red')),
            dict(x=0.15, y=0.2, text="Honest Leaders", showarrow=False, font=dict(size=12, color='green')),
            dict(x=-0.15, y=0.8, text="Strugglers", showarrow=False, font=dict(size=12, color='orange')),
            dict(x=-0.15, y=0.2, text="Underdogs", showarrow=False, font=dict(size=12, color='blue'))
        ]
        
        fig.update_layout(
            title="ESG Risk vs. Stock Performance Matrix",
            xaxis_title="Stock Return (%)",
            yaxis_title="Greenwashing Risk Score",
            xaxis=dict(tickformat='.0%'),
            height=600,
            annotations=annotations,
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_sentiment_histogram(news_sentiments: list):
        """Media Consensus Histogram"""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=news_sentiments,
            nbinsx=20,
            marker_color='steelblue',
            opacity=0.75
        ))
        
        # Add mean line
        mean_sentiment = np.mean(news_sentiments)
        fig.add_vline(x=mean_sentiment, line_dash="dash", line_color="red", line_width=2,
                     annotation_text=f"Mean: {mean_sentiment:.2f}")
        
        fig.update_layout(
            title="Media Sentiment Distribution",
            xaxis_title="Sentiment Score",
            yaxis_title="Number of Articles",
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_time_series(audit_history: pd.DataFrame):
        """Historical Risk Tracking"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=audit_history['audit_date'],
            y=audit_history['greenwashing_score'],
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        # Add risk threshold zones
        fig.add_hrect(y0=0, y1=0.3, fillcolor="green", opacity=0.1, line_width=0, annotation_text="Low Risk")
        fig.add_hrect(y0=0.3, y1=0.6, fillcolor="orange", opacity=0.1, line_width=0, annotation_text="Medium Risk")
        fig.add_hrect(y0=0.6, y1=1.0, fillcolor="red", opacity=0.1, line_width=0, annotation_text="High Risk")
        
        fig.update_layout(
            title="Greenwashing Risk Over Time",
            xaxis_title="Date",
            yaxis_title="Risk Score",
            yaxis_range=[0, 1],
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_sector_benchmark(sector_stats: pd.DataFrame):
        """Sector Comparison Bar Chart"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=sector_stats['sector'],
            y=sector_stats['avg_risk'],
            marker_color='steelblue',
            text=sector_stats['avg_risk'].round(2),
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Average Greenwashing Risk by Sector",
            xaxis_title="Sector",
            yaxis_title="Average Risk Score",
            yaxis_range=[0, 1],
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_sentiment_gauge(sentiment_score: float, risk_level: str):
        """Gauge chart for overall risk assessment"""
        color_map = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Risk Level: {risk_level}"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color_map.get(risk_level, 'gray')},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 60], 'color': "lightyellow"},
                    {'range': [60, 100], 'color': "lightcoral"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    @staticmethod
    def create_sentiment_comparison(sec_sentiment: float, news_sentiment: float):
        """Side-by-side comparison of SEC vs News sentiment"""
        fig = go.Figure()
        
        categories = ['SEC Disclosure', 'Media Coverage']
        values = [sec_sentiment, news_sentiment]
        colors = ['blue' if v > 0 else 'red' for v in values]
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{v:.2f}" for v in values],
            textposition='outside'
        ))
        
        fig.add_hline(y=0, line_color="black", line_width=1)
        
        fig.update_layout(
            title="Sentiment Comparison: The Delta",
            yaxis_title="Sentiment Score",
            yaxis_range=[-1, 1],
            template='plotly_white',
            height=400
        )
        
        return fig