mod_clasificacion.py
import streamlit as st
import pandas as pd

def clasificar_por_estado():
    if "inventario" not in st.session_state or st.session_state.inventario is None:
        st.warning("⚠️ Debe importar el inventario en la pestaña 'Importar SAP' primero.")
        return

    st.header("🚦 Clasificación y Seguimiento de Pedidos")

    # 1. CARGA DEL EXCEL DE PEDIDOS
    with st.expander("📦 CARGAR SEGUIMIENTO DE COMPRAS (PR / PO)"):
        archivo_p = st.file_uploader("Subir Excel de Pedidos Pendientes", type=["xlsx"], key="u_pedidos_vfinal_fix")
        if archivo_p:
            df_p = pd.read_excel(archivo_p)
            df_p = df_p.rename(columns={"Documento compras": "NUM_DOCUMENTO", "Material": "SKU_PEDIDO"})
            if "NUM_DOCUMENTO" in df_p.columns and "SKU_PEDIDO" in df_p.columns:
                st.session_state.pedidos = df_p
                st.success(f"✅ Archivo de pedidos cargado ({len(df_p)} líneas).")

    # 2. PROCESAMIENTO DE DATOS
    df_inv = st.session_state.inventario.copy()
    
    def asignar_estado(row):
        stock = float(row.get("Stock Valorado", 0))
        seguridad = float(row.get("Stock Seguridad", 0))
        if stock < seguridad: return "Crítico"
        elif stock == seguridad: return "Advertencia"
        else: return "OK"
    
    df_inv["Estado"] = df_inv.apply(asignar_estado, axis=1)

    # --- LÓGICA DE CRUCE BLINDADA (Elimina el .0 y ceros a la izquierda) ---
    if "pedidos" in st.session_state and st.session_state.pedidos is not None:
        p_df = st.session_state.pedidos.copy()
        
        # Función para limpiar cualquier dato y dejarlo como texto puro
        def limpiar_a_texto(dato):
            if pd.isna(dato): return ""
            # Convertir a string, quitar el .0 si existe, quitar espacios y ceros iniciales
            s = str(dato).split('.')[0].strip().lstrip('0')
            return s

        df_inv["SKU_LINK"] = df_inv["SKU"].apply(limpiar_a_texto)
        p_df["SKU_LINK"] = p_df["SKU_PEDIDO"].apply(limpiar_a_texto)
        
        # Limpiar también el número de documento para quitar el .0 en la visualización
        p_df["NUM_DOCUMENTO_LIMPIO"] = p_df["NUM_DOCUMENTO"].apply(limpiar_a_texto)
        
        # Nos quedamos con el último pedido de cada SKU
        p_unico = p_df.drop_duplicates(subset=["SKU_LINK"], keep='last')
        
        # Unimos las tablas
        df_inv = pd.merge(df_inv, p_unico[["SKU_LINK", "NUM_DOCUMENTO_LIMPIO"]], on="SKU_LINK", how="left")
        df_inv["Seguimiento"] = df_inv["NUM_DOCUMENTO_LIMPIO"].replace("", "❌ SIN PEDIDO").fillna("❌ SIN PEDIDO")
    else:
        df_inv["Seguimiento"] = "⚠️ Cargue pedidos para seguimiento"

    # --- 3. MÉTRICAS Y GRÁFICA ---
    conteo = df_inv["Estado"].value_counts()
    col_m1, col_m2 = st.columns(2) 
    with col_m1:
        st.metric("🔴 Críticos", conteo.get("Crítico", 0))
        st.metric("🟡 Advertencia", conteo.get("Advertencia", 0))
        st.metric("🔵 OK", conteo.get("OK", 0))
    with col_m2:
        st.bar_chart(conteo, color="#1c7ed6") 

    st.divider()

    # --- 4. TABS CON LISTADOS ---
    tab_c, tab_a, tab_o = st.tabs(["🔴 LISTA CRÍTICOS", "🟡 ADVERTENCIA", "🔵 OK"])

    with tab_c:
        df_c = df_inv[df_inv["Estado"] == "Crítico"]
        if not df_c.empty:
            # Seleccionamos columnas finales para mostrar
            st.dataframe(df_c[["SKU", "Descripción", "Stock Valorado", "Stock Seguridad", "Seguimiento"]], use_container_width=True)
        else:
            st.success("No hay materiales críticos.")

    with tab_a:
        st.dataframe(df_inv[df_inv["Estado"] == "Advertencia"], use_container_width=True)
    with tab_o:
        st.dataframe(df_inv[df_inv["Estado"] == "OK"], use_container_width=True)