import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Importación de módulos locales
from estilos import aplicar_estilos_industriales
from mod_logo import mostrar_logo
from mod_importar import importar_archivo
from mod_seguimiento import mostrar_seguimiento_cruzado
from mod_busqueda import buscador_sku
from mod_operacion import operacion_qr
from mod_reset import resetear_historial

# ==========================================
# 1. MOTOR DE VELOCIDAD (CACHÉ)
# ==========================================
@st.cache_data(show_spinner="Optimizando datos de SAP...")
def procesar_excel_universal(file):
    """Lee el Excel una sola vez y lo guarda en la memoria rápida."""
    try:
        df = pd.read_excel(file)
        # Limpieza automática de espacios en blanco en los nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        return None

# ==========================================
# 2. CONFIGURACIÓN Y LOGIN
# ==========================================
st.set_page_config(page_title="ALMACEN RECAMBIOS MTTO", layout="wide")
aplicar_estilos_industriales()

conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("<h2 style='text-align: center;'>🔐 Acceso al Sistema</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col2:
    user_input = st.text_input("Usuario", key="user").strip().lower()
    pass_input = st.text_input("Contraseña", type="password", key="pass").strip()

# Validación
if user_input == "admin" and pass_input == "1234":
    
    # --- INICIALIZACIÓN DE ESTADOS (Session State) ---
    if "inventario" not in st.session_state:
        st.session_state.inventario = None
    if "pedidos_abiertos" not in st.session_state:
        st.session_state.pedidos_abiertos = None
    if "pr_activas" not in st.session_state:
        st.session_state.pr_activas = None
    if "historial" not in st.session_state:
        st.session_state.historial = pd.DataFrame(
            columns=["Fecha", "Hora", "SKU", "Movimiento", "Cantidad", "OT"]
        )

    # --- INTERFAZ PRINCIPAL ---
    st.divider()
    mostrar_logo()
    st.title("📦 SISTEMA INTEGRADO DE RECAMBIOS MTTO.")
    
    # Definición de pestañas
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Carga de Datos",
        "📊 Seguimiento y Cruce",
        "🔎 Buscador rápido",
        "🎯 Operación QR",
        "📜 Historial General",
        "🗑 Reset"
    ])

    with tab1:
        # Pasamos la función de caché al módulo de importar
        importar_archivo(procesar_excel_universal)
        
    with tab2:
        if st.session_state.inventario is not None:
            mostrar_seguimiento_cruzado()
        else:
            st.info("ℹ️ Pendiente cargar datos en la pestaña 1")
        
    with tab3:
        if st.session_state.inventario is not None:
            buscador_sku(st.session_state.inventario)
        else: 
            st.info("ℹ️ Cargue el Excel de SAP primero en la pestaña Carga de Datos")
        
    with tab4:
        if st.session_state.inventario is not None:
            operacion_qr(st.session_state.inventario, st.session_state.historial, conn)
        else: 
            st.warning("⚠️ Debe cargar el inventario primero")

    with tab5:
        st.subheader("📜 Registro Histórico Completo (Nube)")
        try:
            # TTL=60 permite que la app sea rápida durante 1 minuto antes de volver a preguntar a Google
            df_historico = conn.read(ttl=60)
            
            if df_historico is not None and not df_historico.empty:
                busqueda = st.text_input("🔍 Buscar por SKU o OT:", placeholder="Escriba algo...")
                if busqueda:
                    mask = df_historico.apply(lambda r: r.astype(str).str.contains(busqueda, case=False).any(), axis=1)
                    st.dataframe(df_historico[mask], use_container_width=True)
                else:
                    st.dataframe(df_historico, use_container_width=True)
                
                csv_total = df_historico.to_csv(index=False, sep=';').encode('utf-8-sig')
                st.download_button("📥 Descargar Historial (.csv)", csv_total, "historial_total.csv", "text/csv")
            else:
                st.info("No hay datos en la nube.")
        except Exception as e:
            st.error(f"Error de conexión con historial: {e}")
        
    with tab6:
        resetear_historial()
else:
    if user_input != "" or pass_input != "":
        st.error("❌ Credenciales incorrectas.")



