import streamlit as st

from utils.auth import requerir_paciente
from utils.storage import get_paciente, init_state

st.set_page_config(page_title="Onboarding — Palpitaciones", page_icon="📝", layout="wide")
init_state()
requerir_paciente()

st.title("📝 Onboarding del paciente")

paciente = get_paciente(st.session_state.paciente_actual_id)

st.success(f"Bienvenido/a, **{paciente['nombre']}**.")

with st.expander("Consentimiento informado y política de datos", expanded=True):
    st.markdown(
        """
        - Tus datos de salud se utilizan exclusivamente para tu seguimiento clínico en
          el Centro Integral de Arritmias Tucumán (CIAT), conforme a la **Ley 25.326 de
          Protección de Datos Personales (Argentina)**.
        - Esta app es una herramienta de **apoyo a la decisión**, no reemplaza la consulta
          médica ni un ECG de 12 derivaciones.
        - Toda conducta clínica relevante será validada por tu equipo médico.
        """
    )
    acepto = st.checkbox("Acepto el consentimiento informado y la política de datos", value=True)

st.subheader("Vinculación de wearable")
st.write(f"Dispositivo vinculado: **{paciente['wearable']}** ✅ (simulado)")

st.subheader("Cuestionario basal")

col1, col2 = st.columns(2)
with col1:
    st.text_input("Nombre", value=paciente["nombre"], disabled=True)
    st.number_input("Edad", value=paciente["edad"], disabled=True)
    st.text_input("Sexo", value=paciente["sexo"], disabled=True)
    st.text_area("Antecedentes cardiológicos", value=paciente["antecedentes"]["otros"], disabled=True)

with col2:
    st.text_area("Medicación actual", value="\n".join(paciente["medicacion"]), disabled=True)
    st.text_area(
        "Características habituales de tus palpitaciones",
        value=paciente["caracteristicas_habituales"],
        disabled=True,
    )
    cardiopatia = "Sí" if paciente["antecedentes"]["cardiopatia_estructural"] else "No"
    st.text_input("¿Antecedente de cardiopatía estructural?", value=cardiopatia, disabled=True)

st.caption(
    "En esta demo el cuestionario basal viene precargado con datos de prueba. "
    "En la versión real sería completado por el paciente en su primer ingreso."
)

if acepto:
    st.page_link("pages/2_Paciente_Episodio.py", label="Continuar: registrar un episodio →", icon="❤️")
