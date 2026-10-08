"""
train_model.py
Trains a Scikit-Learn Decision Tree Classifier for CROPWISE AI.
Inputs: Soil_Type, pH, Temperature, Humidity, Rainfall
Output: Recommended Crop
"""

# =============================================================================
# CROPWISE AI - Decision Tree Classifier Training Pipeline
# =============================================================================
# Trains, evaluates, and serializes the core Machine Learning model for CropWise AI:
# - Loads crop_data.csv and encodes categorical soil & crop labels using LabelEncoder.
# - Splits data (80% train, 20% test) with stratified sampling.
# - Fits a DecisionTreeClassifier using the CART algorithm with Gini impurity criterion.
# - Validates performance with 5-fold cross-validation and classification reports.
# - Serializes model bundle to models/crop_decision_tree.pkl and metadata to JSON.
# =============================================================================

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def train_crop_decision_tree():
    print("=" * 65)
    print("  🌱 CROPWISE AI - DECISION TREE MODEL TRAINING PIPELINE")
    print("=" * 65)
    
    # 1. Load dataset
    data_path = "crop_data.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset '{data_path}' not found! Run generate_dataset.py first.")
        
    df = pd.read_csv(data_path)
    print(f"[*] Loaded dataset with {len(df)} rows and {len(df.columns)} columns.")
    print(f"[*] Features: Soil_Type, pH, Temperature, Humidity, Rainfall")
    print(f"[*] Target classes ({df['Crop'].nunique()} crops): {sorted(df['Crop'].unique().tolist())}")
    print(f"[*] Soil types ({df['Soil_Type'].nunique()} types): {sorted(df['Soil_Type'].unique().tolist())}\n")
    
    # 2. Encode categorical features
    soil_encoder = LabelEncoder()
    df['Soil_Type_Encoded'] = soil_encoder.fit_transform(df['Soil_Type'])
    
    crop_encoder = LabelEncoder()
    df['Crop_Encoded'] = crop_encoder.fit_transform(df['Crop'])
    
    feature_cols = ['Soil_Type_Encoded', 'pH', 'Temperature', 'Humidity', 'Rainfall']
    X = df[feature_cols]
    y = df['Crop_Encoded']
    
    # 3. Train-Test Split (Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Training samples: {len(X_train)} | Testing samples: {len(X_test)}")
    
    # 4. Train Decision Tree Classifier
    dt_model = DecisionTreeClassifier(
        criterion='gini',
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42
    )
    
    dt_model.fit(X_train, y_train)
    
    # 5. Evaluate Model
    y_pred = dt_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cv_scores = cross_val_score(dt_model, X, y, cv=5)
    
    print(f"\n[✓] Test Set Accuracy: {acc * 100:.2f}%")
    print(f"[✓] 5-Fold Cross Validation Accuracy: {cv_scores.mean() * 100:.2f}% (±{cv_scores.std() * 100:.2f}%)")
    print(f"[✓] Decision Tree Depth: {dt_model.get_depth()} | Total Leaves: {dt_model.get_n_leaves()}")
    
    # Feature Importances
    importances = dict(zip(['Soil_Type', 'pH', 'Temperature', 'Humidity', 'Rainfall'], dt_model.feature_importances_))
    print("\n[*] Feature Importances:")
    for feat, imp in importances.items():
        print(f"    - {feat:<15}: {imp * 100:6.2f}%")
        
    print("\n[*] Classification Report Summary:")
    print(classification_report(y_test, y_pred, target_names=crop_encoder.classes_))
    
    # 6. Save Model Bundle
    os.makedirs("models", exist_ok=True)
    model_bundle = {
        "model": dt_model,
        "soil_encoder": soil_encoder,
        "crop_encoder": crop_encoder,
        "feature_cols": feature_cols
    }
    
    model_file = os.path.join("models", "crop_decision_tree.pkl")
    joblib.dump(model_bundle, model_file)
    print(f"[✓] Serialized model bundle saved to: {model_file}")
    
    # 7. Save Model Metadata JSON for easy frontend / explainability inspection
    metadata = {
        "model_type": "DecisionTreeClassifier",
        "algorithm": "Decision Tree (CART Gini Criterion)",
        "features": ["Soil_Type", "pH", "Temperature", "Humidity", "Rainfall"],
        "soil_types": list(soil_encoder.classes_),
        "crops": list(crop_encoder.classes_),
        "test_accuracy": round(float(acc), 4),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "tree_depth": int(dt_model.get_depth()),
        "total_leaves": int(dt_model.get_n_leaves()),
        "feature_importances": {k: round(float(v), 4) for k, v in importances.items()},
        "soil_mapping": {cls: int(idx) for idx, cls in enumerate(soil_encoder.classes_)},
        "crop_mapping": {cls: int(idx) for idx, cls in enumerate(crop_encoder.classes_)}
    }
    
    meta_file = os.path.join("models", "model_metadata.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[✓] Model metadata saved to: {meta_file}")
    
    # 8. Test Sample Inference
    print("\n" + "=" * 65)
    print("  🧪 VERIFICATION: SAMPLE INFERENCE TESTS")
    print("=" * 65)
    test_cases = [
        {"Soil_Type": "Clayey", "pH": 6.5, "Temperature": 28.0, "Humidity": 85.0, "Rainfall": 1600.0, "Expected": "Paddy"},
        {"Soil_Type": "Loamy", "pH": 6.8, "Temperature": 18.0, "Humidity": 50.0, "Rainfall": 500.0, "Expected": "Wheat"},
        {"Soil_Type": "Black", "pH": 7.5, "Temperature": 30.0, "Humidity": 60.0, "Rainfall": 750.0, "Expected": "Cotton"},
        {"Soil_Type": "Sandy", "pH": 6.2, "Temperature": 27.0, "Humidity": 55.0, "Rainfall": 600.0, "Expected": "Groundnut"},
        {"Soil_Type": "Laterite", "pH": 5.0, "Temperature": 19.0, "Humidity": 88.0, "Rainfall": 2300.0, "Expected": "Tea"},
    ]
    
    for tc in test_cases:
        s_enc = soil_encoder.transform([tc["Soil_Type"]])[0]
        input_df = pd.DataFrame([{
            'Soil_Type_Encoded': s_enc,
            'pH': tc["pH"],
            'Temperature': tc["Temperature"],
            'Humidity': tc["Humidity"],
            'Rainfall': tc["Rainfall"]
        }])
        pred_idx = dt_model.predict(input_df)[0]
        pred_crop = crop_encoder.inverse_transform([pred_idx])[0]
        probs = dt_model.predict_proba(input_df)[0]
        top3_indices = np.argsort(probs)[::-1][:3]
        top3_crops = [crop_encoder.classes_[i] for i in top3_indices if probs[i] > 0]
        print(f"Input: Soil={tc['Soil_Type']:<8} pH={tc['pH']:<4} Temp={tc['Temperature']:<4} Hum={tc['Humidity']:<4} Rain={tc['Rainfall']:<6} | Predicted: {pred_crop:<11} (Expected: {tc['Expected']:<11}) | Alternatives: {top3_crops[1:]}")

if __name__ == "__main__":
    train_crop_decision_tree()
