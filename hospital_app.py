# app.py — Smart Hospital Patient Navigator
# Structured for teaching: each section has one job

import streamlit as st
import pandas as pd
import pickle

# ─────────────────────────────────────────────
# SECTION 1: LOAD MODEL
# One function, one job — loads the saved ML model
# ─────────────────────────────────────────────

@st.cache_resource
def load_model():
    with open('hospital_model.pkl', 'rb') as f:
        return pickle.load(f)

bundle = load_model()

# Unpack everything from the model bundle with clear names
model         = bundle['model']
scaler        = bundle['scaler']
features      = bundle['features']
cols_to_scale = bundle['cols_to_scale']
dept_map_inv  = bundle['dept_map_inv']   # number → department name
gender_map    = bundle['gender_map']     # "Male"/"Female" → 0/1
temp_map      = bundle['temp_map']
hr_map        = bundle['hr_map']
dur_map       = bundle['dur_map']
cc_map        = bundle['cc_map']


# ─────────────────────────────────────────────
# SECTION 2: DEPARTMENT INFO
# A plain dictionary — easy to read and extend
# ─────────────────────────────────────────────

DEPT_INFO = {
    'Respiratory Medicine': {
        'icon': '🫁', 'color': '#0284c7',
        'desc': 'Specialises in conditions affecting the lungs and airways.',
        'steps': ['Visit Level 2, Wing B', 'Estimated wait: 15–25 min', 'Please wear a mask'],
    },
    'Cardiology': {
        'icon': '❤️', 'color': '#dc2626',
        'desc': 'Specialises in heart and cardiovascular conditions.',
        'steps': ['Visit Level 3, Wing A', 'Estimated wait: 20–30 min', 'Bring any previous ECG reports'],
    },
    'Gastroenterology': {
        'icon': '🫃', 'color': '#d97706',
        'desc': 'Specialises in digestive system and abdominal conditions.',
        'steps': ['Visit Level 1, Wing C', 'Estimated wait: 10–20 min', 'Avoid eating before consultation'],
    },
    'Neurology': {
        'icon': '🧠', 'color': '#7c3aed',
        'desc': 'Specialises in brain, spine, and nervous system conditions.',
        'steps': ['Visit Level 4, Wing A', 'Estimated wait: 25–35 min', 'Bring list of current medications'],
    },
    'General Medicine': {
        'icon': '🩺', 'color': '#059669',
        'desc': 'Handles general health concerns and non-specialist conditions.',
        'steps': ['Visit Level 1, Wing A', 'Estimated wait: 10–15 min', 'Registration desk is open 24/7'],
    },
    'Dermatology': {
        'icon': '🔬', 'color': '#b45309',
        'desc': 'Specialises in skin, hair, and nail conditions.',
        'steps': ['Visit Level 2, Wing D', 'Estimated wait: 15–20 min', 'Bring photos of affected area if possible'],
    },
}


# ─────────────────────────────────────────────
# SECTION 3: PREDICTION LOGIC
# Pure Python — no Streamlit, no HTML
# Students can test this function in isolation
# ─────────────────────────────────────────────

def predict_department(inputs: dict) -> tuple[str, float, list]:
    """
    Takes a dict of patient inputs.
    Returns: (department_name, confidence_percent, all_probabilities)
    """
    # Step 1: Build a one-row DataFrame from the inputs
    patient_df = pd.DataFrame([inputs])

    # Step 2: Scale only the numeric columns (age, etc.)
    patient_df[cols_to_scale] = scaler.transform(patient_df[cols_to_scale])

    # Step 3: Run the model
    predicted_class = model.predict(patient_df[features])[0]
    all_proba       = model.predict_proba(patient_df[features])[0]

    # Step 4: Convert outputs to human-readable values
    dept_name  = dept_map_inv[predicted_class]
    confidence = all_proba[predicted_class] * 100

    return dept_name, confidence, all_proba


# ─────────────────────────────────────────────
# SECTION 4: USER INTERFACE
# Each sub-section is a separate function
# Makes it easy to find, edit, and explain each part
# ─────────────────────────────────────────────

def show_header():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a8a, #1a56db, #0ea5e9);
                    padding: 3rem 2rem; text-align: center; margin-bottom: 2rem;">
            <p style="color: rgba(255,255,255,0.7); font-size: 13px; text-transform: uppercase;">
                🏥 Future Classroom · Machine Learning
            </p>
            <h1 style="color: white; font-size: 36px; margin: 8px 0;">
                Smart Hospital Patient Navigator
            </h1>
            <p style="color: rgba(255,255,255,0.85); font-size: 18px;">
                Find the Right Department for Your Symptoms
            </p>
        </div>
    """, unsafe_allow_html=True)


def show_symptom_section():
    """Returns a dict of symptom checkboxes {symptom_name: True/False}"""
    st.subheader("1. What are your main symptoms?")

    col1, col2, col3, col4 = st.columns(4)
    symptoms = {}

    with col1:
        symptoms['fever'] = st.checkbox("🌡️ Fever")
        symptoms['cough'] = st.checkbox("🤧 Cough")
    with col2:
        symptoms['headache']   = st.checkbox("🤕 Headache")
        symptoms['chest_pain'] = st.checkbox("💔 Chest Pain")
    with col3:
        symptoms['stomach_pain']     = st.checkbox("🤢 Stomach Pain")
        symptoms['shortness_breath'] = st.checkbox("😮‍💨 Shortness of Breath")
    with col4:
        symptoms['nausea_vomiting'] = st.checkbox("🤮 Nausea / Vomiting")
        symptoms['dizziness']       = st.checkbox("😵 Dizziness")

    col5, _, _, _ = st.columns(4)
    with col5:
        symptoms['skin_rash'] = st.checkbox("🔴 Skin Rash")

    return symptoms


def show_duration_section():
    """Returns chief_complaint and duration strings"""
    st.subheader("2. How long have you had these symptoms?")

    col1, col2 = st.columns(2)
    with col1:
        chief_complaint = st.selectbox("Chief complaint", options=list(cc_map.keys()))
    with col2:
        duration = st.selectbox("Duration", options=list(dur_map.keys()), index=1)

    return chief_complaint, duration


def show_severity_section():
    """Returns temperature and heart rate strings"""
    st.subheader("3. How would you rate the severity?")

    col1, col2 = st.columns(2)
    with col1:
        temperature = st.selectbox("Temperature", options=list(temp_map.keys()), index=1)
    with col2:
        heart_rate = st.selectbox("Heart rate", options=list(hr_map.keys()), index=1)

    return temperature, heart_rate


def show_history_section():
    """Returns a dict of medical history checkboxes"""
    st.subheader("4. Do you have any of the following?")

    col1, col2, col3, _ = st.columns(4)
    history = {}
    with col1: history['hypertension']  = st.checkbox("🩺 High Blood Pressure")
    with col2: history['heart_disease'] = st.checkbox("❤️ Heart Disease")
    with col3: history['asthma']        = st.checkbox("💨 Asthma")

    return history


def show_patient_info_section():
    """Returns age (int) and gender (str)"""
    st.subheader("5. Patient Information")

    col1, col2 = st.columns(2)
    with col1:
        age    = st.number_input("Age", min_value=1, max_value=120, value=35)
    with col2:
        gender = st.selectbox("Gender", options=['Female', 'Male'])

    return age, gender


def show_result(dept_name: str, confidence: float, all_proba):
    """Displays the prediction result card and confidence bars"""
    info = DEPT_INFO[dept_name]

    st.markdown("---")
    st.markdown("### AI Recommendation")
    st.caption("Based on the information you provided")

    result_col, proba_col = st.columns([3, 2])

    # — Left column: main recommendation card
    with result_col:
        steps_html = "".join(
            f'<p>📍 {step}</p>' for step in info['steps']
        )
        st.markdown(f"""
            <div style="background: #0b202e; border: 1.5px solid #7dd3fc;
                        border-radius: 16px; padding: 28px;">
                <div style="font-size: 44px;">{info['icon']}</div>
                <h2 style="color: {info['color']};">{dept_name}</h2>
                <p>{info['desc']}</p>
                <p>Your reported symptoms and vitals match patients typically directed here.</p>
                <strong>What to do next:</strong>
                {steps_html}
                <p style="font-size: 12px; color: #6b7280; margin-top: 16px;">
                    ⚠️ This is an AI suggestion, not a medical diagnosis.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # — Right column: confidence bars for all departments
    with proba_col:
        st.markdown("**Confidence by department**")

        # Sort departments from highest to lowest confidence
        sorted_depts = sorted(dept_map_inv.items(), key=lambda x: all_proba[x[0]], reverse=True)

        for dept_idx, dname in sorted_depts:
            pct      = all_proba[dept_idx] * 100
            is_top   = (dname == dept_name)
            bar_color = DEPT_INFO[dname]['color'] if is_top else '#e5e7eb'
            label     = f"**{dname}**" if is_top else dname

            st.markdown(f"{DEPT_INFO[dname]['icon']} {label} — {pct:.1f}%")
            st.markdown(f"""
                <div style="background:#f3f4f6; border-radius:6px; height:8px; margin-bottom:10px;">
                    <div style="background:{bar_color}; width:{pct}%; height:100%; border-radius:6px;"></div>
                </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN — the script entry point
# This is the only place that calls Streamlit's
# form and stitches everything together
# ─────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Smart Hospital Patient Navigator", page_icon="🏥", layout="wide")

    show_header()

    with st.form("triage_form"):
        symptoms        = show_symptom_section()
        chief_complaint, duration = show_duration_section()
        temperature, heart_rate  = show_severity_section()
        history         = show_history_section()
        age, gender     = show_patient_info_section()

        submitted = st.form_submit_button("Get AI Recommendation →")

    if submitted:
        # Build the flat input dict the model expects
        # (encoding string values to numbers using the maps from the model bundle)
        inputs = {
            'age'              : age,
            'gender'           : gender_map.get(gender, 0),
            'temperature_level': temp_map.get(temperature, 1),
            'heart_rate_level' : hr_map.get(heart_rate, 1),
            'duration'         : dur_map.get(duration, 1),
            'chief_complaint'  : cc_map.get(chief_complaint, 9),
            **{k: int(v) for k, v in symptoms.items()},   # convert True/False → 1/0
            **{k: int(v) for k, v in history.items()},
        }

        dept_name, confidence, all_proba = predict_department(inputs)
        show_result(dept_name, confidence, all_proba)


if __name__ == "__main__":
    main()
