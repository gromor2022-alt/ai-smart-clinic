import streamlit as st
import pandas as pd
from openai import OpenAI
from reportlab.pdfgen import canvas
import tempfile

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(page_title="AI Smart Clinic", layout="wide")

# =========================
# PASSWORD PROTECTION
# =========================

PASSWORD = "clinicdemo"

def check_password():

    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("AI Smart Clinic Demo")
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

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# =========================
# HEADER
# =========================

st.title("🏥 AI Smart Clinic")
st.caption("Intelligent Clinical Decision Support System")

st.info("Demo Version — For demonstration only. Not for clinical use.")

st.divider()

# =========================
# KPI DASHBOARD
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Patients Today", "86")
col2.metric("Avg Wait Time", "14 min")
col3.metric("Bed Occupancy", "79%")
col4.metric("Pending Reports", "12")

st.divider()

# =========================
# USER ROLE
# =========================

mode = st.sidebar.selectbox(
"Select User Role",
["Doctor","Admin","Nurse"]
)

# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
"🩺 Patient Intake",
"🧠 Medical Scribe",
"🧪 Report Analyzer",
"💊 Prescription Safety",
"📊 Admin Dashboard",
"📩 Patient Follow-up"
])

# =========================
# TAB 1 PATIENT INTAKE
# =========================

with tab1:

    st.header("Patient Intake & AI Triage")

    age = st.number_input("Age",1,120)
    gender = st.selectbox("Gender",["Male","Female","Other"])

    symptoms = st.text_area("Symptoms")

    history = st.text_area("Medical History")

    if st.button("Generate Patient Summary"):

        prompt=f"""
        Patient age {age}
        Gender {gender}

        Symptoms:
        {symptoms}

        History:
        {history}

        Generate medical summary, possible causes and suggested tests.
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        with st.expander("View AI Medical Summary"):

            st.write(result)

        st.progress(0.82)
        st.caption("AI Confidence Score: 82%")

        if st.button("Generate Patient PDF"):

            temp_file = tempfile.NamedTemporaryFile(delete=False)

            c = canvas.Canvas(temp_file.name)

            c.drawString(100,750,"AI Smart Clinic Patient Summary")
            c.drawString(100,720,result[:800])

            c.save()

            with open(temp_file.name,"rb") as f:

                st.download_button(
                    label="Download Summary PDF",
                    data=f,
                    file_name="patient_summary.pdf"
                )

# =========================
# TAB 2 MEDICAL SCRIBE
# =========================

with tab2:

    st.header("AI Medical Scribe")

    notes = st.text_area("Doctor Dictation")

    if st.button("Generate Clinical Notes"):

        prompt=f"""
        Convert doctor dictation into structured clinical notes

        {notes}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        with st.expander("Clinical Notes"):

            st.write(result)

        st.progress(0.88)
        st.caption("AI Confidence Score: 88%")

# =========================
# TAB 3 REPORT ANALYZER
# =========================

with tab3:

    st.header("AI Medical Report Analyzer")

    report = st.text_area("Paste Lab Report Values")

    if st.button("Analyze Report"):

        prompt=f"""
        Analyze these medical lab results and highlight abnormalities

        {report}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        with st.expander("Report Analysis"):

            st.write(result)

        st.progress(0.84)
        st.caption("AI Confidence Score: 84%")

# =========================
# TAB 4 PRESCRIPTION CHECK
# =========================

with tab4:

    st.header("Prescription Safety Checker")

    meds = st.text_area("Enter Medicines")

    if st.button("Check Drug Interaction"):

        prompt=f"""
        Check these medicines for interactions or safety risks

        {meds}
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        with st.expander("Drug Safety Analysis"):

            st.write(result)

        st.error("⚠ Potential interaction detected")

# =========================
# TAB 5 ADMIN DASHBOARD
# =========================

with tab5:

    st.header("Hospital Operations Dashboard")

    st.subheader("Live Patient Queue")

    queue = pd.DataFrame({
    "Patient":["R Sharma","A Khan","M Gupta","S Patel"],
    "Department":["Cardiology","General","Orthopedics","Dermatology"],
    "Wait Time":["12 min","8 min","5 min","20 min"]
    })

    st.dataframe(queue)

    st.subheader("OPD Traffic")

    opd = pd.DataFrame({
    "Hour":["8AM","9AM","10AM","11AM","12PM"],
    "Patients":[5,18,30,22,14]
    })

    st.bar_chart(opd.set_index("Hour"))

    st.warning("⚠ High patient load detected in Cardiology")

# =========================
# TAB 6 PATIENT FOLLOWUP
# =========================

with tab6:

    st.header("AI Patient Follow-up Generator")

    name = st.text_input("Patient Name")

    reason = st.text_area("Follow-up Reason")

    if st.button("Generate Follow-up Message"):

        prompt=f"""
        Write a polite followup message for patient {name}

        reason: {reason}

        The message should be suitable for WhatsApp
        """

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        st.success(result)