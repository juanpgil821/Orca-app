import streamlit as st
import requests
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Intelligence", page_icon="🐋", layout="wide")
API_KEY = "NGT4JK1SBUWM3G0D"

# Estilo visual avanzado
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { border: 1px solid #2e3344; padding: 10px; border-radius: 10px; background-color: #161b22; }
    div[data-testid="stMetricValue"] { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

def fetch_all_data(symbol):
    # Función para llamar a la API con manejo de errores
    def call_api(function):
        url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={API_KEY}'
        response = requests.get(url).json()
        return response

    try:
        overview = call_api("OVERVIEW")
        if not overview or "Symbol" not in overview:
            return None
            
        quote = call_api("GLOBAL_QUOTE").get("Global Quote", {})
        cash = call_api("CASH_FLOW").get("annualReports", [])
        
        return {
            "price": float(quote.get("05. price", 0)) if quote else 0,
            "ov": overview,
            "cf": cash,
            "name": overview.get("Name", symbol)
        }
    except:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA Terminal | Análisis de Valor")

with st.sidebar:
    st.header("Configuración")
    ticker = st.text_input("Ticker", "AAPL").upper()
    st.markdown("---")
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15) / 100
    st.info("Nota: Alpha Vantage permite 5 consultas por minuto. Si ves error, espera un poco.")

if ticker:
    with st.spinner(f"Analizando {ticker}..."):
        data = fetch_all_data(ticker)
        
        if data and data['price'] > 0:
            ov = data['ov']
            price = data['price']
            
            # --- SOLUCIÓN ERROR 1: QUALITY SCORE DINÁMICO ---
            # Extraemos datos reales o usamos 0 si no existen
            roe = float(ov.get("ReturnOnEquityTTM", 0))
            margin = float(ov.get("OperatingMarginTTM", 0))
            div_yield = float(ov.get("DividendYield", 0))
            per = float(ov.get("PERatio", 0))
            
            # Cálculo de Score (Escalado real)
            s_roe = min(roe / 0.30, 1) * 40 # 40 pts max si ROE > 30%
            s_mar = min(margin / 0.30, 1) * 40 # 40 pts max si Margen > 30%
            s_per = 20 if 0 < per < 25 else 10 # 20 pts si el PER es razonable
            
            qs = round(s_roe + s_mar + s_per, 2)

            # --- CÁLCULO VALOR INTRÍNSECO (Fórmula ORCA) ---
            shares = float(ov.get("SharesOutstanding", 1))
            intrinsic = price # Fallback
            
            if data['cf']:
                last_fcf = float(data['cf'][0].get("operatingCashflow", 0)) - abs(float(data['cf'][0].get("capitalExpenditures", 0)))
                # DCF proyectado
                proyectado = sum([(last_fcf * (1.05**t)) / ((1 + disc_rate)**t) for t in range(1, 6)])
                intrinsic = (proyectado + (last_fcf * 15)) / shares

            # --- VISUALIZACIÓN ---
            col1, col2, col3 = st.columns(3)
            
            margin_safety = 0.9 if qs > 80 else 0.75
            val_adj = intrinsic * margin_safety
            upside = ((val_adj / price) - 1) * 100
            
            col1.metric("Precio Actual", f"${price:,.2f}")
            col2.metric("Valor ORCA (Adj)", f"${val_adj:,.2f}", f"{upside:.2f}%")
            
            if upside > 15: sig, col = "COMPRA FUERTE", "#00ff88"
            elif upside > 0: sig, col = "COMPRA / HOLD", "#00d4ff"
            else: sig, col = "SOBREVALORADA", "#ff4b4b"
            
            col3.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; border:2px solid {col};'>"
                         f"Señal:<br><span style='color:{col}; font-size:20px; font-weight:bold;'>{sig}</span></div>", 
                         unsafe_allow_html=True)

            # Dashboard de Calidad
            st.markdown("---")
            c_a, c_b = st.columns([1, 2])
            with c_a:
                st.subheader("Calidad del Negocio")
                st.metric("Quality Score", f"{qs}/100")
                st.progress(qs / 100)
            
            with c_b:
                st.subheader("Ratios Clave")
                r1, r2, r3 = st.columns(3)
                r1.write(f"**ROE:** {roe*100:.2f}%")
                r2.write(f"**Márgen Op:** {margin*100:.2f}%")
                r3.write(f"**P/E Ratio:** {per:.2f}")

            # --- SOLUCIÓN ERROR 2: DETALLES DEL NEGOCIO ---
            st.markdown("---")
            with st.expander("📖 Descripción Detallada de la Empresa", expanded=True):
                desc = ov.get("Description", "No hay descripción disponible para este ticker en Alpha Vantage.")
                st.write(f"**{data['name']}**")
                st.write(desc)
                st.caption(f"Sector: {ov.get('Sector')} | Industria: {ov.get('Industry')}")

        else:
            st.warning("⚠️ Sin datos. Posibles causas: 1. Límite de 5 consultas/min alcanzado. 2. Ticker incorrecto. 3. Alpha Vantage no tiene este ticker.")
