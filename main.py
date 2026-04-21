import streamlit as st
import yfinance as yf
import database as db  # <--- IMPORTACIÓN DE TU BASE DE DATOS

# --- FUNCIONES AUXILIARES ---

def classify_qs(qs):
    if qs is None:
        return "Unknown"
    elif qs >= 75:
        return "Gem 💎"
    elif qs >= 60:
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
    
    # --- LÓGICA DE INTERCEPTACIÓN DATABASE.PY ---
    hc = db.get_ticker_data(ticker_input)
    if hc:
        st.success(f"🎯 Datos cargados de HTM-30: {hc['name']}")
        # Definimos los valores por defecto basados en la base de datos
        def_dcf = hc['dcf_val']
        def_mr = hc['mr_val']
        def_qs = hc['quality_score']
        def_eps_g = hc['eps_growth']
        def_bb_y = hc['buyback_yield']
        def_fcf_y = hc['fcf_yield']
    else:
        # Valores por defecto estándar si no está en la base de datos
        def_dcf = 0.0
        def_mr = 0.0
        def_qs = 75
        def_eps_g = 0.0
        def_bb_y = 0.0
        def_fcf_y = 0.0

    st.subheader("Valuación de Sheets")
    val_dcf = st.number_input("Valor DCF (Sheets)", min_value=0.0, step=0.1, value=def_dcf)
    val_mr = st.number_input("Valor MR (Sheets)", min_value=0.0, step=0.1, value=def_mr)
    qs_sheets = st.slider("Quality Score (QS)", 0, 100, def_qs)
    
    st.subheader("Métricas Manuales (Input)")
    m_eps_g = st.number_input("EPS Growth TTM (%)", value=def_eps_g)
    m_bb_y = st.number_input("Buyback Yield (%)", value=def_bb_y)
    m_fcf_y = st.number_input("FCF Yield (%)", value=def_fcf_y)
    
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
                'roe': (raw.get('returnOnEquity', 0.0) or 0.0) * 100,
                'rev_g': (raw.get('revenueGrowth', 0.0) or 0.0) * 100,
                'op_m': (raw.get('operatingMargins', 0.0) or 0.0) * 100,
                'div_y': (raw.get('dividendYield', 0.0) or 0.0) * 100
            }
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# --- PANEL CENTRAL ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Panel de Control: {ticker_input}")
    
    # FILA 1: MERCADO
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d.get('price', 0):.2f}")
    c2.metric("Shares (B)", f"{d.get('shares', 0) / 1e9:.3f}B")
    c3.metric("P/E TTM", f"{d.get('pe_ttm', 0):.2f}x")
    c4.metric("EPS TTM", f"${d.get('eps_ttm', 0):.2f}")

    # FILA 2: CALIDAD (API)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d.get('cr', 0):.2f}")
    c6.metric("Debt/Equity", f"{d.get('de', 0):.2f}%")
    c7.metric("ROE", f"{d.get('roe', 0):.1f}%")
    c8.metric("Operating Margin", f"{d.get('op_m', 0):.1f}%")

    # FILA 3: FUTURO (HÍBRIDO API + MANUAL)
    c9, c10, c11, c12 = st.columns(4)
    c9.metric("Rev. Growth", f"{d.get('rev_g', 0):.1f}%")
    c10.metric("EPS Growth (M)", f"{m_eps_g:.1f}%")
    c11.metric("Buyback Yield (M)", f"{m_bb_y:.1f}%")
    c12.metric("FCF Yield (M)", f"{m_fcf_y:.1f}%")

    st.markdown("---")

    # --- ORCA INTELLIGENCE (LÓGICA AJUSTADA) ---
    # Usamos porcentajes reales (ej. 25.0 en lugar de 0.25) para las comparaciones
    roe = d.get('roe', 0)
    margin = d.get('op_m', 0)
    rev_g = d.get('rev_g', 0)
    de = d.get('de', 0)
    cr = d.get('cr', 0)
    div_y = d.get('div_y', 0) # API ya viene x100
    
    eps_g = m_eps_g
    bb_y = m_bb_y
    fcf_y = m_fcf_y
    total_yield = bb_y + div_y

    alerts = []

    # 🟢 SEÑALES DE FORTALEZA
    if roe > 25 and margin > 25 and de < 100:
        alerts.append("🟢 **Elite Compounder:** Rentabilidad y márgenes elevados con baja deuda. Negocio capaz de reinvertir a altas tasas.")

    if roe > 30 and margin > 20:
        alerts.append("🟢 **Capital Efficiency Engine:** Management altamente eficiente en el uso del capital de los accionistas.")

    if eps_g > 15 and roe > 20:
        alerts.append("🟢 **High Quality Growth:** Crecimiento fuerte de beneficios respaldado por una rentabilidad real.")

    if margin > 30 and rev_g > 10:
        alerts.append("🟢 **Scalable Model:** El negocio crece con fuerza manteniendo márgenes de élite. Fuerte pricing power.")

    if fcf_y > 7 and margin > 20:
        alerts.append("🟢 **Cash Flow Machine:** Generación masiva de caja operativa. Capacidad total de autofinanciación.")

    if total_yield > 6:
        alerts.append("🟢 **Shareholder Yield Alpha:** Alta retribución al accionista mediante dividendos y recompras.")

    if de < 50 and cr > 1.5:
        alerts.append("🟢 **Financially Strong:** Balance blindado. Baja deuda y alta liquidez inmediata.")

    if fcf_y > (100/d.get('pe_ttm', 1) if d.get('pe_ttm', 0) > 0 else 0):
        alerts.append("🟢 **Cash King:** La generación de caja real supera al beneficio contable reportado.")

    # 🟡 SEÑALES DE ADVERTENCIA
    if roe > 25 and de > 150:
        alerts.append("🟡 **Leveraged Quality:** Rentabilidad alta pero impulsada por un endeudamiento agresivo.")

    if rev_g > 15 and margin < 10:
        alerts.append("🟡 **Growth Without Profit:** Crecimiento rápido en ventas pero con incapacidad de retener beneficios.")

    if margin > 20 and rev_g < 5:
        alerts.append("🟡 **Mature Cash Cow:** Negocio muy rentable pero estancado en su capacidad de expansión.")

    if cr < 0.9 and (d.get('price', 0) * d.get('shares', 0)) > 20e9:
        alerts.append("🟡 **Working Capital King:** Liquidez baja típica de gigantes operativos eficientes (modelo Amazon/Walmart).")

    if eps_g > 20 and roe < 10:
        alerts.append("🟡 **Turnaround Play:** Fuerte crecimiento de beneficios pero la rentabilidad sobre el capital aún es débil.")

    if eps_g > 15 and fcf_y < 2:
        alerts.append("🟡 **Earnings Quality Warning:** Los beneficios crecen en papel, pero el dinero real (FCF) no está entrando.")

    # 🔴 SEÑALES DE RIESGO
    if rev_g < 5 and roe < 10:
        alerts.append("🔴 **Classic Value Trap:** Parece barato por múltiplos pero el negocio no tiene momentum ni rentabilidad.")

    if de > 200 and roe < 15:
        alerts.append("🔴 **Debt Overhang:** La carga de deuda es excesiva para el retorno que genera la operación.")

    if cr < 0.8 and (d.get('price', 0) * d.get('shares', 0)) < 20e9:
        alerts.append("🔴 **Liquidity Stress:** Riesgo de insolvencia a corto plazo. No cubre sus obligaciones corrientes.")

    if roe < 0:
        alerts.append("🔴 **Capital Destroyer:** La empresa está quemando el capital de los accionistas. ROE negativo.")

    # AJUSTE ESCALA: total_yield > 5.0 (5%) y fcf_y < 3.0 (3%)
    if total_yield > 5 and fcf_y < 3:
        alerts.append("🔴 **Yield Trap Risk:** El dividendo o las recompras son insostenibles; se pagan con deuda o caja finita.")

    if rev_g < 0 and margin < 0 and roe < 0:
        alerts.append("🔴 **Zombie Mode:** Empresa en muerte cerebral: sin crecimiento, sin márgenes y sin rentabilidad.")

    # RENDER DE ALERTAS
    if alerts:
        with st.expander("🔍 ORCA Intelligence: Diagnóstico del Analista Senior", expanded=True):
            for a in alerts:
                if "🟢" in a: st.info(a)
                elif "🟡" in a: st.warning(a)
                else: st.error(a)

    st.markdown("---")

    # --- VALUACIÓN ---
    st.subheader("🎯 Veredicto de Inversión")

    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    factor_orca = (100-max(5, (75 - qs_sheets) * 0.4 + 5))/100
    precio_compra = iv_base * factor_orca

    qs_category = classify_qs(qs_sheets)

    if iv_base > 0:
        res1, res2, res3 = st.columns(3)
        res1.metric("Intrínseco Promedio", f"${iv_base:.2f}")
        res2.metric("Factor ORCA", f"{factor_orca:.3f}")
        res3.metric("Precio de Compra", f"${precio_compra:.2f}",
                    delta=f"{((precio_compra/d.get('price', 1))-1)*100:.1f}% vs Mercado")

        price = d.get('price', 0)

        if qs_sheets < 30:
            st.error(f"⛔ REJECTED ({qs_category})")
        else:
            if price <= precio_compra:
                st.success(f"✅ BUY ({qs_category})")
            elif price <= iv_base:
                st.warning(f"⚖️ HOLD ({qs_category})")
            else:
                st.error(f"🚫 OVERVALUED ({qs_category})")
    else:
        st.info("Introduce DCF y MR desde Sheets.")
else:
    st.info("Introduce un Ticker y carga métricas.")


