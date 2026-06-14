"""Generación de trazados de ECG sintéticos de 1 derivación para la demo.

Los trazados NO son ECG reales: son señales simplificadas que ilustran los
patrones (regular/irregular, QRS angosto/ancho) que describe utils/triage.py.
"""

import numpy as np

FS = 125  # muestras por segundo
DURACION_S = 8


def _complejo(qrs_ancho: bool, con_p: bool = True, amplitud_qrs: float = 1.6) -> np.ndarray:
    largo = FS  # un "latido" ocupa hasta 1 segundo de espacio
    t = np.linspace(0, 1, largo)
    onda = np.zeros(largo)

    if con_p:
        onda += 0.12 * np.exp(-((t - 0.15) ** 2) / (2 * 0.012 ** 2))

    sigma_qrs = 0.05 if qrs_ancho else 0.012
    onda += amplitud_qrs * np.exp(-((t - 0.35) ** 2) / (2 * sigma_qrs ** 2))
    onda -= 0.35 * amplitud_qrs * np.exp(-((t - 0.35 - sigma_qrs * 1.8) ** 2) / (2 * (sigma_qrs * 0.8) ** 2))

    onda += 0.28 * np.exp(-((t - 0.65) ** 2) / (2 * 0.05 ** 2))
    return onda


def generar(tipo: str, seed: int = 0) -> dict:
    """Devuelve {"tiempo": [...], "voltaje": [...]} para el tipo de trazado dado."""
    rng = np.random.default_rng(seed)
    n_total = FS * DURACION_S
    señal = np.zeros(n_total)

    params = {
        "sinusal_normal": dict(frecuencia=72, irregular=False, qrs_ancho=False, con_p=True),
        "fa_irregular": dict(frecuencia=110, irregular=True, qrs_ancho=False, con_p=False),
        "tpsv_regular": dict(frecuencia=180, irregular=False, qrs_ancho=False, con_p=False),
        "tv_qrs_ancho": dict(frecuencia=170, irregular=False, qrs_ancho=True, con_p=False),
        "bradicardia": dict(frecuencia=42, irregular=False, qrs_ancho=False, con_p=True),
        "extrasistoles_ves": dict(frecuencia=78, irregular="ves", qrs_ancho=False, con_p=True),
    }[tipo]

    rr_base = int(FS * 60 / params["frecuencia"])
    complejo_normal = _complejo(qrs_ancho=params["qrs_ancho"], con_p=params["con_p"])
    complejo_ancho = _complejo(qrs_ancho=True, con_p=False, amplitud_qrs=1.9)

    pos = 0
    contador = 0
    while pos < n_total - FS:
        if params["irregular"] == "ves" and contador % 4 == 3:
            complejo = complejo_ancho
            rr = int(rr_base * 0.6)
        else:
            complejo = complejo_normal
            if params["irregular"] is True:
                rr = int(rr_base * rng.uniform(0.6, 1.5))
            else:
                rr = rr_base

        fin = min(pos + FS, n_total)
        señal[pos:fin] += complejo[: fin - pos]
        pos += max(rr, FS // 4)
        contador += 1

    señal += rng.normal(0, 0.01, n_total)
    tiempo = np.round(np.arange(n_total) / FS, 3)
    return {"tiempo": tiempo.tolist(), "voltaje": np.round(señal, 4).tolist()}
