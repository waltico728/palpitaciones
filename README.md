# Palpitaciones (demo)

Telemedicina asistida por IA para pacientes con arritmias. Demo funcional en
Streamlit con datos de prueba ficticios. Ver [CLAUDE.md](CLAUDE.md) para el
documento maestro del proyecto y la lógica de triage.

## Cómo correrla

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Flujo

- **Paciente**: iniciá sesión eligiendo tu nombre de la lista (si ya tenés
  perfil) o registrate desde cero en la pestaña "Registrarme por primera
  vez". Después podés pasar por el onboarding, registrar un episodio
  (trazado de ejemplo o imagen + diario de síntomas) y revisar tu historial.
- **Médico**: ingresá con la clave de acceso del equipo médico para ver el
  tablero con la cola priorizada (rojos primero), el detalle del episodio y
  la acción de confirmar/reclasificar + escribir indicación.

Todo el estado vive en `st.session_state` durante la sesión (incluyendo los
pacientes que se registren); los archivos en `data/` son solo la semilla
inicial de pacientes y episodios de ejemplo. **Al reiniciarse el servidor se
pierden los datos creados durante la sesión** — para uso real esto debería
migrar a una base de datos persistente.

## Acceso del equipo médico

La clave por defecto es `1234` (ver [utils/auth.py](utils/auth.py)). Para
cambiarla en Streamlit Community Cloud sin tocar el código, agregá en
**Settings → Secrets** de la app:

```toml
clave_medico = "tu_clave_nueva"
```

## Desplegar en Streamlit Community Cloud

1. Creá un repositorio en GitHub y subí este proyecto:
   ```bash
   git remote add origin https://github.com/<tu-usuario>/palpitaciones.git
   git branch -M main
   git push -u origin main
   ```
2. Entrá a [share.streamlit.io](https://share.streamlit.io), conectá tu
   cuenta de GitHub y elegí este repositorio.
3. Indicá `app.py` como archivo principal y desplegá.
4. (Opcional) Configurá `clave_medico` en Secrets como se explica arriba.

## Aviso

Esta app es una herramienta de apoyo a la decisión y de organización del
flujo clínico, **no un dispositivo de diagnóstico autónomo**. Ninguna
conducta clínica relevante se ejecuta sin validación médica. Es una demo
con datos de prueba ficticios; no maneja datos reales de pacientes.
