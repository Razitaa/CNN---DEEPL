# Weather Forecasting with Deep Learning

A comprehensive deep learning project for weather prediction in Indonesia, focusing on temperature and solar irradiance forecasting using advanced neural network architectures including BiLSTM-CNN, Transformers, and Ensemble models.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Models](#models)
- [Dataset](#dataset)
- [Results](#results)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

This project implements state-of-the-art deep learning models for weather forecasting, specifically tailored for Indonesian climate patterns. The system provides 7-day ahead predictions for:

- **Temperature Forecasting**: Daily temperature predictions (average, maximum, minimum)
- **Solar Irradiance Forecasting**: Solar radiation predictions for energy planning

The models are trained on comprehensive weather data from multiple Indonesian weather stations and utilize various advanced architectures to achieve high prediction accuracy.

## ✨ Features

- **Multiple Model Architectures**:

  - BiLSTM-CNN hybrid models
  - Pure Transformer models
  - Ensemble learning approaches
  - Quantile regression models
  - Variance-aware models

- **Comprehensive Data Processing**:

  - Robust data cleaning and preprocessing
  - Feature engineering with temporal patterns
  - Regional clustering for Indonesian geography
  - Outlier detection and handling

- **Advanced Training Techniques**:

  - Custom loss functions
  - Learning rate scheduling
  - Early stopping with model checkpointing
  - Multiple evaluation metrics

- **Web Interface**:
  - Flask-based web application
  - Interactive prediction interface
  - Real-time forecasting

## 📁 Project Structure

```
.
├── app/                          # Web application
│   └── flask_meteo/             # Flask application files
│       ├── main.py              # Flask server
│       ├── quantile_ultimate_model.keras
│       └── quantile_ultimate_scalers.pkl
│
├── data/                         # Data directory
│   ├── raw/                     # Raw datasets
│   │   ├── weather_data_indonesia.csv
│   │   ├── weather_data_2020_2025.csv
│   │   ├── solar_irradiance_complete_dataset.csv
│   │   ├── climate_data.csv
│   │   ├── province_detail.csv
│   │   └── station_detail.csv
│   └── processed/               # Processed datasets
│
├── models/                       # Model directory
│   ├── trained_models/          # Trained model files (.keras)
│   │   ├── temperature_model_7days.keras
│   │   ├── quantile_ultimate_model.keras
│   │   ├── pure_transformer_model.keras
│   │   ├── improved_temperature_model.keras
│   │   ├── variance_aware_temperature_model.keras
│   │   ├── ultimate_best_model.keras
│   │   └── ... (other model variants)
│   │
│   ├── scalers/                 # Scaler files for normalization
│   │   ├── temperature_scalers.pkl
│   │   ├── quantile_ultimate_scalers.pkl
│   │   ├── improved_scalers.pkl
│   │   └── ... (other scalers)
│   │
│   ├── checkpoints/             # Training checkpoints
│   ├── checkpoints_quantile/    # Quantile model checkpoints
│   ├── checkpoints_transformer/ # Transformer model checkpoints
│   ├── ensemble_models/         # Ensemble model files
│   ├── ensemble_models_improved/
│   ├── ensemble_models_final_v32/
│   └── realmodelfixed/         # Fixed model versions
│
├── notebooks/                    # Jupyter notebooks
│   ├── processing.ipynb         # Main training notebook
│   ├── predv2.ipynb            # Prediction experiments
│   ├── featureselection.ipynb  # Feature selection analysis
│   └── mergedata.ipynb         # Data merging utilities
│
├── scripts/                      # Python scripts
│   └── predict_temperature.py   # Temperature prediction script
│
├── results/                      # Results and outputs
│   ├── predictions/             # Prediction results
│   │   ├── ultimate_results.csv
│   │   ├── improved_results.csv
│   │   └── results_2020_2025.csv
│   │
│   └── visualizations/          # Plots and visualizations
│       ├── ensemble_analysis.png
│       ├── temperature_training.png
│       ├── prediction_analysis.png
│       └── ... (other visualizations)
│
├── docs/                         # Documentation
│
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── .gitignore                   # Git ignore file
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for training)
- pip package manager

### Setup

1. **Clone the repository**:

```bash
git clone https://github.com/Razitaa/CNN---DEEPL.git
cd CNN---DEEPL
```

2. **Create a virtual environment** (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Required Python packages**:

- tensorflow >= 2.10.0
- keras
- numpy
- pandas
- scikit-learn
- matplotlib
- seaborn
- flask (for web interface)
- pickle

## 🚀 Usage

### Training Models

1. **Prepare the data**: Place your weather data files in `data/raw/`

2. **Run the training notebook**:

```bash
jupyter notebook notebooks/processing.ipynb
```

The notebook includes:

- Data loading and cleaning
- Feature engineering
- Model training with multiple architectures
- Evaluation and visualization
- Model export with scalers

### Making Predictions

#### Using Python Script

```python
from scripts.predict_temperature import predict_temperature_7days

# Predict temperature for the next 7 days
predictions = predict_temperature_7days(
    recent_data_csv='data/raw/weather_data_indonesia.csv',
    location='Jakarta'
)
print(predictions)
```

#### Using the Web Interface

1. **Start the Flask application**:

```bash
cd app/flask_meteo
python main.py
```

2. **Open your browser** and navigate to:

```
http://localhost:5000
```

3. **Enter location and date** to get predictions

## 🧠 Models

### Temperature Forecasting Models

1. **Base BiLSTM-CNN Model** (`temperature_model_7days.keras`)

   - Bidirectional LSTM layers for temporal patterns
   - CNN layers for feature extraction
   - 7-day ahead predictions

2. **Improved Model** (`improved_temperature_model.keras`)

   - Enhanced architecture with attention mechanisms
   - Better handling of long-term dependencies

3. **Variance-Aware Model** (`variance_aware_temperature_model.keras`)

   - Includes uncertainty estimation
   - Provides prediction confidence intervals

4. **Ultimate Best Model** (`ultimate_best_model.keras`)
   - Ensemble of best-performing architectures
   - Highest accuracy achieved

### Solar Irradiance Models

1. **Pure Transformer** (`pure_transformer_model.keras`)

   - Self-attention mechanisms
   - Captures complex temporal patterns

2. **Quantile Ultimate Model** (`quantile_ultimate_model.keras`)
   - Quantile regression for uncertainty quantification
   - Multiple prediction percentiles

### Ensemble Models

Located in `models/ensemble_models/`:

- Combines predictions from multiple models
- Reduces prediction variance
- Improves overall accuracy

## 📊 Dataset

The project uses comprehensive weather data from Indonesian meteorological stations:

### Available Datasets

1. **weather_data_indonesia.csv**: Historical weather data

   - Temperature (average, max, min)
   - Humidity
   - Sunshine hours
   - Precipitation
   - Cloud cover

2. **solar_irradiance_complete_dataset.csv**: Solar radiation data

   - Solar radiation (MJ/m²)
   - Sunshine hours
   - Cloud cover percentage
   - Station coordinates

3. **weather_data_2020_2025.csv**: Recent data (2020-2025)
   - Updated measurements
   - Enhanced quality control

### Data Features

- **Temporal Features**: Date, month, day of year, season
- **Location Features**: Longitude, latitude, region cluster
- **Meteorological Features**:
  - Temperature metrics (Tavg, Tx, Tn)
  - Relative humidity (RH_avg)
  - Sunshine hours (ss)
  - Solar radiation
  - Cloud cover

## 📈 Results

Model performance metrics are stored in `results/predictions/`:

- **ultimate_results.csv**: Best model predictions
- **improved_results.csv**: Improved model results
- **results_2020_2025.csv**: Recent period predictions

### Evaluation Metrics

- **RMSE** (Root Mean Square Error)
- **MAE** (Mean Absolute Error)
- **R² Score**
- **MAPE** (Mean Absolute Percentage Error)

### Visualizations

All visualization plots are available in `results/visualizations/`:

- Training history plots
- Prediction vs actual comparisons
- Error distribution analysis
- Ensemble performance analysis

## 🌐 API

### Flask Web API

The Flask application provides RESTful endpoints for predictions:

#### Endpoint: `/predict`

**Method**: POST

**Request Body**:

```json
{
  "location": "Jakarta",
  "date": "2025-12-15",
  "days": 7
}
```

**Response**:

```json
{
  "predictions": [
    {"date": "2025-12-15", "temperature": 28.5, "solar_radiation": 18.2},
    {"date": "2025-12-16", "temperature": 29.1, "solar_radiation": 19.5},
    ...
  ],
  "model_used": "quantile_ultimate_model",
  "confidence": "95%"
}
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add comments and docstrings
- Update documentation for new features
- Test your changes thoroughly

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Razitaa** - [GitHub Profile](https://github.com/Razitaa)

## 🙏 Acknowledgments

- Indonesian Meteorological Agency (BMKG) for weather data
- TensorFlow and Keras development teams
- Open-source community

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact the repository owner.

---

**Note**: This project is for educational and research purposes. For production use, additional validation and testing are recommended.
