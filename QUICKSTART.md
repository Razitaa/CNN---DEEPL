# Quick Start Guide

## Prerequisites

- Python 3.8+
- pip package manager
- 8GB+ RAM recommended
- GPU with CUDA support (optional, for training)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Razitaa/CNN---DEEPL.git
cd CNN---DEEPL
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Use Pre-trained Models (Recommended)

#### A. Command Line Prediction

```python
from scripts.predict_temperature import predict_temperature_7days

# Make prediction
predictions = predict_temperature_7days(
    recent_data_csv='data/raw/weather_data_indonesia.csv',
    location='Jakarta'
)

print(predictions)
```

#### B. Web Interface

1. Start the Flask server:

```bash
cd app/flask_meteo
python main.py
```

2. Open browser: `http://localhost:5000`

3. Enter location and get predictions!

### Option 2: Train Your Own Models

1. **Open Jupyter Notebook:**

```bash
jupyter notebook notebooks/processing.ipynb
```

2. **Run all cells** to:
   - Load and clean data
   - Engineer features
   - Train models
   - Evaluate performance
   - Save models

## Quick Test

Create a file `test_prediction.py`:

```python
import pandas as pd
import numpy as np
from tensorflow import keras
import pickle

# Load model
model = keras.models.load_model('models/trained_models/temperature_model_7days.keras')

# Load scalers
with open('models/scalers/temperature_scalers.pkl', 'rb') as f:
    scalers = pickle.load(f)

print("✓ Model loaded successfully!")
print(f"✓ Model input shape: {model.input_shape}")
print(f"✓ Model output shape: {model.output_shape}")
```

Run it:

```bash
python test_prediction.py
```

## Project Structure

```
├── app/              # Web application
├── data/             # Datasets
├── models/           # Trained models
├── notebooks/        # Jupyter notebooks
├── scripts/          # Python scripts
├── results/          # Predictions & plots
└── docs/             # Documentation
```

## Common Issues & Solutions

### Issue: Module not found

**Solution:**

```bash
pip install --upgrade -r requirements.txt
```

### Issue: CUDA out of memory

**Solution:** Reduce batch size in training notebook or use CPU:

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Use CPU
```

### Issue: Model file not found

**Solution:** Check if model files are in `models/trained_models/`:

```bash
ls models/trained_models/
```

## Next Steps

1. **Read Documentation**: See [README.md](README.md) for full details
2. **Explore Models**: Check [docs/MODEL_ARCHITECTURE.md](docs/MODEL_ARCHITECTURE.md)
3. **Understand Data**: Read [docs/DATA_GUIDE.md](docs/DATA_GUIDE.md)
4. **API Usage**: See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

## Getting Help

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `/docs` folder
- **Examples**: Look in `/notebooks` for working examples

## Quick Commands Reference

| Task                 | Command                                                                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Install dependencies | `pip install -r requirements.txt`                                                                                                                  |
| Start Jupyter        | `jupyter notebook`                                                                                                                                 |
| Start Flask app      | `cd app/flask_meteo && python main.py`                                                                                                             |
| Run predictions      | `python scripts/predict_temperature.py`                                                                                                            |
| Check model info     | `python -c "from tensorflow import keras; m = keras.models.load_model('models/trained_models/temperature_model_7days.keras'); print(m.summary())"` |

## Minimum Example

```python
# minimum_example.py
import numpy as np
from tensorflow import keras

# Load model (14 days input → 7 days output)
model = keras.models.load_model('models/trained_models/ultimate_best_model.keras')

# Create dummy input (1 sample, 14 days, 10 features)
X = np.random.randn(1, 14, 10)

# Predict
predictions = model.predict(X)

print(f"Predictions for next 7 days: {predictions[0]}")
```

## Success!

You're ready to start forecasting! 🎉

For detailed information, see [README.md](README.md).
