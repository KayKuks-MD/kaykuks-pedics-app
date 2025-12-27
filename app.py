import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(page_title="KayKuks Pediatric App", layout="centered")

st.title("🧒 KayKuks Pediatric Growth & BP App")
st.write("WHO-based pediatric growth and blood pressure assessment")

# =====================================================
# LOAD WHO DATA
# =====================================================
@st.cache_data
def load_data():
    return {
        "boys_0_2": pd.read_csv("hfa_boys_0_2.csv"),
        "girls_0_2": pd.read_csv("hfa_girls_0_2.csv"),
        "boys_2_5": pd.read_csv("hfa_boys_2_5.csv"),
        "girls_2_5": pd.read_csv("hfa_girls_2_5.csv"),
        "boys_5_19": pd.read_csv("hfa_boys_5_19.csv"),
        "girls_5_19": pd.read_csv("hfa_girls_5_19.csv"),
    }

data = load_data()

# =====================================================
# USER INPUT
# =====================================================
age = st.number_input("Age (years)", 0.0, 19.0, 5.0)
sex = st.selectbox("Sex", ["Male", "Female"])
height = st.number_input("Height (cm)", 40.0, 200.0)
weight = st.number_input("Weight (kg)", 2.0, 150.0)

# =====================================================
# BMI
# =====================================================
def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

bmi = calculate_bmi(weight, height)

st.subheader("📊 BMI")
st.write(f"**BMI:** {bmi:.2f}")

if bmi < 18.5:
    st.info("Underweight")
elif bmi < 25:
    st.success("Normal weight")
elif bmi < 30:
    st.warning("Overweight")
else:
    st.error("Obese")

# =====================================================
# HEIGHT FOR AGE (WHO Z SCORE)
# =====================================================
def get_height_zscore(age, sex, height):
    age_months = age * 12

    if age < 2:
        df = data["boys_0_2"] if sex == "Male" else data["girls_0_2"]
    elif age < 5:
        df = data["boys_2_5"] if sex == "Male" else data["girls_2_5"]
    else:
        df = data["boys_5_19"] if sex == "Male" else data["girls_5_19"]

    # Identify age column dynamically
    age_col = df.columns[0]

    # Convert age column safely
    df[age_col] = (
        df[age_col]
        .astype(str)
        .str.extract(r"(\d+\.?\d*)")[0]
        .astype(float)
    )

    # Find closest age
    df["diff"] = (df[age_col] - age_months).abs()
    row = df.loc[df["diff"].idxmin()]

    L = row["L"]
    M = row["M"]
    S = row["S"]

    z = ((height / M) ** L - 1) / (L * S)
    return z

z = get_height_zscore(age, sex, height)

st.subheader("📏 Height-for-Age Z-Score")
st.write(f"**Z-score:** {z:.2f}")

if z < -3:
    st.error("Severe stunting")
elif z < -2:
    st.warning("Stunted")
elif z <= 2:
    st.success("Normal height")
else:
    st.info("Tall for age")

# =====================================================
# BLOOD PRESSURE (SCREENING)
# =====================================================
st.subheader("🩺 Blood Pressure Screening")

sbp = st.number_input("Systolic BP (mmHg)", 50, 200)
dbp = st.number_input("Diastolic BP (mmHg)", 30, 150)

def interpret_bp(sbp, dbp):
    if sbp < 90 and dbp < 60:
        return "Normal"
    elif sbp < 120 or dbp < 80:
        return "Elevated"
    elif sbp < 130 or dbp < 80:
        return "Stage 1 Hypertension"
    else:
        return "Stage 2 Hypertension"

if st.button("Interpret Blood Pressure"):
    st.success(f"Blood Pressure Category: **{interpret_bp(sbp, dbp)}**")

st.caption("⚕️ Educational tool — not for diagnosis.")
