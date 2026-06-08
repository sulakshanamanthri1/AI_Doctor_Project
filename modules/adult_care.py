import json
import re
import difflib


def load_mental_health_data(json_path="data/adult_care/combined_dataset_fixed.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def preprocess_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_keyword_map(data):
    keyword_map = {}

    for item in data:
        question = preprocess_text(item["question"])
        answer = item["answer"]

        if "stressed" in question or "stress" in question:
            keywords = ["stress", "stressed", "pressure", "tense"]
        elif "anxious" in question or "anxiety" in question:
            keywords = ["anxious", "anxiety", "nervous", "worried", "panic"]
        elif "sleep" in question:
            keywords = ["sleep", "insomnia", "sleepless", "cannot sleep", "cant sleep", "awake"]
        elif "depressed" in question or "depression" in question:
            keywords = ["depressed", "depression", "sad", "hopeless", "low"]
        elif "lonely" in question:
            keywords = ["lonely", "alone", "isolated"]
        elif "overwhelmed" in question:
            keywords = ["overwhelmed", "burdened", "too much", "exhausted mentally"]
        elif "tired" in question:
            keywords = ["tired", "fatigue", "exhausted", "weak"]
        elif "overthinking" in question:
            keywords = ["overthinking", "overthink", "thinking too much", "racing thoughts"]
        else:
            keywords = question.split()

        for keyword in keywords:
            keyword_map[keyword] = answer

    return keyword_map


def get_mental_health_tip(user_input, json_path="data/adult_care/combined_dataset_fixed.json"):
    data = load_mental_health_data(json_path)
    keyword_map = build_keyword_map(data)

    user_input_clean = preprocess_text(user_input)

    # 1. direct keyword search
    for keyword, answer in keyword_map.items():
        if keyword in user_input_clean:
            return answer

    # 2. fuzzy match fallback
    all_keywords = list(keyword_map.keys())
    best_match = difflib.get_close_matches(user_input_clean, all_keywords, n=1, cutoff=0.6)

    if best_match:
        return keyword_map[best_match[0]]

    # 3. default response
    return "I'm sorry you're feeling this way. Please take some rest, talk to someone you trust, and consider professional support if these feelings continue."