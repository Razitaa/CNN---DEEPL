
import numpy as np
import pandas as pd
import pickle
from tensorflow import keras
from datetime import timedelta

def load_model_and_scalers():
    """Load trained model and scalers"""
    model = keras.models.load_model('temperature_model_7days.keras')
    
    with open('temperature_scalers.pkl', 'rb') as f:
        data = pickle.load(f)
    
    return model, data['scaler_X'], data['scaler_y'], data['feature_cols']

def predict_temperature_7days(recent_data_csv, location=None):
    """
    Predict temperature for next 7 days
    
    Parameters:
    -----------
    recent_data_csv : str
        Path to CSV file with recent weather data
    location : str, optional
        Specific location to predict for (if None, uses first location)
    
    Returns:
    --------
    DataFrame with predictions
    """
    # Load model
    model, scaler_X, scaler_y, feature_cols = load_model_and_scalers()
    
    # Load data
    df = pd.read_csv(recent_data_csv)
    df['date'] = pd.to_datetime(df['date'])
    
    if location:
        df = df[df['location'] == location]
    else:
        location = df['location'].iloc[0]
    
    # Need last 14 days
    recent_data = df.tail(14).copy()
    
    if len(recent_data) < 14:
        raise ValueError("Need at least 14 days of data for prediction")
    
    # Prepare input
    X_input = recent_data[feature_cols].values[-14:]
    X_input = X_input.reshape(1, 14, -1)
    
    # Normalize and predict
    X_input_scaled = scaler_X.transform(X_input.reshape(-1, X_input.shape[-1])).reshape(X_input.shape)
    y_pred_scaled = model.predict(X_input_scaled, verbose=0)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).reshape(-1)
    
    # Create result DataFrame
    last_date = recent_data['date'].iloc[-1]
    forecast_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    
    result = pd.DataFrame({
        'date': forecast_dates,
        'location': location,
        'predicted_temperature': y_pred
    })
    
    return result

# Example usage:
# predictions = predict_temperature_7days('weather_data_2020_2025.csv', location='Jakarta')
# print(predictions)
