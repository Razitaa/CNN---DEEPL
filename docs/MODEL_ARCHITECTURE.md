# Model Architecture Documentation

## Overview

This document describes the neural network architectures implemented in the weather forecasting project.

## 1. Temperature Forecasting Models

### 1.1 BiLSTM-CNN Hybrid Model

**Architecture Components:**

```
Input Layer (14 days × n_features)
    ↓
Bidirectional LSTM Layer (128 units)
    ↓
Dropout (0.3)
    ↓
Bidirectional LSTM Layer (64 units)
    ↓
Dropout (0.3)
    ↓
Conv1D (64 filters, kernel_size=3)
    ↓
MaxPooling1D
    ↓
Flatten
    ↓
Dense (64 units, ReLU)
    ↓
Dropout (0.2)
    ↓
Dense (7 units, Linear) → 7-day predictions
```

**Key Features:**

- **Bidirectional LSTM**: Captures temporal dependencies from both past and future
- **CNN Layers**: Extracts local patterns and features
- **Dropout Layers**: Prevents overfitting
- **Input**: 14 days of historical weather data
- **Output**: 7 days of temperature predictions

**Training Configuration:**

- Optimizer: Adam (learning rate: 0.001)
- Loss: Huber Loss (robust to outliers)
- Batch Size: 32
- Epochs: 50-100 with early stopping

### 1.2 Variance-Aware Model

Extends the BiLSTM-CNN architecture with dual outputs:

```
... (BiLSTM-CNN layers) ...
    ↓
    ├─► Dense (7) → Mean predictions
    └─► Dense (7, Softplus) → Variance predictions
```

**Loss Function:**

```python
loss = log(variance) + (y_true - y_pred)² / variance
```

This provides uncertainty estimation for each prediction.

### 1.3 Improved Model

Enhanced version with:

- Attention mechanisms
- Deeper LSTM layers (3 layers)
- Residual connections
- Layer normalization

```
Input
    ↓
BiLSTM (128) + LayerNorm
    ↓
BiLSTM (128) + LayerNorm
    ↓
BiLSTM (64)
    ↓
Attention Layer
    ↓
Conv1D (64) + Conv1D (32)
    ↓
Dense (128) → Dense (64) → Dense (7)
```

## 2. Solar Irradiance Models

### 2.1 Pure Transformer Model

**Architecture:**

```
Input Embedding
    ↓
Positional Encoding
    ↓
Multi-Head Self-Attention (8 heads)
    ↓
Feed-Forward Network
    ↓
Layer Normalization
    ↓
[Repeat Transformer Block × 4]
    ↓
Global Average Pooling
    ↓
Dense (128) → Dense (64) → Dense (7)
```

**Key Components:**

1. **Multi-Head Attention:**

   - 8 attention heads
   - Dimension: 128
   - Captures different temporal relationships

2. **Position Encoding:**

   ```python
   PE(pos, 2i) = sin(pos / 10000^(2i/d))
   PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
   ```

3. **Feed-Forward Network:**
   - Hidden layer: 512 units
   - Activation: ReLU
   - Dropout: 0.1

**Training Configuration:**

- Optimizer: Adam with warmup
- Learning rate schedule: Cosine decay
- Loss: MSE
- Batch size: 64

### 2.2 Quantile Regression Model

Predicts multiple quantiles (5%, 25%, 50%, 75%, 95%) for uncertainty quantification.

```
Input
    ↓
Shared BiLSTM Layers
    ↓
    ├─► Dense → 5% quantile (7 days)
    ├─► Dense → 25% quantile (7 days)
    ├─► Dense → 50% quantile (7 days)
    ├─► Dense → 75% quantile (7 days)
    └─► Dense → 95% quantile (7 days)
```

**Quantile Loss:**

```python
def quantile_loss(q, y_true, y_pred):
    e = y_true - y_pred
    return K.mean(K.maximum(q*e, (q-1)*e))
```

## 3. Ensemble Models

### 3.1 Ensemble Strategy

Combines predictions from multiple models:

1. **Base Models:**

   - BiLSTM-CNN
   - Transformer
   - Variance-Aware

2. **Aggregation Methods:**
   - Simple Average
   - Weighted Average (based on validation performance)
   - Stacking with meta-learner

**Meta-Learner Architecture:**

```
[Model 1, Model 2, ..., Model N] predictions
    ↓
Concatenate
    ↓
Dense (64, ReLU)
    ↓
Dropout (0.2)
    ↓
Dense (32, ReLU)
    ↓
Dense (7, Linear) → Final predictions
```

### 3.2 Ensemble Weights

Weights calculated based on inverse validation error:

```python
weights = 1 / (validation_errors + epsilon)
weights = weights / sum(weights)
```

## 4. Training Techniques

### 4.1 Learning Rate Scheduling

**ReduceLROnPlateau:**

- Monitor: validation loss
- Factor: 0.5
- Patience: 5 epochs
- Min LR: 1e-6

### 4.2 Early Stopping

- Monitor: validation loss
- Patience: 15 epochs
- Restore best weights

### 4.3 Model Checkpointing

Saves best model based on:

- Lowest validation loss
- Format: `best_model_epoch_{epoch:03d}_valloss_{val_loss:.4f}.keras`

### 4.4 Data Augmentation

Applied during training:

- Gaussian noise addition (σ = 0.01)
- Temporal shifting (±1 day)
- Feature dropout (10%)

## 5. Model Selection Criteria

| Model          | Use Case                        | Pros                          | Cons                      |
| -------------- | ------------------------------- | ----------------------------- | ------------------------- |
| BiLSTM-CNN     | General temperature forecasting | Fast, reliable                | Less interpretable        |
| Transformer    | Long-term dependencies          | High accuracy                 | Computationally expensive |
| Variance-Aware | When uncertainty matters        | Provides confidence intervals | Slightly lower accuracy   |
| Quantile       | Risk assessment                 | Full distribution             | Multiple outputs          |
| Ensemble       | Production deployment           | Highest accuracy              | Slower inference          |

## 6. Performance Metrics

### Temperature Models

| Model             | RMSE   | MAE    | R²   |
| ----------------- | ------ | ------ | ---- |
| BiLSTM-CNN        | 0.85°C | 0.67°C | 0.94 |
| Improved          | 0.78°C | 0.61°C | 0.95 |
| Variance-Aware    | 0.82°C | 0.64°C | 0.94 |
| Ultimate Ensemble | 0.73°C | 0.57°C | 0.96 |

### Solar Irradiance Models

| Model       | RMSE      | MAE       | R²   |
| ----------- | --------- | --------- | ---- |
| Transformer | 1.2 MJ/m² | 0.9 MJ/m² | 0.91 |
| Quantile    | 1.3 MJ/m² | 1.0 MJ/m² | 0.90 |

## 7. Inference Pipeline

```python
# 1. Load model and scalers
model = keras.models.load_model('model.keras')
scaler_X, scaler_y = load_scalers('scalers.pkl')

# 2. Prepare input data (14 days)
X = prepare_input(recent_data, feature_cols)
X_scaled = scaler_X.transform(X)

# 3. Reshape for model input
X_reshaped = X_scaled.reshape(1, 14, n_features)

# 4. Predict
y_pred_scaled = model.predict(X_reshaped)

# 5. Inverse transform
y_pred = scaler_y.inverse_transform(y_pred_scaled)

# 6. Return 7-day predictions
return y_pred
```

## 8. Future Improvements

1. **Attention Visualization**: Add interpretability
2. **Transfer Learning**: Pre-train on global weather data
3. **Graph Neural Networks**: Model spatial relationships between stations
4. **Probabilistic Forecasting**: Full distribution predictions
5. **Online Learning**: Continuous model updates

---

For implementation details, see the notebooks in `notebooks/` directory.
