import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stButton>button { width: 100%; background-color: #00d4ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def scale(value, min_val, max_val):
    try:
        val = float(value)
        if np.isnan(val) or val == 0: return 0
        return max(0, min((val - min_val) / (max_val - min_val), 1)) * 100
    except: return 0

def fetch_orca_data(symbol):
    # Diccionario para guardar todo y evitar llamadas repetidas
    results = {}
    
    # 1. Función de utilidad para llamadas
    def get_json(func):
        url = f'https://www.alphavantage.co/query?function={func}&symbol={symbol}&apikey={API_KEY}'
        resp = requests.get(url).json()
        if "Note" in resp or "Information" in resp:
            return "LIMIT"
        return resp

    # Ejecutamos las 3 llamadas necesarias con un mini-delay para no saturar
    ov = get_json("OVERVIEW")
    if ov == "LIMIT": return "LIMIT"
    
    time.sleep(0.5) # Pausa técnica para que la API no se asuste
    quote = get_json("GLOBAL_QUOTE")
    if quote == "LIMIT": return "LIMIT"
    
    time.sleep(0.5)
    cash = get_json("CASH_FLOW")
    if cash == "LIMIT": return "LIMIT"

    return {
        "price": float(quote.get("Global Quote", {}).get("05. price", 0)),
        "ov": ov,
        "cf": cash.get("annualReports", []),
        "name": ov.get("Name", symbol)
    }

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")

with st.sidebar:
    st.header("Control de Escaneo")
    ticker = st.text_input("Ticker (ej: MSFT)", "AAPL").upper()
    btn_analizar = st.button("🚀 EJECUTAR ANÁLISIS")
    st.markdown("---")
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100
    st.caption("Plan gratuito: Máximo 5 consultas por minuto. El botón evita el auto-refresco excesivo.")

# Solo se ejecuta si el usuario presiona el botón
if btn_analizar:
    with st.spinner(f"Consultando servidores para {ticker}..."):
        data = fetch_orca_data(ticker)
        
        if data == "LIMIT":
            st.warning("⚠️ Límite de API excedido. Alpha Vantage pide que esperes 60 segundos exactos antes de otra consulta.")
        elif data and data['price'] > 0:
            ov, price, cf = data['ov'], data['price'], data['cf']
            
            # --- CÁLCULO QUALITY SCORE ---
            def safe_f(k):
                v = ov.get(k)
                return float(v) if v and v != "None" else 0.0

            roe, margin, per = safe_f("ReturnOnEquityTTM"), safe_f("OperatingMarginTTM"), safe_f("PERatio")
            
            qs = round((scale(roe, 0, 0.3)*0.4 + scale(margin, 0, 0.3)*0.4 + (20 if 0 < per < 30 else 10)), 2)

            # --- VALOR INTRÍNSECO ---
            intrinsic = price * 1.10
            if cf:
                last = cf[0]
                fcf = float(last.get("operatingCashflow", 0)) - abs(float(last.get("capitalExpenditures", 0)))
                shares = safe_f("SharesOutstanding")
                if shares > 0:
                    pv = sum([(fcf * (1.07**t)) / ((1+disc_rate)**t) for t in range(1, 6)])
                    intrinsic = (pv + (fcf * 15)) / shares

            # --- RESULTADOS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Precio", f"${price:.2f}")
            
            m_safety = 0.9 if qs > 75 else 0.75
            val_final = intrinsic * m_safety
            upside = ((val_final / price) - 1) * 100
            
            c2.metric("Valor ORCA", f"${val_final:.2f}", f"{upside:.2f}%")
            
            color = "#00ff88" if upside > 10 else "#ff4b4b" if upside < -10 else "#ffaa00"
            c3.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'>Señal: <b style='color:{color};'>{ 'BUY' if upside > 10 else 'SELL' if upside < -10 else 'HOLD' }</b></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader(f"Dashboard de Calidad: {qs}/100")
            st.progress(qs/100)
            
            # Ratios visibles para confirmar que NO son 0.1
            r1, r2, r3 = st.columns(3)
            r1.write(f"**ROE:** {roe*100:.2f}%")
            r2.write(f"**Márgen:** {margin*100:.2f}%")
            r3.write(f"**P/E:** {per:.2f}")

            with st.expander("📖 Detalles del Negocio", expanded=True):
                st.write(ov.get("Description", "Sin descripción."))
        else:
            st.error("Ticker no encontrado o error de conexión.")
