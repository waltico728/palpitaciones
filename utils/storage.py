"""Estado de la app: carga de datos de ejemplo en st.session_state.

Todo vive en memoria durante la sesión (sin base de datos externa). Los
archivos en data/ son solo la semilla inicial.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _cargar_json(nombre: str):
    with open(DATA_DIR / nombre, encoding="utf-8") as f:
        return json.load(f)


def init_state():
    if "pacientes" not in st.session_state:
        st.session_state.pacientes = _cargar_json("pacientes_demo.json")

    if "episodios" not in st.session_state:
        st.session_state.episodios = _cargar_json("episodios_demo.json")

    if "ecg_samples" not in st.session_state:
        st.session_state.ecg_samples = _cargar_json("ecg_samples.json")

    if "paciente_actual_id" not in st.session_state:
        st.session_state.paciente_actual_id = None

    if "rol" not in st.session_state:
        st.session_state.rol = None


def get_pacientes() -> list:
    init_state()
    return st.session_state.pacientes


def get_paciente(paciente_id: str) -> dict | None:
    return next((p for p in get_pacientes() if p["id"] == paciente_id), None)


def agregar_paciente(paciente: dict):
    init_state()
    st.session_state.pacientes.append(paciente)


def nuevo_paciente_id() -> str:
    init_state()
    existentes = [int(p["id"][1:]) for p in st.session_state.pacientes if p["id"].startswith("p")]
    return f"p{max(existentes, default=0) + 1}"


def get_episodios(paciente_id: str | None = None) -> list:
    init_state()
    episodios = st.session_state.episodios
    if paciente_id is None:
        return episodios
    return [e for e in episodios if e["paciente_id"] == paciente_id]


def get_episodio(episodio_id: str) -> dict | None:
    return next((e for e in get_episodios() if e["id"] == episodio_id), None)


def agregar_episodio(episodio: dict):
    init_state()
    st.session_state.episodios.append(episodio)


def nuevo_episodio_id() -> str:
    init_state()
    existentes = [int(e["id"][1:]) for e in st.session_state.episodios if e["id"].startswith("e")]
    return f"e{max(existentes, default=0) + 1}"


ORDEN_TRIAGE = {"ROJO": 0, "AMARILLO": 1, "VERDE": 2}
