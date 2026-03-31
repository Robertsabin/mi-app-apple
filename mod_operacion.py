import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime

def operacion_qr(df_inventario, historial):
    st.header("🎯 Registro de Inventario (QR)")

    # Estados iniciales
    if "ot_manual" not in st.session_state: st.session_state.ot_manual = ""
    if "contador_escaneo" not in st.session_state: st.session_state.contador_escaneo = 0

    # 1. Configuración de entrada
    col1, col2, col3 = st.columns([1, 1, 1.8])
    with col1:
        tipo = st.radio("Movimiento:", ["ENTRADA", "SALIDA"])
    with col2:
        cantidad_input = st.number_input("Cantidad:", min_value=1, value=1, step=1)
    with col3:
        # CORRECCIÓN AQUÍ: Añadimos el número 2 para crear dos columnas
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
    
    # 2. CUADRO DE ESCANEO
    sku_raw = st.text_input(
        "Haga clic aquí antes de disparar con la pistola:", 
        placeholder="Esperando lectura...", 
        key=f"input_qr_{st.session_state.contador_escaneo}"
    )

    if sku_raw:
        sku_leido = str(sku_raw).strip().upper()
        # Limpieza segura de SKUs del maestro para evitar errores de búsqueda
        maestro_skus = df_inventario["SKU"].astype(str).str.strip().str.upper().unique().tolist()
        
        if sku_leido in maestro_skus:
            valor_final = cantidad_input if tipo == "ENTRADA" else (cantidad_input * -1)
            
            nuevo_movimiento = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "SKU": sku_leido,
                "Movimiento": tipo,
                "Cantidad": valor_final,
                "OT": st.session_state.ot_manual if st.session_state.ot_manual else "SIN OT"
            }])

            st.session_state.historial = pd.concat([nuevo_movimiento, st.session_state.historial], ignore_index=True)
            st.session_state.contador_escaneo += 1
            st.rerun() 
        else:
            if len(sku_leido) > 3:
                st.error(f"❌ El SKU '{sku_leido}' no existe en SAP.")
                if st.button("Limpiar error"):
                    st.session_state.contador_escaneo += 1
                    st.rerun()

    st.divider()
    
    # 3. SECCIÓN DE CONTROL DE TABLA
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.subheader("📋 Movimientos de la Sesión")
    with col_t2:
        if st.button("🗑️ BORRAR TODO", use_container_width=True):
            st.session_state.historial = pd.DataFrame(columns=["Fecha", "Hora", "SKU", "Movimiento", "Cantidad", "OT"])
            st.rerun()

    st.dataframe(st.session_state.historial, use_container_width=True)

    if not st.session_state.historial.empty:
        csv = st.session_state.historial.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button(
            "📥 DESCARGAR REPORTE PARA EXCEL", 
            data=csv, 
            file_name=f"reporte_recambios_{datetime.now().strftime('%d_%m_%Y')}.csv", 
            mime='text/csv', 
            use_container_width=True
        )
