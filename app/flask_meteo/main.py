"""
Flask Weather Forecast API with Quantile Regression Model
- Fetch real-time data from Open-Meteo API
- Predict using trained quantile model
- Provide Grafana-compatible endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
import pickle
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from functools import lru_cache
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Grafana

# ==================== CONFIGURATION ====================
MODEL_PATH = 'quantile_ultimate_model.keras'
SCALER_PATH = 'quantile_ultimate_scalers.pkl'
SEQUENCE_LENGTH = 14  # Updated from model input shape
N_FEATURES = 16       # Updated from model input shape
FORECAST_DAYS = 7

# Open-Meteo API config
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Data storage (in-memory, bisa diganti Redis/DB)
latest_data = {
    'timestamp': None,
    'raw_data': None,
    'predictions': None,
    'location': None
}

# ==================== LOAD MODEL WITH MULTIPLE STRATEGIES ====================
logger.info("Loading model and scalers...")

def load_model_robust():
    """
    Load model with multiple fallback strategies
    Handles custom loss functions and serialization issues
    """
    import tensorflow.keras.backend as K
    
    # Define quantile loss
    def make_quantile_loss(q):
        def quantile_loss(y_true, y_pred):
            e = y_true - y_pred
            return K.mean(K.maximum(q * e, (q - 1) * e))
        quantile_loss.__name__ = f'quantile_loss_q{int(q*100)}'
        return quantile_loss
    
    # Create custom objects
    custom_objects = {
        'quantile_loss': make_quantile_loss,
        'loss_p10': make_quantile_loss(0.1),
        'loss_p50': make_quantile_loss(0.5),
        'loss_p90': make_quantile_loss(0.9),
        'p10_loss': make_quantile_loss(0.1),
        'p50_loss': make_quantile_loss(0.5),
        'p90_loss': make_quantile_loss(0.9),
        'p50_mae': keras.metrics.MeanAbsoluteError(),
    }
    
    # Strategy 1: Load with custom objects
    try:
        logger.info("Attempting Strategy 1: Load with custom objects...")
        model = keras.models.load_model(
            MODEL_PATH, 
            custom_objects=custom_objects,
            compile=False
        )
        logger.info("✅ Strategy 1 SUCCESS - Model loaded with custom objects")
        return model
    except Exception as e1:
        logger.warning(f"Strategy 1 failed: {str(e1)[:100]}")
    
    # Strategy 2: Load without custom objects (inference only)
    try:
        logger.info("Attempting Strategy 2: Load without compile...")
        model = keras.models.load_model(MODEL_PATH, compile=False)
        logger.info("✅ Strategy 2 SUCCESS - Model loaded (inference only)")
        return model
    except Exception as e2:
        logger.warning(f"Strategy 2 failed: {str(e2)[:100]}")
    
    # Strategy 3: Load with custom_object_scope
    try:
        logger.info("Attempting Strategy 3: Load with custom scope...")
        with keras.saving.custom_object_scope(custom_objects):
            model = keras.models.load_model(MODEL_PATH, compile=False)
        logger.info("✅ Strategy 3 SUCCESS - Model loaded with scope")
        return model
    except Exception as e3:
        logger.warning(f"Strategy 3 failed: {str(e3)[:100]}")
    
    logger.error("❌ All strategies failed to load model")
    return None

# Load model
model = load_model_robust()

# Load scalers with patching
def load_scalers_robust():
    """Load scalers with robust error handling"""
    import sys
    from types import ModuleType
    
    try:
        # Strategy 1: Normal load
        with open(SCALER_PATH, 'rb') as f:
            scalers = pickle.load(f)
        logger.info("✅ Scalers loaded successfully (Strategy 1)")
        return scalers
    except AttributeError as e:
        if 'Config' in str(e):
            logger.warning(f"Config class missing, applying patch...")
            
            # Strategy 2: Patch missing Config class
            try:
                # Create dummy Config class
                class Config:
                    def __init__(self, *args, **kwargs):
                        self.__dict__.update(kwargs)
                    def __reduce__(self):
                        return (self.__class__, (), self.__dict__)
                
                # Inject into __main__ module
                sys.modules['__main__'].Config = Config
                
                # Try loading again
                with open(SCALER_PATH, 'rb') as f:
                    scalers = pickle.load(f)
                logger.info("✅ Scalers loaded successfully (Strategy 2 - with patch)")
                return scalers
            except Exception as e2:
                logger.error(f"Strategy 2 failed: {e2}")
        else:
            logger.error(f"Scaler load failed: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to load scalers: {e}")
    
    return None

scalers = load_scalers_robust()

# Final check
if model is not None and scalers is not None:
    logger.info("✅ Model and scalers loaded successfully")
    logger.info(f"   Model input shape: {model.input_shape}")
    logger.info(f"   Model output shape: {model.output_shape}")
    logger.info(f"   Scaler keys: {list(scalers.keys())}")
    
    # Test prediction with correct shape
    try:
        test_input = np.random.randn(1, SEQUENCE_LENGTH, N_FEATURES).astype(np.float32)
        test_pred = model.predict(test_input, verbose=0)
        
        # Handle different output formats
        if isinstance(test_pred, list):
            logger.info(f"✅ Model inference test passed - Output: List of {len(test_pred)} tensors")
            for i, pred in enumerate(test_pred):
                logger.info(f"   Tensor {i} shape: {pred.shape}")
        else:
            logger.info(f"✅ Model inference test passed - Output shape: {test_pred.shape}")
    except Exception as e:
        logger.warning(f"⚠️ Model test failed: {e}")
else:
    logger.error("❌ Failed to load model or scalers")
    model = None
    scalers = None

# ==================== HELPER FUNCTIONS ====================

def fetch_openmeteo_data(latitude, longitude, days=30):
    """
    Fetch weather data from Open-Meteo API
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        days: Number of historical days to fetch
    
    Returns:
        DataFrame with weather data
    """
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean',
                'precipitation_sum',
                'windspeed_10m_max',
                'shortwave_radiation_sum'
            ],
            'timezone': 'auto'
        }
        
        logger.info(f"Fetching data from Open-Meteo for lat={latitude}, lon={longitude}")
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'date': pd.to_datetime(data['daily']['time']),
            'tavg': data['daily']['temperature_2m_mean'],
            'tmax': data['daily']['temperature_2m_max'],
            'tmin': data['daily']['temperature_2m_min'],
            'prcp': data['daily']['precipitation_sum'],
            'wspd': data['daily']['windspeed_10m_max'],
            'srad': data['daily']['shortwave_radiation_sum']
        })
        
        # Handle missing values (using newer pandas syntax)
        df = df.ffill().bfill()
        
        logger.info(f"✅ Fetched {len(df)} days of data")
        return df
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch Open-Meteo data: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error processing Open-Meteo data: {e}")
        return None


def create_features(df):
    """
    Create features from raw weather data
    UPDATED: Match EXACTLY with training feature engineering
    """
    df = df.copy()
    
    # Rename tavg to temperature (match training)
    df['temperature'] = df['tavg']
    
    # Time features
    df['day_of_year'] = df['date'].dt.dayofyear
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    
    # Cyclical encoding for day of year
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # Cyclical encoding for month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Cyclical encoding for day of week
    df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Temperature lag features (match training)
    df['temp_lag1'] = df['temperature'].shift(1)
    df['temp_lag2'] = df['temperature'].shift(2)
    df['temp_lag3'] = df['temperature'].shift(3)
    df['temp_lag7'] = df['temperature'].shift(7)
    
    # Temperature difference features
    df['temp_diff1'] = df['temperature'].diff(1)
    df['temp_diff7'] = df['temperature'].diff(7)
    
    # Rolling statistics
    df['temp_std3'] = df['temperature'].rolling(window=3, min_periods=1).std().fillna(0)
    df['temp_std7'] = df['temperature'].rolling(window=7, min_periods=1).std().fillna(0)
    
    # Fill NaN values from lag/diff features
    df = df.bfill().ffill()
    
    logger.info(f"Created features: {df.columns.tolist()}")
    
    return df


def prepare_sequence(df, sequence_length=14):
    """
    Prepare sequence for prediction
    UPDATED: Uses feature_cols from saved scalers
    
    Args:
        df: DataFrame with features
        sequence_length: Length of input sequence (14)
    
    Returns:
        Numpy array ready for prediction (shape: sequence_length, 16)
    """
    # Get feature columns from saved scalers (if available)
    if scalers is not None and 'feature_cols' in scalers:
        feature_cols = scalers['feature_cols']
        logger.info(f"Using saved feature_cols from scalers: {len(feature_cols)} features")
    else:
        # Fallback: Manual feature list (MUST BE 16 FEATURES)
        feature_cols = [
            # Base weather features (6)
            'tavg', 'tmax', 'tmin', 'prcp', 'wspd', 'srad',
            # Cyclical time features (4)
            'day_sin', 'day_cos', 'month_sin', 'month_cos',
            # Rolling statistics (3)
            'tavg_roll7', 'tavg_roll7_std', 'prcp_roll7',
            # Lag features (3)
            'tavg_lag1', 'tavg_lag3', 'tavg_lag7'
            # Total should be 16
        ]
        logger.warning(f"Using fallback feature_cols: {len(feature_cols)} features")
    
    # Validate we have exactly 16 features
    if len(feature_cols) != N_FEATURES:
        logger.error(f"Feature count mismatch! Expected {N_FEATURES}, got {len(feature_cols)}")
        logger.error(f"Feature list: {feature_cols}")
    
    # Check if all features exist in dataframe
    missing_features = [f for f in feature_cols if f not in df.columns]
    if missing_features:
        logger.error(f"Missing features in dataframe: {missing_features}")
        logger.info(f"Available columns: {df.columns.tolist()}")
    
    # Get last sequence_length rows
    X = df[feature_cols].tail(sequence_length).values
    
    logger.info(f"Prepared sequence shape: {X.shape} (expected: ({sequence_length}, {N_FEATURES}))")
    
    return X


def predict_forecast(X, model, scalers, forecast_days=7):
    """
    Make probabilistic forecast using quantile regression model
    UPDATED: Uses correct scaler keys
    
    Args:
        X: Input features (sequence)
        model: Trained Keras model
        scalers: Dictionary containing scaler_X and scaler_y
        forecast_days: Number of days to forecast
    
    Returns:
        Dictionary with forecast results
    """
    try:
        # Normalize input using correct scaler key
        X_scaled = scalers['scaler_X'].transform(X.reshape(-1, X.shape[-1]))
        X_scaled = X_scaled.reshape(1, X.shape[0], X.shape[1])
        
        logger.info(f"Input shape for prediction: {X_scaled.shape}")
        
        # Predict (model outputs: [p10, p50, p90])
        predictions = model.predict(X_scaled, verbose=0)
        
        logger.info(f"Raw prediction type: {type(predictions)}")
        
        # Handle different output formats
        if isinstance(predictions, list):
            # Model outputs list of 3 tensors: [p10_tensor, p50_tensor, p90_tensor]
            logger.info(f"Model returned list of {len(predictions)} tensors")
            p10_raw = predictions[0].reshape(-1, 1)  # Shape: (7, 1)
            p50_raw = predictions[1].reshape(-1, 1)  # Shape: (7, 1)
            p90_raw = predictions[2].reshape(-1, 1)  # Shape: (7, 1)
        else:
            # Single tensor output
            logger.info(f"Raw prediction shape: {predictions.shape}")
            
            if len(predictions.shape) == 2:
                # Shape: (1, forecast_days*3) - need to reshape
                predictions = predictions.reshape(1, -1, 3)
            
            # Extract quantiles
            p10_raw = predictions[0][:, 0:1]
            p50_raw = predictions[0][:, 1:2]
            p90_raw = predictions[0][:, 2:3]
        
        # Denormalize predictions using correct scaler key
        p10 = scalers['scaler_y'].inverse_transform(p10_raw).flatten()
        p50 = scalers['scaler_y'].inverse_transform(p50_raw).flatten()
        p90 = scalers['scaler_y'].inverse_transform(p90_raw).flatten()
        
        # Create forecast dates
        start_date = datetime.now().date() + timedelta(days=1)
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                 for i in range(forecast_days)]
        
        # Format results
        forecast = []
        for i in range(min(forecast_days, len(p50))):
            forecast.append({
                'date': dates[i],
                'p10': round(float(p10[i]), 2),
                'forecast': round(float(p50[i]), 2),
                'p50': round(float(p50[i]), 2),
                'p90': round(float(p90[i]), 2),
                'range': round(float(p90[i] - p10[i]), 2),
                'uncertainty': round(float((p90[i] - p10[i]) / 2), 2)
            })
        
        # Calculate statistics
        stats = {
            'mean': round(float(np.mean(p50[:forecast_days])), 2),
            'std': round(float(np.std(p50[:forecast_days])), 2),
            'min': round(float(np.min(p50[:forecast_days])), 2),
            'max': round(float(np.max(p50[:forecast_days])), 2),
            'avg_uncertainty': round(float(np.mean(p90[:forecast_days] - p10[:forecast_days])), 2)
        }
        
        logger.info(f"✅ Prediction successful: {len(forecast)} days forecasted")
        
        return {
            'success': True,
            'forecast': forecast,
            'statistics': stats
        }
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


def update_data_and_predict(latitude, longitude, location_name="Unknown"):
    """
    Main function to fetch data and make predictions
    This runs every 30 minutes
    """
    global latest_data
    
    logger.info(f"🔄 Updating data for {location_name}...")
    
    # Fetch data from Open-Meteo
    df = fetch_openmeteo_data(latitude, longitude)
    if df is None:
        logger.error("Failed to fetch data")
        return False
    
    # Create features
    df = create_features(df)
    
    # Prepare sequence
    X = prepare_sequence(df, SEQUENCE_LENGTH)
    
    # Make predictions
    predictions = predict_forecast(X, model, scalers, FORECAST_DAYS)
    
    # Store results
    latest_data = {
        'timestamp': datetime.now().isoformat(),
        'raw_data': df.tail(30).to_dict('records'),
        'predictions': predictions,
        'location': {
            'name': location_name,
            'latitude': latitude,
            'longitude': longitude
        }
    }
    
    logger.info(f"✅ Data updated successfully at {latest_data['timestamp']}")
    return True


# ==================== API ENDPOINTS ====================

@app.route('/')
def index():
    """API information"""
    return jsonify({
        'api': 'Weather Forecast API with Quantile Regression',
        'version': '1.0.1',
        'model': 'quantile_ultimate_model',
        'config': {
            'sequence_length': SEQUENCE_LENGTH,
            'n_features': N_FEATURES,
            'forecast_days': FORECAST_DAYS
        },
        'endpoints': {
            '/health': 'Health check',
            '/predict': 'Manual prediction (POST)',
            '/forecast': 'Get latest forecast (GET)',
            '/forecast/grafana': 'Grafana-compatible forecast data',
            '/historical/grafana': 'Grafana-compatible historical data',
            '/metrics': 'Prometheus-style metrics'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model is not None else 'unhealthy',
        'model_loaded': model is not None,
        'scalers_loaded': scalers is not None,
        'last_update': latest_data.get('timestamp'),
        'timestamp': datetime.now().isoformat(),
        'config': {
            'sequence_length': SEQUENCE_LENGTH,
            'n_features': N_FEATURES
        }
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Manual prediction endpoint
    
    POST Body:
    {
        "latitude": -5.45,
        "longitude": 105.26,
        "location": "Bandar Lampung"
    }
    """
    if model is None or scalers is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        location = data.get('location', 'Unknown')
        
        # Update data and predict
        success = update_data_and_predict(latitude, longitude, location)
        
        if not success:
            return jsonify({'error': 'Failed to fetch data or predict'}), 500
        
        return jsonify(latest_data)
        
    except Exception as e:
        logger.error(f"Error in /predict: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/forecast', methods=['GET'])
def get_forecast():
    """
    Get latest forecast data
    """
    if latest_data['timestamp'] is None:
        return jsonify({
            'error': 'No data available. Please call /predict first or wait for scheduled update.'
        }), 404
    
    return jsonify(latest_data)


@app.route('/forecast/grafana', methods=['GET', 'POST'])
def forecast_grafana():
    """
    Grafana-compatible forecast endpoint
    Returns time series data in Grafana JSON format
    """
    if latest_data['timestamp'] is None:
        return jsonify([]), 200
    
    if not latest_data['predictions']['success']:
        return jsonify([]), 200
    
    forecast = latest_data['predictions']['forecast']
    
    # Convert to Grafana format
    grafana_data = []
    for item in forecast:
        timestamp = int(datetime.strptime(item['date'], '%Y-%m-%d').timestamp() * 1000)
        
        grafana_data.append({
            'target': 'forecast_p50',
            'datapoints': [[item['forecast'], timestamp]]
        })
        grafana_data.append({
            'target': 'forecast_p10',
            'datapoints': [[item['p10'], timestamp]]
        })
        grafana_data.append({
            'target': 'forecast_p90',
            'datapoints': [[item['p90'], timestamp]]
        })
    
    # Group by target
    grouped = {}
    for item in grafana_data:
        target = item['target']
        if target not in grouped:
            grouped[target] = {'target': target, 'datapoints': []}
        grouped[target]['datapoints'].extend(item['datapoints'])
    
    return jsonify(list(grouped.values()))


@app.route('/historical/grafana', methods=['GET', 'POST'])
def historical_grafana():
    """
    Grafana-compatible historical data endpoint
    """
    if latest_data['timestamp'] is None or latest_data['raw_data'] is None:
        return jsonify([]), 200
    
    raw_data = latest_data['raw_data']
    
    # Convert to Grafana format
    targets = ['tavg', 'tmax', 'tmin']
    grafana_data = []
    
    for target in targets:
        datapoints = []
        for row in raw_data:
            if 'date' in row and target in row:
                timestamp = int(datetime.fromisoformat(row['date']).timestamp() * 1000)
                value = row[target]
                datapoints.append([value, timestamp])
        
        grafana_data.append({
            'target': target,
            'datapoints': datapoints
        })
    
    return jsonify(grafana_data)


@app.route('/metrics')
def metrics():
    """
    Prometheus-style metrics endpoint
    """
    if latest_data['timestamp'] is None:
        return "# No data available\n", 200
    
    metrics_text = f"""# HELP weather_last_update_timestamp Last update timestamp
# TYPE weather_last_update_timestamp gauge
weather_last_update_timestamp {int(datetime.fromisoformat(latest_data['timestamp']).timestamp())}

# HELP weather_forecast_mean Mean forecasted temperature
# TYPE weather_forecast_mean gauge
weather_forecast_mean {latest_data['predictions']['statistics']['mean']}

# HELP weather_forecast_uncertainty Average forecast uncertainty
# TYPE weather_forecast_uncertainty gauge
weather_forecast_uncertainty {latest_data['predictions']['statistics']['avg_uncertainty']}
"""
    
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}


# ==================== SCHEDULER ====================

def scheduled_update():
    """Scheduled task that runs every 30 minutes"""
    # Default location (sesuaikan dengan kebutuhan lu)
    # Contoh: Bandar Lampung
    LATITUDE = -5.45
    LONGITUDE = 105.26
    LOCATION = "Bandar Lampung"
    
    # Bisa juga load dari environment variable
    latitude = float(os.getenv('DEFAULT_LAT', LATITUDE))
    longitude = float(os.getenv('DEFAULT_LON', LONGITUDE))
    location = os.getenv('DEFAULT_LOCATION', LOCATION)
    
    update_data_and_predict(latitude, longitude, location)


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=scheduled_update,
    trigger="interval",
    minutes=30,
    id='update_weather_data',
    name='Update weather data every 30 minutes',
    replace_existing=True
)

# ==================== MAIN ====================

if __name__ == '__main__':
    # Start scheduler
    logger.info("🚀 Starting Flask Weather Forecast API")
    
    if model is not None:
        # Run initial update
        logger.info("Running initial data fetch...")
        scheduled_update()
        
        # Start scheduler
        scheduler.start()
        logger.info("✅ Scheduler started (updates every 30 minutes)")
    else:
        logger.error("❌ Model not loaded. API running in limited mode.")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False  # Set True for development
    )