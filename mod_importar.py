mod_importar.py
import streamlit as st
import pandas as pd

def importar_archivo():
    st.markdown("### 📥 Carga de Archivos Maestros")
    st.info("Sube los 3 archivos de SAP para cruzar el inventario con las compras pendientes.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. Stock SAP")
        f_sap = st.file_uploader("Inventario Actual", type=["xlsx", "xls"], key="u_sap")
        if f_sap:
            try:
                st.session_state.inventario = pd.read_excel(f_sap)
                st.success("✅ SAP cargado")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.subheader("2. Pedidos Abiertos")
        f_ped = st.file_uploader("Pedidos (Compras)", type=["xlsx", "xls"], key="u_ped")
        if f_ped:
            try:
                st.session_state.pedidos_abiertos = pd.read_excel(f_ped)
                st.success("✅ Pedidos cargados")
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        st.subheader("3. PRs Activas")
        f_pr = st.file_uploader("Solicitudes (PR)", type=["xlsx", "xls"], key="u_pr")
        if f_pr:
            try:
                st.session_state.pr_activas = pd.read_excel(f_pr)
                st.success("✅ PRs cargadas")
            except Exception as e:
                st.error(f"Error: {e}")

    # Mostrar resumen si el inventario principal está cargado
    if st.session_state.inventario is not None:
        st.divider()
        with st.expander("Ver vista previa del Inventario SAP"):
            st.dataframe(st.session_state.inventario.head(10), use_container_width=True)