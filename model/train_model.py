import pandas as pd
import numpy as np
import pickle

from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

DATA_PATH = "data/DiseaseAndSymptoms.csv"
MODEL_PATH = "model/disease_model.pkl"


def train_and_save_model():
    
    df = pd.read_csv(DATA_PATH)

    symptom_columns = [col for col in df.columns if col.startswith("Symptom_")]

    all_symptoms = set()
    for col in symptom_columns:
        all_symptoms.update(
            df[col].dropna().astype(str).str.strip().str.lower().unique()
        )

    all_symptoms = sorted(list(all_symptoms))
    symptom_index = {symptom: idx for idx, symptom in enumerate(all_symptoms)}

    X = []
    y = []

    for _, row in df.iterrows():
        vector = [0] * len(all_symptoms)

        for col in symptom_columns:
            value = row[col]
            if pd.notna(value):
                symptom = str(value).strip().lower()
                if symptom in symptom_index:
                    vector[symptom_index[symptom]] = 1

        X.append(vector)
        y.append(row["Disease"])

    X = np.array(X)
    y = np.array(y)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softmax",
        eval_metric="mlogloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
print("\nXGBoost model trained and saved successfully!")


if __name__ == "__main__":
    train_and_save_model()