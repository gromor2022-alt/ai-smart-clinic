import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI
import random
from reportlab.pdfgen import canvas
import tempfile

# ---------------------------
# DB SETUP
# ---------------------------
conn = sqlite3.connect("clinic.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT, password TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS patients(
name TEXT, age INTEGER, department TEXT, abha TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS beds(
total INTEGER, occupied INTEGER
)""")

conn.commit()

# default admin
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users VALUES('admin','admin123')")
    conn.commit()

# default beds
c.execute("SELECT * FROM beds")
if not c.fetchone():
    c.execute("INSERT INTO beds VALUES(120,80)")
    conn.commit()

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Smart Clinic", layout="wide")

# ---------------------------
# CSS
# ---------------------------
st.markdown("""
<style>
.main {background: linear-gradient(135deg,#eef2ff,#f8fafc);}
.card {background:white;padding:15px;border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.08);}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOGIN
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🏥 AI Smart Clinic Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        if c.fetchone():
            st.session_state.logged_in = True
        else:
            st.error("Invalid login")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------------------
# OPENAI
# ---------------------------
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ---------------------------
# HEADER
# ---------------------------
st.title("🏥 AI Smart Clinic")
st.markdown("<div class='card'><h3>ABDM Ready AI Clinic System</h3></div>", unsafe_allow_html=True)

# ---------------------------
# KPI
# ---------------------------
c1,c2,c3,c4 = st.columns(4)

c.execute("SELECT COUNT(*) FROM patients")
patients_count = c.fetchone()[0]

c.execute("SELECT total,occupied FROM beds")
beds = c.fetchone()

with c1: st.metric("Total Patients", patients_count)
with c2: st.metric("Beds Occupied", beds[1])
with c3: st.metric("Available Beds", beds[0]-beds[1])
with c4: st.metric("System Status","Active")

# ---------------------------
# TABS
# ---------------------------
tabs = st.tabs(["Patient Intake","Dashboard","Beds","AI Tools"])

# ---------------------------
# PATIENT
# ---------------------------
with tabs[0]:

    st.header("Patient Intake")

    name = st.text_input("Name")
    age = st.number_input("Age",1,120)
    dept = st.selectbox("Department",["Cardiology","General","Ortho"])

    st.subheader("ABHA")

    if "abha" not in st.session_state:
        st.session_state.abha = None

    if st.button("Generate OTP"):
        st.success("OTP Sent")

    otp = st.text_input("OTP")

    if st.button("Create ABHA"):
        abha = "91-"+str(random.randint(1000,9999))
        st.session_state.abha = abha
        st.success(f"ABHA: {abha}")

    if st.session_state.abha:
        st.info(f"Linked ABHA: {st.session_state.abha}")

    if st.button("Save Patient"):
        c.execute("INSERT INTO patients VALUES(?,?,?,?)",
                  (name,age,dept,st.session_state.abha))
        conn.commit()
        st.success("Patient Saved")

# ---------------------------
# DASHBOARD
# ---------------------------
with tabs[1]:

    st.header("Dashboard")

    df = pd.read_sql_query("SELECT * FROM patients", conn)
    st.dataframe(df)

    if not df.empty:
        st.bar_chart(df["department"].value_counts())

# ---------------------------
# BEDS
# ---------------------------
with tabs[2]:

    st.header("Bed Management")

    total,occupied = beds
    st.metric("Total", total)
    st.metric("Occupied", occupied)
    st.metric("Available", total-occupied)

    if st.button("Admit"):
        c.execute("UPDATE beds SET occupied=occupied+1")
        conn.commit()

    if st.button("Discharge"):
        c.execute("UPDATE beds SET occupied=occupied-1")
        conn.commit()

# ---------------------------
# AI TOOLS
# ---------------------------
with tabs[3]:

    st.header("AI Tools")

    text = st.text_area("Enter clinical notes")

    if st.button("Analyze"):
        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":text}]
        )
        st.write(response.choices[0].message.content)