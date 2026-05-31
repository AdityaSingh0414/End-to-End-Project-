from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

def train_forecasting_model(X_train, y_train, model_type='Linear Regression'):
    """Trains a forecasting model."""
    if model_type == 'Linear Regression':
        model = LinearRegression()
    elif model_type == 'Random Forest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    elif model_type == 'XGBoost':
        model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
    else:
        raise ValueError("Unsupported model type")
        
    model.fit(X_train, y_train)
    return model
