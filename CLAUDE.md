# Palpitaciones — Documento maestro del proyecto

Telemedicina asistida por IA para pacientes con arritmias. Captura del síntoma
en tiempo real mediante wearable (ECG de 1 derivación) + diario estructurado,
clasificación preliminar por IA, triage de prioridad y revisión médica
asíncrona desde un tablero.

Referencia completa: [docs/Palpitaciones_Documento_Diseno.docx](docs/Palpitaciones_Documento_Diseno.docx)

## Objetivo y alcance de esta primera versión (demo Streamlit)

Construir una demo funcional que muestre el flujo completo paciente → IA →
triage → médico, con datos de prueba ficticios. Todo en memoria /
`st.session_state` + archivos locales en `data/`. Sin base de datos externa
ni autenticación real.

## Usuarios

- **Paciente**: registra episodios de palpitaciones (ECG simulado + diario de
  síntomas) y recibe el resultado del triage.
- **Médico**: revisa la cola priorizada (rojos primero), confirma o
  reclasifica el triage y escribe una indicación.

## Restricción central — rol de la IA

**La IA es apoyo a la decisión y organización del flujo, NO un diagnóstico
autónomo.** Ninguna conducta clínica relevante se ejecuta sin validación
médica. El trazado de una sola derivación no reemplaza un ECG de 12
derivaciones ni el juicio clínico. Esto debe quedar visible como descargo de
seguridad en la app (onboarding y resultado de triage).

## Lógica de triage (criterios de alerta)

| Nivel | Criterios (trazado + síntomas) | Conducta |
|---|---|---|
| **ROJO** | Síncope o presíncope; dolor torácico; disnea de reposo; QRS ancho con sospecha de TV; taquicardia sostenida >150–180 lpm mal tolerada; antecedente de cardiopatía estructural; **bradicardia <40 lpm, o 40–50 lpm con síncope/presíncope/mareo.** | Instrucción de consulta urgente / emergencias. Aviso inmediato al equipo médico. |
| **AMARILLO** | Trazado irregular sugestivo de FA nueva; taquicardia regular bien tolerada; extrasístoles ventriculares frecuentes; recurrencia post-ablación; **bradicardia 40–50 lpm sin síntomas de alarma.** | Revisión médica priorizada en 24–48 h. |
| **VERDE** | Ritmo sinusal; episodios breves autolimitados y bien tolerados; trazado sin hallazgos relevantes. | Revisión de rutina; mensaje tranquilizador y educativo. |

Los umbrales son orientativos y deben poder ajustarse por el médico
responsable. La IA prioriza y sugiere; nunca decide de forma autónoma una
conducta clínica.

## Datos de un episodio

- Trazado de ECG de 1 derivación (simulado/de ejemplo o imagen subida).
- Lectura preliminar (frecuencia, regularidad, ancho de QRS, sospecha de FA).
- Diario: hora de inicio, duración, forma de inicio/fin, desencadenantes,
  síntomas asociados (disnea, dolor torácico, mareo, síncope), tolerancia.
- Nivel de triage asignado + mensaje al paciente.
- Estado de revisión médica (pendiente / confirmado / reclasificado) +
  indicación del médico.

## Pacientes a los que está dirigida (para datos de prueba)

Diagnóstico en estudio, arritmias conocidas (FA paroxística, TPSV,
extrasístoles, taquicardias), seguimiento post-ablación, control
farmacológico con antiarrítmicos.

## Stack

Python + Streamlit. Multipágina (`pages/`). Datos de ejemplo en `data/`
(JSON). Sin servicios externos.
