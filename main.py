import streamlit as st
import yfinance as yf

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="ORCA Terminal 2.0", layout="wide")

st.title("🚢 ORCA 2.0: Terminal de Fundamentales e Inteligencia")
st.markdown("---")

# --- BARRA LATERAL: INPUTS DE SHEETS (INTELIGENCIA) ---
with st.sidebar:
    st.header("📥 Datos Validados (Sheets)")
    ticker_input = st.text_input("Introduce Ticker", value="ADBE").upper()
    
    st.subheader("Valuación")
    val_dcf = st.number_input("Valor DCF de Sheets", min_value=0.0, step=0.1)
    val_mr = st.number_input("Valor MR de Sheets", min_value=0.0, step=0.1)
    qs_sheets = st.slider("Quality Score (QS)", 0, 100, 75)
    
    st.markdown("---")
    if st.button("🚀 Cargar Métricas de Mercado"):
        try:
            # Traemos la data cruda solo para visualización
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
                'bb_y': raw.get('yield', 0.0) * 100, # Aproximación inicial
                'eps_g': raw.get('earningsGrowth', 0.0) * 100
            }
        except Exception as e:
            st.error(f"Error al cargar: {e}")

# --- PANEL CENTRAL: VISUALIZACIÓN DE VARIABLES ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Métricas Clave: {ticker_input}")
    
    # Fila 1: Básicos
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d.get('price', 0):.2f}")
    c2.metric("Shares (B)", f"{d.get('shares', 0) / 1e9:.3f}B")
    c3.metric("P/E TTM", f"{d.get('pe_ttm', 0):.2f}x")
    c4.metric("EPS TTM", f"${d.get('eps_ttm', 0):.2f}")

    # Fila 2: Salud Financiera y Rentabilidad
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d.get('cr', 0):.2f}")
    c6.metric("Debt to Equity", f"{d.get('de', 0):.2f}%")
    c7.metric("ROE", f"{d.get('roe', 0):.1f}%")
    c8.metric("Op. Margins", f"{d.get('op_m', 0):.1f}%")

    # Fila 3: Crecimiento y Retorno
    c9, c10, c11 = st.columns(3)
    c9.metric("Rev. Growth (YoY)", f"{d.get('rev_g', 0):.1f}%")
    c10.metric("EPS Growth", f"{d.get('eps_g', 0):.1f}%")
    c11.metric("Buyback Yield", f"{d.get('bb_y', 0):.2f}%")

    st.markdown("---")

    # --- LÓGICA DE EJECUCIÓN (ORCA) ---
    st.subheader("🎯 Veredicto de Inteligencia")
    
    # Cálculo del Intrínseco Promedio de Sheets
    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    
    # Fórmula B: 0.5 + (QS/100 * 0.5)
    factor_orca = 0.5 + (qs_sheets / 100) * 0.5
    precio_compra = iv_base * factor_orca

    if iv_base > 0:
        res1, res2, res3 = st.columns(3)
        res1.metric("Intrínseco (Sheets)", f"${iv_base:.2f}")
        res2.metric("Factor de Seguridad (B)", f"{factor_orca:.3f}")
        res3.metric("Precio de Compra", f"${precio_compra:.2f}", 
                   delta=f"{((precio_compra/d.get('price', 1))-1)*100:.1f}% vs Mercado")

        # Alerta final
        if d.get('price', 0) <= precio_compra:
            st.success(f"💎 SEÑAL BUY: {ticker_input} está en zona de seguridad.")
        elif d.get('price', 0) <= iv_base:
            st.warning("⚖️ HOLD: Por debajo del intrínseco, pero falta margen de seguridad.")
        else:
            st.error("🚫 OVERVALUED: Precio de mercado por encima del valor real.")
else:
    st.info("Introduce un Ticker y pulsa 'Cargar Métricas' para ver los fundamentales.")


