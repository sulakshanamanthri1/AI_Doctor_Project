import streamlit as st
import pandas as pd

from modules.predictor import (
    predict_disease,
    get_top_disease_matches,
    get_analysis_message
)
from modules.precautions import get_precautions
from modules.medicines import get_medicines
from modules.adult_care import get_mental_health_tip

st.set_page_config(
    page_title="AI Virtual Doctor System",
    page_icon="",
    layout="wide"
)
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef7ff, #f8f3ff, #fff8ef);
    background-attachment: fixed;
}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem;
    margin-top: 0rem !important;
}

header[data-testid="stHeader"] {
    display: none;
}

section[data-testid="stToolbar"] {
    display: none;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #4a148c;
    margin-bottom: 8px;
}

.sub-title {
    text-align: center;
    font-size: 18px;
    color: #455a64;
    margin-bottom: 25px;
}

.glass-card {
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(10px);
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.10);
    border: 1px solid rgba(255,255,255,0.5);
    margin-bottom: 20px;
}

.section-heading {
    font-size: 24px;
    font-weight: 700;
    color: #6a1b9a;
    margin-bottom: 12px;
}

.analysis-box {
    background: linear-gradient(135deg, #e8eaf6, #f3e5f5);
    padding: 18px;
    border-radius: 18px;
    color: #4a148c;
    font-size: 24px;
    font-weight: 700;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

.match-pill {
    display: inline-block;
    background: #ede7f6;
    color: #4a148c;
    border-radius: 999px;
    padding: 8px 14px;
    margin: 6px 8px 6px 0;
    font-size: 14px;
    font-weight: 600;
}

.med-box {
    background: #ffffff;
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    border: 1px solid #eeeeee;
    margin-bottom: 12px;
}

.footer-note {
    text-align: center;
    color: #546e7a;
    font-size: 14px;
    margin-top: 20px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6a1b9a, #283593);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    padding: 12px 18px;
    font-size: 16px;
    font-weight: 700;
    background: linear-gradient(90deg, #7b1fa2, #3949ab);
    color: white;
    box-shadow: 0 6px 14px rgba(0,0,0,0.15);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #6a1b9a, #303f9f);
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stMultiSelect div[data-baseweb="select"] > div {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_symptoms():
    df = pd.read_csv("data/DiseaseAndSymptoms.csv")
    symptom_columns = [col for col in df.columns if col.startswith("Symptom_")]

    all_symptoms = set()
    for col in symptom_columns:
        all_symptoms.update(
            df[col].dropna().astype(str).str.strip().str.lower().tolist()
        )

    return sorted(list(all_symptoms))


all_symptoms = load_all_symptoms()



st.markdown('<div class="main-title"> AI Virtual Doctor System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Analysis for Preliminary Health Conditions and Mental Well-being Support</div>',
    unsafe_allow_html=True
)
st.sidebar.title("Navigation")
module = st.sidebar.radio(
    "Choose Module",
    ["Preliminary Health Analysis", "Adult Care / Mental Well-being"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("### Features")
st.sidebar.markdown("""
- Preliminary health analysis  
- Top possible conditions  
- Precautions  
- Medicines  
- Mental well-being support    
""")
if module == "Preliminary Health Analysis":
    with st.container():
        st.markdown('<div class="section-heading"> Preliminary Health Condition Analysis</div>', unsafe_allow_html=True)
        st.write("Select symptoms from the list and optionally add manual symptoms.")

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_symptoms = st.multiselect(
                "Select Symptoms",
                all_symptoms,
                placeholder="Choose symptoms from dropdown"
            )

        with col2:
            typed_symptoms = st.text_area(
                "Type extra symptoms",
                placeholder="Example:\nfever, cold, cough",
                height=120
            )

        predict_btn = st.button("Analyze Condition")

    if predict_btn:
        manual_symptoms = []
        if typed_symptoms.strip():
            manual_symptoms = [sym.strip() for sym in typed_symptoms.split(",") if sym.strip()]

        user_symptoms = selected_symptoms + manual_symptoms
        user_symptoms = list(set([sym.strip().lower() for sym in user_symptoms if sym.strip()]))

        if not user_symptoms:
            st.warning("Please select or enter at least one symptom.")
        else:
            status, message, normalized_symptoms = get_analysis_message(user_symptoms)
            top_matches = get_top_disease_matches(user_symptoms, top_n=3)

            best_condition = predict_disease(user_symptoms)
            precautions = get_precautions(best_condition)
            medicines = get_medicines(best_condition)

            st.markdown(
                '<div class="analysis-box">Preliminary Condition Analysis</div>',
                unsafe_allow_html=True
            )

            if status == "need_more_symptoms":
                st.warning(message)
            elif status == "no_match":
                st.error(message)
            else:
                st.success(message)

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown('<div class="section-heading"> Entered Symptoms</div>', unsafe_allow_html=True)
                for symptom in normalized_symptoms:
                    st.write(f"- {symptom}")

            with col_b:
                st.markdown('<div class="section-heading"> Possible Conditions</div>', unsafe_allow_html=True)

                if top_matches:
                    for i, disease in enumerate(top_matches, 1):
                        st.write(f"**{i}. {disease}**")
                else:
                    st.write("No matching conditions found.")

            if best_condition != "No matching disease found":
                st.markdown(f"### Suggested Primary Condition for Guidance: **{best_condition}**")

                col_c, col_d = st.columns(2)

                with col_c:
                    st.markdown('<div class="section-heading">🛡 Precautions</div>', unsafe_allow_html=True)
                    if precautions:
                        for i, precaution in enumerate(precautions, 1):
                            st.write(f"{i}. {precaution}")
                    else:
                        st.write("No precautions found.")

                with col_d:
                    st.markdown('<div class="section-heading"> Medicines</div>', unsafe_allow_html=True)
                    if medicines:
                        for i, med in enumerate(medicines, 1):
                            st.markdown(f"""
                            <div class="med-box">
                                <b>{i}. Medicine:</b> {med['Medicine']}<br>
                                <b>Dosage:</b> {med['Dosage']}<br>
                                <b>Drug Type:</b> {med['Drug_Type']}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.write("No medicines found.")

            st.warning(" This system provides preliminary health condition analysis only and is not a substitute for professional medical advice.")
            st.info("For better accuracy, enter more symptoms instead of only 2 or 3 general symptoms like fever, cough, or cold.")

elif module == "Adult Care / Mental Well-being":
    st.markdown('<div class="section-heading"> Mental Well-being</div>', unsafe_allow_html=True)
    st.write("Share how you are feeling and get supportive guidance.")

    if "mental_response" not in st.session_state:
        st.session_state.mental_response = ""

    mental_input = st.text_area(
        "How are you feeling today?",
        placeholder="Example: stressed, anxious, lonely",
        height=180,
        key="mental_input"
    )

    support_btn = st.button("Get Support Tip", key="support_btn")

    if support_btn:
        if not mental_input.strip():
            st.session_state.mental_response = "Please enter how you are feeling."
        else:
            response = get_mental_health_tip(mental_input)
            if not response:
                response = "Please share a little more about how you are feeling."
            st.session_state.mental_response = response

    if st.session_state.mental_response:
        st.markdown('<div class="section-heading">Supportive Response</div>', unsafe_allow_html=True)
        st.info(st.session_state.mental_response)
        st.warning("This module provides general mental well-being support only and is not a substitute for professional care.")