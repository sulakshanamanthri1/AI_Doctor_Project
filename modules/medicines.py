import pandas as pd
DATA_PATH = "data/disease_medicines.csv"
data = pd.read_csv(DATA_PATH)
def get_medicines(disease):
    result = data[data["Disease"].str.strip().str.lower() == disease.strip().lower()]
    if result.empty:
        return []
    medicines = []
    for _, row in result.iterrows():
        medicines.append({
            "Medicine": row["Medicine"] if pd.notna(row["Medicine"]) else "",
            "Dosage": row["Dosage"] if pd.notna(row["Dosage"]) else "",
            "Drug_Type": row["Drug_Type"] if pd.notna(row["Drug_Type"]) else ""
        })
    return medicines