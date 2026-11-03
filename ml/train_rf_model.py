"""
Multiplayer Gameplay Dataset Generator & Random Forest ML Training Pipeline
Project: Multiplayer In-Game Cheat Detection System
File: ml/train_rf_model.py
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

FEATURE_COLUMNS = [
    'kills',
    'deaths',
    'kdr',
    'headshot_pct',
    'accuracy_pct',
    'reaction_time_ms',
    'movement_speed',
    'actions_per_second',
    'session_duration_s'
]

def generate_multiplayer_dataset(output_path="dataset/multiplayer_gameplay_dataset.csv", num_samples=3500, random_seed=42):
    """
    Generates a realistic synthetic multiplayer gameplay dataset modeling both:
    1. Legitimate competitive players (casual, intermediate, esports pros)
    2. Cheaters exhibiting specific cheats (Aimbot, Triggerbot, Speedhack, Macro/Spinbot)
    """
    np.random.seed(random_seed)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    num_legit = int(num_samples * 0.70)   # 70% legitimate
    num_cheaters = num_samples - num_legit # 30% suspicious/cheaters

    records = []

    # 1. Legitimate Players (Diverse skill tiers: Casual to Pro)
    for _ in range(num_legit):
        skill_tier = np.random.choice(['casual', 'average', 'esports_pro'], p=[0.45, 0.40, 0.15])
        session_duration = round(float(np.random.uniform(180, 1200)), 1)
        
        if skill_tier == 'casual':
            kills = int(np.random.poisson(lam=4))
            deaths = int(np.random.poisson(lam=8))
            headshot_pct = round(float(np.random.normal(loc=14.0, scale=4.5)), 2)
            accuracy_pct = round(float(np.random.normal(loc=22.0, scale=5.0)), 2)
            reaction_time = round(float(np.random.normal(loc=290.0, scale=35.0)), 1)
            movement_speed = round(float(np.random.normal(loc=4.8, scale=0.6)), 2)
            aps = round(float(np.random.normal(loc=3.8, scale=0.9)), 2)
        elif skill_tier == 'average':
            kills = int(np.random.poisson(lam=9))
            deaths = int(np.random.poisson(lam=7))
            headshot_pct = round(float(np.random.normal(loc=24.0, scale=5.0)), 2)
            accuracy_pct = round(float(np.random.normal(loc=32.0, scale=6.0)), 2)
            reaction_time = round(float(np.random.normal(loc=240.0, scale=28.0)), 1)
            movement_speed = round(float(np.random.normal(loc=5.5, scale=0.7)), 2)
            aps = round(float(np.random.normal(loc=5.5, scale=1.1)), 2)
        else: # esports pro
            kills = int(np.random.poisson(lam=18))
            deaths = int(np.random.poisson(lam=5))
            headshot_pct = round(float(np.random.normal(loc=38.0, scale=5.5)), 2)
            accuracy_pct = round(float(np.random.normal(loc=45.0, scale=6.0)), 2)
            reaction_time = round(float(np.random.normal(loc=185.0, scale=18.0)), 1) # Humans rarely cross <160ms reliably
            movement_speed = round(float(np.random.normal(loc=6.2, scale=0.6)), 2)
            aps = round(float(np.random.normal(loc=8.2, scale=1.4)), 2)

        # Clamping realistic bounds
        kills = max(0, min(50, kills))
        deaths = max(0, min(30, deaths))
        kdr = round(kills / max(1, deaths), 2)
        headshot_pct = max(0.0, min(55.0, headshot_pct))
        accuracy_pct = max(5.0, min(60.0, accuracy_pct))
        reaction_time = max(165.0, min(500.0, reaction_time)) # Biological limit threshold
        movement_speed = max(2.5, min(7.5, movement_speed))
        aps = max(1.0, min(12.0, aps))

        records.append({
            'kills': kills,
            'deaths': deaths,
            'kdr': kdr,
            'headshot_pct': headshot_pct,
            'accuracy_pct': accuracy_pct,
            'reaction_time_ms': reaction_time,
            'movement_speed': movement_speed,
            'actions_per_second': aps,
            'session_duration_s': session_duration,
            'cheat_type': 'None',
            'is_cheat': 0
        })

    # 2. Suspicious / Cheaters (Different Cheat Profiles)
    cheat_profiles = ['Aimbot', 'Triggerbot', 'Speedhack', 'Spinbot_Macro']
    for _ in range(num_cheaters):
        cheat_type = np.random.choice(cheat_profiles, p=[0.40, 0.30, 0.15, 0.15])
        session_duration = round(float(np.random.uniform(120, 1000)), 1)
        
        if cheat_type == 'Aimbot':
            # Instant headlock, abnormal headshots and near-perfect accuracy
            kills = int(np.random.poisson(lam=28))
            deaths = int(np.random.poisson(lam=2))
            headshot_pct = round(float(np.random.uniform(72.0, 96.0)), 2)
            accuracy_pct = round(float(np.random.uniform(78.0, 98.0)), 2)
            reaction_time = round(float(np.random.normal(loc=130.0, scale=25.0)), 1)
            movement_speed = round(float(np.random.normal(loc=5.8, scale=0.7)), 2)
            aps = round(float(np.random.normal(loc=6.5, scale=1.5)), 2)
        elif cheat_type == 'Triggerbot':
            # Impossible superhuman reaction times (<100ms) with high accuracy
            kills = int(np.random.poisson(lam=22))
            deaths = int(np.random.poisson(lam=3))
            headshot_pct = round(float(np.random.uniform(45.0, 75.0)), 2)
            accuracy_pct = round(float(np.random.uniform(65.0, 88.0)), 2)
            reaction_time = round(float(np.random.uniform(30.0, 95.0)), 1) # Non-human reflex!
            movement_speed = round(float(np.random.normal(loc=5.5, scale=0.8)), 2)
            aps = round(float(np.random.normal(loc=7.0, scale=1.5)), 2)
        elif cheat_type == 'Speedhack':
            # Engine speed multiplier modification (>12 m/s)
            kills = int(np.random.poisson(lam=18))
            deaths = int(np.random.poisson(lam=4))
            headshot_pct = round(float(np.random.uniform(25.0, 60.0)), 2)
            accuracy_pct = round(float(np.random.uniform(40.0, 70.0)), 2)
            reaction_time = round(float(np.random.normal(loc=190.0, scale=35.0)), 1)
            movement_speed = round(float(np.random.uniform(12.5, 24.0)), 2) # Physics break!
            aps = round(float(np.random.uniform(10.0, 18.0)), 2)
        else: # Spinbot_Macro
            # Unrealistic actions per second and erratic flicks
            kills = int(np.random.poisson(lam=26))
            deaths = int(np.random.poisson(lam=1))
            headshot_pct = round(float(np.random.uniform(60.0, 90.0)), 2)
            accuracy_pct = round(float(np.random.uniform(60.0, 85.0)), 2)
            reaction_time = round(float(np.random.uniform(50.0, 120.0)), 1)
            movement_speed = round(float(np.random.normal(loc=7.5, scale=1.5)), 2)
            aps = round(float(np.random.uniform(22.0, 48.0)), 2) # Macro input rate!

        kills = max(0, min(80, kills))
        deaths = max(0, min(20, deaths))
        kdr = round(kills / max(1, deaths), 2)

        records.append({
            'kills': kills,
            'deaths': deaths,
            'kdr': kdr,
            'headshot_pct': headshot_pct,
            'accuracy_pct': accuracy_pct,
            'reaction_time_ms': reaction_time,
            'movement_speed': movement_speed,
            'actions_per_second': aps,
            'session_duration_s': session_duration,
            'cheat_type': cheat_type,
            'is_cheat': 1
        })

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} gameplay rows -> {output_path}")
    print(f"  Legitimate: {(df['is_cheat'] == 0).sum()} ({(df['is_cheat'] == 0).mean()*100:.1f}%)")
    print(f"  Suspicious: {(df['is_cheat'] == 1).sum()} ({(df['is_cheat'] == 1).mean()*100:.1f}%)")
    return df

def train_random_forest_model(dataset_path="dataset/multiplayer_gameplay_dataset.csv", model_dir="ml/model"):
    """
    Trains a robust Random Forest classifier for in-game cheat detection.
    Saves:
      1. cheat_detection_model.pkl (Random Forest Classifier)
      2. rf_scaler.pkl (StandardScaler)
      3. rf_metadata.json (Metrics, threshold definitions, feature importances)
    """
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating new dataset...")
        df = generate_multiplayer_dataset(output_path=dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    X = df[FEATURE_COLUMNS].copy()
    y = df['is_cheat'].values

    # Leakage-safe 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Scale numerical features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest Classifier (n_jobs=1 avoids Windows loky deadlock)
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=6,
        min_samples_leaf=3,
        class_weight='balanced',
        random_state=42,
        n_jobs=1
    )
    rf_model.fit(X_train_scaled, y_train)

    # Evaluation
    y_pred = rf_model.predict(X_test_scaled)
    y_prob = rf_model.predict_proba(X_test_scaled)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Feature Importance
    importances = rf_model.feature_importances_
    feat_imp = sorted(
        [{"feature": f, "importance": round(float(imp), 4)} for f, imp in zip(FEATURE_COLUMNS, importances)],
        key=lambda x: x['importance'],
        reverse=True
    )

    print("\n" + "="*70, flush=True)
    print(" RANDOM FOREST MODEL TRAINING RESULTS", flush=True)
    print("="*70, flush=True)
    print(f" Accuracy:  {acc*100:.2f}%", flush=True)
    print(f" Precision: {prec*100:.2f}%", flush=True)
    print(f" Recall:    {rec*100:.2f}%", flush=True)
    print(f" F1-Score:  {f1*100:.2f}%", flush=True)
    print(f" ROC-AUC:   {roc_auc:.4f}", flush=True)
    print("\nFeature Importances:", flush=True)
    for item in feat_imp:
        print(f"  {item['feature']:<20}: {item['importance']:.4f}", flush=True)
    print("="*70, flush=True)

    # Save artifacts
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "random_forest_cheat_detector.pkl")
    scaler_path = os.path.join(model_dir, "rf_scaler.pkl")
    meta_path = os.path.join(model_dir, "rf_metadata.json")

    joblib.dump(rf_model, model_path)
    joblib.dump(scaler, scaler_path)

    metadata = {
        "model_name": "Random Forest Gameplay Anomaly Detector",
        "algorithm": "RandomForestClassifier",
        "n_estimators": 120,
        "features": FEATURE_COLUMNS,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4)
        },
        "confusion_matrix": {
            "tn": cm[0][0],
            "fp": cm[0][1],
            "fn": cm[1][0],
            "tp": cm[1][1]
        },
        "feature_importances": feat_imp,
        "thresholds": {
            "suspicious_threshold": 45.0, # Prob >= 45% flags for review
            "high_risk_threshold": 75.0
        }
    }

    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    print(f"Model saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    print(f"Metadata saved to: {meta_path}")

    return rf_model, scaler, metadata

if __name__ == '__main__':
    generate_multiplayer_dataset()
    train_random_forest_model()
