import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(page_title="KayKuks Pediatric App", layout="centered")
st.title("🧒 KayKuks Pediatric Growth & BP App")

# ============================================================
# LOAD DATA
# ============================================================
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

# ============================================================
# USER INPUT
# ============================================================
st.subheader("👶 Child Information")

age = st.number_input("Age (years)", 0.0, 19.0, 5.0)
sex = st.selectbox("Sex", ["Male", "Female"])
height = st.number_input("Height (cm)", 40.0, 220.0)
weight = st.number_input("Weight (kg)", 2.0, 200.0)

# ============================================================
# BMI
# ============================================================
bmi = weight / ((height / 100) ** 2)
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

# ============================================================
# HEIGHT FOR AGE Z SCORE
# ============================================================
def get_height_zscore(age, sex, height):
    age_months = age * 12

    # Choose dataset
    if age < 2:
        df = data["boys_0_2"] if sex == "Male" else data["girls_0_2"]
    elif age < 5:
        df = data["boys_2_5"] if sex == "Male" else data["girls_2_5"]
    else:
        df = data["boys_5_19"] if sex == "Male" else data["girls_5_19"]

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    # ---- Detect age column ----
    age_col = None
    for col in df.columns:
        if "age" in col or "month" in col:
            age_col = col
            break

    if age_col is None:
        st.error("❌ Could not find age column in WHO file.")
        st.write("Columns found:", df.columns.tolist())
        st.stop()

    # Convert age to numeric
    df[age_col] = pd.to_numeric(df[age_col], errors="coerce")

    # ---- Detect LMS columns ----
    def find_col(letter):
        for c in df.columns:
            if c.strip().lower() == letter:
                return c
        return None

    L_col = find_col("l")
    M_col = find_col("m")
    S_col = find_col("s")

    if not all([L_col, M_col, S_col]):
        st.error("❌ WHO file must contain columns L, M, and S.")
        st.write("Columns found:", df.columns.tolist())
        st.stop()

    # Find nearest age row
    df["diff"] = (df[age_col] - age_months).abs()
    row = df.loc[df["diff"].idxmin()]

    # LMS formula
    L, M, S = row[L_col], row[M_col], row[S_col]
    z = ((height / M) ** L - 1) / (L * S)

    return z

# ============================================================
# DISPLAY HEIGHT RESULT
# ============================================================
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

# ============================================================
# BLOOD PRESSURE
# ============================================================
st.subheader("🩺 Blood Pressure")

sbp = st.number_input("Systolic BP (mmHg)", 50, 200)
dbp = st.number_input("Diastolic BP (mmHg)", 30, 150)

if st.button("Interpret BP"):
    if sbp < 90 and dbp < 60:
        st.success("Normal blood pressure")
    elif sbp < 120:
        st.info("Elevated blood pressure")
    elif sbp < 130:
        st.warning("Stage 1 Hypertension")
    else:
        st.error("Stage 2 Hypertension")
