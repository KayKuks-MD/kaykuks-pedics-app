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
# LOAD & CLEAN DATA
# =====================================================
@st.cache_data
def load_data():
    files = {
        "boys_0_2": "hfa_boys_0_2.csv",
        "girls_0_2": "hfa_girls_0_2.csv",
        "boys_2_5": "hfa_boys_2_5.csv",
        "girls_2_5": "hfa_girls_2_5.csv",
        "boys_5_19": "hfa_boys_5_19.csv",
        "girls_5_19": "hfa_girls_5_19.csv",
    }
    
    data_dict = {}
    for key, filename in files.items():
        try:
            df = pd.read_csv(filename)
            
            # --- THE FIX STARTS HERE ---
            # 1. Get the first column name (usually 'Day', 'Month', or 'Age')
            age_col = df.columns[0]
            
            # 2. Force this column to be numeric. 
            # 'coerce' turns text like "Month" into NaN (Not a Number) so we can drop it.
            df[age_col] = pd.to_numeric(df[age_col], errors='coerce')
            
            # 3. Remove rows where the age didn't convert (e.g., header rows repeated)
            df = df.dropna(subset=[age_col])
            # --- THE FIX ENDS HERE ---
            
            data_dict[key] = df
        except FileNotFoundError:
            st.error(f"⚠️ Error: File '{filename}' not found. Please upload it.")
            # Return an empty DF to prevent crash, though app won't work fully
            data_dict[key] = pd.DataFrame() 
            
    return data_dict

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
    # Convert age in years to months for WHO comparison
    age_months = age * 12

    if age < 2:
        df_key = "boys_0_2" if sex == "Male" else "girls_0_2"
    elif age < 5:
        df_key = "boys_2_5" if sex == "Male" else "girls_2_5"
    else:
        df_key = "boys_5_19" if sex == "Male" else "girls_5_19"

    if df_key not in data or data[df_key].empty:
        return None

    # Use .copy() to ensure we don't accidentally modify the cached data
    df = data[df_key].copy()
    age_col = df.columns[0]

    # Find the row closest to the child's age
    # Since we cleaned the data in load_data(), math works here now!
    df["diff"] = (df[age_col] - age_months).abs()
    row = df.loc[df["diff"].idxmin()]

    L = row["L"]
    M = row["M"]
    S = row["S"]

    # LMS Formula
    z = ((height / M) ** L - 1) / (L * S)
    return z

z = get_height_zscore(age, sex, height)

st.subheader("📏 Height-for-Age Z-Score")

if z is not None:
    st.write(f"**Z-score:** {z:.2f}")

    # Interpretation
    if z < -3:
        st.error("Severe stunting (<-3 SD)")
    elif z < -2:
        st.warning("Stunted (<-2 SD)")
    elif z <= 2:
        st.success("Normal height")
    else:
        st.info("Tall for age (>+2 SD)")
else:
    st.warning("Could not calculate Z-score (Data missing).")

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
