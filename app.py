import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

# Estilo visual oscuro
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def scale(value, min_val, max_val):
    if value is None or np.isnan(value):
        return 0
    score = max(0, min((value - min_val) / (max_val - min_val), 1))
    return score * 100

def safe_float(value, default=0):
    try:
        if value in [None, "", "None"]:
            return default
        return float(value)
    except:
        return default

def fetch_data(symbol):
    url_quote = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    url_cash = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={API_KEY}'
    url_overview = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    
    try:
        quote = requests.get(url_quote).json().get("Global Quote", {})
        overview = requests.get(url_overview).json()
        cash = requests.get(url_cash).json()
        
            price_raw = quote.get("05. price")

if not price_raw:
    return None

return {
    "price": float(price_raw),
            "overview": overview,
            "cashflow": cash.get("annualReports", []),
            "name": overview.get("Name", symbol)
        }
    except:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence (API Mode)")

with st.sidebar:
    st.header("Control")
    ticker = st.text_input("Ticker", "AAPL").upper()
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100
    st.info("Plan gratuito: Máximo 5 consultas por minuto.")

if ticker:
    with st.spinner(f"Calculando modelo ORCA para {ticker}..."):
        data = fetch_data(ticker)
        
        if data:
            price = data['price']
            ov = data['overview']
            cf = data['cashflow']
            
            # --- QUALITY SCORE (FIXED) ---
            roe = safe_float(ov.get("ReturnOnEquityTTM") or ov.get("ReturnOnEquity"))
            margin = safe_float(ov.get("OperatingMarginTTM") or ov.get("OperatingMargin"))
            
            qs = round(
                (scale(roe, 0, 0.3) * 0.4 +
                 scale(margin, 0, 0.3) * 0.4 +
                 50 * 0.2),
                2
            )

            # --- VALOR INTRÍNSECO ---
            intrinsic = price * 1.10 # fallback
            
            if cf:
                last_report = cf[0]
                ocf = safe_float(last_report.get("operatingCashflow"))
                capex = abs(safe_float(last_report.get("capitalExpenditures")))
                fcf = ocf - capex
                shares = safe_float(ov.get("SharesOutstanding"), 1)
                
                if shares > 1:
                    growth = 1.07
                    pv = sum([
                        (fcf * (growth ** t)) / ((1 + disc_rate) ** t)
                        for t in range(1, 6)
                    ])
                    intrinsic = (pv + (fcf * 15)) / shares

            # --- RESULTADOS ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Precio Mercado", f"${price:.2f}")
            
            margin_safety = 0.9 if qs > 75 else 0.75
            final_val = intrinsic * margin_safety
            upside = ((final_val / price) - 1) * 100
            
            col2.metric("Valor ORCA (Adj)", f"${final_val:.2f}", f"{upside:.2f}%")
            
            if upside > 10:
                status, color = "COMPRA", "#00ff88"
            elif upside < -10:
                status, color = "VENTA", "#ff4b4b"
            else:
                status, color = "HOLD", "#ffaa00"
            
            col3.markdown(
                f"<h3 style='text-align:center;'>Señal:<br><span style='color:{color}'>{status}</span></h3>",
                unsafe_allow_html=True
            )
            
            st.write(f"**ORCA Quality Score: {qs}/100**")
            st.progress(qs / 100)
            
            # DEBUG opcional (puedes borrarlo luego)
            with st.expander("Debug (Quality Score inputs)"):
                st.write("ROE:", roe)
                st.write("Margin:", margin)
            
            with st.expander("Detalles del Negocio"):
                st.write(ov.get("Description", "No disponible."))
        else:
            st.error("No se pudieron obtener datos. Revisa el ticker o espera 1 minuto (límite de API).")
