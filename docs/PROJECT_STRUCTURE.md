# Project Structure

```
CNN---DEEPL/
│
├── app/                                    # Web Application
│   └── flask_meteo/                       # Flask web service
│       ├── main.py                        # Main Flask application
│       ├── quantile_ultimate_model.keras  # Production model
│       └── quantile_ultimate_scalers.pkl  # Production scalers
│
├── data/                                   # Data Directory
│   ├── raw/                               # Raw, unprocessed data
│   │   ├── weather_data_indonesia.csv     # Historical weather data
│   │   ├── weather_data_2020_2025.csv     # Recent data (2020-2025)
│   │   ├── solar_irradiance_complete_dataset.csv  # Solar radiation data
│   │   ├── climate_data.csv               # Climate statistics
│   │   ├── province_detail.csv            # Province information
│   │   └── station_detail.csv             # Weather station metadata
│   │
│   └── processed/                         # Processed, feature-engineered data
│       └── (Generated during training)
│
├── models/                                 # Machine Learning Models
│   ├── trained_models/                    # Saved trained models (.keras)
│   │   ├── temperature_model_7days.keras  # Base temperature model
│   │   ├── improved_temperature_model.keras  # Enhanced version
│   │   ├── variance_aware_temperature_model.keras  # With uncertainty
│   │   ├── pure_transformer_model.keras   # Transformer architecture
│   │   ├── quantile_ultimate_model.keras  # Quantile regression
│   │   ├── ultimate_best_model.keras      # Best ensemble model
│   │   ├── best_improved_transformer.keras
│   │   ├── best_model_01.keras
│   │   ├── best_model_2020_2025.keras
│   │   └── final_temperature_model.keras
│   │
│   ├── scalers/                           # Data normalization objects
│   │   ├── temperature_scalers.pkl        # For temperature models
│   │   ├── improved_scalers.pkl
│   │   ├── improved_temperature_scalers.pkl
│   │   ├── variance_aware_temperature_scalers.pkl
│   │   ├── pure_transformer_scalers.pkl
│   │   ├── quantile_ultimate_scalers.pkl
│   │   ├── ultimate_scalers.pkl
│   │   ├── final_temperature_scalers.pkl
│   │   ├── scalers_2020_2025.pkl
│   │   └── ensemble_scalers*.pkl
│   │
│   ├── checkpoints/                       # Training checkpoints
│   │   ├── best_model_epoch_001_valloss_0.8826.keras
│   │   ├── best_model_epoch_002_valloss_0.7653.keras
│   │   └── ... (up to epoch 030 and beyond)
│   │
│   ├── checkpoints_quantile/              # Quantile model checkpoints
│   │   └── best_quantile.keras
│   │
│   ├── checkpoints_transformer/           # Transformer checkpoints
│   │
│   ├── ensemble_models/                   # Ensemble model components
│   ├── ensemble_models_improved/          # Improved ensemble
│   ├── ensemble_models_final_v32/         # Final ensemble version
│   └── realmodelfixed/                    # Fixed/corrected models
│
├── notebooks/                              # Jupyter Notebooks
│   ├── processing.ipynb                   # Main training pipeline
│   ├── predv2.ipynb                       # Prediction experiments
│   ├── featureselection.ipynb             # Feature selection analysis
│   └── mergedata.ipynb                    # Data merging and preparation
│
├── scripts/                                # Python Scripts
│   └── predict_temperature.py             # Temperature prediction CLI
│
├── results/                                # Results and Outputs
│   ├── predictions/                       # Prediction CSV files
│   │   ├── ultimate_results.csv           # Best model predictions
│   │   ├── improved_results.csv           # Improved model results
│   │   └── results_2020_2025.csv          # Recent period results
│   │
│   └── visualizations/                    # Plots and charts
│       ├── ensemble_analysis.png          # Ensemble performance
│       ├── ensemble_analysis_improved.png
│       ├── ensemble_analysis_final_v32.png
│       ├── temperature_training.png       # Training curves
│       ├── improved_training.png
│       ├── ultimate_training.png
│       ├── variance_aware_training.png
│       ├── transformer_analysis.png
│       ├── quantile_ultimate_analysis.png
│       ├── prediction_analysis.png        # Prediction quality
│       ├── improved_predictions_samples.png
│       ├── temperature_predictions_samples.png
│       ├── variance_aware_predictions.png
│       ├── scatter_actual_vs_predicted.png  # Scatter plots
│       ├── variance_aware_scatter.png
│       ├── ultimate_performance.png       # Performance metrics
│       └── final_comprehensive_analysis.png
│
├── docs/                                   # Documentation
│   ├── MODEL_ARCHITECTURE.md              # Model details
│   ├── DATA_GUIDE.md                      # Dataset documentation
│   └── API_DOCUMENTATION.md               # API reference
│
├── .git/                                   # Git repository
├── .gitignore                             # Git ignore rules
├── README.md                              # Project README
├── requirements.txt                       # Python dependencies
└── LICENSE                                # Project license

```

## Directory Descriptions

### `/app`

Contains the web application interface for the forecasting system. The Flask application provides a user-friendly interface and API endpoints for making predictions.

### `/data`

Stores all datasets used in the project:

- **raw/**: Original, unprocessed data from sources
- **processed/**: Cleaned and feature-engineered datasets ready for training

### `/models`

Central repository for all machine learning models and related files:

- **trained_models/**: Final trained model files in Keras format
- **scalers/**: Pickle files containing normalization/scaling objects
- **checkpoints/**: Intermediate model states saved during training
- **ensemble_models/**: Components and configurations for ensemble models
- **realmodelfixed/**: Corrected versions of models after bug fixes

### `/notebooks`

Jupyter notebooks for interactive development and analysis:

- **processing.ipynb**: Main training pipeline with data processing and model training
- **predv2.ipynb**: Prediction experiments and model evaluation
- **featureselection.ipynb**: Feature importance and selection analysis
- **mergedata.ipynb**: Data integration from multiple sources

### `/scripts`

Command-line scripts for automation and batch processing:

- **predict_temperature.py**: Script for making temperature predictions

### `/results`

Stores outputs from model training and evaluation:

- **predictions/**: CSV files with prediction results
- **visualizations/**: Plots, charts, and figures for analysis

### `/docs`

Comprehensive project documentation:

- Technical specifications
- User guides
- API references

## File Naming Conventions

### Models

- `*_model_*.keras`: Trained Keras model files
- `best_*`: Best performing model from training
- `improved_*`: Enhanced version of base model
- `variance_aware_*`: Models with uncertainty quantification
- `quantile_*`: Quantile regression models
- `ultimate_*`: Best overall models
- `pure_transformer_*`: Pure transformer architecture

### Scalers

- `*_scalers.pkl`: Pickle files containing sklearn scaler objects
- Scaler names match corresponding model names

### Checkpoints

- `best_model_epoch_{epoch:03d}_valloss_{val_loss:.4f}.keras`
- Format includes epoch number and validation loss for easy identification

### Data Files

- `weather_data_*.csv`: Weather observation data
- `solar_irradiance_*.csv`: Solar radiation measurements
- `*_detail.csv`: Metadata files
- `results_*.csv`: Prediction output files

### Visualizations

- `*_training.png`: Training history plots
- `*_analysis.png`: Model performance analysis
- `*_predictions*.png`: Prediction visualizations
- `scatter_*.png`: Scatter plot comparisons

## Workflow

1. **Data Preparation** (`/notebooks/mergedata.ipynb`)

   - Load raw data from `/data/raw/`
   - Clean and merge datasets
   - Save processed data to `/data/processed/`

2. **Feature Engineering** (`/notebooks/processing.ipynb`)

   - Create temporal and spatial features
   - Generate lag features
   - Normalize data and save scalers to `/models/scalers/`

3. **Model Training** (`/notebooks/processing.ipynb`)

   - Train multiple model architectures
   - Save checkpoints to `/models/checkpoints/`
   - Save best models to `/models/trained_models/`

4. **Evaluation** (`/notebooks/predv2.ipynb`)

   - Test models on holdout data
   - Generate visualizations in `/results/visualizations/`
   - Save predictions to `/results/predictions/`

5. **Deployment** (`/app/flask_meteo/`)
   - Load production model and scalers
   - Serve predictions via Flask API
   - Handle user requests

## Key Files

| File                        | Purpose                                |
| --------------------------- | -------------------------------------- |
| `README.md`                 | Project overview and quick start guide |
| `requirements.txt`          | Python package dependencies            |
| `.gitignore`                | Files to exclude from version control  |
| `processing.ipynb`          | Main training notebook                 |
| `predict_temperature.py`    | CLI prediction script                  |
| `main.py`                   | Flask web application                  |
| `ultimate_best_model.keras` | Best performing model                  |
| `MODEL_ARCHITECTURE.md`     | Detailed model documentation           |

## Model Versions

The project contains multiple model versions representing the evolution of the forecasting system:

1. **v1.0**: Base BiLSTM-CNN model (`temperature_model_7days.keras`)
2. **v1.5**: Improved with attention (`improved_temperature_model.keras`)
3. **v2.0**: Variance-aware version (`variance_aware_temperature_model.keras`)
4. **v2.5**: Pure transformer (`pure_transformer_model.keras`)
5. **v3.0**: Quantile regression (`quantile_ultimate_model.keras`)
6. **v3.5**: Ultimate ensemble (`ultimate_best_model.keras`)

## Size Estimates

| Directory                 | Approx Size |
| ------------------------- | ----------- |
| `/data/raw/`              | ~500 MB     |
| `/models/trained_models/` | ~800 MB     |
| `/models/checkpoints/`    | ~1.5 GB     |
| `/results/`               | ~50 MB      |
| Total                     | ~3 GB       |

## Maintenance

- **Regular Updates**: Models should be retrained monthly with new data
- **Checkpoint Cleanup**: Old checkpoints can be deleted to save space
- **Result Archiving**: Move old results to archive directory periodically
- **Documentation**: Update docs when adding new models or features

---

For more information, see individual documentation files in `/docs/`.
