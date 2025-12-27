import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# APP CONFIG
# =====================================================
st.set_page_config(
    page_title="KayKuks Pediatric App", 
    layout="centered", 
    page_icon="🧒"
)

st.title("🧒 KayKuks Pediatric Growth & BP App")
st.markdown("---")

# =====================================================
# LOAD & CLEAN DATA
# =====================================================
@st.cache_data
def load_data():
    """
    Loads WHO growth data and ensures the Age column is numeric.
    """
    files = {
        "boys_0_2": "hfa_boys_0_2.csv",
        "girls_0_2": "hfa_girls_0_2.csv",
        "boys_2_5": "hfa_boys_2_5.csv",
        "girls_2_5": "hfa_girls_2_5.csv",
        "boys_5_19": "hfa_boys_5_19.csv",
        "girls_5_19": "hfa_girls_5_19.csv",
    }
    
    loaded_data = {}
    for key, path in files.items():
        try:
            df = pd.read_csv(path)
            
            # Identify the first column (Age/Month) dynamically
            age_col = df.columns[0]
            
            # Force conversion to numeric, coercing errors to NaN
            df[age_col] = pd.to_numeric(
                df[age_col].astype(str).str.extract(r"(\d+\.?\d*)")[0], 
                errors='coerce'
            )
            
            # Drop rows where Age could not be parsed
            df = df.dropna(subset=[age_col])
            loaded_data[key] = df
            
        except FileNotFoundError:
            st.error(f"⚠️ Missing file: `{path}`. Please ensure it is uploaded.")
        except Exception as e:
            st.error(f"Error loading {path}: {e}")
            
    return loaded_data

data = load_data()

# =====================================================
# USER INPUT (SIDEBAR)
# =====================================================
with st.sidebar:
    st.header("Patient Demographics")
    age = st.number_input("Age (years)", min_value=0.0, max_value=19.0, value=5.0, step=0.1)
    sex = st.selectbox("Sex", ["Male", "Female"])
    height = st.number_input("Height (cm)", min_value=40.0, max_value=200.0, value=110.0)
    weight = st.number_input("Weight (kg)", min_value=2.0, max_value=150.0, value=20.0)

# =====================================================
# LOGIC: BMI
# =====================================================
def calculate_bmi(w, h):
    return w / ((h / 100) ** 2)

bmi = calculate_bmi(weight, height)

# =====================================================
# LOGIC: HEIGHT FOR AGE (LMS Z-SCORE)
# =====================================================
def get_height_zscore(age_years, sex, height_cm):
    age_months = age_years * 12

    # Select the correct dataset based on Age and Sex
    if age_years < 2:
        key = "boys_0_2" if sex == "Male" else "girls_0_2"
    elif age_years < 5:
        key = "boys_2_5" if sex == "Male" else "girls_2_5"
    else:
        key = "boys_5_19" if sex == "Male" else "girls_5_19"

    # Safety check if data loaded correctly
    if key not in data:
        return None

    # Use .copy() to ensure we don't modify the cached data
    df = data[key].copy()
    age_col = df.columns[0]

    # Find the row with the closest age
    # We calculate the absolute difference between list of ages and patient age
    idx = (df[age_col] - age_months).abs().idxmin()
    row = df.loc[idx]

    L = row["L"]
    M = row["M"]
    S = row["S"]

    # LMS Formula: Z = ((X/M)^L - 1) / (L*S)
    # Handle L=0 edge case if necessary (though rare in standard WHO tables)
    if L != 0:
        z_score = ((height_cm / M) ** L - 1) / (L * S)
    else:
        z_score = np.log(height_cm / M) / S
        
    return z_score

# =====================================================
# DISPLAY: RESULTS
# =====================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 BMI")
    st.metric("Value", f"{bmi:.2f}")
    
    if bmi < 18.5:
        st.info("Underweight")
    elif bmi < 25:
        st.success("Normal weight")
    elif bmi < 30:
        st.warning("Overweight")
    else:
        st.error("Obese")

with col2:
    st.subheader("📏 Growth (Height)")
    z_val = get_height_zscore(age, sex, height)
    
    if z_val is not None:
        st.metric("Height-for-Age Z-Score", f"{z_val:.2f}")
        
        if z_val < -3:
            st.error("Severe Stunting (<-3 SD)")
        elif z_val < -2:
            st.warning("Stunted (<-2 SD)")
        elif z_val <= 2:
            st.success("Normal Height")
        else:
            st.info("Tall for Age (>+2 SD)")
    else:
        st.warning("Growth data unavailable for this age/sex.")

st.markdown("---")

# =====================================================
# LOGIC: BLOOD PRESSURE
# =====================================================
st.subheader("🩺 Blood Pressure Screening")
st.caption("Simple screening thresholds (AAP 2017 simplified). For precise diagnosis, use height percentiles.")

c_bp1, c_bp2 = st.columns(2)
sbp = c_bp1.number_input("Systolic BP (mmHg)", 50, 200, 100)
dbp = c_bp2.number_input("Diastolic BP (mmHg)", 30, 150, 60)

def interpret_bp(sbp, dbp):
    if sbp < 90 and dbp < 60:
        return "Normal", "success"
    elif sbp < 120 and dbp < 80:
        return "Normal (or Elevated depending on %ile)", "success"
    elif sbp < 130 and dbp < 80:
        return "Elevated", "warning"
    elif sbp < 140 or (dbp >= 80 and dbp < 90):
        return "Stage 1 Hypertension", "error"
    else:
        return "Stage 2 Hypertension", "error"

if st.button("Interpret Blood Pressure"):
    category, status = interpret_bp(sbp, dbp)
    if status == "success":
        st.success(f"**Result:** {category}")
    elif status == "warning":
        st.warning(f"**Result:** {category}")
    else:
        st.error(f"**Result:** {category}")

st.markdown("---")
st.caption("⚕️ **Disclaimer:** This tool is for educational purposes only and does not replace professional medical advice.")
