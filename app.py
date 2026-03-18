import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ORCA Terminal", page_icon="🐋", layout="wide")

# Diseño visual (Modo Oscuro Profesional)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    .stProgress .st-bo { background-color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SOPORTE (Tus Celdas) ---
def get_row(df, names):
    if df is None or df.empty: return None
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    if value is None or np.isnan(value): return 0
    score = max(0, min((value - min_val) / (max_val - min_val), 1))
    return score * 100

@st.cache_data(ttl=3600)
def fetch_orca_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Intentamos obtener info básica primero
        info = ticker.info
        
        # FIX: Si 'info' falla o viene vacío (bloqueo común en la nube)
        if not info or 'currentPrice' not in info:
            hist_recent = ticker.history(period="5d")
            if hist_recent.empty: return None
            price = hist_recent['Close'].iloc[-1]
            name = symbol
        else:
            price = info.get("currentPrice")
            name = info.get("shortName", symbol)

        # Extraer Financieros para FCF y Quality Score
        financials = ticker.financials
        cashflow = ticker.cashflow
        hist_5y = ticker.history(period="5y")

        # --- LÓGICA CALIDAD (Celda 11) ---
        def calculate_qs():
            roe = info.get("returnOnEquity", 0.1)
            margin = info.get("operatingMargins", 0.1)
            debt = info.get("debtToEquity", 100) / 100
            
            s1 = scale(roe, 0, 0.3) * 0.4
            s2 = scale(margin, 0, 0.3) * 0.4
            s3 = scale(3 - debt, 0, 3) * 0.2
            return round(s1 + s2 + s3, 2)

        qs = calculate_qs()

        # --- LÓGICA VALOR INTRÍNSECO (Celda 5, 7 y 13) ---
        shares = info.get("sharesOutstanding")
        if not shares:
            # Si no hay shares en info, no podemos calcular por acción
            return {"name": name, "price": price, "qs": qs, "error": "No shares data"}

        # FCF Simplificado para la App
        ocf = get_row(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
        capex = get_row(cashflow, ["Capital Expenditure", "Capital Expenditures"])
        
        if ocf is not None and capex is not None:
            fcf_ttm = ocf.iloc[0] + capex.iloc[0]
            # Modelo DCF rápido (Celda 7)
            growth = 1.05 # 5% conservador
            discount = 0.15
            pv = sum([(fcf_ttm * (growth**t)) / ((1+discount)**t) for t in range(1, 6)])
            intrinsic = (pv + (fcf_ttm * 15)) / shares # Terminal value simplificado
        else:
            intrinsic = price * 0.8 # Fallback si no hay cashflow

        return {
            "name": name,
            "price": price,
            "intrinsic": intrinsic,
            "qs": qs,
            "history": hist_5y,
            "info": info
        }
    except:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")

with st.sidebar:
    st.header("Terminal de Control")
    ticker_input = st.text_input("Ticker (ej: AAPL, V, MSFT)", "AAPL").upper()
    st.markdown("---")
    st.write("Configuración DCF:")
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15)

if ticker_input:
    data = fetch_orca_data(ticker_input)
    
    if data:
        # Fila 1: Métricas
        col1, col2, col3 = st.columns(3)
        col1.metric("Precio Actual", f"${data['price']:.2f}")
        
        # Lógica de Margen de Seguridad según Quality Score (Celda 13)
        margin = 0.9 if data['qs'] > 80 else 0.7
        val_final = data['intrinsic'] * margin
        upside = ((val_final / data['price']) - 1) * 100
        
        col2.metric("Valor Intrínseco (Adj)", f"${val_final:.2f}", f"{upside:.2f}%")
        
        if upside > 10:
            status, color = "COMPRA (BUY)", "#00ff88"
        elif upside < -10:
            status, color = "VENTA (SELL)", "#ff4b4b"
        else:
            status, color = "MANTENER (HOLD)", "#ffaa00"
            
        col3.markdown(f"<h3 style='text-align:center;'>Señal:<br><span style='color:{color}'>{status}</span></h3>", unsafe_allow_html=True)

        # Fila 2: Quality Score
        st.write(f"**Calidad del Negocio (ORCA Quality Score): {data['qs']}/100**")
        st.progress(data['qs'] / 100)

        # Fila 3: Gráfico
        st.subheader("Histórico de Precios")
        st.area_chart(data['history']['Close'])
        
        with st.expander("Ver Análisis Detallado"):
            st.write(f"Empresa: {data['name']}")
            st.write(data['info'].get('longBusinessSummary', 'Sin descripción.'))
    else:
        st.error(f"Error: Yahoo Finance no responde para {ticker_input}. Intenta con otro ticker o reinicia la app.")
