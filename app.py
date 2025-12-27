import streamlit as st
import pandas as pd
import numpy as np

# ======================================================
# APP CONFIG
# ======================================================
st.set_page_config(page_title="KayKuks Pediatric App", layout="centered")
st.title("🧒 KayKuks Pediatric Growth & BP App")

# ======================================================
# LOAD WHO DATA
# ======================================================
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

# ======================================================
# USER INPUTS
# ======================================================
st.subheader("👶 Child Information")

age = st.number_input("Age (years)", 0.0, 19.0, 5.0)
sex = st.selectbox("Sex", ["Male", "Female"])
height = st.number_input("Height (cm)", 40.0, 220.0)
weight = st.number_input("Weight (kg)", 2.0, 200.0)

# ======================================================
# BMI CALCULATION
# ======================================================
bmi = weight / ((height / 100) ** 2)

st.subheader("📊 BMI Result")
st.write(f"**BMI:** {bmi:.2f}")

if bmi < 18.5:
    st.info("Underweight")
elif bmi < 25:
    st.success("Normal weight")
elif bmi < 30:
    st.warning("Overweight")
else:
    st.error("Obese")

# ======================================================
# HEIGHT FOR AGE Z-SCORE (WHO)
# ======================================================
def get_height_zscore(age, sex, height):
    age_months = age * 12

    if age < 2:
        df = data["boys_0_2"] if sex == "Male" else data["girls_0_2"]
    elif age < 5:
        df = data["boys_2_5"] if sex == "Male" else data["girls_2_5"]
    else:
        df = data["boys_5_19"] if sex == "Male" else data["girls_5_19"]

    # Standard WHO column names
    df.columns = [c.strip() for c in df.columns]

    # Convert age column to numeric
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

    # Find closest age row
    df["diff"] = (df["Age"] - age_months).abs()
    row = df.loc[df["diff"].idxmin()]

    L = row["L"]
    M = row["M"]
    S = row["S"]

    z = ((height / M) ** L - 1) / (L * S)
    return z


# ======================================================
# DISPLAY HEIGHT-FOR-AGE
# ======================================================
z = get_height_zscore(age, sex, height)

st.subheader("📏 Height-for-Age (WHO Z-score)")
st.write(f"**Z-score:** {z:.2f}")

if z < -3:
    st.error("Severely stunted")
elif z < -2:
    st.warning("Stunted")
elif z <= 2:
    st.success("Normal height")
else:
    st.info("Tall for age")

# ======================================================
# BLOOD PRESSURE (BASIC CLASSIFICATION)
# ======================================================
st.subheader("🩺 Blood Pressure")

sbp = st.number_input("Systolic BP (mmHg)", 50, 200)
dbp = st.number_input("Diastolic BP (mmHg)", 30, 150)

if st.button("Interpret Blood Pressure"):
    if sbp < 90 and dbp < 60:
        st.success("Normal BP")
    elif sbp < 120:
        st.info("Elevated BP")
    elif sbp < 130:
        st.warning("Stage 1 Hypertension")
    else:
        st.error("Stage 2 Hypertension")
