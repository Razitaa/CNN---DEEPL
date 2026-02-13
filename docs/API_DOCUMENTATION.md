# API Documentation

## Overview

The Flask-based API provides endpoints for weather forecasting using trained deep learning models. The API supports both temperature and solar irradiance predictions.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. For production deployment, implement appropriate authentication mechanisms.

## Endpoints

### 1. Health Check

**Endpoint**: `GET /`

**Description**: Check if the API is running.

**Response**:

```json
{
  "status": "ok",
  "message": "Weather Forecasting API is running",
  "version": "1.0"
}
```

### 2. Predict Temperature

**Endpoint**: `POST /api/predict/temperature`

**Description**: Predict temperature for the next 7 days.

**Request Body**:

```json
{
  "location": "Jakarta",
  "start_date": "2025-12-15",
  "features": {
    "recent_data": [
      {
        "date": "2025-12-01",
        "Tavg": 28.5,
        "Tx": 32.1,
        "Tn": 25.2,
        "RH_avg": 78,
        "ss": 6.5
      }
      // ... 13 more days (total 14 days)
    ]
  }
}
```

**Parameters**:

- `location` (string, required): Location name
- `start_date` (string, required): Start date for prediction (YYYY-MM-DD)
- `features.recent_data` (array, required): Last 14 days of weather data

**Response**:

```json
{
  "status": "success",
  "location": "Jakarta",
  "predictions": [
    {
      "date": "2025-12-15",
      "temperature_avg": 28.7,
      "temperature_max": 32.3,
      "temperature_min": 25.5,
      "confidence": 0.95
    },
    {
      "date": "2025-12-16",
      "temperature_avg": 29.1,
      "temperature_max": 32.8,
      "temperature_min": 25.8,
      "confidence": 0.93
    }
    // ... 5 more days
  ],
  "model_used": "ultimate_best_model",
  "metadata": {
    "prediction_time": "2025-12-11T10:30:00Z",
    "model_version": "2.0",
    "input_days": 14,
    "forecast_days": 7
  }
}
```

**Error Response**:

```json
{
  "status": "error",
  "message": "Insufficient historical data. Need at least 14 days.",
  "error_code": "INSUFFICIENT_DATA"
}
```

### 3. Predict Solar Irradiance

**Endpoint**: `POST /api/predict/solar`

**Description**: Predict solar irradiance for the next 7 days.

**Request Body**:

```json
{
  "station_id": "96749",
  "longitude": 106.8,
  "start_date": "2025-12-15",
  "features": {
    "recent_data": [
      {
        "date": "2025-12-01",
        "Tavg": 28.5,
        "ss": 7.2,
        "RH_avg": 75,
        "cloud_cover_pct": 40
      }
      // ... 13 more days
    ]
  }
}
```

**Response**:

```json
{
  "status": "success",
  "station_id": "96749",
  "predictions": [
    {
      "date": "2025-12-15",
      "solar_radiation_MJ": 19.5,
      "sunshine_hours": 7.8,
      "quantiles": {
        "q05": 17.2,
        "q25": 18.5,
        "q50": 19.5,
        "q75": 20.3,
        "q95": 21.8
      }
    }
    // ... 6 more days
  ],
  "model_used": "quantile_ultimate_model",
  "metadata": {
    "prediction_time": "2025-12-11T10:30:00Z",
    "model_version": "1.5"
  }
}
```

### 4. Batch Predictions

**Endpoint**: `POST /api/predict/batch`

**Description**: Get predictions for multiple locations at once.

**Request Body**:

```json
{
  "locations": [
    {
      "location": "Jakarta",
      "station_id": "96749",
      "recent_data": [...]
    },
    {
      "location": "Surabaya",
      "station_id": "96935",
      "recent_data": [...]
    }
  ],
  "prediction_type": "temperature",
  "start_date": "2025-12-15"
}
```

**Response**:

```json
{
  "status": "success",
  "predictions": [
    {
      "location": "Jakarta",
      "forecast": [...]
    },
    {
      "location": "Surabaya",
      "forecast": [...]
    }
  ]
}
```

### 5. Model Information

**Endpoint**: `GET /api/models`

**Description**: Get information about available models.

**Response**:

```json
{
  "status": "success",
  "models": [
    {
      "name": "ultimate_best_model",
      "type": "temperature",
      "description": "Ensemble model with BiLSTM-CNN and Transformer",
      "metrics": {
        "rmse": 0.73,
        "mae": 0.57,
        "r2": 0.96
      },
      "version": "2.0",
      "trained_date": "2025-11-15"
    },
    {
      "name": "quantile_ultimate_model",
      "type": "solar_irradiance",
      "description": "Quantile regression model",
      "metrics": {
        "rmse": 1.3,
        "mae": 1.0,
        "r2": 0.9
      },
      "version": "1.5",
      "trained_date": "2025-11-10"
    }
  ]
}
```

### 6. Historical Data

**Endpoint**: `GET /api/data/historical`

**Description**: Retrieve historical weather data for a location.

**Query Parameters**:

- `location` (string, required): Location name
- `start_date` (string, required): Start date (YYYY-MM-DD)
- `end_date` (string, required): End date (YYYY-MM-DD)
- `variables` (string, optional): Comma-separated list of variables (default: all)

**Example**:

```
GET /api/data/historical?location=Jakarta&start_date=2025-11-01&end_date=2025-11-30&variables=Tavg,RH_avg
```

**Response**:

```json
{
  "status": "success",
  "location": "Jakarta",
  "data": [
    {
      "date": "2025-11-01",
      "Tavg": 28.5,
      "RH_avg": 78
    },
    {
      "date": "2025-11-02",
      "Tavg": 29.1,
      "RH_avg": 75
    }
    // ...
  ],
  "count": 30
}
```

## Error Codes

| Code               | Description                          |
| ------------------ | ------------------------------------ |
| 400                | Bad Request - Invalid parameters     |
| 404                | Not Found - Resource not found       |
| 500                | Internal Server Error - Server error |
| INSUFFICIENT_DATA  | Not enough historical data provided  |
| INVALID_DATE       | Date format is incorrect             |
| MODEL_NOT_FOUND    | Requested model does not exist       |
| LOCATION_NOT_FOUND | Location not in database             |

## Rate Limiting

- **Rate**: 100 requests per minute per IP
- **Burst**: 10 requests per second

When rate limit is exceeded:

```json
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

## Python Client Example

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/api/predict/temperature"

# Prepare request
payload = {
    "location": "Jakarta",
    "start_date": "2025-12-15",
    "features": {
        "recent_data": [
            {
                "date": "2025-12-01",
                "Tavg": 28.5,
                "Tx": 32.1,
                "Tn": 25.2,
                "RH_avg": 78,
                "ss": 6.5
            }
            # ... more data
        ]
    }
}

# Make request
response = requests.post(url, json=payload)

# Parse response
if response.status_code == 200:
    data = response.json()
    if data['status'] == 'success':
        print("Predictions:")
        for pred in data['predictions']:
            print(f"{pred['date']}: {pred['temperature_avg']}°C")
    else:
        print(f"Error: {data['message']}")
else:
    print(f"HTTP Error: {response.status_code}")
```

## JavaScript Client Example

```javascript
const axios = require("axios");

async function getPrediction() {
  const url = "http://localhost:5000/api/predict/temperature";

  const payload = {
    location: "Jakarta",
    start_date: "2025-12-15",
    features: {
      recent_data: [
        {
          date: "2025-12-01",
          Tavg: 28.5,
          Tx: 32.1,
          Tn: 25.2,
          RH_avg: 78,
          ss: 6.5,
        },
        // ... more data
      ],
    },
  };

  try {
    const response = await axios.post(url, payload);

    if (response.data.status === "success") {
      console.log("Predictions:");
      response.data.predictions.forEach((pred) => {
        console.log(`${pred.date}: ${pred.temperature_avg}°C`);
      });
    }
  } catch (error) {
    console.error("Error:", error.response?.data?.message || error.message);
  }
}

getPrediction();
```

## Running the API Server

### Development Mode

```bash
cd app/flask_meteo
python main.py
```

The server will start on `http://localhost:5000`

### Production Mode

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app

# Using uWSGI
uwsgi --http :5000 --wsgi-file main.py --callable app --processes 4
```

### Docker Deployment

```bash
# Build image
docker build -t weather-api .

# Run container
docker run -p 5000:5000 weather-api
```

## Testing

```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Security Considerations

For production deployment:

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Add Authentication**: Implement API keys or OAuth
3. **Input Validation**: Sanitize all inputs
4. **Rate Limiting**: Implement proper rate limiting
5. **CORS**: Configure CORS appropriately
6. **Logging**: Enable comprehensive logging
7. **Monitoring**: Set up monitoring and alerts

## Support

For API issues or questions, please open an issue on GitHub or contact the maintainers.

---

Last updated: December 2025
