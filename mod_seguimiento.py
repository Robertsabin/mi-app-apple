import streamlit as st
import streamlit as st
import pandas as pd

def mostrar_seguimiento_cruzado():
    st.markdown("### 📊 Clasificación y Cruce de Repuestos (Control Total)")
    
    if "inventario" not in st.session_state or st.session_state.inventario is None:
        st.warning("⚠️ Cargue primero el Inventario SAP en la pestaña 'Carga de Datos'.")
        return

    # 1. Función de limpieza
    def clean_sku_final(serie):
        return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0')

    # 2. Preparar Base SAP
    df = st.session_state.inventario.copy()
    df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]
    
    c_sku = next((c for c in df.columns if "material" in c.lower()), None)
    c_stock = next((c for c in df.columns if "valorado" in c.lower()), None)
    c_seg = next((c for c in df.columns if "seguridad" in c.lower()), None)
    c_planif = "Caract.planif.nec." 
    c_tipo = "Est.mat.específ.ce."   
    c_desc = next((c for c in df.columns if "descripción" in c.lower()), "Descripción")

    df['SKU_JOIN'] = clean_sku_final(df[c_sku])

    # 3. CRUCE CON PEDIDOS
    df['Nº Pedido'] = ""; df['Cant. Pedido'] = 0
    if st.session_state.pedidos_abiertos is not None:
        df_p = st.session_state.pedidos_abiertos.copy()
        df_p.columns = [str(c).strip().replace('\n', ' ') for c in df_p.columns]
        df_p['SKU_JOIN'] = clean_sku_final(df_p["Material"])
        p_res = df_p[df_p["Por entregar (cantidad)"] > 0].groupby('SKU_JOIN').agg({
            "Documento compras": lambda x: ', '.join(x.astype(str).unique()),
            "Por entregar (cantidad)": 'sum'
        }).reset_index()
        df = pd.merge(df, p_res, on='SKU_JOIN', how='left')
        df['Nº Pedido'] = df["Documento compras"].fillna("")
        df['Cant. Pedido'] = df["Por entregar (cantidad)"].fillna(0)

    # 4. CRUCE CON PRs
    df['Nº PR'] = ""; df['Cant. PR'] = 0
    if st.session_state.pr_activas is not None:
        df_pr = st.session_state.pr_activas.copy()
        df_pr.columns = [str(c).strip().replace('\n', ' ') for c in df_pr.columns]
        df_pr['SKU_JOIN'] = clean_sku_final(df_pr["Material"])
        pr_res = df_pr[df_pr["Cantidad solicitada"] > 0].groupby('SKU_JOIN').agg({
            "Solicitud de pedido": lambda x: ', '.join(x.astype(str).unique()),
            "Cantidad solicitada": 'sum'
        }).reset_index()
        df = pd.merge(df, pr_res, on='SKU_JOIN', how='left', suffixes=('', '_pr'))
        df['Nº PR'] = df["Solicitud de pedido"].fillna("")
        df['Cant. PR'] = df["Cantidad solicitada"].fillna(0)

    # 5. Semáforo
    df['V_Stock'] = pd.to_numeric(df[c_stock], errors='coerce').fillna(0)
    df['V_Seg'] = pd.to_numeric(df[c_seg], errors='coerce').fillna(0)
    df['Estado'] = df.apply(lambda r: "🔴 CRÍTICO" if r['V_Stock'] < r['V_Seg'] else ("🟡 ADVERTENCIA" if r['V_Stock'] == r['V_Seg'] else "🟢 OK"), axis=1)

    # --- 6. FILTROS ESTILO EXCEL (Multiselect) ---
    st.write("---")
    st.markdown("#### 🎯 Filtros de Selección")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        # Filtro de Planificación (ND / PD)
        opciones_planif = sorted(df[c_planif].dropna().unique().tolist())
        sel_planif = st.multiselect("Planificación (ND/PD):", opciones_planif, default=opciones_planif)
        
    with f2:
        # Filtro de Tipo (YA / YI / Y1 / Y2)
        opciones_tipo = sorted(df[c_tipo].dropna().unique().tolist())
        sel_tipo = st.multiselect("Tipo (YA/YI/Y1/Y2):", opciones_tipo, default=opciones_tipo)
        
    with f3:
        # Filtro de Estado
        sel_estado = st.multiselect("Estado:", ["🔴 CRÍTICO", "🟡 ADVERTENCIA", "🟢 OK"], default=["🔴 CRÍTICO", "🟡 ADVERTENCIA", "🟢 OK"])

    # Aplicar filtros
    df_filtrado = df[
        (df[c_planif].isin(sel_planif)) & 
        (df[c_tipo].isin(sel_tipo)) & 
        (df['Estado'].isin(sel_estado))
    ]

    # --- 7. MÉTRICAS Y TABLA ---
    res = df_filtrado['Estado'].value_counts()
    m1, m2, m3 = st.columns(3)
    m1.metric("🔴 CRÍTICO", res.get("🔴 CRÍTICO", 0))
    m2.metric("🟡 ADVERTENCIA", res.get("🟡 ADVERTENCIA", 0))
    m3.metric("🟢 OK", res.get("🟢 OK", 0))

    cols = ['Estado', c_sku, c_desc, c_planif, c_tipo, 'V_Stock', 'V_Seg', 'Nº Pedido', 'Cant. Pedido', 'Nº PR', 'Cant. PR']
    df_ver = df_filtrado[cols].rename(columns={c_sku: "SKU", c_desc: "Descripción", c_planif: "Planif.", c_tipo: "Tipo", "V_Stock": "Stock", "V_Seg": "Seg."})
    
    st.dataframe(df_ver.sort_values("Estado"), use_container_width=True, hide_index=True)
    st.success(f"Viendo {len(df_ver)} registros filtrados.")
