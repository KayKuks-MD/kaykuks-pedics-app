import streamlit as st

# App title
st.set_page_config(page_title="KayKuks Pediatric App", layout="centered")

st.title("🧒 KayKuks Pediatric BMI Calculator")
st.write("Calculate Body Mass Index (BMI) for children and adolescents.")

# Input section
age = st.number_input("Age (years)", min_value=0.0, max_value=18.0, step=0.1)
sex = st.selectbox("Sex", ["Male", "Female"])
weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
height = st.number_input("Height (cm)", min_value=0.0, step=0.1)

# BMI Calculation
if st.button("Calculate BMI"):
    if height > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        st.success(f"**BMI: {bmi:.2f} kg/m²**")

        # Simple interpretation (not percentile-based yet)
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
    else:
        st.error("Height must be greater than zero.")
