import streamlit as st
import pandas as pd
from openai import OpenAI
from reportlab.pdfgen import canvas
import tempfile
import random

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(page_title="AI Smart Clinic", layout="wide")

# ---------------------------
# PASSWORD
# ---------------------------

PASSWORD = "clinicdemo"

def check_password():

    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:

        st.title("🏥 AI Smart Clinic")
        st.text_input("Enter Demo Password", type="password",
                      on_change=password_entered, key="password")
        return False

    elif not st.session_state["password_correct"]:

        st.text_input("Enter Demo Password", type="password",
                      on_change=password_entered, key="password")
        st.error("Incorrect Password")
        return False

    else:
        return True


if not check_password():
    st.stop()

# ---------------------------
# OPENROUTER CLIENT
# ---------------------------

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ---------------------------
# HEADER
# ---------------------------

st.title("🏥 AI Smart Clinic")
st.caption("AI Powered Clinical Decision Support System")

st.info("Demo Version — Not for real medical use")

st.divider()

# ---------------------------
# KPI DASHBOARD
# ---------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric("Patients Today", "86")
c2.metric("Avg Wait Time", "14 min")
c3.metric("Bed Occupancy", "79%")
c4.metric("Pending Reports", "12")

st.divider()

# ---------------------------
# USER ROLE
# ---------------------------

role = st.sidebar.selectbox(
"Select Role",
["Doctor","Admin","Nurse"]
)

# ---------------------------
# TABS
# ---------------------------

tabs = st.tabs([
"Patient Intake",
"Medical Scribe",
"Report Analyzer",
"Prescription Safety",
"Admin Dashboard",
"OPD Prediction",
"Bed Management",
"Appointment Optimizer",
"Patient Follow-up"
])

# --------------------------------------------------
# PATIENT INTAKE
# --------------------------------------------------

with tabs[0]:

    st.header("🩺 Patient Intake & AI Triage")

    age = st.number_input("Age",1,120)

    gender = st.selectbox("Gender",["Male","Female","Other"])

    symptoms = st.text_area("Symptoms")

    history = st.text_area("Medical History")

    if st.button("Generate Summary"):

        prompt=f"""
        Patient age {age}
        gender {gender}

        symptoms {symptoms}

        history {history}

        generate medical summary and possible diagnosis
        """

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content

        st.write(result)

        st.progress(0.82)

        if st.button("Download PDF"):

            temp=tempfile.NamedTemporaryFile(delete=False)

            c=canvas.Canvas(temp.name)

            c.drawString(100,750,"Patient Summary")

            c.drawString(100,720,result[:800])

            c.save()

            with open(temp.name,"rb") as f:

                st.download_button(
                "Download",
                f,
                file_name="summary.pdf"
                )

# --------------------------------------------------
# MEDICAL SCRIBE
# --------------------------------------------------

with tabs[1]:

    st.header("🧠 AI Medical Scribe")

    notes = st.text_area("Doctor Dictation")

    if st.button("Generate Notes"):

        prompt=f"convert this into structured clinical notes {notes}"

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)

        st.progress(0.88)

# --------------------------------------------------
# REPORT ANALYZER
# --------------------------------------------------

with tabs[2]:

    st.header("🧪 Medical Report Analyzer")

    report = st.text_area("Paste Lab Results")

    if st.button("Analyze"):

        prompt=f"analyze medical lab report {report}"

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)

        st.progress(0.84)

# --------------------------------------------------
# PRESCRIPTION CHECK
# --------------------------------------------------

with tabs[3]:

    st.header("💊 Prescription Safety")

    meds = st.text_area("Enter Medicines")

    if st.button("Check Interaction"):

        prompt=f"check drug interaction {meds}"

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)

        st.error("⚠ Possible interaction detected")

# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

with tabs[4]:

    st.header("📊 Hospital Dashboard")

    queue=pd.DataFrame({

    "Patient":["R Sharma","A Khan","M Gupta","S Patel"],
    "Department":["Cardiology","General","Ortho","Dermatology"],
    "Wait Time":["12 min","8 min","5 min","20 min"]

    })

    st.dataframe(queue)

    opd=pd.DataFrame({

    "Hour":["8AM","9AM","10AM","11AM","12PM"],
    "Patients":[5,18,30,22,14]

    })

    st.bar_chart(opd.set_index("Hour"))

# --------------------------------------------------
# OPD PREDICTION
# --------------------------------------------------

with tabs[5]:

    st.header("AI OPD Queue Prediction")

    tomorrow=random.randint(80,140)

    st.metric("Predicted Patients Tomorrow",tomorrow)

    st.warning("High load expected in Cardiology")

# --------------------------------------------------
# BED MANAGEMENT
# --------------------------------------------------

with tabs[6]:

    st.header("Bed Management System")

    beds=120

    occupied=random.randint(80,110)

    available=beds-occupied

    st.metric("Total Beds",beds)

    st.metric("Occupied Beds",occupied)

    st.metric("Available Beds",available)

# --------------------------------------------------
# APPOINTMENT OPTIMIZER
# --------------------------------------------------

with tabs[7]:

    st.header("AI Appointment Optimizer")

    doctor=st.selectbox("Select Doctor",

    ["Cardiology","Orthopedic","Dermatology","General"])

    if st.button("Suggest Slots"):

        slots=[

        "10:30 AM",

        "11:15 AM",

        "12:40 PM",

        "3:00 PM"

        ]

        st.write("Recommended Slots")

        st.write(slots)

# --------------------------------------------------
# FOLLOW UP
# --------------------------------------------------

with tabs[8]:

    st.header("📩 Patient Follow-up")

    name=st.text_input("Patient Name")

    reason=st.text_area("Follow up reason")

    if st.button("Generate Message"):

        prompt=f"write whatsapp follow up message for {name} regarding {reason}"

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        st.success(response.choices[0].message.content)