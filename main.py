import streamlit as st
import yfinance as yf

# --- FUNCIONES AUXILIARES ---

def classify_qs(qs):
    if qs is None:
        return "Unknown"
    elif qs >= 90:
        return "Gem 💎"
    elif qs >= 70:
        return "Core"
    elif qs >= 40:
        return "Standard"
    elif qs >= 30:
        return "Speculative"
    else:
        return "Avoid"

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ORCA Terminal 2.0", layout="wide", page_icon="🚢")
st.title("🚢 ORCA 2.0: Terminal de Ejecución e Inteligencia")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📥 Datos Validados (Sheets)")
    ticker_input = st.text_input("Introduce Ticker", value="ADBE").upper()
    
    st.subheader("Valuación de Sheets")
    val_dcf = st.number_input("Valor DCF (Sheets)", min_value=0.0, step=0.1)
    val_mr = st.number_input("Valor MR (Sheets)", min_value=0.0, step=0.1)
    qs_sheets = st.slider("Quality Score (QS)", 0, 100, 75)
    
    st.markdown("---")
    
    if st.button("🚀 Cargar Métricas de Mercado"):
        try:
            raw = yf.Ticker(ticker_input).info
            st.session_state['data'] = {
                'price': raw.get('currentPrice', 0.0),
                'shares': raw.get('sharesOutstanding', 0),
                'pe_ttm': raw.get('trailingPE', 0.0),
                'eps_ttm': raw.get('trailingEps', 0.0),
                'cr': raw.get('currentRatio', 0.0),
                'de': raw.get('debtToEquity', 0.0),
                'roe': raw.get('returnOnEquity', 0.0) * 100,
                'rev_g': raw.get('revenueGrowth', 0.0) * 100,
                'op_m': raw.get('operatingMargins', 0.0) * 100,
                'bb_y': raw.get('yield', 0.0) * 100,
                'eps_g': raw.get('earningsGrowth', 0.0) * 100
            }
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# --- PANEL CENTRAL ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Fundamentales: {ticker_input}")
    
    # Fila 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d.get('price', 0):.2f}")
    c2.metric("Shares (B)", f"{d.get('shares', 0) / 1e9:.3f}B")
    c3.metric("P/E TTM", f"{d.get('pe_ttm', 0):.2f}x")
    c4.metric("EPS TTM", f"${d.get('eps_ttm', 0):.2f}")

    # Fila 2
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d.get('cr', 0):.2f}")
    c6.metric("Debt to Equity", f"{d.get('de', 0):.2f}%")
    c7.metric("ROE", f"{d.get('roe', 0):.1f}%")
    c8.metric("Operating Margin", f"{d.get('op_m', 0):.1f}%")

    # Fila 3
    c9, c10, c11 = st.columns(3)
    c9.metric("Rev. Growth (YoY)", f"{d.get('rev_g', 0):.1f}%")
    c10.metric("EPS Growth", f"{d.get('eps_g', 0):.1f}%")
    c11.metric("Yield", f"{d.get('bb_y', 0):.2f}%")

    st.markdown("---")

    # --- ORCA INTELLIGENCE 2.0 ---
    roe_val = d.get('roe', 0) / 100
    margin_val = d.get('op_m', 0) / 100
    bb_yield = d.get('bb_y', 0) / 100
    cr_val = d.get('cr', 0)
    de_val = d.get('de', 0)
    eps_g_val = d.get('eps_g', 0) / 100
    rev_g_val = d.get('rev_g', 0) / 100

    alerts = []

    if roe_val > 0.25 and margin_val > 0.25 and de_val < 100:
        alerts.append("💎 Elite Compounder")

    if roe_val > 0.30 and margin_val > 0.20:
        alerts.append("🏭 Capital Efficiency Engine")

    if bb_yield > 0.04 and roe_val > 0.15:
        alerts.append("💰 Capital Return Machine")

    if eps_g_val > 0.15 and roe_val > 0.20:
        alerts.append("🚀 High Quality Growth")

    if margin_val > 0.30 and rev_g_val > 0.10:
        alerts.append("📈 Scalable Model")

    if eps_g_val > 0.20 and roe_val < 0.10:
        alerts.append("🔄 Turnaround Play")

    if eps_g_val > 0.15 and de_val > 150:
        alerts.append("🧪 Leveraged Growth")

    if margin_val < 0.10 and roe_val < 0.10

