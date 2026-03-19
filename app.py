import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")

# Tu clave de FMP
FMP_API_KEY = "WT1cUD2lTgWclzCUDARjqmhe0Qu1Fveg"

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stButton>button { width: 100%; background-color: #00d4ff; color: black; font-weight: bold; border-radius: 10px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

def scale(value, min_val, max_val):
    try:
        val = float(value)
        if val == 0 or np.isnan(val): return 0
        return max(0, min((val - min_val) / (max_val - min_val), 1)) * 100
    except: return 0

def fetch_orca_data(symbol):
    # Limpieza profunda del ticker
    clean_symbol = str(symbol).strip().upper()
    if not clean_symbol: return None

    try:
        # Llamadas con timeout para evitar que la app se quede colgada
        p_url = f"https://financialmodelingprep.com/api/v3/profile/{clean_symbol}?apikey={FMP_API_KEY}"
        r_url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{clean_symbol}?apikey={FMP_API_KEY}"
        
        p_res = requests.get(p_url, timeout=10).json()
        r_res = requests.get(r_url, timeout=10).json()
        
        # FMP devuelve una LISTA de diccionarios [ {...} ]
        if isinstance(p_res, list) and len(p_res) > 0:
            profile_data = p_res[0]
            # Los ratios a veces no existen para tickers muy nuevos o raros
            ratios_data = r_res[0] if (isinstance(r_res, list) and len(r_res) > 0) else {}
            
            return {
                "profile": profile_data,
                "ratios": ratios_data
            }
        return None
    except Exception as e:
        st.sidebar.warning(f"Error de red: {e}")
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")

with st.sidebar:
    st.header("Escáner de Valor")
    ticker_input = st.text_input("Ticker (ej: MSFT, AAPL, V)", "AAPL")
    btn = st.button("🚀 ANALIZAR AHORA")
    st.markdown("---")
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100

if btn:
    with st.spinner(f"Accediendo a datos de {ticker_input}..."):
        data = fetch_orca_data(ticker_input)
        
        if data:
            p = data['profile']
            r = data['ratios']
            
            # Extracción segura de datos
            price = p.get("price", 0)
            roe = r.get("returnOnEquityTTM", 0)
            margin = r.get("operatingProfitMarginTTM", 0)
            pe = r.get("priceEarningsRatioTTM", 0)
            
            # --- QUALITY SCORE DINÁMICO ---
            s_roe = scale(roe, 0, 0.3) * 0.4
            s_margin = scale(margin, 0, 0.3) * 0.4
            s_val = 20 if 0 < pe < 25 else 10
            qs = round(s_roe + s_margin + s_val, 2)
            
            # --- VALOR INTRÍNSECO (Fórmula ORCA Simplificada) ---
            # Si no hay datos de analistas, usamos un múltiplo de seguridad
            intrinsic = price * 1.15 
            
            # --- DASHBOARD ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Precio Actual", f"${price:.2f}")
            
            m_safety = 0.90 if qs > 75 else 0.75
            val_final = intrinsic * m_safety
            upside = ((val_final / price) - 1) * 100
            
            col2.metric("Valor ORCA", f"${val_final:.2f}", f"{upside:.2f}%")
            
            # Señal Visual
            color = "#00ff88" if upside > 10 else "#ff4b4b" if upside < -10 else "#ffaa00"
            status = "BUY" if upside > 10 else "SELL" if upside < -10 else "HOLD"
            col3.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'>Señal:<br><b style='color:{color}; font-size:20px;'>{status}</b></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader(f"Calidad del Negocio: {qs}/100")
            st.progress(qs/100)
            
            # Ratios Reales
            r1, r2, r3 = st.columns(3)
            r1.metric("ROE", f"{roe*100:.2f}%")
            r2.metric("Márgen Op.", f"{margin*100:.2f}%")
            r3.metric("P/E Ratio", f"{pe:.2f}")

            with st.expander("📖 Descripción de la Empresa", expanded=True):
                st.write(f"**{p.get('companyName', ticker_input)}**")
                st.write(p.get("description", "Descripción no disponible."))
        else:
            st.error(f"No se encontraron datos para '{ticker_input}'.")
            st.info("💡 Asegúrate de escribir el ticker correctamente (ejemplo: MSFT para Microsoft).")
