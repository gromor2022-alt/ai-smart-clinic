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
# CUSTOM CSS (🔥 UI MAGIC)
# ---------------------------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}
.stButton>button {
    border-radius: 8px;
    background-color: #2563eb;
    color: white;
    padding: 10px 16px;
}
.stTextInput>div>div>input, .stTextArea textarea {
    border-radius: 8px;
}
h1, h2, h3 {
    color: #1e293b;
}
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# PASSWORD
# ---------------------------
PASSWORD = "clinicdemo"

def check_password():
    def password_entered():
        st.session_state["password_correct"] = st.session_state["password"] == PASSWORD

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
# OPENAI CLIENT
# ---------------------------
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ---------------------------
# HEADER
# ---------------------------
st.title("🏥 AI Smart Clinic")
st.caption("AI Powered Clinical Decision Support + ABDM Ready")

# HERO SECTION
st.markdown("""
<div class='card'>
<h3>AI Smart Clinic Dashboard</h3>
<p>AI-powered diagnosis, patient management & ABDM integration</p>
</div>
""", unsafe_allow_html=True)

st.image("https://images.unsplash.com/photo-1588776814546-1ffcf47267a5", use_column_width=True)

# ---------------------------
# KPI CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

def card(title, value):
    st.markdown(f"""
    <div class='card'>
    <h4>{title}</h4>
    <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

with c1: card("Patients Today", "86")
with c2: card("Avg Wait Time", "14 min")
with c3: card("Bed Occupancy", "79%")
with c4: card("Pending Reports", "12")

st.divider()

# ---------------------------
# ROLE
# ---------------------------
role = st.sidebar.selectbox("Select Role", ["Doctor","Admin","Nurse"])

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

# ---------------------------
# PATIENT INTAKE + ABHA
# ---------------------------
with tabs[0]:

    st.header("🩺 Patient Intake & AI Triage")

    age = st.number_input("Age",1,120)
    gender = st.selectbox("Gender",["Male","Female","Other"])
    symptoms = st.text_area("Symptoms")
    history = st.text_area("Medical History")

    st.markdown("### 🔗 ABHA Integration")

    if "abha_id" not in st.session_state:
        st.session_state.abha_id = None

    abha_mobile = st.text_input("Mobile Number")

    if st.button("Generate OTP"):
        st.success("OTP Sent (Demo Mode)")

    otp = st.text_input("Enter OTP")

    if st.button("Verify & Create ABHA"):
        fake_abha = "91-" + str(random.randint(1000,9999)) + "-" + str(random.randint(1000,9999))
        st.session_state.abha_id = fake_abha
        st.success(f"ABHA Created: {fake_abha}")

    if st.session_state.abha_id:
        st.info(f"Linked ABHA: {st.session_state.abha_id}")

    st.divider()

    if st.button("Generate AI Summary"):
        prompt=f"""
        Patient age {age}
        gender {gender}
        symptoms {symptoms}
        history {history}
        generate medical summary and diagnosis
        """

        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
        )

        result=response.choices[0].message.content
        st.write(result)

        if st.button("Download PDF"):
            temp=tempfile.NamedTemporaryFile(delete=False)
            c=canvas.Canvas(temp.name)
            c.drawString(100,750,"Patient Summary")
            c.drawString(100,720,result[:800])
            c.save()

            with open(temp.name,"rb") as f:
                st.download_button("Download",f,file_name="summary.pdf")

# ---------------------------
# MEDICAL SCRIBE
# ---------------------------
with tabs[1]:
    st.header("🧠 AI Medical Scribe")
    notes = st.text_area("Doctor Notes")

    if st.button("Generate Notes"):
        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":notes}]
        )
        st.write(response.choices[0].message.content)

# ---------------------------
# REPORT ANALYZER
# ---------------------------
with tabs[2]:
    st.header("🧪 Report Analyzer")
    report = st.text_area("Lab Report")

    if st.button("Analyze"):
        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":report}]
        )
        st.write(response.choices[0].message.content)

# ---------------------------
# PRESCRIPTION
# ---------------------------
with tabs[3]:
    st.header("💊 Prescription Safety")
    meds = st.text_area("Medicines")

    if st.button("Check"):
        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":meds}]
        )
        st.write(response.choices[0].message.content)
        st.error("⚠ Possible interaction")

# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
with tabs[4]:
    st.header("📊 Dashboard")

    df = pd.DataFrame({
        "Patient":["R Sharma","A Khan","M Gupta","S Patel"],
        "Department":["Cardio","General","Ortho","Derm"],
        "Wait":["12 min","8 min","5 min","20 min"]
    })
    st.dataframe(df)

    chart=pd.DataFrame({
        "Hour":["8AM","9AM","10AM","11AM","12PM"],
        "Patients":[5,18,30,22,14]
    })
    st.bar_chart(chart.set_index("Hour"))

# ---------------------------
# OPD
# ---------------------------
with tabs[5]:
    st.header("OPD Prediction")
    st.metric("Tomorrow Patients", random.randint(80,140))

# ---------------------------
# BED
# ---------------------------
with tabs[6]:
    st.header("Bed Management")
    beds=120
    occ=random.randint(80,110)
    st.metric("Total",beds)
    st.metric("Occupied",occ)
    st.metric("Available",beds-occ)

# ---------------------------
# APPOINTMENT
# ---------------------------
with tabs[7]:
    st.header("Appointment Optimizer")
    if st.button("Suggest"):
        st.write(["10:30 AM","11:15 AM","3:00 PM"])

# ---------------------------
# FOLLOW UP
# ---------------------------
with tabs[8]:
    st.header("Follow Up")
    name=st.text_input("Name")
    reason=st.text_area("Reason")

    if st.button("Generate"):
        response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":reason}]
        )
        st.success(response.choices[0].message.content)