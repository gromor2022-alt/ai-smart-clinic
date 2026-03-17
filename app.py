import streamlit as st
import pandas as pd
from openai import OpenAI

# ===============================
# AI CLIENT
# ===============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

st.set_page_config(page_title="AI Smart Clinic", layout="wide")

st.title("🏥 AI Smart Clinic")
st.write("AI-powered assistant for clinics and hospitals.")

# ===============================
# TABS
# ===============================

tab1, tab2, tab3, tab4 = st.tabs([
"Patient Intake",
"Report Analyzer",
"Prescription Safety",
"Admin Dashboard"
])

# ===============================
# TAB 1 — PATIENT INTAKE
# ===============================

with tab1:

    st.header("AI Patient Intake Assistant")

    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    symptoms = st.text_area("Symptoms")
    history = st.text_area("Medical History")

    if st.button("Generate Patient Summary"):

        prompt = f"""
        Patient age: {age}
        Gender: {gender}
        Symptoms: {symptoms}
        Medical history: {history}

        Generate a short medical summary with possible causes and suggested tests.
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.subheader("AI Generated Summary")
        st.write(result)

# ===============================
# TAB 2 — REPORT ANALYZER
# ===============================

with tab2:

    st.header("AI Medical Report Analyzer")

    report_text = st.text_area("Paste Lab Report Values")

    if st.button("Analyze Report"):

        prompt = f"""
        Analyze the following medical lab report values and explain abnormalities.

        {report_text}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.subheader("AI Report Analysis")
        st.write(result)

# ===============================
# TAB 3 — PRESCRIPTION CHECK
# ===============================

with tab3:

    st.header("Prescription Safety Checker")

    drugs = st.text_area("Enter medicines")

    if st.button("Check Prescription"):

        prompt = f"""
        Check the following medicines for interactions or safety warnings.

        {drugs}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.subheader("Safety Analysis")
        st.write(result)

# ===============================
# TAB 4 — ADMIN DASHBOARD
# ===============================

with tab4:

    st.header("Hospital Admin Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Beds", 120)
    col2.metric("Occupied Beds", 95)
    col3.metric("Available Beds", 25)

    st.write("### OPD Load Prediction")

    st.info("High patient inflow expected between 9 AM – 11 AM")

    st.write("### Pending Lab Reports")

    st.warning("14 lab reports pending more than 2 hours")