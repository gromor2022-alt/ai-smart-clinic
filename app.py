import streamlit as st
import pandas as pd
from openai import OpenAI
from reportlab.pdfgen import canvas
import tempfile

# ==============================
# PASSWORD PROTECTION
# ==============================

PASSWORD = "clinicdemo"

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Demo Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Demo Password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect Password")
        return False
    else:
        return True


if not check_password():
    st.stop()

# ==============================
# OPENROUTER AI CLIENT
# ==============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ==============================
# PAGE SETTINGS
# ==============================

st.set_page_config(page_title="AI Smart Clinic", layout="wide")

st.title("🏥 AI Smart Clinic")

st.markdown("""
AI-powered assistant designed to help clinics and hospitals improve patient intake,
analyze medical reports, check prescription safety, and monitor hospital operations.
""")

# ==============================
# TABS
# ==============================

tab1, tab2, tab3, tab4 = st.tabs([
"Patient Intake",
"Report Analyzer",
"Prescription Safety",
"Admin Dashboard"
])

# ==============================
# TAB 1 — PATIENT INTAKE
# ==============================

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

        Generate a short clinical summary, possible causes and suggested tests.
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.subheader("AI Generated Summary")
        st.write(result)

        # TRIAGE SEVERITY

        severity_prompt = f"""
        Based on these symptoms determine severity: Mild, Moderate, or Urgent.

        Symptoms:
        {symptoms}
        """

        severity_response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": severity_prompt}]
        )

        severity = severity_response.choices[0].message.content

        st.subheader("Triage Severity")
        st.success(severity)

        # PDF DOWNLOAD

        if st.button("Generate Patient PDF"):

            temp_file = tempfile.NamedTemporaryFile(delete=False)

            c = canvas.Canvas(temp_file.name)
            c.drawString(100, 750, "AI Smart Clinic - Patient Summary")
            c.drawString(100, 720, result)

            c.save()

            with open(temp_file.name, "rb") as file:
                st.download_button(
                    label="Download Patient Report",
                    data=file,
                    file_name="patient_summary.pdf"
                )

# ==============================
# TAB 2 — REPORT ANALYZER
# ==============================

with tab2:

    st.header("AI Medical Report Analyzer")

    report_text = st.text_area("Paste Lab Report Values")

    if st.button("Analyze Report"):

        prompt = f"""
        Analyze the following medical lab report values and highlight abnormalities.

        {report_text}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        st.subheader("AI Report Analysis")
        st.write(result)

# ==============================
# TAB 3 — PRESCRIPTION CHECKER
# ==============================

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

# ==============================
# TAB 4 — ADMIN DASHBOARD
# ==============================

with tab4:

    st.header("Hospital Admin Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Beds", 120)
    col2.metric("Occupied Beds", 95)
    col3.metric("Available Beds", 25)

    st.write("### OPD Traffic Today")

    data = pd.DataFrame({
        "Hour": ["8AM","9AM","10AM","11AM","12PM","1PM"],
        "Patients":[5,18,30,22,14,9]
    })

    st.bar_chart(data.set_index("Hour"))

    st.write("### Pending Lab Reports")

    st.warning("14 lab reports pending more than 2 hours")