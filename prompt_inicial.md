# Prompt inicial para Claude Code

Copiá y pegá esto como tu primer mensaje dentro de Claude Code, ya parado en la
carpeta del proyecto (con CLAUDE.md y el documento de diseño adentro):

---

Leé el archivo CLAUDE.md y el documento de diseño en docs/ para entender el
proyecto completo.

Quiero que construyas la primera versión de la app "Palpitaciones": una demo
funcional en Streamlit que muestre el flujo completo descrito en CLAUDE.md, con
datos de prueba ficticios.

Empezá por lo siguiente:

1. Creá la estructura del proyecto (app.py, pages/, data/, requirements.txt,
   README.md) y un archivo de pacientes y episodios de ejemplo en data/.
2. Implementá la vista Paciente: onboarding simulado, registro de episodio
   (subir imagen de ECG o elegir un trazado de ejemplo + formulario de síntomas),
   y el cálculo del triage ROJO/AMARILLO/VERDE según las reglas de CLAUDE.md,
   con el mensaje correspondiente.
3. Implementá la vista Médico: tablero con la cola priorizada (rojos primero),
   detalle del episodio, y la acción de confirmar/reclasificar + escribir
   indicación.
4. Incluí el descargo de seguridad visible y respetá la restricción de que la IA
   es apoyo a la decisión, no diagnóstico autónomo.

No uses base de datos externa ni autenticación real todavía: todo en memoria /
session_state y archivos locales. Asegurate de que arranque con
`streamlit run app.py` después de `pip install -r requirements.txt`.

Antes de escribir código, mostrame un plan breve de archivos y pantallas para
que lo aprobemos juntos. Después implementalo paso a paso y andá mostrándome
cómo correrlo localmente para probar.

---

Después de esa primera versión, pedile cosas como:
- "Agregá la pantalla de tendencias del paciente con un gráfico de frecuencia de episodios."
- "El mensaje del triage verde quedó muy técnico, hacelo más cálido para el paciente."
- "Preparalo para desplegar en Streamlit Community Cloud: creá el repo, el .gitignore y explicame cómo subirlo a GitHub."
