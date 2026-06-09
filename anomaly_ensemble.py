
import numpy as np
import joblib
import os

# This file adds autoencoder to the existing IsolationForest
# Combined score = better accuracy

models_dir = r"C:\Users\abhij\Desktop\VIO\models\anomaly"

def load_autoencoder_models():
    """Load autoencoder models and thresholds"""
    try:
        from tensorflow.keras.models import load_model

        ae_models = {
            'ae_sf'          : load_model(f"{models_dir}/autoencoder_sf.keras"),
            'scaler_ae_sf'   : joblib.load(f"{models_dir}/scaler_ae_sf.pkl"),
            'threshold_ae_sf': joblib.load(f"{models_dir}/threshold_ae_sf.pkl"),
            'features_ae_sf' : joblib.load(f"{models_dir}/features_ae.pkl"),
            'ae_gl'          : load_model(f"{models_dir}/autoencoder_gl.keras"),
            'scaler_ae_gl'   : joblib.load(f"{models_dir}/scaler_ae_gl.pkl"),
            'threshold_ae_gl': joblib.load(f"{models_dir}/threshold_ae_gl.pkl"),
            'features_ae_gl' : joblib.load(f"{models_dir}/features_ae_gl.pkl"),
        }
        print("Autoencoder models loaded")
        return ae_models
    except Exception as e:
        print(f"Autoencoder load failed: {e}")
        return None

def get_autoencoder_score(data_dict, well_type, ae_models):
    """
    Get reconstruction error from autoencoder
    High error = anomaly
    Returns: reconstruction_error, is_anomaly (bool)
    """
    if ae_models is None:
        return 0.0, False

    try:
        if well_type == "Self flow":
            features   = ae_models['features_ae_sf']
            scaler     = ae_models['scaler_ae_sf']
            model      = ae_models['ae_sf']
            threshold  = ae_models['threshold_ae_sf']
        else:
            features   = ae_models['features_ae_gl']
            scaler     = ae_models['scaler_ae_gl']
            model      = ae_models['ae_gl']
            threshold  = ae_models['threshold_ae_gl']

        X        = np.array([data_dict.get(f, 0) for f in features]).reshape(1, -1)
        X_scaled = scaler.transform(X)
        X_pred   = model.predict(X_scaled, verbose=0)
        mse      = float(np.mean(np.power(X_scaled - X_pred, 2)))

        return mse, mse > threshold

    except Exception as e:
        print(f"Autoencoder prediction error: {e}")
        return 0.0, False

def ensemble_anomaly_score(iso_score, ae_mse, ae_threshold):
    """
    Combine IsolationForest + Autoencoder scores
    IsolationForest: good at sudden spikes
    Autoencoder    : good at slow drift
    Together       : catches both types
    """
    # Normalize autoencoder score to 0-1
    ae_normalized = min(1.0, ae_mse / (ae_threshold + 1e-6))

    # IsolationForest score: higher = more normal
    # Convert to anomaly probability: lower iso_score = more anomalous
    iso_normalized = 1 - min(1.0, max(0.0, (iso_score + 0.2) / 0.4))

    # Weighted ensemble
    ensemble_score = (0.6 * iso_normalized) + (0.4 * ae_normalized)

    return ensemble_score

def get_ensemble_severity(iso_score, ae_mse, ae_is_anomaly):
    """Get final severity from ensemble of both models"""

    # If BOTH models agree it is anomaly — higher confidence
    if iso_score < 0 and ae_is_anomaly:
        return "CRITICAL"

    # IsolationForest says anomaly, autoencoder agrees partially
    if iso_score < 0.010 and ae_is_anomaly:
        return "HIGH"

    # IsolationForest says anomaly, autoencoder normal
    if iso_score < 0.010:
        return "MEDIUM"

    # Autoencoder says anomaly, IsolationForest normal
    # This catches slow drift that IsolationForest misses
    if ae_is_anomaly and iso_score < 0.030:
        return "MEDIUM"

    if ae_is_anomaly:
        return "LOW"

    # Both say normal
    if iso_score >= 0.054:
        return "NORMAL"
    elif iso_score >= 0.030:
        return "LOW"
    elif iso_score >= 0.010:
        return "MEDIUM"
    else:
        return "HIGH"
