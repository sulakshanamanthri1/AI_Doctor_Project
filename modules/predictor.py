import pickle
import numpy as np
import pandas as pd
from collections import defaultdict

MODEL_PATH = "model/disease_model.pkl"
DATA_PATH = "data/DiseaseAndSymptoms.csv"

# Load trained model
with open(MODEL_PATH, "rb") as file:
    model_data = pickle.load(file)

model = model_data["model"]
label_encoder = model_data["label_encoder"]
all_symptoms = model_data["all_symptoms"]
symptom_index = model_data["symptom_index"]

# Load original dataset
df = pd.read_csv(DATA_PATH)
symptom_columns = [col for col in df.columns if col.startswith("Symptom_")]

# Symptom synonym mapping
SYMPTOM_MAP = {
    "cold": "continuous_sneezing",
    "runny nose": "runny_nose",
    "running nose": "runny_nose",
    "fever": "high_fever",
    "body pain": "muscle_pain",
    "throat pain": "throat_irritation",
    "sore throat": "throat_irritation",
    "stomach ache": "stomach_pain",
    "breathing problem": "breathlessness",
    "vomit": "vomiting",
    "tiredness": "fatigue"
}

SEVERE_DISEASE_RULES = {
    "Tuberculosis": ["weight_loss", "night_sweats", "cough", "chest_pain"],
    "Pneumonia": ["breathlessness", "chest_pain", "high_fever", "cough"],
    "Heart attack": ["chest_pain", "breathlessness", "sweating"],
    "Hepatitis B": ["yellowish_skin", "yellowing_of_eyes", "fatigue"]
}

# Common diseases to prefer for generic symptoms
COMMON_DISEASE_PRIORITY = [
    "Common Cold",
    "Flu",
    "Allergy",
    "Viral Fever",
    "Bronchial Asthma",
    "GERD",
    "Migraine",
    "Typhoid"
]


def normalize_symptom(symptom):
    symptom = symptom.strip().lower().replace(" ", "_")
    original_text = symptom.replace("_", " ")
    return SYMPTOM_MAP.get(original_text, symptom)


# Model prediction
def predict_with_model(user_symptoms):
    input_vector = [0] * len(all_symptoms)

    for symptom in user_symptoms:
        if symptom in symptom_index:
            input_vector[symptom_index[symptom]] = 1

    input_vector = np.array(input_vector).reshape(1, -1)
    prediction = model.predict(input_vector)[0]
    predicted_disease = label_encoder.inverse_transform([prediction])[0]

    return predicted_disease


def predict_by_overlap(user_symptoms):
    disease_scores = defaultdict(int)

    for _, row in df.iterrows():
        disease = str(row["Disease"]).strip()
        disease_symptoms = set()

        for col in symptom_columns:
            value = row[col]
            if pd.notna(value):
                disease_symptoms.add(str(value).strip().lower())

        matched_count = len(set(user_symptoms) & disease_symptoms)
        disease_scores[disease] = max(disease_scores[disease], matched_count)

    ranked = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def is_severe_disease_allowed(disease, normalized_symptoms):
    if disease not in SEVERE_DISEASE_RULES:
        return True

    required_symptoms = SEVERE_DISEASE_RULES[disease]
    matched_required = [sym for sym in required_symptoms if sym in normalized_symptoms]
    return len(matched_required) >= 2


def reorder_common_diseases(ranked):
    common_list = []
    other_list = []

    for disease, score in ranked:
        if disease in COMMON_DISEASE_PRIORITY:
            common_list.append((disease, score))
        else:
            other_list.append((disease, score))

    common_list = sorted(common_list, key=lambda x: x[1], reverse=True)
    other_list = sorted(other_list, key=lambda x: x[1], reverse=True)

    return common_list + other_list


def get_preliminary_analysis(user_symptoms, top_n=3):
    normalized_symptoms = [normalize_symptom(symptom) for symptom in user_symptoms]
    normalized_symptoms = list(set(normalized_symptoms))

    ranked = predict_by_overlap(normalized_symptoms)

    # remove diseases with 0 match
    ranked = [(disease, score) for disease, score in ranked if score > 0]

    if not ranked:
        return {
            "status": "no_match",
            "message": "No close condition found. Please enter more specific symptoms.",
            "top_conditions": [],
            "normalized_symptoms": normalized_symptoms
        }

    # filter severe diseases unless enough support exists
    filtered_ranked = []
    for disease, score in ranked:
        if is_severe_disease_allowed(disease, normalized_symptoms):
            filtered_ranked.append((disease, score))

    if not filtered_ranked:
        filtered_ranked = ranked

    # if symptoms are very few, prefer common diseases
    if len(normalized_symptoms) <= 3:
        filtered_ranked = reorder_common_diseases(filtered_ranked)

    # keep only disease names, not scores
    top_conditions = [disease for disease, score in filtered_ranked[:top_n]]

    # if only few symptoms, show need more symptoms
    if len(normalized_symptoms) < 4:
        return {
            "status": "need_more_symptoms",
            "message": "This is a preliminary analysis. Please add more symptoms for better accuracy.",
            "top_conditions": top_conditions,
            "normalized_symptoms": normalized_symptoms
        }

    return {
        "status": "ok",
        "message": "Preliminary health condition analysis generated successfully.",
        "top_conditions": top_conditions,
        "normalized_symptoms": normalized_symptoms
    }


# Best condition for precautions/medicines
def predict_disease(user_symptoms):
    result = get_preliminary_analysis(user_symptoms, top_n=1)
    if result["top_conditions"]:
        return result["top_conditions"][0]
    return "No matching disease found"


# Top conditions for UI
def get_top_disease_matches(user_symptoms, top_n=3):
    result = get_preliminary_analysis(user_symptoms, top_n=top_n)
    return result["top_conditions"]


# Status/message for UI
def get_analysis_message(user_symptoms):
    result = get_preliminary_analysis(user_symptoms, top_n=3)
    return result["status"], result["message"], result["normalized_symptoms"]