import pandas as pd
import streamlit as st

from utils.auth import requerir_paciente
from utils.storage import get_episodios, get_paciente, init_state

st.set_page_config(page_title="Mi historial — Palpitaciones", page_icon="📈", layout="wide")
init_state()
requerir_paciente()

st.title("📈 Mi historial de episodios")

paciente = get_paciente(st.session_state.paciente_actual_id)
st.caption(f"Paciente: **{paciente['nombre']}**")

episodios = sorted(get_episodios(paciente["id"]), key=lambda e: e["fecha_hora"], reverse=True)

if not episodios:
    st.info("Todavía no tenés episodios registrados.")
    st.page_link("pages/2_Paciente_Episodio.py", label="Registrar un episodio", icon="❤️")
    st.stop()

st.subheader("Frecuencia de episodios")
conteo = pd.DataFrame(episodios)["fecha_hora"].str[:10].value_counts().sort_index()
st.bar_chart(conteo)

st.subheader("Episodios registrados")

ESTADO_LABEL = {
    "pendiente": "⏳ Pendiente de revisión",
    "confirmado": "✅ Revisado por el médico",
    "reclasificado": "🔁 Reclasificado por el médico",
}

for ep in episodios:
    nivel = ep["triage"]["nivel"]
    icono = {"ROJO": "🔴", "AMARILLO": "🟡", "VERDE": "🟢"}[nivel]
    with st.expander(f"{icono} {ep['fecha_hora']} — Prioridad {nivel} — {ESTADO_LABEL[ep['revision_medica']['estado']]}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Diario del episodio**")
            d = ep["diario"]
            st.write(f"- Hora de inicio: {d['hora_inicio']}")
            st.write(f"- Duración: {d['duracion_min']} min")
            st.write(f"- Inicio: {d['forma_inicio']} / Fin: {d['forma_fin']}")
            st.write(f"- Desencadenante: {d['desencadenantes']}")
            st.write(f"- Tolerancia: {'Bien tolerado' if d['tolerancia'] == 'bien_tolerado' else 'Mal tolerado'}")

        with col2:
            st.markdown("**Resultado**")
            st.write(ep["triage"]["mensaje"])

            revision = ep["revision_medica"]
            if revision["estado"] != "pendiente":
                st.markdown("**Indicación del médico**")
                st.info(revision["indicacion"])
                if revision["nivel_medico"] and revision["nivel_medico"] != nivel:
                    st.caption(f"El equipo médico ajustó la prioridad de este episodio a {revision['nivel_medico']}.")
