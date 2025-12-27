import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="KayKuks Pediatric App",
    layout="centered"
)

st.title("🧒 KayKuks Pediatric BMI & BP Calculator")
st.write("Calculate BMI and interpret Blood Pressure for children and adolescents.")

# ---------------- BMI INPUTS ----------------
st.header("📏 BMI Calculator")

age = st.number_input("Age (years)", min_value=0.0, max_value=18.0, step=0.1)
sex = st.selectbox("Sex", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
height = st.number_input("Height (cm)", min_value=0.0, step=0.1)

if st.button("Calculate BMI"):
    if height > 0 and weight > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        st.success(f"**BMI: {bmi:.2f} kg/m²**")

        # Basic BMI interpretation (temporary – WHO percentiles later)
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

# ---------------- BP SECTION ----------------
st.header("🩺 Pediatric Blood Pressure Calculator")

sbp = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=200)
dbp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150)

if st.button("Interpret Blood Pressure"):
    if age < 1:
        st.warning("BP interpretation is unreliable under 1 year.")
    else:
        if sbp < 90 and dbp < 60:
            st.success("Normal Blood Pressure")
        elif 90 <= sbp < 95 or 60 <= dbp < 80:
            st.warning("Elevated Blood Pressure")
        elif 95 <= sbp < 120 or 80 <= dbp < 90:
            st.error("Stage 1 Hypertension")
        else:
            st.error("Stage 2 Hypertension")
