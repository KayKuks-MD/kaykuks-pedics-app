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
# BMI (DISPLAY ONLY – NO ADULT INTERPRETATION)
# ============================================================
bmi = weight / ((height / 100) ** 2)
st.subheader("📊 BMI")
st.write(f"**BMI:** {bmi:.2f}")
st.info("BMI in children must be interpreted using BMI-for-age charts.")

# ============================================================
# HEIGHT-FOR-AGE Z-SCORE (WHO TABLE LOOKUP)
# ============================================================
def get_height_zscore(age, sex, height):
    age_months = int(round(age * 12))

    # Select correct dataset
    if age < 2:
        df = data["boys_0_2"] if sex == "Male" else data["girls_0_2"]
    elif age < 5:
        df = data["boys_2_5"] if sex == "Male" else data["girls_2_5"]
    else:
        df = data["boys_5_19"] if sex == "Male" else data["girls_5_19"]

    # Clean column names
    df.columns = [c.strip().lower() for c in df.columns]

    # First column = age
    age_col = df.columns[0]

    # Rename age column
    df = df.rename(columns={age_col: "age_months"})
    df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")

    # Z-score columns
    z_cols = {
        -3: df.columns[1],
        -2: df.columns[2],
        -1: df.columns[3],
         0: df.columns[4],
         1: df.columns[5],
         2: df.columns[6],
         3: df.columns[7],
    }

    # Find closest age row
    df["diff"] = (df["age_months"] - age_months).abs()
    row = df.loc[df["diff"].idxmin()]

    # Get heights at each Z
    heights = {z: row[col] for z, col in z_cols.items()}

    # Interpolate Z-score
    z_scores = np.array(list(heights.keys()))
    height_vals = np.array(list(heights.values()))

    z = np.interp(height, height_vals, z_scores)

    return z

# ============================================================
# DISPLAY HEIGHT RESULT
# ============================================================
try:
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

except Exception as e:
    st.error("Could not calculate height-for-age Z-score.")
    st.write(e)

# ============================================================
# BLOOD PRESSURE
# ============================================================
st.subheader("🩺 Blood Pressure")

sbp = st.number_input("Systolic BP (mmHg)", 50, 200)
dbp = st.number_input("Diastolic BP (mmHg)", 30, 150)

if st.button("Interpret BP"):
    if age >= 13:
        if sbp < 120 and dbp < 80:
            st.success("Normal BP")
        elif sbp < 130:
            st.warning("Elevated BP")
        elif sbp < 140:
            st.warning("Stage 1 Hypertension")
        else:
            st.error("Stage 2 Hypertension")
    else:
        st.info("BP interpretation for children <13 years requires age-, sex-, and height-based percentiles.")
