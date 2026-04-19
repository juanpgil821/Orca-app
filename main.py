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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ORCA Terminal 2.0", layout="wide", page_icon="🚢")
st.title("🚢 ORCA 2.0: Terminal de Ejecución e Inteligencia")
st.markdown("---")

# --- SIDEBAR: INPUTS DE VALORACIÓN ---
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
            ticker_obj = yf.Ticker(ticker_input)
            raw = ticker_obj.info
            
            # 1. CÁLCULO DE BUYBACK YIELD REAL (TTM)
            # Extraemos del Cash Flow el gasto real en recompra de acciones
            try:
                cf = ticker_obj.cashflow
                # Buscamos la fila de recompra, suele ser negativa (salida de caja)
                buyback_cash = abs(cf.loc['Repurchase Of Capital Stock'].iloc[0])
                market_cap = raw.get('marketCap', 1)
                bb_yield_calc = (buyback_cash / market_cap) * 100
            except:
                bb_yield_calc = 0.0

            # 2. ESTABILIZACIÓN DE EPS GROWTH (Evitar anomalías extremas)
            eps_g_raw = raw.get('earningsGrowth', 0.0)
            if eps_g_raw > 2.0: eps_g_raw = 0.20  # Capamos crecimientos absurdos para el analista
            elif eps_g_raw < -1.0: eps_g_raw = -0.50

            # 3. CONSOLIDACIÓN EN SESSION STATE
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
                'div_y': raw.get('dividendYield', 0.0) * 100 if raw.get('dividendYield') else 0.0,
                'bb_y': bb_yield_calc,
                'eps_g': eps_g_raw * 100
            }
        except Exception as e:
            st.error(f"Error al conectar con la API: {e}")

# --- PANEL CENTRAL: VISUALIZACIÓN ---
d = st.session_state.get('data', {})

if d:
    st.subheader(f"📊 Fundamentales: {ticker_input}")
    
    # Fila 1: Mercado
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Precio", f"${d.get('price', 0):.2f}")
    c2.metric("Shares (B)", f"{d.get('shares', 0) / 1e9:.3f}B")
    c3.metric("P/E TTM", f"{d.get('pe_ttm', 0):.2f}x")
    c4.metric("EPS TTM", f"${d.get('eps_ttm', 0):.2f}")

    # Fila 2: Calidad Financiera
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Current Ratio", f"{d.get('cr', 0):.2f}")
    c6.metric("Debt to Equity", f"{d.get('de', 0):.2f}%")
    c7.metric("ROE", f"{d.get('roe', 0):.1f}%")
    c8.metric("Operating Margin", f"{d.get('op_m', 0):.1f}%")

    # Fila 3: Crecimiento y Retorno
    c9, c10, c11 = st.columns(3)
    c9.metric("Rev. Growth (YoY)", f"{d.get('rev_g', 0):.1f}%")
    c10.metric("EPS Growth (Adj)", f"{d.get('eps_g', 0):.1f}%")
    # Sumamos dividendo + recompras para el Yield Total
    total_yield = d.get('div_y', 0) + d.get('bb_y', 0)
    c11.metric("Total Shareholder Yield", f"{total_yield:.2f}%", 
              help=f"Div: {d.get('div_y',0):.2f}% | Buyback: {d.get('bb_y',0):.2f}%")

    st.markdown("---")

    # --- ORCA INTELLIGENCE 2.0: ANALISTA SENIOR ---
    roe_val = d.get('roe', 0) / 100
    margin_val = d.get('op_m', 0) / 100
    bb_yield = d.get('bb_y', 0) / 100
    cr_val = d.get('cr', 0)
    de_val = d.get('de', 0)
    eps_g_val = d.get('eps_g', 0) / 100
    rev_g_val = d.get('rev_g', 0) / 100

    alerts = []

    # Diagnósticos Positivos (Institucionales)
    if roe_val > 0.25 and margin_val > 0.25 and de_val < 100:
        alerts.append("💎 **Elite Compounder:** Rentabilidad y márgenes elevados con baja deuda. Capacidad de reinversión masiva.")

    if roe_val > 0.30 and margin_val > 0.20:
        alerts.append("🏭 **Capital Efficiency Engine:** Uso del capital superior al promedio del mercado.")

    if bb_yield > 0.04 and roe_val > 0.15:
        alerts.append(f"💰 **Capital Return Machine:** Recompra significativa ({bb_yield:.1%}) respaldada por rentabilidad real.")

    if eps_g_val > 0.15 and roe_val > 0.20:
        alerts.append("🚀 **High Quality Growth:** Crecimiento fuerte acompañado de alta eficiencia.")

    if margin_val > 0.30 and rev_g_val > 0.10:
        alerts.append("📈 **Scalable Model:** Crecimiento sin sacrificio de márgenes.")

    if margin_val > 0.20 and total_yield > 0.03:
        alerts.append("💵 **Cash Flow Machine:** Generación sólida de caja y retorno al accionista.")

    # Diagnósticos de Riesgo y Alertas
    if eps_g_val > 0.20 and roe_val < 0.10:
        alerts.append("🔄 **Turnaround Play:** Alto crecimiento esperado pero rentabilidad actual débil. Riesgo de ejecución.")

    if eps_g_val > 0.15 and de_val > 150:
        alerts.append("🧪 **Leveraged Growth:** Crecimiento impulsado por deuda. Frágil ante desaceleraciones.")

    if margin_val < 0.10 and roe_val < 0.10 and total_yield > 0.04:
        alerts.append("⚠️ **Yield Trap Risk:** Dividendo alto pero negocio subyacente débil. Sostenibilidad en duda.")

    if de_val > 200 and roe_val < 0.15:
        alerts.append("⚠️ **Debt Overhang Risk:** Carga de deuda excesiva para los retornos que genera.")

    # Corrección de Liquidez para Gigantes (WMT, MO, etc)
    if cr_val < 0.9:
        mkt_cap = d.get('price', 0) * d.get('shares', 0)
        if mkt_cap > 20_000_000_000:
            alerts.append(f"🛡️ **Defensive Giant (Working Capital King):** CR bajo ({cr_val}) normal en líderes con alto poder de negociación.")
        else:
            alerts.append(f"💧 **Liquidity Stress:** Riesgo de liquidez a corto plazo en empresa sin escala suficiente.")

    if roe_val < 0:
        alerts.append("🔥 **Capital Destruction:** ROE negativo. El negocio consume más de lo que genera.")

    if margin_val <= 0 and roe_val <= 0:
        alerts.append("💀 **Zombie Mode:** Sin márgenes ni retorno. Empresa en estado crítico.")

    if alerts:
        with st.expander("🔍 ORCA Intelligence: Institutional Diagnostics", expanded=True):
            for a in alerts:
                if any(icon in a for icon in ["💎","🏭","💰","🚀","📈","🛡️","💵"]):
                    st.info(a)
                elif any(icon in a for icon in ["🔄","🧪","⚠️"]):
                    st.warning(a)
                else:
                    st.error(a)

    st.markdown("---")

    # --- VALUACIÓN Y VEREDICTO FINAL ---
    st.subheader("🎯 Veredicto de Inversión")

    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    
    # NUEVA FÓRMULA B: 0.5 + (QS/100 * 0.5)
    factor_orca = 0.5 + (qs_sheets / 100) * 0.5
    precio_compra = iv_base * factor_orca
    qs_category = classify_qs(qs_sheets)

    if iv_base > 0:
        res1, res2, res3 = st.columns(3)
        res1.metric("Intrínseco Promedio", f"${iv_base:.2f}")
        res2.metric("Factor ORCA (B)", f"{factor_orca:.3f}")
        res3.metric("Precio de Compra", f"${precio_compra:.2f}",
                    delta=f"{((precio_compra/d.get('price', 1))-1)*100:.1f}% vs Mercado")

        price = d.get('price', 0)

        if qs_sheets < 30:
            st.error(f"⛔ REJECTED: Calidad insuficiente ({qs_category})")
        else:
            if price <= precio_compra:
                st.success(f"✅ BUY: Zona de seguridad alcanzada ({qs_category})")
            elif price <= iv_base:
                st.warning(f"⚖️ HOLD: Por debajo del valor real, pero falta margen de seguridad ({qs_category})")
            else:
                st.error(f"🚫 OVERVALUED: El precio ignora el margen de seguridad ({qs_category})")
    else:
        st.info("Introduce los datos de DCF y MR desde Sheets para ver el veredicto.")

else:
    st.info("Introduce un Ticker en el sidebar y pulsa 'Cargar Métricas' para iniciar.")


