from datetime import datetime

import pandas as pd
import streamlit as st

from utils.auth import requerir_paciente
from utils.ecg_synth import generar
from utils.storage import agregar_episodio, get_paciente, init_state, nuevo_episodio_id
from utils.triage import evaluar_episodio

st.set_page_config(page_title="Nuevo episodio — Palpitaciones", page_icon="❤️", layout="wide")
init_state()
requerir_paciente()

st.title("❤️ Registrar un episodio de palpitaciones")

paciente = get_paciente(st.session_state.paciente_actual_id)
st.caption(f"Paciente: **{paciente['nombre']}**")

SINTOMAS_OPCIONES = {
    "sincope": "Síncope (pérdida de conocimiento)",
    "presincope": "Presíncope (sensación de que me iba a desmayar)",
    "dolor_toracico": "Dolor o presión en el pecho",
    "disnea_reposo": "Falta de aire en reposo",
    "disnea_esfuerzo": "Falta de aire con el esfuerzo",
    "mareo": "Mareo",
    "palpitaciones_leves": "Solo palpitaciones, sin otros síntomas",
}

st.subheader("1. Registro de ECG (30 segundos)")
modo = st.radio(
    "¿Cómo querés cargar el trazado?",
    ["Elegir un trazado de ejemplo", "Subir una imagen de ECG"],
    horizontal=True,
)

ecg_key = None
lectura_ia_manual = None
if modo == "Elegir un trazado de ejemplo":
    samples = st.session_state.ecg_samples
    ecg_key = st.selectbox(
        "Trazado de ejemplo",
        options=list(samples.keys()),
        format_func=lambda k: samples[k]["etiqueta"],
    )
    datos = generar(ecg_key)
    df = pd.DataFrame({"Tiempo (s)": datos["tiempo"], "Voltaje (mV)": datos["voltaje"]})
    st.line_chart(df, x="Tiempo (s)", y="Voltaje (mV)", height=200)
    st.caption(samples[ecg_key]["descripcion"])
else:
    archivo = st.file_uploader("Imagen del trazado de ECG", type=["png", "jpg", "jpeg"])
    if archivo:
        st.image(archivo, caption="Trazado subido por el paciente", width=400)

        st.markdown("**Datos del wearable durante el episodio**")
        st.caption(
            "En esta demo no se analiza la imagen del ECG directamente: la lectura "
            "preliminar de la IA se calcula a partir de los datos que reporta el "
            "wearable durante el episodio."
        )
        col_a, col_b = st.columns(2)
        with col_a:
            fc_dispositivo = st.number_input(
                "Frecuencia cardíaca registrada por el wearable (lpm)",
                min_value=30,
                max_value=250,
                value=80,
            )
        with col_b:
            alerta_fa = st.checkbox("El wearable detectó posible ritmo irregular / FA")

        regularidad = "irregular" if alerta_fa else "regular"
        lectura_ia_manual = {
            "frecuencia": int(fc_dispositivo),
            "regularidad": regularidad,
            "qrs": "estrecho",
            "sospecha_fa": alerta_fa,
            "sospecha_tv": False,
            "extrasistoles_frecuentes": False,
        }

        if alerta_fa:
            ecg_key = "fa_irregular"
        elif fc_dispositivo >= 150:
            ecg_key = "tpsv_regular"
        elif fc_dispositivo <= 50:
            ecg_key = "bradicardia"
        else:
            ecg_key = "sinusal_normal"

        datos = generar(ecg_key)
        df = pd.DataFrame({"Tiempo (s)": datos["tiempo"], "Voltaje (mV)": datos["voltaje"]})
        st.line_chart(df, x="Tiempo (s)", y="Voltaje (mV)", height=200)
        st.caption("Trazado de referencia mostrado a modo ilustrativo según los datos del wearable.")

st.subheader("2. Diario del episodio")

col1, col2 = st.columns(2)
with col1:
    hora_inicio = st.time_input("Hora de inicio del episodio")
    duracion_min = st.number_input("Duración aproximada (minutos)", min_value=0, max_value=600, value=5)
    forma_inicio = st.selectbox("Forma de inicio", ["Súbita", "Gradual"])
    forma_fin = st.selectbox("Forma de finalización", ["Aún presente al registrar", "Súbita", "Gradual"])

with col2:
    desencadenantes = st.text_input("¿Hubo algún desencadenante?", placeholder="Ej: esfuerzo, café, estrés, sin causa clara")
    sintomas_sel = st.multiselect(
        "Síntomas asociados",
        options=list(SINTOMAS_OPCIONES.keys()),
        format_func=lambda k: SINTOMAS_OPCIONES[k],
    )
    tolerancia = st.radio(
        "¿Cómo tolerás el episodio?",
        ["bien_tolerado", "mal_tolerado"],
        format_func=lambda v: "Lo tolero bien" if v == "bien_tolerado" else "Lo tolero mal / me afecta mucho",
    )
    recurrencia_post_ablacion = st.checkbox(
        "Es similar a las palpitaciones que tenía antes de mi última ablación"
    )

st.markdown("---")

if st.button("Enviar episodio", type="primary", disabled=ecg_key is None):
    lectura_ia = lectura_ia_manual or st.session_state.ecg_samples[ecg_key]["lectura_ia"]
    diario = {
        "hora_inicio": hora_inicio.strftime("%H:%M"),
        "duracion_min": duracion_min,
        "forma_inicio": forma_inicio,
        "forma_fin": forma_fin,
        "desencadenantes": desencadenantes or "No especificado",
        "sintomas": sintomas_sel,
        "tolerancia": tolerancia,
        "recurrencia_post_ablacion": recurrencia_post_ablacion,
    }

    triage = evaluar_episodio(lectura_ia, diario, paciente)

    episodio = {
        "id": nuevo_episodio_id(),
        "paciente_id": paciente["id"],
        "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ecg_sample_key": ecg_key,
        "lectura_ia": lectura_ia,
        "diario": diario,
        "triage": triage,
        "revision_medica": {"estado": "pendiente", "nivel_medico": None, "indicacion": "", "fecha": None},
    }
    agregar_episodio(episodio)

    st.success("✅ Registro recibido. Acá está el resultado de la evaluación preliminar:")

    nivel = triage["nivel"]
    color = {"ROJO": "error", "AMARILLO": "warning", "VERDE": "success"}[nivel]
    getattr(st, color)(f"**Nivel de prioridad: {nivel}**\n\n{triage['mensaje']}")

    st.caption(
        "Tu registro fue evaluado por una IA como apoyo a la decisión y quedará "
        "disponible para que tu equipo médico lo revise. No reemplaza un ECG de "
        "12 derivaciones ni el juicio clínico."
    )

    st.page_link("pages/3_Paciente_Historial.py", label="Ver mi historial", icon="📈")
