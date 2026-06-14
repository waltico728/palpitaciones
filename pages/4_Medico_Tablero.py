from datetime import datetime

import pandas as pd
import streamlit as st

from utils.auth import requerir_medico
from utils.ecg_synth import generar
from utils.storage import ORDEN_TRIAGE, get_episodio, get_episodios, get_paciente, guardar_episodio, init_state

st.set_page_config(page_title="Tablero médico — Palpitaciones", page_icon="🩺", layout="wide")
init_state()
requerir_medico()

st.title("🩺 Tablero médico")

st.warning(
    "La clasificación de la IA es **apoyo a la decisión**. Confirmá o reclasificá cada "
    "episodio antes de que se considere revisado."
)

episodios = get_episodios()
episodios_ordenados = sorted(
    episodios,
    key=lambda e: (
        e["revision_medica"]["estado"] != "pendiente",  # pendientes primero
        ORDEN_TRIAGE[e["triage"]["nivel"]],
        e["fecha_hora"],
    ),
)

st.subheader("Cola priorizada")

filas = []
for ep in episodios_ordenados:
    paciente = get_paciente(ep["paciente_id"])
    filas.append(
        {
            "ID": ep["id"],
            "Paciente": paciente["nombre"],
            "Fecha": ep["fecha_hora"],
            "Triage IA": ep["triage"]["nivel"],
            "Estado": ep["revision_medica"]["estado"],
        }
    )

st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)

st.subheader("Detalle del episodio")

opciones = {ep["id"]: f"{ep['id']} — {get_paciente(ep['paciente_id'])['nombre']} — {ep['triage']['nivel']} — {ep['fecha_hora']}" for ep in episodios_ordenados}
seleccion_id = st.selectbox("Elegí un episodio", options=list(opciones.keys()), format_func=lambda k: opciones[k])

ep = get_episodio(seleccion_id)
paciente = get_paciente(ep["paciente_id"])

col1, col2 = st.columns([1, 1.3])

with col1:
    st.markdown("### Paciente")
    st.write(f"**{paciente['nombre']}**, {paciente['edad']} años, {paciente['sexo']}")
    st.write(f"Motivo: {paciente['motivo']}")
    st.write(f"Antecedentes: {paciente['antecedentes']['otros']}")
    st.write(f"Cardiopatía estructural: {'Sí' if paciente['antecedentes']['cardiopatia_estructural'] else 'No'}")
    st.write("Medicación: " + ", ".join(paciente["medicacion"]))

    st.markdown("### Diario del episodio")
    d = ep["diario"]
    st.write(f"- Fecha/hora: {ep['fecha_hora']} (inicio del episodio: {d['hora_inicio']})")
    st.write(f"- Duración: {d['duracion_min']} min")
    st.write(f"- Forma de inicio/fin: {d['forma_inicio']} / {d['forma_fin']}")
    st.write(f"- Desencadenante: {d['desencadenantes']}")
    st.write(f"- Síntomas: {', '.join(d['sintomas']) if d['sintomas'] else 'Ninguno referido'}")
    st.write(f"- Tolerancia: {'Bien tolerado' if d['tolerancia'] == 'bien_tolerado' else 'Mal tolerado'}")
    if d.get("recurrencia_post_ablacion"):
        st.write("- El paciente refiere que es similar a episodios previos a su ablación.")

with col2:
    st.markdown("### Trazado de ECG")
    datos = generar(ep["ecg_sample_key"])
    df = pd.DataFrame({"Tiempo (s)": datos["tiempo"], "Voltaje (mV)": datos["voltaje"]})
    st.line_chart(df, x="Tiempo (s)", y="Voltaje (mV)", height=200)
    st.caption(st.session_state.ecg_samples[ep["ecg_sample_key"]]["descripcion"])

    st.markdown("### Lectura preliminar de la IA")
    lia = ep["lectura_ia"]
    st.write(
        f"- Frecuencia: **{lia['frecuencia']} lpm**\n"
        f"- Regularidad: **{lia['regularidad']}**\n"
        f"- QRS: **{lia['qrs']}**\n"
        f"- Sospecha de FA: **{'Sí' if lia['sospecha_fa'] else 'No'}**\n"
        f"- Sospecha de TV: **{'Sí' if lia['sospecha_tv'] else 'No'}**\n"
        f"- Extrasístoles ventriculares frecuentes: **{'Sí' if lia['extrasistoles_frecuentes'] else 'No'}**"
    )

    st.markdown("### Triage sugerido por la IA")
    nivel = ep["triage"]["nivel"]
    color = {"ROJO": "error", "AMARILLO": "warning", "VERDE": "success"}[nivel]
    getattr(st, color)(f"**{nivel}**")
    for j in ep["triage"]["justificacion"]:
        st.write(f"- {j}")

st.markdown("---")
st.subheader("Confirmar / reclasificar")

revision = ep["revision_medica"]
if revision["estado"] != "pendiente":
    st.info(
        f"Este episodio ya fue revisado el {revision['fecha']} "
        f"con nivel **{revision['nivel_medico']}**."
    )

with st.form(key=f"form_{ep['id']}"):
    nivel_medico = st.radio(
        "Nivel final (médico)",
        ["ROJO", "AMARILLO", "VERDE"],
        index=["ROJO", "AMARILLO", "VERDE"].index(revision["nivel_medico"] or ep["triage"]["nivel"]),
        horizontal=True,
    )
    indicacion = st.text_area("Indicación para el paciente", value=revision["indicacion"], height=120)
    enviado = st.form_submit_button("Guardar revisión", type="primary")

    if enviado:
        nuevo_estado = "confirmado" if nivel_medico == ep["triage"]["nivel"] else "reclasificado"
        ep["revision_medica"] = {
            "estado": nuevo_estado,
            "nivel_medico": nivel_medico,
            "indicacion": indicacion,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        guardar_episodio(ep)
        st.success("Revisión guardada.")
        st.rerun()
