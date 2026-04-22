import streamlit as st
import pandas as pd

def mostrar_seguimiento_cruzado():
    st.markdown("### 📊 Clasificación y Cruce de Repuestos (Control Total)")
    
    if "inventario" not in st.session_state or st.session_state.inventario is None:
        st.warning("⚠️ Cargue primero el Inventario SAP en la pestaña 'Carga de Datos'.")
        return

    # 1. Función de limpieza de SKUs
    def clean_sku_final(serie):
        return serie.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0')

    # 2. Preparar Base SAP y Buscador de Columnas Inteligente
    df = st.session_state.inventario.copy()
    df.columns = [str(col).strip() for col in df.columns] # Limpiar espacios en nombres de columnas
    
    # Buscamos las columnas por palabras clave para evitar el KeyError
    c_sku = next((c for c in df.columns if "material" in c.lower()), None)
    c_stock = next((c for c in df.columns if "valorado" in c.lower()), None)
    c_seg = next((c for c in df.columns if "seguridad" in c.lower()), None)
    c_desc = next((c for c in df.columns if "descripción" in c.lower() or "texto breve" in c.lower()), "Descripción")
    
    # Columnas problemáticas (Planificación y Tipo)
    c_planif = next((c for c in df.columns if "planif" in c.lower()), None)
    c_tipo = next((c for c in df.columns if "específ.ce" in c.lower() or "est.mat" in c.lower()), None)

    # Verificación de seguridad: si faltan columnas críticas, avisamos
    if not c_planif or not c_tipo:
        st.error(f"❌ No se encontraron las columnas de Planificación o Tipo en el Excel. Columnas detectadas: {list(df.columns)}")
        return

    df['SKU_JOIN'] = clean_sku_final(df[c_sku])

    # 3. CRUCE CON PEDIDOS
    df['Nº Pedido'] = ""; df['Cant. Pedido'] = 0
    if st.session_state.get('pedidos_abiertos') is not None:
        df_p = st.session_state.pedidos_abiertos.copy()
        df_p.columns = [str(c).strip() for c in df_p.columns]
        c_sku_p = next((c for c in df_p.columns if "material" in c.lower()), None)
        c_entregar = next((c for c in df_p.columns if "entregar" in c.lower()), None)
        c_doc = next((c for c in df_p.columns if "documento" in c.lower() or "pedido" in c.lower()), None)

        if c_sku_p and c_entregar:
            df_p['SKU_JOIN'] = clean_sku_final(df_p[c_sku_p])
            p_res = df_p[df_p[c_entregar] > 0].groupby('SKU_JOIN').agg({
                c_doc: lambda x: ', '.join(x.astype(str).unique()),
                c_entregar: 'sum'
            }).reset_index()
            df = pd.merge(df, p_res, on='SKU_JOIN', how='left')
            df['Nº Pedido'] = df[c_doc].fillna("")
            df['Cant. Pedido'] = df[c_entregar].fillna(0)

    # 4. CRUCE CON PRs
    df['Nº PR'] = ""; df['Cant. PR'] = 0
    if st.session_state.get('pr_activas') is not None:
        df_pr = st.session_state.pr_activas.copy()
        df_pr.columns = [str(c).strip() for c in df_pr.columns]
        c_sku_pr = next((c for c in df_pr.columns if "material" in c.lower()), None)
        c_cant_pr = next((c for c in df_pr.columns if "cantidad" in c.lower()), None)
        c_doc_pr = next((c for c in df_pr.columns if "solicitud" in c.lower() or "pr" in c.lower()), None)

        if c_sku_pr and c_cant_pr:
            df_pr['SKU_JOIN'] = clean_sku_final(df_pr[c_sku_pr])
            pr_res = df_pr[df_pr[c_cant_pr] > 0].groupby('SKU_JOIN').agg({
                c_doc_pr: lambda x: ', '.join(x.astype(str).unique()),
                c_cant_pr: 'sum'
            }).reset_index()
            df = pd.merge(df, pr_res, on='SKU_JOIN', how='left', suffixes=('', '_pr'))
            df['Nº PR'] = df[c_doc_pr].fillna("")
            df['Cant. PR'] = df[c_cant_pr].fillna(0)

    # 5. Semáforo
    df['V_Stock'] = pd.to_numeric(df[c_stock], errors='coerce').fillna(0)
    df['V_Seg'] = pd.to_numeric(df[c_seg], errors='coerce').fillna(0)
    df['Estado'] = df.apply(lambda r: "🔴 CRÍTICO" if r['V_Stock'] < r['V_Seg'] else ("🟡 ADVERTENCIA" if r['V_Stock'] == r['V_Seg'] else "🟢 OK"), axis=1)

    # --- 6. FILTROS ---
    st.write("---")
    st.markdown("#### 🎯 Filtros de Selección")
    f1, f2, f3 = st.columns(3)
    
    with f1:
        opciones_planif = sorted(df[c_planif].dropna().unique().tolist())
        sel_planif = st.multiselect("Planificación:", opciones_planif, default=opciones_planif)
        
    with f2:
        opciones_tipo = sorted(df[c_tipo].dropna().unique().tolist())
        sel_tipo = st.multiselect("Tipo Mat.:", opciones_tipo, default=opciones_tipo)
        
    with f3:
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

    cols_finales = ['Estado', c_sku, c_desc, c_planif, c_tipo, 'V_Stock', 'V_Seg', 'Nº Pedido', 'Cant. Pedido', 'Nº PR', 'Cant. PR']
    df_ver = df_filtrado[cols_finales].rename(columns={c_sku: "SKU", c_desc: "Descripción", c_planif: "Planif.", c_tipo: "Tipo", "V_Stock": "Stock", "V_Seg": "Seg."})
    
    st.dataframe(df_ver.sort_values("Estado"), use_container_width=True, hide_index=True)
    st.success(f"Viendo {len(df_ver)} registros filtrados.")
