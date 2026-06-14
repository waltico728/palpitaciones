"""Lógica de triage ROJO / AMARILLO / VERDE para Palpitaciones.

Implementa la tabla de criterios de alerta de CLAUDE.md. Es una
clasificación de APOYO A LA DECISIÓN: el médico confirma o reclasifica
siempre desde el tablero.
"""

SINTOMAS_ROJOS = {"sincope", "presincope", "dolor_toracico", "disnea_reposo"}
SINTOMAS_BRADICARDIA_ROJA = {"sincope", "presincope", "mareo"}


def evaluar_episodio(lectura_ia: dict, diario: dict, paciente: dict) -> dict:
    """Devuelve {"nivel": "ROJO"|"AMARILLO"|"VERDE", "mensaje": str, "justificacion": [str, ...]}."""

    sintomas = set(diario.get("sintomas", []))
    tolerancia = diario.get("tolerancia", "bien_tolerado")
    cardiopatia_estructural = paciente.get("antecedentes", {}).get("cardiopatia_estructural", False)

    justificacion = []

    # --- ROJO ---
    sintomas_alarma = sintomas & SINTOMAS_ROJOS
    if sintomas_alarma:
        justificacion.append(f"Síntoma de alarma referido: {', '.join(sorted(sintomas_alarma))}.")

    if lectura_ia["qrs"] == "ancho" and lectura_ia.get("sospecha_tv"):
        justificacion.append("Trazado con QRS ancho y sospecha de taquicardia ventricular.")

    if lectura_ia["frecuencia"] > 150 and tolerancia == "mal_tolerado":
        justificacion.append(
            f"Taquicardia sostenida ({lectura_ia['frecuencia']} lpm) mal tolerada."
        )

    if lectura_ia["frecuencia"] < 40:
        justificacion.append(f"Bradicardia marcada ({lectura_ia['frecuencia']} lpm).")
    elif lectura_ia["frecuencia"] <= 50 and (sintomas & SINTOMAS_BRADICARDIA_ROJA):
        justificacion.append(
            f"Bradicardia ({lectura_ia['frecuencia']} lpm) con síntomas asociados: "
            f"{', '.join(sorted(sintomas & SINTOMAS_BRADICARDIA_ROJA))}."
        )

    hallazgo_relevante = (
        lectura_ia["regularidad"] == "irregular"
        or lectura_ia["qrs"] == "ancho"
        or lectura_ia["frecuencia"] > 100
        or lectura_ia.get("extrasistoles_frecuentes")
    )
    if cardiopatia_estructural and hallazgo_relevante:
        justificacion.append(
            "Antecedente de cardiopatía estructural en paciente con hallazgo relevante en el trazado."
        )

    if justificacion:
        return {
            "nivel": "ROJO",
            "mensaje": (
                "⚠️ Tu registro muestra signos que requieren atención médica urgente. "
                "Por favor, dirigite a un servicio de emergencias o guardia ahora mismo "
                "y lleva este registro con vos. El equipo médico fue notificado de inmediato."
            ),
            "justificacion": justificacion,
        }

    # --- AMARILLO ---
    justificacion = []

    if lectura_ia["regularidad"] == "irregular" and lectura_ia.get("sospecha_fa"):
        justificacion.append("Trazado irregular sugestivo de fibrilación auricular nueva.")

    if lectura_ia["regularidad"] == "regular" and lectura_ia["frecuencia"] > 100 and tolerancia != "mal_tolerado":
        justificacion.append(
            f"Taquicardia regular ({lectura_ia['frecuencia']} lpm) bien tolerada."
        )

    if lectura_ia.get("extrasistoles_frecuentes"):
        justificacion.append("Extrasístoles ventriculares frecuentes.")

    if diario.get("recurrencia_post_ablacion"):
        justificacion.append("Episodio compatible con recurrencia post-ablación.")

    if 40 <= lectura_ia["frecuencia"] <= 50:
        justificacion.append(f"Bradicardia ({lectura_ia['frecuencia']} lpm) sin síntomas de alarma.")

    if justificacion:
        return {
            "nivel": "AMARILLO",
            "mensaje": (
                "🟡 Recibimos tu registro. No parece una urgencia, pero el equipo médico va a "
                "revisarlo de forma prioritaria en las próximas 24 a 48 horas. Si en ese tiempo "
                "aparece dolor en el pecho, falta de aire en reposo, mareo intenso o un desmayo, "
                "consultá de inmediato a un servicio de emergencias."
            ),
            "justificacion": justificacion,
        }

    # --- VERDE ---
    return {
        "nivel": "VERDE",
        "mensaje": (
            "🟢 ¡Buenas noticias! Tu registro no muestra hallazgos que indiquen una urgencia. "
            "Quedó guardado en tu historial para que el equipo médico lo revise en tu próximo "
            "control de rutina. Si los síntomas cambian o empeoran, registrá un nuevo episodio "
            "o contactanos."
        ),
        "justificacion": ["Ritmo sin hallazgos de alarma y episodio bien tolerado."],
    }
