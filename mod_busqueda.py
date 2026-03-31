mod_busqueda.py
import streamlit as st

def buscador_sku(df):
    st.header("🔎 Búsqueda instantánea de SKU")

    q = st.text_input("Buscar SKU o descripción:", placeholder="Ej: 82076415 / tornillo…")

    if q:
        q = q.lower()
        # Buscamos en las columnas SKU o Descripción
        f = df[
            df["SKU"].astype(str).str.contains(q) | 
            df["Descripción"].astype(str).str.lower().str.contains(q)
        ]
        
        if not f.empty:
            st.success(f"Se han encontrado {len(f)} resultados")
            st.dataframe(f, use_container_width=True)
        else:
            st.info("No se encontraron coincidencias.")