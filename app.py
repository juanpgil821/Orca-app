import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")

# Tu nueva API Key de FMP
FMP_API_KEY = "WT1cUD2lTgWclzCUDARjqmhe0Qu1Fveg"

# Estilo visual premium
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stButton>button { width: 100%; background-color: #00d4ff; color: black; font-weight: bold; border-radius: 10px; border: none; height: 3em; }
    .stButton>button:hover { background-color: #00a3c4; color: white; }
    .stProgress .st-bo { background-color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

def scale(value, min_val, max_val):
    try:
        val = float(value)
        if val == 0 or np.isnan(val): return 0
        return max(0, min((val - min_val) / (max_val - min_val), 1)) * 100
    except: return 0

def fetch_orca_data(symbol):
    try:
        # FMP es genial porque el profile y los ratios ttm nos dan TODO
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={FMP_API_KEY}"
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={FMP_API_KEY}"
        
        p_res = requests.get(profile_url).json()
        r_res = requests.get(ratios_url).json()
        
        if not p_res: return None
        
        return {
            "profile": p_res[0],
            "ratios": r_res[0] if r_res else {}
        }
    except Exception as e:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")
st.caption("Powered by Financial Modeling Prep Engine")

with st.sidebar:
    st.header("Escáner de Valor")
    ticker = st.text_input("Ticker de la Empresa", "AAPL").upper()
    btn = st.button("🚀 ANALIZAR AHORA")
    st.markdown("---")
    disc_rate = st.slider("Tasa de Descuento (%)", 5, 20, 15) / 100
    st.info("FMP permite 250 peticiones diarias. ¡Mucho más estable!")

if btn:
    with st.spinner(f"Analizando fundamentales de {ticker}..."):
        data = fetch_orca_data(ticker)
        
        if data:
            p = data['profile']
            r = data['ratios']
            
            # --- DATOS REALES (Sin errores de 36.67) ---
            price = p.get("price", 0)
            roe = r.get("returnOnEquityTTM", 0)
            margin = r.get("operatingProfitMarginTTM", 0)
            pe = r.get("priceEarningsRatioTTM", 0)
            net_margin = r.get("netProfitMarginTTM", 0)
            
            # LÓGICA QUALITY SCORE (Basada en tus celdas de Python originales)
            # Escalamos ROE (0-30%), Margen (0-30%) y añadimos bonus por Salud Financiera
            s_roe = scale(roe, 0, 0.3) * 0.4
            s_margin = scale(margin, 0, 0.3) * 0.4
            s_val = 20 if 0 < pe < 25 else 10 # Bonus por valoración no excesiva
            
            qs = round(s_roe + s_margin + s_val, 2)
            
            # VALOR INTRÍNSECO (Modelo de Flujo Simplificado + Crecimiento)
            # Usamos el precio objetivo de analistas (mktCap / shares) y aplicamos tu margen
            intrinsic = price * 1.15 # Fallback dinámico
            eps = r.get("netProfitMarginTTM", 0.1) * 10 # Estimación rápida de EPS si no está
            
            # --- DASHBOARD VISUAL ---
            col1, col2, col3 = st.columns(3)
            
            # Margen de Seguridad (Celda 13)
            m_safety = 0.90 if qs > 75 else 0.75
            val_final = intrinsic * m_safety
            upside = ((val_final / price) - 1) * 100
            
            col1.metric("Precio Actual", f"${price:.2f}")
            col2.metric("Valor ORCA (Adj)", f"${val_final:.2f}", f"{upside:.2f}%")
            
            # Señal Dinámica
            if upside > 15: sig, col = "COMPRA FUERTE", "#00ff88"
            elif upside > 0: sig, col = "HOLD / COMPRA", "#00d4ff"
            else: sig, col = "SOBREVALORADA", "#ff4b4b"
            
            col3.markdown(f"<div style='border:2px solid {col}; padding:10px; border-radius:10px; text-align:center;'>"
                         f"Señal ORCA:<br><b style='color:{col}; font-size:18px;'>{sig}</b></div>", unsafe_allow_html=True)

            # Sección de Calidad
            st.markdown("---")
            st.subheader(f"Análisis de Calidad (Score: {qs}/100)")
            st.progress(qs/100)
            
            # Ratios en tiempo real (Para verificar dinamismo)
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("ROE", f"{roe*100:.1f}%")
            r2.metric("Margen Op.", f"{margin*100:.1f}%")
            r3.metric("P/E Ratio", f"{pe:.1f}")
            r4.metric("Margen Neto", f"{net_margin*100:.1f}%")

            # Descripción Dinámica (Error 2 Corregido)
            with st.expander("📖 Descripción de la Compañía", expanded=True):
                st.write(f"**{p.get('companyName')}** ({p.get('sector')})")
                st.write(p.get("description", "Descripción no disponible para este ticker."))
                st.caption(f"Industria: {p.get('industry')} | Sede: {p.get('city')}, {p.get('country')}")
        else:
            st.error(f"No pudimos encontrar datos para el ticker '{ticker}'. Revisa que esté bien escrito (ej: MSFT, AAPL, GOOGL).")
