import plotly.express as px

def get_best_chart(df, x_col, y_col=None):
    """Automatically selects the best chart type based on data types."""
    if y_col is None:
        # Single column distribution
        if df[x_col].dtype == 'object' or df[x_col].nunique() < 10:
            return px.pie(df, names=x_col, title=f"Distribution of {x_col}")
        else:
            return px.histogram(df, x=x_col, title=f"Histogram of {x_col}")
            
    x_type = df[x_col].dtype
    y_type = df[y_col].dtype
    
    # Date + Numeric -> Line Chart
    if 'datetime' in str(x_type) and 'numeric' in str(y_type) or 'int' in str(y_type) or 'float' in str(y_type):
        # We assume if x has 'date' in name, it's date
        if 'date' in x_col.lower() or 'datetime' in str(x_type):
            return px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            
    # Category + Numeric -> Bar Chart
    if (x_type == 'object' or df[x_col].nunique() < 20) and ('int' in str(y_type) or 'float' in str(y_type)):
        return px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        
    # Two Numeric -> Scatter Plot
    if ('int' in str(x_type) or 'float' in str(x_type)) and ('int' in str(y_type) or 'float' in str(y_type)):
        return px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        
    # Default fallback
    return px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
