import pandas as pd
DATA_PATH = "data/disease_precautions.csv"
data = pd.read_csv(DATA_PATH)
def get_precautions(disease):
    result = data[data["Disease"].str.strip().str.lower() == disease.strip().lower()]
    if result.empty:
        return []
    precautions = []
    precaution_columns = [col for col in data.columns if col.startswith("Precaution_")]
    for col in precaution_columns:
        value = result.iloc[0][col]
        if pd.notna(value):
            precautions.append(value)
    return precautions