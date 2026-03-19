import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stButton>button { background-color: #00d4ff; color: black; font-weight: bold; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

def scale(value, min_val, max_val):
    try:
        val = float(value)
        if val == 0 or np.isnan(val): return 0
        return max(0, min((val - min_val) / (max_val - min_val), 1)) * 100
    except: return 0

# --- MOTOR DE DATOS (1 SOLA LLAMADA) ---
def fetch_orca_data(symbol):
    # Usamos OVERVIEW porque contiene casi todo: Nombre, Descripción, Ratios y Precio estimado (52-week-high/low)
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    try:
        resp = requests.get(url).json()
        if "Note" in resp or "Information" in resp:
            return "LIMIT"
        if not resp or "Symbol" not in resp:
            return None
        return resp
    except:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")

with st.sidebar:
    st.header("Escáner de Mercado")
    ticker = st.text_input("Ticker", "AAPL").upper()
    btn = st.button("🚀 ANALIZAR AHORA")
    st.markdown("---")
    disc_rate = st.slider("Tasa Descuento (%)", 5, 25, 15) / 100

if btn:
    with st.spinner(f"Accediendo a terminal ORCA para {ticker}..."):
        data = fetch_orca_data(ticker)
        
        if data == "LIMIT":
            st.error("⏳ Bloqueo de API: Alpha Vantage detectó demasiadas peticiones. Por favor, espera 60 segundos exactos sin tocar la app.")
        elif data:
            # Extraer Ratios (Corrigiendo el error 36.67)
            # Alpha Vantage entrega strings, los convertimos a float con cuidado
            try:
                # Precio: Como OVERVIEW no trae el precio exacto actual, usamos el 'AnalystTargetPrice' 
                # o una media del rango de 52 semanas como referencia si GLOBAL_QUOTE falla.
                price = float(data.get("AnalystTargetPrice", 0)) * 0.9 # Estimación conservadora
                roe = float(data.get("ReturnOnEquityTTM", 0))
                margin = float(data.get("OperatingMarginTTM", 0))
                per = float(data.get("PERatio", 0))
                eps = float(data.get("EPS", 0))
                name = data.get("Name", ticker)
                desc = data.get("Description", "Descripción no disponible.")
                
                # Calidad (Quality Score dinámico)
                s_roe = scale(roe, 0, 0.3) * 0.4
                s_margin = scale(margin, 0, 0.3) * 0.4
                s_val = 20 if 0 < per < 25 else 10
                qs = round(s_roe + s_margin + s_val, 2)
                
                # Valor Intrínseco Simplificado (Modelo Benjamin Graham / ORCA)
                # Intrinsic = EPS * (8.5 + 2g) -> g es crecimiento esperado
                intrinsic = eps * (8.5 + 2 * 5) # 5% de crecimiento base
                
            except:
                st.warning("Algunos ratios financieros no están disponibles para este Ticker.")
                price, qs, intrinsic, name, desc = 0, 0, 0, ticker, "Datos incompletos."

            # --- VISUALIZACIÓN ---
            if price > 0:
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Est. (Target)", f"${price:.2f}")
                
                m_safety = 0.9 if qs > 75 else 0.75
                val_final = intrinsic * m_safety
                upside = ((val_final / price) - 1) * 100
                
                col2.metric("Valor ORCA", f"${val_final:.2f}", f"{upside:.2f}%")
                
                color = "#00ff88" if upside > 10 else "#ff4b4b" if upside < -10 else "#ffaa00"
                col3.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'>Señal: <b style='color:{color}; font-size:20px;'>{ 'BUY' if upside > 10 else 'SELL' if upside < -10 else 'HOLD' }</b></div>", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader(f"Dashboard de Calidad: {qs}/100")
                st.progress(qs/100)
                
                # Ratios Reales
                r1, r2, r3 = st.columns(3)
                r1.write(f"**ROE:** {roe*100:.2f}%")
                r2.write(f"**Margen:** {margin*100:.2f}%")
                r3.write(f"**P/E Ratio:** {per:.2f}")

                with st.expander("📖 Descripción de la Empresa", expanded=True):
                    st.write(f"**{name}**")
                    st.write(desc)
            else:
                st.error("No hay suficientes datos financieros para calcular el valor de este ticker.")
        else:
            st.error("No se encontró el Ticker o la API no respondió.")
