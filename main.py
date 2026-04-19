import streamlit as st
import yfinance as yf

# --- FUNCIONES AUXILIARES ---
def classify_qs(qs):
    if qs is None: return "Unknown"
    elif qs >= 90: return "Gem 💎"
    elif qs >= 70: return "Core"
    elif qs >= 40: return "Standard"
    elif qs >= 30: return "Speculative"
    else: return "Avoid"

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ORCA Terminal 2.0", layout="wide", page_icon="🚢")
st.title("🚢 ORCA 2.0: Terminal de Ejecución e Inteligencia")
st.markdown("---")

# --- SIDEBAR: DATOS VALIDADOS Y MANUALES ---
with st.sidebar:
    st.header("📥 Datos Validados (Sheets)")
    ticker_input = st.text_input("Introduce Ticker", value="ADBE").upper()
    
    st.subheader("Valuación")
    val_dcf = st.number_input("Valor DCF", min_value=0.0, step=0.1)
    val_mr = st.number_input("Valor MR", min_value=0.0, step=0.1)
    qs_sheets = st.slider("Quality Score (QS)", 0, 100, 75)
    
    st.subheader("Métricas Manuales (Verificadas)")
    m_eps_g = st.number_input("EPS Growth TTM (%)", value=0.0, help="Crecimiento de beneficios del último año")
    m_bb_y = st.number_input("Buyback Yield (%)", value=0.0, help="Rendimiento por recompra de acciones")
    m_fcf_y = st.number_input("FCF Yield (%)", value=0.0, help="Flujo de caja libre / Market Cap")
    
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
                'op_m': (raw.get('operatingMargins', 0.0) or 0.0) * 100,
                'rev_g': (raw.get('revenueGrowth', 0.0) or 0.0) * 100,
                'div_y': (raw.get('dividendYield', 0.0) or 0.0) * 100
            }
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# --- PANEL CENTRAL: LAS 12 VARIABLES (3x4) ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Panel de Control: {ticker_input}")
    
    # Fila 1: Mercado
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d['price']:.2f}")
    c2.metric("Shares (B)", f"{d['shares']/1e9:.3f}B")
    c3.metric("P/E TTM", f"{d['pe_ttm']:.2f}x")
    c4.metric("EPS TTM", f"${d['eps_ttm']:.2f}")

    # Fila 2: Calidad (API)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d['cr']:.2f}")
    c6.metric("Debt/Equity", f"{d['de']:.1f}%")
    c7.metric("ROE", f"{d['roe']:.1f}%")
    c8.metric("Op. Margin", f"{d['op_m']:.1f}%")

    # Fila 3: Futuro (Híbrido API + Manuales de Sheets)
    c9, c10, c11, c12 = st.columns(4)
    c9.metric("Rev. Growth (API)", f"{d['rev_g']:.1f}%")
    c10.metric("EPS Growth (Man)", f"{m_eps_g:.1f}%")
    c11.metric("Buyback Yield (Man)", f"{m_bb_y:.1f}%")
    c12.metric("FCF Yield (Man)", f"{m_fcf_y:.1f}%")

    st.markdown("---")

    # --- ORCA INTELLIGENCE: LAS 20 CATEGORÍAS ---
    # Conversión a decimales para lógica
    roe, margin, rev_g, de, cr = d['roe']/100, d['op_m']/100, d['rev_g']/100, d['de'], d['cr']
    eps_g, bb_y, fcf_y, div_y = m_eps_g/100, m_bb_y/100, m_fcf_y/100, d['div_y']/100
    total_yield = bb_y + div_y
    mcap = d['price'] * d['shares']

    alerts = []

    # 🟢 FORTALEZA (8)
    if roe > 0.25 and margin > 0.25 and de < 100: alerts.append("🟢 **Elite Compounder:** Rentabilidad y márgenes elevados con baja deuda.")
    if roe > 0.30 and margin > 0.20: alerts.append("🟢 **Capital Efficiency Engine:** Management altamente eficiente en el uso del capital.")
    if eps_g > 0.15 and roe > 0.20: alerts.append("🟢 **High Quality Growth:** Crecimiento fuerte respaldado por rentabilidad real.")
    if margin > 0.30 and rev_g > 0.10: alerts.append("🟢 **Scalable Model:** El negocio crece sin sacrificar márgenes.")
    if fcf_y > 0.07 and margin > 0.20: alerts.append("🟢 **Cash Flow Machine:** Generación masiva de caja operativa.")
    if total_yield > 0.06: alerts.append("🟢 **Shareholder Yield Alpha:** Alta retribución al dueño vía dividendos/recompras.")
    if de < 50 and cr > 1.5: alerts.append("🟢 **Financially Strong:** Balance blindado y gran liquidez.")
    if fcf_y > (1/d['pe_ttm'] if d['pe_ttm']>0 else 0): alerts.append("🟢 **Cash King:** La caja real supera al beneficio contable.")

    # 🟡 ADVERTENCIA (6)
    if roe > 0.25 and de > 150: alerts.append("🟡 **Leveraged Quality:** Rentabilidad alta pero impulsada por deuda.")
    if rev_g > 0.15 and margin < 0.10: alerts.append("🟡 **Growth Without Profit:** Crece en ventas pero no retiene beneficios.")
    if margin > 0.20 and rev_g < 0.05: alerts.append("🟡 **Mature Cash Cow:** Negocio sólido pero con poco espacio de crecimiento.")
    if cr < 0.9 and mcap > 20e9: alerts.append("🟡 **Working Capital King:** CR bajo típico de gigantes eficientes (estilo Amazon).")
    if eps_g > 0.20 and roe < 0.10: alerts.append("🟡 **Turnaround Play:** Expectativa de recuperación con rentabilidad aún débil.")
    if eps_g > 0.15 and fcf_y < 0.02: alerts.append("🟡 **Earnings Quality Warning:** El beneficio crece en papel, pero la caja no entra.")

    # 🔴 RIESGO (6)
    if rev_g < 0.05 and roe < 0.10: alerts.append("🔴 **Classic Value Trap:** Parece barato pero el negocio está estancado.")
    if de > 200 and roe < 0.15: alerts.append("🔴 **Debt Overhang:** Carga de deuda excesiva para los retornos generados.")
    if cr < 0.8 and mcap < 20e9: alerts.append("🔴 **Liquidity Stress:** Riesgo de insolvencia a corto plazo en Small/Mid Cap.")
    if roe < 0: alerts.append("🔴 **Capital Destroyer:** El negocio quema el dinero de los accionistas.")
    if total_yield > 0.05 and fcf_y < 0.03: alerts.append("🔴 **Yield Trap Risk:** El retorno al accionista es insostenible frente al FCF.")
    if rev_g < 0 and margin < 0 and roe < 0: alerts.append("🔴 **Zombie Mode:** Sin crecimiento, sin márgenes y sin rentabilidad.")

    with st.expander("🔍 ORCA Intelligence: Diagnóstico del Analista Senior", expanded=True):
        if alerts:
            for a in alerts:
                if "🟢" in a: st.info(a)
                elif "🟡" in a: st.warning(a)
                else: st.error(a)
        else:
            st.write("Sin alertas significativas. El negocio opera en parámetros estándar.")

    st.markdown("---")

    # --- SECCIÓN DE VEREDICTO ---
    st.subheader("🎯 Veredicto de Inversión")
    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    
    # Factor de seguridad ajustado por Quality Score
    factor_orca = 0.5 + (qs_sheets / 100) * 0.5
    precio_compra = iv_base * factor_orca
    qs_category = classify_qs(qs_sheets)

    if iv_base > 0:
        res1, res2, res3 = st.columns(3)
        res1.metric("Intrínseco Promedio", f"${iv_base:.2f}")
        res2.metric("Factor ORCA (B)", f"{factor_orca:.3f}")
        res3.metric("Precio de Compra", f"${precio_compra:.2f}",
                    delta=f"{((precio_compra/d['price'])-1)*100:.1f}% vs Mercado")

        if qs_sheets < 30:
            st.error(f"⛔ REJECTED: Calidad insuficiente ({qs_category})")
        elif d['price'] <= precio_compra:
            st.success(f"✅ BUY: El precio ofrece margen de seguridad ({qs_category})")
        elif d['price'] <= iv_base:
            st.warning(f"⚖️ HOLD: Cerca del valor intrínseco, sin margen claro ({qs_category})")
        else:
            st.error(f"🚫 OVERVALUED: Precio por encima del valor intrínseco ({qs_category})")
    else:
        st.info("Introduce datos de DCF/MR en el sidebar para obtener el veredicto.")

else:
    st.info("👈 Introduce un Ticker y haz clic en 'Cargar Métricas de Mercado' para comenzar.")


