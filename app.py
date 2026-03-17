import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ORCA System", page_icon="🐋", layout="wide")

# Estilo CSS para que se vea más profesional
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA (Tus Celdas) ---

def get_row(df, names):
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    if value is None: return None
    score = max(0, min((value - min_val) / (max_val - min_val), 1))
    return score * 100

@st.cache_data(ttl=3600) # Cache para no saturar Yahoo Finance
def calculate_orca_metrics(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    hist = stock.history(period="5y")
    financials = stock.financials
    cashflow = stock.cashflow
    
    # --- Lógica Celda 5 (FCF Growth) ---
    ocf_row = get_row(cashflow, ["Total Cash From Operating Activities", "Operating Cash Flow"])
    capex_row = get_row(cashflow, ["Capital Expenditures", "Capital Expenditure"])
    
    fcf_growth = 0.05 # Default
    if ocf_row is not None and capex_row is not None:
        fcf_hist = ocf_row + capex_row # Capex suele ser negativo en yf
        fcf_hist = fcf_hist.dropna()
        if len(fcf_hist) > 1:
            start, end = fcf_hist.iloc[-1], fcf_hist.iloc[0]
            if start > 0 and end > 0:
                fcf_growth = (end / start) ** (1 / (len(fcf_hist)-1)) - 1
    
    # --- Lógica Celda 11 (Quality Score) ---
    def get_qs():
        fs = np.mean([scale(3 - (info.get("debtToEquity", 100)/100), 0, 3), scale(info.get("currentRatio", 1), 0.5, 3)])
        pr = np.mean([scale(info.get("returnOnEquity", 0.1), 0, 0.3), scale(info.get("operatingMargins", 0.1), 0, 0.3)])
        gr = np.mean([scale(info.get("revenueGrowth", 0.05), -0.1, 0.3), scale(info.get("earningsGrowth", 0.05), -0.1, 0.3)])
        return round(np.nanmean([fs*0.4, pr*0.4, gr*0.2]) * 10, 2)

    qs = get_qs()
    
    # --- Lógica Celda 13 (Intrinsic Value) ---
    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    fcf_ttm = (ocf_row.iloc[0] + capex_row.iloc[0]) if ocf_row is not None else 0
    
    # DCF Simplificado (Celda 7)
    discount_rate = 0.15
    multiplier = 1 + max(0.0, min(fcf_growth, 0.10))
    pfcf = price / (fcf_ttm / shares) if fcf_ttm and shares else 15
    
    pv_fcfs = sum([fcf_ttm * (multiplier ** t) / ((1 + discount_rate) ** t) for t in range(1, 6)])
    terminal_v = (fcf_ttm * (multiplier ** 5) * pfcf) / ((1 + discount_rate) ** 5)
    intrinsic = (pv_fcfs + terminal_v) / shares
    
    # Ajuste por Margen de Seguridad (Celda 13)
    margin = 0.90 if qs > 80 else 0.70
    final_intrinsic = intrinsic * margin
    
    return {
        "price": price,
        "intrinsic": final_intrinsic,
        "qs": qs,
        "info": info,
        "history": hist
    }

# --- INTERFAZ DE LA APP ---

st.title("🐋 ORCA System: Terminal Financiera")

# Sidebar para búsqueda
with st.sidebar:
    st.header("Buscador")
    target = st.text_input("Ticker de la empresa", "AAPL").upper()
    st.info("Introduce un ticker de Yahoo Finance (ej: MSFT, TSLA, GOOGL)")

if target:
    try:
        with st.spinner(f"Ejecutando algoritmos ORCA para {target}..."):
            data = calculate_orca_metrics(target)
            
            # --- FILA 1: MÉTRICAS CLAVE ---
            col1, col2, col3 = st.columns(3)
            
            diff = ((data['intrinsic'] / data['price']) - 1) * 100
            
            col1.metric("Precio Actual", f"${data['price']:.2f}")
            col2.metric("Valor Intrínseco ORCA", f"${data['intrinsic']:.2f}", f"{diff:.2f}%")
            
            # Señal Visual
            if diff > 10:
                signal, color = "BUY", "green"
            elif diff < -10:
                signal, color = "SELL", "red"
            else:
                signal, color = "HOLD", "orange"
            
            col3.markdown(f"### Señal: <span style='color:{color}'>{signal}</span>", unsafe_allow_html=True)

            # --- FILA 2: QUALITY SCORE ---
            st.subheader(f"Calidad del Negocio (Quality Score: {data['qs']}/100)")
            st.progress(data['qs'] / 100)

            # --- FILA 3: GRÁFICO ---
            st.subheader("Evolución de Precio (5 años)")
            st.line_chart(data['history']['Close'])

            # --- FILA 4: DATOS ADICIONALES ---
            with st.expander("Ver detalles técnicos de la empresa"):
                st.write(data['info'].get('longBusinessSummary', 'No hay descripción disponible.'))

    except Exception as e:
        st.error(f"No pudimos encontrar datos para {target}. Verifica el ticker.")
