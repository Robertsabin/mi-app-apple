import streamlit as st
import pandas as pd

def importar_archivo(funcion_procesar):
    """
    Función optimizada para cargar archivos SAP.
    Recibe 'funcion_procesar' que tiene el motor de caché activado.
    """
    st.markdown("### 📥 Carga de Archivos Maestros")
    st.info("Sube los 3 archivos de SAP para cruzar el inventario con las compras pendientes.")

    col1, col2, col3 = st.columns(3)

    # 1. CARGA DE STOCK SAP
    with col1:
        st.subheader("1. Stock SAP")
        f_sap = st.file_uploader("Inventario Actual", type=["xlsx", "xls"], key="u_sap")
        if f_sap:
            # Solo procesamos si el archivo no ha sido cargado ya en esta sesión
            if st.session_state.inventario is None or st.session_state.get('last_f_sap') != f_sap.name:
                st.session_state.inventario = funcion_procesar(f_sap)
                st.session_state['last_f_sap'] = f_sap.name
                st.success("✅ SAP cargado")

    # 2. CARGA DE PEDIDOS ABIERTOS
    with col2:
        st.subheader("2. Pedidos Abiertos")
        f_ped = st.file_uploader("Pedidos (Compras)", type=["xlsx", "xls"], key="u_ped")
        if f_ped:
            if st.session_state.pedidos_abiertos is None or st.session_state.get('last_f_ped') != f_ped.name:
                st.session_state.pedidos_abiertos = funcion_procesar(f_ped)
                st.session_state['last_f_ped'] = f_ped.name
                st.success("✅ Pedidos cargados")

    # 3. CARGA DE PRs ACTIVAS
    with col3:
        st.subheader("3. PRs Activas")
        f_pr = st.file_uploader("Solicitudes (PR)", type=["xlsx", "xls"], key="u_pr")
        if f_pr:
            if st.session_state.pr_activas is None or st.session_state.get('last_f_pr') != f_pr.name:
                st.session_state.pr_activas = funcion_procesar(f_pr)
                st.session_state['last_f_pr'] = f_pr.name
                st.success("✅ PRs cargadas")

    # --- VISTA PREVIA OPTIMIZADA ---
    if st.session_state.inventario is not None:
        st.divider()
        # Añadimos una pequeña métrica para confirmar la carga al usuario
        st.metric("Artículos cargados en SAP", f"{len(st.session_state.inventario):,}")
        
        with st.expander("🔍 Ver vista previa del Inventario SAP"):
            # Mostramos solo las primeras 10 filas para no saturar el navegador
            st.dataframe(st.session_state.inventario.head(10), use_container_width=True)
