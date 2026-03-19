import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

# --- ESTILO ---
st.markdown("""
<style>
.main { background-color: #0e1117; color: white; }
div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
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
        quote_res = requests.get(url_quote).json()
        overview = requests.get(url_overview).json()
        cash = requests.get(url_cash).json()

        # Detectar límite de API
        if "Note" in quote_res:
            return {"error": "⚠️ Límite de API alcanzado. Espera 60 segundos."}

        if "Global Quote" not in quote_res:
            return {"error": "❌ Ticker inválido o sin datos."}

        quote = quote_res.get("Global Quote", {})
        price_raw = quote.get("05. price")

        if not price_raw:
            return {"error": "⚠️ Precio no disponible."}

        return {
            "price": float(price_raw),
            "overview": overview,
            "cashflow": cash.get("annualReports", []),
            "name": overview.get("Name", symbol)
        }

    except Exception as e:
        return {"error": str(e)}

# --- UI ---
st.title("🐋 ORCA: Intrinsic Intelligence (API Mode)")

with st.sidebar:
    st.header("Control")
    ticker = st.text_input("Ticker", "AAPL").upper()
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100
    st.info("Plan gratuito: Máximo 5 consultas por minuto.")

# --- EJECUCIÓN ---
if ticker:
    with st.spinner(f"Calculando modelo ORCA para {ticker}..."):
        data = fetch_data(ticker)

        # --- ERROR HANDLING ---
        if data and "error" in data:
            st.error(data["error"])

        elif data:
            price = data["price"]

            if price == 0:
                st.error("❌ Precio inválido (0).")
            # --- DEBUG ---
            with st.expander("Debug"):
                st.write("ROE:", roe)
                st.write("Margin:", margin)

            with st.expander("Detalles del Negocio"):
                st.write(ov.get("Description", "No disponible."))

        else:
            st.error("❌ Error desconocido obteniendo datos.")
