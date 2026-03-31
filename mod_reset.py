import streamlit as st
import streamlit as st

def resetear_historial():
    st.header("🗑 Resetear Movimientos")
    st.warning("⚠️ CUIDADO: Esto borrará todo el historial de entradas y salidas de la sesión actual.")

    if st.button("🗑 Confirmar Borrado Total"):
        st.session_state.historial = st.session_state.historial.iloc[0:0]
        st.success("✔ El historial ha sido vaciado correctamente.")
