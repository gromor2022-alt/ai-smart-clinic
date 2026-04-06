import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI
import random

# ---------------- DB ----------------
conn = sqlite3.connect("clinic.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, role TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS patients(name TEXT, age INT, dept TEXT, abha TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS beds(total INT, occupied INT)")
c.execute("CREATE TABLE IF NOT EXISTS billing(name TEXT, amount REAL)")

conn.commit()

# default users
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users VALUES('admin','admin123','Admin')")
    c.execute("INSERT INTO users VALUES('doctor','doc123','Doctor')")
    conn.commit()

# default beds
c.execute("SELECT * FROM beds")
if not c.fetchone():
    c.execute("INSERT INTO beds VALUES(120,80)")
    conn.commit()

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏥 AI Smart Clinic Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
        result = c.fetchone()
        if result:
            st.session_state.logged_in = True
            st.session_state.role = result[0]
        else:
            st.error("Invalid credentials")
    st.stop()

# ---------------- OPENAI ----------------
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ---------------- HEADER ----------------
st.title("🏥 AI Smart Clinic")
st.subheader(f"Logged in as: {st.session_state.role}")

# ---------------- KPI ----------------
c1,c2,c3,c4 = st.columns(4)

patients_df = pd.read_sql_query("SELECT * FROM patients", conn)

c.execute("SELECT total,occupied FROM beds")
beds = c.fetchone()

c.execute("SELECT SUM(amount) FROM billing")
revenue = c.fetchone()[0] or 0

with c1: st.metric("Patients", len(patients_df))
with c2: st.metric("Beds Occupied", beds[1])
with c3: st.metric("Available Beds", beds[0]-beds[1])
with c4: st.metric("Revenue ₹", round(revenue,2))

# ---------------- TABS ----------------
tabs = st.tabs([
"Patient Intake",
"Medical Scribe",
"Report Analyzer",
"Prescription",
"Dashboard",
"Billing",
"Beds"
])

# ---------------- PATIENT ----------------
with tabs[0]:

    st.header("Patient Intake")

    name = st.text_input("Name")
    age = st.number_input("Age",1,120)
    dept = st.selectbox("Department",["Cardiology","General","Ortho"])

    if st.button("Generate ABHA"):
        abha = "91-"+str(random.randint(1000,9999))
        st.session_state.abha = abha
        st.success(f"ABHA: {abha}")

    if st.button("Save Patient"):
        c.execute("INSERT INTO patients VALUES(?,?,?,?)",
                  (name,age,dept,st.session_state.get("abha")))
        conn.commit()
        st.success("Saved")

# ---------------- SCRIBE ----------------
with tabs[1]:
    st.header("AI Medical Scribe")
    notes = st.text_area("Doctor Notes")

    if st.button("Generate"):
        res = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":notes}]
        )
        st.write(res.choices[0].message.content)

# ---------------- ANALYZER ----------------
with tabs[2]:
    st.header("Report Analyzer")
    report = st.text_area("Report")

    if st.button("Analyze"):
        res = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":report}]
        )
        st.write(res.choices[0].message.content)

# ---------------- PRESCRIPTION ----------------
with tabs[3]:
    st.header("Prescription Safety")
    meds = st.text_area("Medicines")

    if st.button("Check"):
        res = client.chat.completions.create(
            model="openrouter/auto",
            messages=[{"role":"user","content":meds}]
        )
        st.write(res.choices[0].message.content)

# ---------------- DASHBOARD ----------------
with tabs[4]:

    st.header("Live Dashboard")

    df = pd.read_sql_query("SELECT * FROM patients", conn)

    st.dataframe(df)

    if not df.empty:
        st.bar_chart(df["dept"].value_counts())

# ---------------- BILLING ----------------
with tabs[5]:

    st.header("Billing System")

    pname = st.text_input("Patient Name")
    amount = st.number_input("Amount")

    if st.button("Add Bill"):
        c.execute("INSERT INTO billing VALUES(?,?)",(pname,amount))
        conn.commit()
        st.success("Bill Added")

    bill_df = pd.read_sql_query("SELECT * FROM billing", conn)
    st.dataframe(bill_df)

# ---------------- BEDS ----------------
with tabs[6]:

    st.header("Bed Management")

    total,occupied = beds

    st.metric("Total Beds", total)
    st.metric("Occupied", occupied)
    st.metric("Available", total-occupied)

    if st.button("Admit"):
        c.execute("UPDATE beds SET occupied=occupied+1")
        conn.commit()

    if st.button("Discharge"):
        c.execute("UPDATE beds SET occupied=occupied-1")
        conn.commit()