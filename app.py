import streamlit as st

from utils.auth import CLAVE_MEDICO, cerrar_sesion, es_medico, es_paciente
from utils.storage import agregar_paciente, get_pacientes, get_paciente, init_state, nuevo_paciente_id

st.set_page_config(page_title="Palpitaciones", page_icon="❤️", layout="wide")

init_state()

st.title("❤️ Palpitaciones")
st.caption("Tu ritmo, registrado en el momento exacto.")

st.warning(
    "**Aviso importante:** Palpitaciones es una herramienta de apoyo a la decisión y de "
    "organización del flujo clínico, **no un dispositivo de diagnóstico autónomo**. "
    "El trazado de una sola derivación no reemplaza un ECG de 12 derivaciones ni el "
    "juicio clínico. Ninguna conducta clínica relevante se ejecuta sin validación médica. "
    "Esta es una demo con datos de prueba ficticios."
)

st.markdown("---")

if es_paciente():
    actual = get_paciente(st.session_state.paciente_actual_id)
    st.success(f"Sesión iniciada como **{actual['nombre']}** (paciente).")
    st.page_link("pages/1_Paciente_Onboarding.py", label="Ir a Onboarding", icon="📝")
    st.page_link("pages/2_Paciente_Episodio.py", label="Registrar un episodio", icon="❤️")
    st.page_link("pages/3_Paciente_Historial.py", label="Ver mi historial", icon="📈")
    if st.button("Cerrar sesión"):
        cerrar_sesion()
        st.rerun()

elif es_medico():
    st.success("Sesión iniciada como **equipo médico**.")
    st.page_link("pages/4_Medico_Tablero.py", label="Ir al tablero médico", icon="🩺")
    if st.button("Cerrar sesión"):
        cerrar_sesion()
        st.rerun()

else:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Soy paciente")
        st.write(
            "Registrá un episodio de palpitaciones con tu wearable y un diario de síntomas, "
            "y recibí una clasificación preliminar y recomendaciones."
        )

        tab_login, tab_registro = st.tabs(["Ya tengo cuenta", "Registrarme por primera vez"])

        with tab_login:
            pacientes = get_pacientes()
            nombres = {p["id"]: p["nombre"] for p in pacientes}

            seleccion = st.selectbox(
                "Elegí tu nombre de la lista para iniciar sesión",
                options=list(nombres.keys()),
                format_func=lambda pid: nombres[pid],
                index=0,
            )

            st.caption(
                "Demo: en esta etapa el ingreso se simula eligiendo un nombre de una lista, "
                "sin contraseña. Cada paciente solo puede ver sus propios episodios. En una "
                "versión real esto requeriría autenticación verificada."
            )

            if st.button("Ingresar como paciente", type="primary"):
                st.session_state.rol = "paciente"
                st.session_state.paciente_actual_id = seleccion
                st.rerun()

        with tab_registro:
            st.caption(
                "Completá tus datos para crear tu perfil. Quedará guardado durante esta "
                "sesión de la app de demostración."
            )

            with st.form("form_registro_paciente"):
                nombre = st.text_input("Nombre completo")
                col_a, col_b = st.columns(2)
                with col_a:
                    edad = st.number_input("Edad", min_value=0, max_value=120, value=40)
                with col_b:
                    sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])

                motivo = st.text_input(
                    "Motivo de consulta",
                    placeholder="Ej: Palpitaciones en estudio, seguimiento post-ablación, etc.",
                )
                wearable = st.selectbox("Wearable que vas a usar", ["Apple Watch", "KardiaMobile", "Otro"])
                cardiopatia_estructural = st.checkbox("¿Tenés antecedente de cardiopatía estructural?")
                antecedentes_otros = st.text_area(
                    "Otros antecedentes cardiológicos relevantes",
                    placeholder="Ej: hipertensión, arritmias previas, cirugías, etc.",
                )
                medicacion = st.text_area(
                    "Medicación actual (una por línea)",
                    placeholder="Ej: Bisoprolol 2.5 mg/día",
                )
                caracteristicas = st.text_area(
                    "Características habituales de tus palpitaciones",
                    placeholder="Ej: episodios breves, de inicio y fin súbitos, etc.",
                )

                acepto_registro = st.checkbox(
                    "Acepto el consentimiento informado y la política de datos "
                    "(Ley 25.326), y entiendo que esta app es apoyo a la decisión, "
                    "no diagnóstico autónomo."
                )

                enviado = st.form_submit_button("Crear mi perfil e ingresar", type="primary")

                if enviado:
                    if not nombre.strip():
                        st.error("Ingresá tu nombre para continuar.")
                    elif not acepto_registro:
                        st.error("Necesitás aceptar el consentimiento informado para continuar.")
                    else:
                        nuevo_id = nuevo_paciente_id()
                        agregar_paciente({
                            "id": nuevo_id,
                            "nombre": nombre.strip(),
                            "edad": int(edad),
                            "sexo": sexo,
                            "motivo": motivo.strip() or "No especificado",
                            "wearable": wearable,
                            "antecedentes": {
                                "cardiopatia_estructural": cardiopatia_estructural,
                                "otros": antecedentes_otros.strip() or "Ninguno referido",
                            },
                            "medicacion": [m.strip() for m in medicacion.splitlines() if m.strip()] or ["Ninguna"],
                            "caracteristicas_habituales": caracteristicas.strip() or "No especificado",
                        })
                        st.session_state.rol = "paciente"
                        st.session_state.paciente_actual_id = nuevo_id
                        st.rerun()

    with col2:
        st.subheader("🩺 Soy médico")
        st.write(
            "Revisá la cola priorizada de episodios (rojos primero), confirmá o reclasificá "
            "el triage y enviá una indicación."
        )

        clave = st.text_input("Clave de acceso del equipo médico", type="password")

        if st.button("Ingresar como médico", type="primary"):
            if clave == CLAVE_MEDICO:
                st.session_state.rol = "medico"
                st.rerun()
            else:
                st.error("Clave incorrecta.")
