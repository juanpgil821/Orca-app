import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal PRO", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stExpander { border: 1px solid #2e3344; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

def scale(value, min_val, max_val):
    try:
        val = float(value)
        if np.isnan(val): return 0
        score = max(0, min((val - min_val) / (max_val - min_val), 1))
        return score * 100
    except: return 0

def fetch_data(symbol):
    # Usamos funciones específicas de Alpha Vantage
    url_quote = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    url_cash = f'https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={API_KEY}'
    url_overview = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}'
    
    try:
        quote_res = requests.get(url_quote).json()
        overview_res = requests.get(url_overview).json()
        cash_res = requests.get(url_cash).json()
        
        # Validar si la API devolvió error de frecuencia
        if "Note" in overview_res or "Information" in overview_res:
            st.error("⏳ Límite de API alcanzado (5 por min). Espera 60 segundos.")
            return None

        return {
            "price": float(quote_res.get("Global Quote", {}).get("05. price", 0)),
            "overview": overview_res,
            "cashflow": cash_res.get("annualReports", []),
            "name": overview_res.get("Name", symbol)
        }
    except Exception as e:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence (API Mode)")

with st.sidebar:
    st.header("Control")
    ticker = st.text_input("Ticker", "AAPL").upper()
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100
    st.info("Plan gratuito: Máximo 5 consultas por minuto.")

if ticker:
    with st.spinner(f"Analizando {ticker}..."):
        data = fetch_data(ticker)
        
        if data and data['price'] > 0:
            price = data['price']
            ov = data['overview']
            cf = data['cashflow']
            
            # --- CORRECCIÓN ERROR 1: EXTRACCIÓN REAL DE RATIOS ---
            # Alpha Vantage usa strings. Si no existe, usamos None para no sesgar el 36.67
            def get_float(key):
                val = ov.get(key)
                if val is None or val == "None" or val == "-": return 0.0
                return float(val)

            roe = get_float("ReturnOnEquityTTM")
            margin = get_float("OperatingMarginTTM")
            per = get_float("PERatio")
            div_yield = get_float("DividendYield")

            # Cálculo de QS más dinámico
            s_roe = scale(roe, 0, 0.3) * 0.4
            s_margin = scale(margin, 0, 0.3) * 0.4
            s_extra = 20 if per > 0 and per < 30 else 10 # Bonus por valoración razonable
            
            qs = round(s_roe + s_margin + s_extra, 2)

            # --- LÓGICA VALOR INTRÍNSECO ---
            intrinsic = price * 1.10
            if cf:
                last_report = cf[0]
                # Los nombres en Alpha Vantage son camelCase dentro de los reportes
                ocf = float(last_report.get("operatingCashflow", 0))
                capex = abs(float(last_report.get("capitalExpenditures", 0)))
                fcf = ocf - capex
                shares = get_float("SharesOutstanding")
                
                if shares > 0:
                    growth = 1.07 
                    pv = sum([(fcf * (growth**t)) / ((1+disc_rate)**t) for t in range(1, 6)])
                    intrinsic = (pv + (fcf * 15)) / shares 

            # --- MOSTRAR RESULTADOS ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Precio Mercado", f"${price:.2f}")
            
            margin_safety = 0.9 if qs > 75 else 0.75
            final_val = intrinsic * margin_safety
            upside = ((final_val / price) - 1) * 100
            
            col2.metric("Valor ORCA (Adj)", f"${final_val:.2f}", f"{upside:.2f}%")
            
            if upside > 15: status, color = "COMPRA FUERTE", "#00ff88"
            elif upside > 0: status, color = "HOLD / COMPRA", "#00d4ff"
            else: status, color = "VENTA / SOBREVALORADA", "#ff4b4b"
            
            col3.markdown(f"<div style='border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;'>"
                         f"Señal: <br><b style='color:{color}; font-size:20px;'>{status}</b></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Dinamismo: Ratios reales en pantalla
            st.subheader(f"Dashboard de Calidad: {qs}/100")
            st.progress(qs / 100)
            
            r1, r2, r3, r4 = st.columns(4)
            r1.write(f"**ROE:** {roe*100:.2f}%")
            r2.write(f"**Márgen Op:** {margin*100:.2f}%")
            r3.write(f"**P/E Ratio:** {per:.2f}")
            r4.write(f"**Div. Yield:** {div_yield*100:.2f}%")

            # --- CORRECCIÓN ERROR 2: DESCRIPCIÓN ---
            st.markdown("---")
            with st.expander("📖 Detalles del Negocio", expanded=True):
                # Alpha Vantage usa "Description" con D mayúscula
                desc = ov.get("Description")
                if desc and desc != "None":
                    st.write(f"**{data['name']}**")
                    st.write(desc)
                    st.caption(f"Sector: {ov.get('Sector')} | Industria: {ov.get('Industry')}")
                else:
                    st.warning("⚠️ Descripción no disponible en el Overview de la API para este ticker.")
        else:
            st.error("No se pudieron obtener datos. Revisa el ticker o espera 1 minuto.")
