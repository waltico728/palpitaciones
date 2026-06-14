"""Estado de la app: carga y persistencia de datos compartidos entre sesiones.

Pacientes y episodios se guardan en archivos JSON en data/runtime/ (en disco,
en el servidor donde corre la app), para que lo que registra un paciente sea
visible para el equipo médico en otra sesión del navegador. Los archivos en
data/ (sin "runtime") son la semilla inicial de datos de ejemplo.

Si la app se reinicia (redeploy o "duerme" por inactividad en Streamlit
Cloud), data/runtime/ se reinicia a la semilla: para uso real esto debería
migrar a una base de datos persistente.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RUNTIME_DIR = DATA_DIR / "runtime"


def _ruta_runtime(nombre: str) -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    destino = RUNTIME_DIR / nombre
    if not destino.exists():
        shutil.copy(DATA_DIR / nombre, destino)
    return destino


def _cargar_json(nombre: str):
    with open(_ruta_runtime(nombre), encoding="utf-8") as f:
        return json.load(f)


def _guardar_json(nombre: str, datos):
    with open(_ruta_runtime(nombre), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def init_state():
    if "ecg_samples" not in st.session_state:
        st.session_state.ecg_samples = json.loads((DATA_DIR / "ecg_samples.json").read_text(encoding="utf-8"))

    if "paciente_actual_id" not in st.session_state:
        st.session_state.paciente_actual_id = None

    if "rol" not in st.session_state:
        st.session_state.rol = None


def get_pacientes() -> list:
    return _cargar_json("pacientes_demo.json")


def get_paciente(paciente_id: str) -> dict | None:
    return next((p for p in get_pacientes() if p["id"] == paciente_id), None)


def agregar_paciente(paciente: dict):
    pacientes = get_pacientes()
    pacientes.append(paciente)
    _guardar_json("pacientes_demo.json", pacientes)


def nuevo_paciente_id() -> str:
    existentes = [int(p["id"][1:]) for p in get_pacientes() if p["id"].startswith("p")]
    return f"p{max(existentes, default=0) + 1}"


def get_episodios(paciente_id: str | None = None) -> list:
    episodios = _cargar_json("episodios_demo.json")
    if paciente_id is None:
        return episodios
    return [e for e in episodios if e["paciente_id"] == paciente_id]


def get_episodio(episodio_id: str) -> dict | None:
    return next((e for e in get_episodios() if e["id"] == episodio_id), None)


def agregar_episodio(episodio: dict):
    episodios = get_episodios()
    episodios.append(episodio)
    _guardar_json("episodios_demo.json", episodios)


def guardar_episodio(episodio: dict):
    """Actualiza (por id) un episodio existente, p. ej. tras la revisión médica."""
    episodios = get_episodios()
    for i, e in enumerate(episodios):
        if e["id"] == episodio["id"]:
            episodios[i] = episodio
            break
    _guardar_json("episodios_demo.json", episodios)


def nuevo_episodio_id() -> str:
    existentes = [int(e["id"][1:]) for e in get_episodios() if e["id"].startswith("e")]
    return f"e{max(existentes, default=0) + 1}"


ORDEN_TRIAGE = {"ROJO": 0, "AMARILLO": 1, "VERDE": 2}
