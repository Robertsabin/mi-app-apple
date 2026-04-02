import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection  # <--- NUEVA LIBRERÍA

# Importación de módulos locales
from estilos import aplicar_estilos_industriales
from mod_logo import mostrar_logo
from mod_importar import importar_archivo
from mod_seguimiento import mostrar_seguimiento_cruzado
from mod_busqueda import buscador_sku
from mod_operacion import operacion_qr
from mod_reset import resetear_historial

# 1. CONFIGURACIÓN DE PÁGINA Y CONEXIÓN
st.set_page_config(page_title="ALMACEN RECAMBIOS MTTO", layout="wide")
aplicar_estilos_industriales()

# Creamos la conexión global que usará tu hoja de Google
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN DIRECTO ---
st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col2:
    user_input = st.text_input("Usuario", key="user").strip().lower()
    pass_input = st.text_input("Contraseña", type="password", key="pass").strip()

# Validación: admin / 1234
if user_input == "admin" and pass_input == "1234":
    
    # Inicializar estados de inventario e historial
    if "inventario" not in st.session_state:
        st.session_state.inventario = None
    if "pedidos_abiertos" not in st.session_state:
        st.session_state.pedidos_abiertos = None
    if "pr_activas" not in st.session_state:
        st.session_state.pr_activas = None
        
    # El historial ahora lo leeremos directamente de Google Sheets si quieres, 
    # pero mantenemos la variable por compatibilidad con tus módulos
    if "historial" not in st.session_state:
        st.session_state.historial = pd.DataFrame(
            columns=["Fecha", "Hora", "SKU", "Movimiento", "Cantidad", "OT"]
        )

    # --- INTERFAZ PRINCIPAL ---
    st.divider()
    mostrar_logo()
    st.title("📦 SISTEMA INTEGRADO DE RECAMBIOS MTTO.")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Carga de Datos",
        "📊 Seguimiento y Cruce",
        "🔎 Buscador rápido",
        "🎯 Operación QR",
        "🗑 Reset"
    ])

    with tab1:
        importar_archivo()
        
    with tab2:
        mostrar_seguimiento_cruzado()
        
    with tab3:
        if st.session_state.inventario is not None:
            buscador_sku(st.session_state.inventario)
        else: 
            st.info("ℹ️ Cargue el Excel de SAP primero en la pestaña Carga de Datos")
        
    with tab4:
        if st.session_state.inventario is not None:
            # Pasamos 'conn' a la función para que mod_operacion pueda guardar en Sheets
            operacion_qr(st.session_state.inventario, st.session_state.historial, conn)
        else: 
            st.warning("⚠️ Debe cargar el inventario primero")
        
    with tab5:
        resetear_historial()
else:
    if user_input != "" or pass_input != "":
        st.error("❌ Credenciales incorrectas.")

