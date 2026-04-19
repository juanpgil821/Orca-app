import streamlit as st
import yfinance as yf

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="ORCA Terminal 2.0", layout="wide", page_icon="🚢")

st.title("🚢 ORCA 2.0: Terminal de Ejecución e Inteligencia")
st.markdown("---")

# --- BARRA LATERAL: INPUTS DE SHEETS (INTELIGENCIA) ---
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
                'bb_y': raw.get('yield', 0.0) * 100, # Proxy de yield
                'eps_g': raw.get('earningsGrowth', 0.0) * 100
            }
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# --- PANEL CENTRAL: VISUALIZACIÓN DE VARIABLES ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Fundamentales: {ticker_input}")
    
    # Fila 1: Datos de Mercado y EPS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d.get('price', 0):.2f}")
    c2.metric("Shares (B)", f"{d.get('shares', 0) / 1e9:.3f}B")
    c3.metric("P/E TTM", f"{d.get('pe_ttm', 0):.2f}x")
    c4.metric("EPS TTM", f"${d.get('eps_ttm', 0):.2f}")

    # Fila 2: Salud y Rentabilidad
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d.get('cr', 0):.2f}")
    c6.metric("Debt to Equity", f"{d.get('de', 0):.2f}%")
    c7.metric("ROE", f"{d.get('roe', 0):.1f}%")
    c8.metric("Operating Margin", f"{d.get('op_m', 0):.1f}%")

    # Fila 3: Crecimiento y Yield
    c9, c10, c11 = st.columns(3)
    c9.metric("Rev. Growth (YoY)", f"{d.get('rev_g', 0):.1f}%")
    c10.metric("EPS Growth (Forecast)", f"{d.get('eps_g', 0):.1f}%")
    c11.metric("Buyback/Div Yield", f"{d.get('bb_y', 0):.2f}%")

    # --- ORCA INTELLIGENCE: Risk & Quality Diagnosis ---
    st.markdown("---")
    
    # Variables normalizadas para el diagnóstico
    roe_val = d.get('roe', 0) / 100
    margin_val = d.get('op_m', 0) / 100
    bb_yield = d.get('bb_y', 0) / 100
    cr_val = d.get('cr', 0)
    de_val = d.get('de', 0)
    eps_g_val = d.get('eps_g', 0) / 100

    alerts = []
    
    # 1. Joyas (Wide Moat)
    if margin_val > 0.30 and roe_val > 0.30:
        alerts.append("💎 **Wide Moat Gem:** Márgenes y ROE de élite. Alta eficiencia operativa.")
    
    # 2. Retorno al Accionista
    if bb_yield > 0.05:
        alerts.append(f"🐂 **Shareholder Yield Alpha:** Recompra o dividendos masivos ({bb_yield:.1%}).")
    
    # 3. Zombie Alert
    if margin_val <= 0 and roe_val <= 0:
        alerts.append("💀 **Zombie Company Alert:** Negocio inviable sin flujo ni márgenes positivos.")
    
    # 4. Destrucción de Capital
    if roe_val < 0:
        alerts.append(f"🚨 **Capital Destroyer:** ROE negativo ({roe_val:.1%}). Quema de valor constante.")
    
    # 5. Apalancamiento Inflado
    if roe_val > 0.50 and de_val > 250:
        alerts.append(f"🧪 **Leveraged ROE:** Rentabilidad inflada por deuda extrema ({de_val:.0f}% D/E).")
    
    # 6. Liquidez y Capital de Trabajo
    if cr_val < 0.9:
        mkt_cap = d.get('price', 0) * d.get('shares', 0)
        if mkt_cap > 50_000_000_000: 
            alerts.append(f"🔄 **Working Capital King:** CR bajo ({cr_val}) gestionado por escala masiva.")
        else:
            alerts.append(f"📉 **Liquidity Trap:** Riesgo de insolvencia técnica. CR muy bajo ({cr_val}).")
            
    # 7. Crecimiento Explosivo
    if eps_g_val > 0.20:
        alerts.append(f"🚀 **Hypergrowth Engine:** Expectativas de crecimiento de EPS > 20%.")

    if alerts:
        with st.expander("🔍 ORCA Intelligence: Risk & Quality Diagnosis", expanded=True):
            for a in alerts:
                if any(icon in a for icon in ["💎", "✨", "🐂", "🔄", "🚀"]): st.info(a)
                elif any(icon in a for icon in ["⚠️", "🧪", "🌫️"]): st.warning(a)
                else: st.error(a)

    st.markdown("---")

    # --- LÓGICA DE VALORACIÓN (ORCA 2.0) ---
    st.subheader("🎯 Veredicto de Inversión")
    
    # Intrínseco promedio de tus modelos validados
    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    
    # Fórmula B: Factor de Confianza Equilibrado
    factor_orca = 0.5 + (qs_sheets / 100) * 0.5
    precio_compra = iv_base * factor_orca

    if iv_base > 0:
        res1, res2, res3 = st.columns(3)
        res1.metric("Intrínseco Promedio", f"${iv_base:.2f}")
        res2.metric("Factor ORCA (B)", f"{factor_orca:.3f}")
        res3.metric("Precio de Compra", f"${precio_compra:.2f}", 
                   delta=f"{((precio_compra/d.get('price', 1))-1)*100:.1f}% vs Mercado")

        # Señal Final
        if d.get('price', 0) <= precio_compra:
            st.success(f"✅ SEÑAL BUY: {ticker_input} está en zona de seguridad absoluta.")
        elif d.get('price', 0) <= iv_base:
            st.warning("⚖️ ZONA HOLD: Por debajo del intrínseco, pero falta margen por calidad.")
        else:
            st.error("🚫 OVERVALUED: Precio actual ignora el margen de seguridad.")
    else:
        st.info("Introduce los valores de DCF y MR desde Sheets para ver el veredicto.")

else:
    st.info("Introduce un Ticker en el sidebar y pulsa 'Cargar Métricas' para iniciar el análisis.")


