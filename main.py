
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import numpy as np
import joblib
import os
import pandas as pd

# ── ADD THIS to main.py after imports ────────────────────────────
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Alert Configuration ───────────────────────────────────────────
# Change these to real values
ALERT_EMAIL_FROM     = "abhij8535@gmail.com"
ALERT_EMAIL_PASSWORD = "Abhij@02"
ALERT_EMAIL_TO       = "sangales78@gmail.com"
ALERT_PHONE          = "+919665174081"

def send_email_alert(well_id, severity, score, sensor_data):
    """Send email when HIGH or CRITICAL anomaly detected"""
    if severity not in ["HIGH", "CRITICAL"]:
        return False
    try:
        msg = MIMEMultipart()
        msg['From']    = ALERT_EMAIL_FROM
        msg['To']      = ALERT_EMAIL_TO
        msg['Subject'] = f"VIO ALERT: {severity} anomaly on {well_id[:12]}"

        body = f"""
VIO Intelligence Platform - Anomaly Alert

Severity    : {severity}
Well ID     : {well_id}
Score       : {score:.6f}
Time        : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

Sensor Readings:
FTHP        : {sensor_data.get('FTHP', 'N/A')}
CHP         : {sensor_data.get('CHP',  'N/A')}
ABP         : {sensor_data.get('ABP',  'N/A')}
Battery     : {sensor_data.get('Battery_Voltage', 'N/A')}

Recommended Action:
{'SHUT IN WELL IMMEDIATELY' if severity == 'CRITICAL' else 'Send field engineer within 2 hours'}

---
VIO Intelligence Platform v2.0
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ALERT_EMAIL_FROM, ALERT_EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email alert sent for {well_id}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

def send_sms_alert(well_id, severity, score):
    """Send SMS via Twilio when CRITICAL anomaly detected"""
    if severity != "CRITICAL":
        return False
    try:
        # Install: pip install twilio
        from twilio.rest import Client
        account_sid = "YOUR_TWILIO_SID"
        auth_token  = "YOUR_TWILIO_TOKEN"
        client      = Client(account_sid, auth_token)
        message     = client.messages.create(
            body=f"VIO CRITICAL ALERT: Well {well_id[:12]} anomaly score={score:.4f}. Immediate action required.",
            from_="+1XXXXXXXXXX",  # your Twilio number
            to=ALERT_PHONE
        )
        print(f"SMS sent: {message.sid}")
        return True
    except Exception as e:
        print(f"SMS failed: {e}")
        return False

# ── App Setup ─────────────────────────────────────────────────────
app = FastAPI(
    title="VIO Intelligence Platform API",
    description="AI-powered oil well monitoring - Anomaly Detection, Predictive Maintenance, Gas Lift Optimization, Leak Detection, Production Optimization",
    version="2.0.0"
)

# ── CORS — allows external teams to call this API ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Key Security ──────────────────────────────────────────────
API_KEY        = "VIO-2024-SECRET-KEY"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# ── Model Paths ───────────────────────────────────────────────────
BASE = r"C:\Users\abhij\Desktop\VIO\models"
models = {}

@app.on_event("startup")
def load_all_models():
    print("Loading VIO models...")

    # Anomaly Detection
    models["anomaly_sf_model"]    = joblib.load(f"{BASE}/anomaly/model_sf_v2.pkl")
    models["anomaly_sf_scaler"]   = joblib.load(f"{BASE}/anomaly/scaler_sf_v2.pkl")
    models["anomaly_sf_features"] = joblib.load(f"{BASE}/anomaly/features_sf_v2.pkl")
    models["anomaly_gl_model"]    = joblib.load(f"{BASE}/anomaly/model_gl_v2.pkl")
    models["anomaly_gl_scaler"]   = joblib.load(f"{BASE}/anomaly/scaler_gl_v2.pkl")
    models["anomaly_gl_features"] = joblib.load(f"{BASE}/anomaly/features_gl_v2.pkl")

    # Maintenance and RUL
    models["rul_model"]               = joblib.load(f"{BASE}/maintenance/model_rul.pkl")
    models["urgency_model"]           = joblib.load(f"{BASE}/maintenance/model_urgency.pkl")
    models["maintenance_scaler"]      = joblib.load(f"{BASE}/maintenance/scaler_maintenance.pkl")
    models["maintenance_features"]    = joblib.load(f"{BASE}/maintenance/features_maintenance.pkl")

    # Gas Lift
    models["gaslift_flow_model"]      = joblib.load(f"{BASE}/gaslift/model_flow_rate.pkl")
    models["gaslift_optimal_model"]   = joblib.load(f"{BASE}/gaslift/model_optimal_injection.pkl")
    models["gaslift_heading_model"]   = joblib.load(f"{BASE}/gaslift/model_heading_slugging.pkl")
    models["gaslift_scaler"]          = joblib.load(f"{BASE}/gaslift/scaler_gaslift.pkl")
    models["gaslift_features"]        = joblib.load(f"{BASE}/gaslift/features_gaslift.pkl")

    # Leak Detection
    models["leak_classifier"]         = joblib.load(f"{BASE}/leak/model_leak_classifier.pkl")
    models["leak_isolation"]          = joblib.load(f"{BASE}/leak/model_leak_isolation.pkl")
    models["leak_scaler"]             = joblib.load(f"{BASE}/leak/scaler_leak.pkl")
    models["leak_features"]           = joblib.load(f"{BASE}/leak/features_leak.pkl")

    # Production Optimization
    models["production_flow_model"]   = joblib.load(f"{BASE}/production/model_production_flow.pkl")
    models["envelope_model"]          = joblib.load(f"{BASE}/production/model_envelope.pkl")
    models["pump_model"]              = joblib.load(f"{BASE}/production/model_pump_detector.pkl")
    models["production_scaler"]       = joblib.load(f"{BASE}/production/scaler_production.pkl")
    models["production_features"]     = joblib.load(f"{BASE}/production/features_production.pkl")
    models["fleet_benchmarks"]        = joblib.load(f"{BASE}/production/fleet_benchmarks.pkl")

    print("All VIO models loaded successfully")

# ── Health Check ──────────────────────────────────────────────────
@app.get("/")
def health_check():
    return {
        "platform" : "VIO Intelligence Platform",
        "version"  : "2.0.0",
        "status"   : "online",
        "models"   : len(models),
        "endpoints": [
            "/api/v1/predict/anomaly",
            "/api/v1/predict/maintenance",
            "/api/v1/predict/gaslift",
            "/api/v1/predict/leak",
            "/api/v1/predict/production",
            "/api/v1/fleet/benchmarks"
        ]
    }

# ── Severity helpers ──────────────────────────────────────────────
def get_anomaly_severity(score):
    if score >= 0.054:  return "NORMAL"
    elif score >= 0.030: return "LOW"
    elif score >= 0.010: return "MEDIUM"
    elif score >= 0.000: return "HIGH"
    else:                return "CRITICAL"

def get_urgency_label(rul):
    if rul >= 21:   return "NORMAL OPERATION"
    elif rul >= 14: return "EARLY WARNING"
    elif rul >= 7:  return "FAILURE IMMINENT"
    else:           return "INTERVENTION REQUIRED"

def get_leak_severity(score):
    if score == 0:       return "NO LEAK"
    elif score <= 0.25:  return "LOW RISK"
    elif score <= 0.50:  return "MEDIUM RISK"
    elif score <= 0.75:  return "HIGH RISK"
    else:                return "CRITICAL LEAK"

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 1 — ANOMALY DETECTION
# ═════════════════════════════════════════════════════════════════
class AnomalyInput(BaseModel):
    well_id:                  str
    well_type:                str
    FTHP:                     float
    CHP:                      float
    ABP:                      float
    GIP:                      float
    FLT:                      float
    Battery_Voltage:          float
    FTHP_delta:               float
    CHP_delta:                float
    FTHP_rmean:               float
    FTHP_rstd:                float
    FTHP_zscore:              float
    CHP_rmean:                float
    CHP_rstd:                 float
    CHP_zscore:               float
    ABP_rmean:                float
    ABP_rstd:                 float
    ABP_zscore:               float
    GIP_rmean:                float
    GIP_rstd:                 float
    GIP_zscore:               float
    FLT_rmean:                float
    FLT_rstd:                 float
    FLT_zscore:               float
    Battery_Voltage_rmean:    float
    Battery_Voltage_rstd:     float
    Battery_Voltage_zscore:   float
    FTHP_CHP_diff:            float
    FTHP_ABP_diff:            float
    CHP_ABP_diff:             float
    FTHP_lag1:                float
    CHP_lag1:                 float
    ABP_lag1:                 float
    hour_sin:                 float
    hour_cos:                 float
    month_sin:                float
    month_cos:                float

@app.post("/api/v1/predict/anomaly")
def predict_anomaly(payload: AnomalyInput):
    well_type = payload.well_type

    if well_type == "Self flow":
        features = models["anomaly_sf_features"]
        scaler   = models["anomaly_sf_scaler"]
        model    = models["anomaly_sf_model"]
    elif well_type == "Gas lift":
        features = models["anomaly_gl_features"]
        scaler   = models["anomaly_gl_scaler"]
        model    = models["anomaly_gl_model"]
    else:
        raise HTTPException(400, f"Unknown well_type: {well_type}")

    data    = payload.dict()
    X       = np.array([data[f] for f in features]).reshape(1, -1)
    X_sc    = scaler.transform(X)
    score   = float(model.decision_function(X_sc)[0])
    pred    = int(model.predict(X_sc)[0])
    severity= get_anomaly_severity(score)
    send_email_alert(payload.well_id, severity, score, payload.dict())
    send_sms_alert(payload.well_id, severity, score)

    return {
        "well_id"        : payload.well_id,
        "well_type"      : well_type,
        "capability"     : "Anomaly Detection",
        "status"         : "ANOMALY" if pred == -1 else "NORMAL",
        "severity"       : severity,
        "anomaly_score"  : round(score, 6),
        "prediction_code": pred
    }

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 2 — PREDICTIVE MAINTENANCE + RUL
# ═════════════════════════════════════════════════════════════════
class MaintenanceInput(BaseModel):
    well_id:                  str
    well_type:                str
    FTHP:                     float
    CHP:                      float
    ABP:                      float
    FLT:                      float
    Battery_Voltage:          float
    battery_rolling_mean_12:  float
    battery_rolling_min_12:   float
    battery_trend:            float
    battery_health_score:     float
    FTHP_mean_24:             float
    FTHP_std_24:              float
    FTHP_roc:                 float
    CHP_mean_24:              float
    CHP_std_24:               float
    CHP_roc:                  float
    ABP_mean_24:              float
    ABP_std_24:               float
    ABP_roc:                  float
    FLT_mean_24:              float
    FLT_std_24:               float
    FLT_roc:                  float
    FTHP_drop_flag:           int
    CHP_drop_flag:            int
    FTHP_consec_drops:        float
    pressure_instability:     float
    FLT_high_flag:            int
    health_index:             float

@app.post("/api/v1/predict/maintenance")
def predict_maintenance(payload: MaintenanceInput):
    features = models["maintenance_features"]
    scaler   = models["maintenance_scaler"]
    data     = payload.dict()

    X     = np.array([data[f] for f in features]).reshape(1, -1)
    X_sc  = scaler.transform(X)

    rul_days = float(models["rul_model"].predict(X_sc)[0])
    urgency  = models["urgency_model"].predict(X_sc)[0]
    rul_days = max(0, min(30, rul_days))

    work_order = None
    if rul_days <= 14:
        work_order = {
            "work_order_id"   : f"WO-{payload.well_id[:8].upper()}-AUTO",
            "priority"        : "P1-CRITICAL" if rul_days <= 7 else "P2-HIGH",
            "predicted_failure": str(
                (pd.Timestamp.now() + pd.Timedelta(days=rul_days)).date()
            ),
            "action"          : "Schedule immediate inspection"
        }

    return {
        "well_id"       : payload.well_id,
        "well_type"     : payload.well_type,
        "capability"    : "Predictive Maintenance & RUL",
        "rul_days"      : round(rul_days, 1),
        "urgency"       : urgency,
        "battery_health": round(payload.battery_health_score, 1),
        "health_index"  : round(payload.health_index, 3),
        "work_order"    : work_order
    }

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 3 — GAS LIFT OPTIMIZATION
# ═════════════════════════════════════════════════════════════════
class GasLiftInput(BaseModel):
    well_id:                  str
    FTHP:                     float
    CHP:                      float
    ABP:                      float
    GIP:                      float
    FLT:                      float
    GIR:                      float
    GIP_rolling_mean:         float
    GIR_rolling_mean:         float
    gir_scmd_rolling_mean:    float
    GIP_FTHP_ratio:           float
    GIP_CHP_ratio:            float
    GIP_roc:                  float
    gir_scmd_roc:             float
    FTHP_std_12:              float
    CHP_std_12:               float
    GIP_std_12:               float
    injection_efficiency:     float
    Battery_Voltage:          float
    CHP_oscillation:          float
    FTHP_oscillation:         float
    slugging_score:           float
    valve_health_score:       float
    valve_response_stability: float

@app.post("/api/v1/predict/gaslift")
def predict_gaslift(payload: GasLiftInput):
    features = models["gaslift_features"]
    scaler   = models["gaslift_scaler"]
    data     = payload.dict()

    X    = np.array([data[f] for f in features]).reshape(1, -1)
    X_sc = scaler.transform(X)

    flow_rate       = float(models["gaslift_flow_model"].predict(X_sc)[0])
    is_optimal      = int(models["gaslift_optimal_model"].predict(X_sc)[0])
    is_heading      = int(models["gaslift_heading_model"].predict(X_sc)[0])

    slugging_status = "STABLE"
    if payload.slugging_score > 0.8:   slugging_status = "SEVERE SLUGGING"
    elif payload.slugging_score > 0.5: slugging_status = "MODERATE SLUGGING"
    elif payload.slugging_score > 0.2: slugging_status = "MILD SLUGGING"

    valve_status = "HEALTHY"
    if payload.valve_health_score < 40:   valve_status = "REPLACE"
    elif payload.valve_health_score < 60: valve_status = "DEGRADING"
    elif payload.valve_health_score < 80: valve_status = "MONITOR"

    recommendation = "OPTIMAL: Maintain current injection rate" if is_optimal == 1 \
        else "ADJUST: Injection rate below optimal efficiency"

    return {
        "well_id"             : payload.well_id,
        "capability"          : "Gas Lift Optimization",
        "predicted_flow_rate" : round(flow_rate, 2),
        "is_optimal_injection": bool(is_optimal),
        "heading_slugging"    : bool(is_heading),
        "slugging_status"     : slugging_status,
        "valve_health_status" : valve_status,
        "valve_health_score"  : round(payload.valve_health_score, 1),
        "recommendation"      : recommendation
    }

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 4 — LEAK & INTEGRITY DETECTION
# ═════════════════════════════════════════════════════════════════
class LeakInput(BaseModel):
    well_id:              str
    well_type:            str
    FTHP:                 float
    CHP:                  float
    ABP:                  float
    FLT:                  float
    CHP_FTHP_diff:        float
    CHP_ABP_diff:         float
    FTHP_ABP_diff:        float
    FTHP_mean_6:          float
    FTHP_mean_24:         float
    FTHP_std_24:          float
    CHP_mean_6:           float
    CHP_mean_24:          float
    CHP_std_24:           float
    ABP_mean_6:           float
    ABP_mean_24:          float
    ABP_std_24:           float
    FTHP_diff:            float
    CHP_diff:             float
    ABP_diff:             float
    FTHP_sudden_drop:     int
    CHP_sudden_drop:      int
    ABP_sudden_drop:      int
    FTHP_decline_rate:    float
    CHP_decline_rate:     float
    scp_indicator:        int
    CHP_trend:            float
    FTHP_trend:           float
    integrity_alert:      int
    FLT_zscore:           float
    cross_zone_flag:      int
    Battery_Voltage:      float

@app.post("/api/v1/predict/leak")
def predict_leak(payload: LeakInput):
    features = models["leak_features"]
    scaler   = models["leak_scaler"]
    data     = payload.dict()

    X    = np.array([data[f] for f in features]).reshape(1, -1)
    X_sc = scaler.transform(X)

    severity  = models["leak_classifier"].predict(X_sc)[0]
    iso_score = float(models["leak_isolation"].decision_function(X_sc)[0])

    leak_score = (
        payload.FTHP_sudden_drop * 0.35 +
        payload.scp_indicator    * 0.25 +
        payload.integrity_alert  * 0.25 +
        payload.cross_zone_flag  * 0.15
    )

    action = "CRITICAL: Shut in well immediately"          if severity == "CRITICAL LEAK" else \
             "HIGH: Notify field engineer within 2 hours"  if severity == "HIGH RISK"     else \
             "MEDIUM: Inspect within 24 hours"             if severity == "MEDIUM RISK"   else \
             "LOW: Log and monitor"                        if severity == "LOW RISK"      else \
             "No action required"

    return {
        "well_id"          : payload.well_id,
        "well_type"        : payload.well_type,
        "capability"       : "Leak & Integrity Detection",
        "leak_severity"    : severity,
        "leak_score"       : round(float(leak_score), 3),
        "isolation_score"  : round(iso_score, 6),
        "scp_detected"     : bool(payload.scp_indicator),
        "integrity_alert"  : bool(payload.integrity_alert),
        "cross_zone_flow"  : bool(payload.cross_zone_flag),
        "action"           : action
    }

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 5 — PRODUCTION OPTIMIZATION
# ═════════════════════════════════════════════════════════════════
class ProductionInput(BaseModel):
    well_id:                   str
    well_type:                 str
    FTHP:                      float
    CHP:                       float
    ABP:                       float
    FLT:                       float
    GIR:                       float
    FTHP_mean_24:              float
    FTHP_std_24:               float
    CHP_mean_24:               float
    CHP_std_24:                float
    FLT_mean_24:               float
    FLT_std_24:                float
    FTHP_envelope_breach:      int
    FLT_envelope_breach:       int
    operating_envelope_score:  float
    energy_efficiency_score:   float
    pump_underperform_flag:    int
    FTHP_FLT_corr_proxy:       float
    is_environmental_variation:int
    corrected_anomaly_weight:  float
    Battery_Voltage:           float

@app.post("/api/v1/predict/production")
def predict_production(payload: ProductionInput):
    features = models["production_features"]
    scaler   = models["production_scaler"]
    data     = payload.dict()

    X    = np.array([data[f] for f in features]).reshape(1, -1)
    X_sc = scaler.transform(X)

    flow_pred     = float(models["production_flow_model"].predict(X_sc)[0])
    envelope_pred = float(models["envelope_model"].predict(X_sc)[0])
    pump_pred     = int(models["pump_model"].predict(X_sc)[0])

    # Fleet benchmark lookup
    benchmarks = models["fleet_benchmarks"]
    well_tier  = "UNKNOWN"
    if payload.well_id in benchmarks.index:
        well_tier = benchmarks.loc[payload.well_id, 'performance_tier']

    recommendations = []
    if pump_pred == 1:
        recommendations.append("PUMP: Underperforming - Check VFD settings")
    if envelope_pred < 0.5:
        recommendations.append("ENVELOPE: Outside optimal zone - Adjust pressure")
    if payload.is_environmental_variation == 1:
        recommendations.append("NOTE: Variation is temperature-driven")
    if payload.energy_efficiency_score < 30:
        recommendations.append("ENERGY: Low efficiency - Inspect motor")
    if well_tier == "UNDERPERFORMER":
        recommendations.append("FLEET: Bottom quartile - Review top performer settings")
    if not recommendations:
        recommendations.append("STATUS: Operating within normal parameters")

    return {
        "well_id"                 : payload.well_id,
        "well_type"               : payload.well_type,
        "capability"              : "Production Optimization",
        "predicted_flow_rate"     : round(flow_pred, 2),
        "envelope_score"          : round(envelope_pred, 3),
        "pump_underperforming"    : bool(pump_pred),
        "energy_efficiency_score" : round(payload.energy_efficiency_score, 1),
        "is_environmental"        : bool(payload.is_environmental_variation),
        "fleet_performance_tier"  : well_tier,
        "recommendations"         : recommendations
    }

# ═════════════════════════════════════════════════════════════════
# ENDPOINT 6 — FLEET BENCHMARKS
# ═════════════════════════════════════════════════════════════════
@app.get("/api/v1/fleet/benchmarks")
def get_fleet_benchmarks():
    benchmarks = models["fleet_benchmarks"]
    result     = benchmarks.reset_index().to_dict(orient="records")
    tiers      = benchmarks['performance_tier'].value_counts().to_dict()
    return {
        "total_wells"      : len(benchmarks),
        "performance_tiers": tiers,
        "wells"            : result
    }

@app.get("/api/v1/fleet/summary")
def get_fleet_summary():
    benchmarks = models["fleet_benchmarks"]
    return {
        "total_wells"       : len(benchmarks),
        "top_performers"    : int((benchmarks['performance_tier'] == 'TOP PERFORMER').sum()),
        "above_average"     : int((benchmarks['performance_tier'] == 'ABOVE AVERAGE').sum()),
        "below_average"     : int((benchmarks['performance_tier'] == 'BELOW AVERAGE').sum()),
        "underperformers"   : int((benchmarks['performance_tier'] == 'UNDERPERFORMER').sum()),
        "avg_FTHP"          : round(float(benchmarks['avg_FTHP'].mean()), 2),
        "avg_efficiency"    : round(float(benchmarks['avg_efficiency'].mean()), 2),
        "best_well"         : benchmarks['avg_FTHP'].idxmax(),
        "worst_well"        : benchmarks['avg_FTHP'].idxmin()
    }
