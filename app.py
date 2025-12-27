import streamlit as st

# ==============================
# APP CONFIG
# ==============================
st.set_page_config(page_title="KayKuks Pediatric App", layout="centered")

st.title("🧒 KayKuks Pediatric BMI & BP Calculator")
st.write("A simple clinical tool for pediatric BMI and blood pressure assessment.")

# ==============================
# INPUT SECTION
# ==============================
age = st.number_input("Age (years)", min_value=0.0, max_value=18.0, step=0.1)
sex = st.selectbox("Sex", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
height = st.number_input("Height (cm)", min_value=0.0, step=0.1)

# ==============================
# BMI CALCULATION
# ==============================
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return weight / (height_m ** 2)

st.subheader("📊 BMI Result")

if st.button("Calculate BMI"):
    if height > 0 and weight > 0:
        bmi = calculate_bmi(weight, height)
        st.success(f"**BMI: {bmi:.2f} kg/m²**")

        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
    else:
        st.error("Please enter valid height and weight.")

# ==============================
# PEDIATRIC BLOOD PRESSURE
# ==============================

st.header("🩺 Pediatric Blood Pressure Assessment")

sbp = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=200)
dbp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150)

# Simplified BP Reference (educational)
BP_REFERENCE = {
    "male": {
        "normal": {"sbp": 90, "dbp": 60},
        "elevated": {"sbp": 95, "dbp": 80},
        "stage1": {"sbp": 120, "dbp": 80},
        "stage2": {"sbp": 140, "dbp": 90},
    },
    "female": {
        "normal": {"sbp": 90, "dbp": 60},
        "elevated": {"sbp": 95, "dbp": 80},
        "stage1": {"sbp": 120, "dbp": 80},
        "stage2": {"sbp": 140, "dbp": 90},
    },
}

def interpret_bp(sex, sbp, dbp):
    ref = BP_REFERENCE[sex.lower()]

    if sbp < ref["normal"]["sbp"] and dbp < ref["normal"]["dbp"]:
        return "Normal Blood Pressure"
    elif sbp < ref["elevated"]["sbp"] or dbp < ref["elevated"]["dbp"]:
        return "Elevated Blood Pressure"
    elif sbp < ref["stage1"]["sbp"] or dbp < ref["stage1"]["dbp"]:
        return "Stage 1 Hypertension"
    else:
        return "Stage 2 Hypertension"

if st.button("Interpret Blood Pressure"):
    bp_result = interpret_bp(sex, sbp, dbp)
    st.success(f"🩺 Blood Pressure Category: **{bp_result}**")

# ==============================
# FOOTER
# ==============================
st.markdown("---")
st.caption("⚕️ Educational use only. Not a substitute for clinical judgment.")
