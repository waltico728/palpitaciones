"""Separación de accesos por rol (demo, sin autenticación real).

No hay usuarios/contraseñas reales todavía: el acceso de paciente se hace
eligiendo un nombre de una lista (simula login) y el acceso de médico se
protege con una clave compartida simple. Esto evita que cualquier persona
navegue directamente a las páginas médicas o vea episodios de otros
pacientes, pero NO reemplaza un sistema de autenticación real ni cumple por
sí solo con la Ley 25.326: para producción se requiere autenticación e
identidad verificada.
"""

from __future__ import annotations

import streamlit as st

def _clave_medico() -> str:
    """Clave de acceso del médico. Por defecto "1234"; se puede sobrescribir
    en producción con st.secrets["clave_medico"] (Streamlit Cloud)."""
    try:
        return st.secrets["clave_medico"]
    except Exception:
        return "1234"


CLAVE_MEDICO = _clave_medico()


def es_medico() -> bool:
    return st.session_state.get("rol") == "medico"


def es_paciente() -> bool:
    return st.session_state.get("rol") == "paciente" and st.session_state.get("paciente_actual_id") is not None


def requerir_paciente():
    """Detiene la página si no hay una sesión de paciente activa."""
    if not es_paciente():
        st.warning("Necesitás iniciar sesión como paciente desde la página de inicio.")
        st.page_link("app.py", label="Volver al inicio", icon="🏠")
        st.stop()


def requerir_medico():
    """Detiene la página si no hay una sesión médica activa."""
    if not es_medico():
        st.warning("Esta sección es exclusiva para el equipo médico. Iniciá sesión desde la página de inicio.")
        st.page_link("app.py", label="Volver al inicio", icon="🏠")
        st.stop()


def cerrar_sesion():
    st.session_state.rol = None
    st.session_state.paciente_actual_id = None
