import streamlit as st
import pandas as pd
from datetime import datetime

# Añadimos 'conn' como tercer argumento para recibir la conexión de Google Sheets
def operacion_qr(df_inventario, historial, conn):
    st.header("🎯 Registro de Inventario (QR)")

    # --- TRADUCTOR DE COLUMNAS SAP ---
    df_inventario.columns = df_inventario.columns.str.strip().str.upper()

    if "SKU" not in df_inventario.columns:
        if "NÚMERO MATERIAL" in df_inventario.columns:
            df_inventario = df_inventario.rename(columns={"NÚMERO MATERIAL": "SKU"})
        elif "NUMERO MATERIAL" in df_inventario.columns:
            df_inventario = df_inventario.rename(columns={"NUMERO MATERIAL": "SKU"})
    
    if "SKU" not in df_inventario.columns:
        st.error(f"❌ No se encuentra la columna identificadora. Columnas en tu Excel: {list(df_inventario.columns)}")
        return
    # ---------------------------------

    if "ot_manual" not in st.session_state: st.session_state.ot_manual = ""
    if "contador_escaneo" not in st.session_state: st.session_state.contador_escaneo = 0

    col1, col2, col3 = st.columns([1, 1, 1.8])
    with col1:
        tipo = st.radio("Movimiento:", ["ENTRADA", "SALIDA"])
    with col2:
        cantidad_input = st.number_input("Cantidad:", min_value=1, value=1, step=1)
    with col3:
        c_ot, c_btn = st.columns(2) 
        with c_ot:
            ot_val = st.text_input("Orden de Trabajo:", max_chars=9, value=st.session_state.ot_manual)
            st.session_state.ot_manual = ot_val
        with c_btn:
            st.write(" ")
            if st.button("🗑️ OT"):
                st.session_state.ot_manual = ""
                st.rerun()

    st.markdown("### 🔦 LECTURA QR")
    
    sku_raw = st.text_input(
        "Haga clic aquí antes de disparar con la pistola:", 
        placeholder="Esperando lectura...", 
        key=f"input_qr_{st.session_state.contador_escaneo}"
    )

    if sku_raw:
        sku_leido = str(sku_raw).strip().upper()
        maestro_skus = df_inventario["SKU"].astype(str).str.strip().str.upper().unique().tolist()
        
        if sku_leido in maestro_skus:
            # 1. Crear el nuevo registro
            nuevo_movimiento = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "SKU": sku_leido,
                "Movimiento": tipo,
                "Cantidad": cantidad_input if tipo == "ENTRADA" else (cantidad_input * -1),
                "OT": st.session_state.ot_manual if st.session_state.ot_manual else "SIN OT"
            }])

            # 2. GUARDAR EN GOOGLE SHEETS (Automático)
            try:
                # Leemos lo que hay ahora en el Sheets
                df_gsheet = conn.read(ttl=0)
                # Concatenamos la nueva fila
                df_actualizado = pd.concat([df_gsheet, nuevo_movimiento], ignore_index=True)
                # Subimos los datos actualizados
                conn.update(data=df_actualizado)
                st.toast("✅ Guardado en Google Sheets", icon="📊")
            except Exception as e:
                st.error(f"Error al conectar con Google Sheets: {e}")

            # 3. Actualizar historial local de la sesión
            st.session_state.historial = pd.concat([nuevo_movimiento, st.session_state.historial], ignore_index=True)
            st.session_state.contador_escaneo += 1
            st.rerun() 
        else:
            if len(sku_leido) > 3:
                st.error(f"❌ El código '{sku_leido}' no existe en la base de datos.")

    st.divider()
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("📋 Movimientos de la Sesión")
    with col_t2:
        if st.button("🗑️ BORRAR SESIÓN", use_container_width=True):
            st.session_state.historial = pd.DataFrame(columns=["Fecha", "Hora", "SKU", "Movimiento", "Cantidad", "OT"])
            st.rerun()

    st.dataframe(st.session_state.historial, use_container_width=True)
