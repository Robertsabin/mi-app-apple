import streamlit as st
import streamlit as st

def aplicar_estilos_industriales():
    st.markdown("""
    <style>
    body, .stApp { background-color: #f4f6f9 !important; color: #1a1a1a !important; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #1c7ed6 !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; padding: 12px; font-weight: 600; color: #445; }
    .stTabs [aria-selected="true"] { color: #1c7ed6 !important; border-bottom: 3px solid #1c7ed6 !important; }
    .stButton>button { background-color: #1c7ed6 !important; color: white !important; font-size: 18px; border-radius: 6px; padding: 10px 0px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)
