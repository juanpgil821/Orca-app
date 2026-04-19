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
                'op_m': raw.get('operatingMargins', 0.0) * 100
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
    c9 = st.columns(1)[0]
    c9.metric("Rev. Growth (YoY)", f"{d.get('rev_g', 0):.1f}%")

    st.markdown("---")

    # --- ORCA INTELLIGENCE (EXPLICATIVO) ---
    roe = d.get('roe', 0) / 100
    margin = d.get('op_m', 0) / 100
    rev_g = d.get('rev_g', 0) / 100
    de = d.get('de', 0)
    cr = d.get('cr', 0)

    alerts = []

    # 🟢 CALIDAD ALTA
    if roe > 0.25 and margin > 0.25 and de < 100:
        alerts.append(
            "💎 Elite Compounder:\n"
            "→ ROE alto: la empresa genera mucho beneficio por cada dólar de capital.\n"
            "→ Márgenes altos: fuerte pricing power o estructura de costos eficiente.\n"
            "→ Baja deuda: menor riesgo financiero.\n"
            "✔ Conclusión: negocio capaz de reinvertir a altas tasas durante largos periodos."
        )

    if roe > 0.30 and margin > 0.20:
        alerts.append(
            "🏭 Capital Efficiency Engine:\n"
            "→ ROE elevado: excelente retorno sobre el capital invertido.\n"
            "→ Márgenes sólidos: eficiencia operativa.\n"
            "✔ Conclusión: management altamente eficiente."
        )

    if margin > 0.30:
        alerts.append(
            "📈 High Margin Business:\n"
            "→ La empresa retiene gran parte de sus ingresos como beneficio.\n"
            "→ Indica ventaja competitiva (marca, tecnología, moat).\n"
            "✔ Conclusión: fuerte capacidad de fijación de precios."
        )

    if roe > 0.20 and de < 100:
        alerts.append(
            "🛡️ Financially Strong:\n"
            "→ Rentabilidad consistente (ROE alto).\n"
            "→ Deuda controlada.\n"
            "✔ Conclusión: balance sólido y sostenible."
        )

    # 🟡 MIXTOS
    if rev_g > 0.10 and margin < 0.15:
        alerts.append(
            "⚖️ Growth Without Margins:\n"
            "→ Crece en ingresos pero no en beneficios.\n"
            "→ Márgenes bajos sugieren ineficiencia o falta de escala.\n"
            "✔ Conclusión: crecimiento aún no rentable."
        )

    if roe > 0.20 and de > 150:
        alerts.append(
            "🧪 Leveraged Quality:\n"
            "→ ROE alto pero impulsado por deuda.\n"
            "→ Apalancamiento aumenta riesgo.\n"
            "✔ Conclusión: calidad condicionada al endeudamiento."
        )

    if margin > 0.20 and rev_g < 0.05:
        alerts.append(
            "🐢 Mature Cash Cow:\n"
            "→ Alta rentabilidad (márgenes fuertes).\n"
            "→ Bajo crecimiento en ingresos.\n"
            "✔ Conclusión: negocio maduro que genera caja pero crece poco."
        )

    if cr < 1 and de < 150:
        alerts.append(
            "🏢 Working Capital Efficiency:\n"
            "→ Bajo capital circulante (CR bajo).\n"
            "→ Puede indicar eficiencia operativa.\n"
            "✔ Conclusión: modelo optimizado, pero requiere monitoreo."
        )

    # 🔴 RIESGOS
    if roe < 0.10 and margin < 0.10:
        alerts.append(
            "🪤 Weak Business:\n"
            "→ Baja rentabilidad sobre capital.\n"
            "→ Márgenes débiles.\n"
            "✔ Conclusión: negocio estructuralmente débil."
        )

    if roe < 0.08 and rev_g < 0.05:
        alerts.append(
            "🪤 Value Trap Risk:\n"
            "→ Sin crecimiento.\n"
            "→ Bajo retorno sobre capital.\n"
            "✔ Conclusión: parece barato pero sin catalizadores."
        )

    if de > 200:
        alerts.append(
            "⚠️ Debt Overhang:\n"
            "→ Alto nivel de deuda.\n"
            "✔ Conclusión: riesgo financiero elevado."
        )

    if cr < 0.8:
        alerts.append(
            "💧 Liquidity Risk:\n"
            "→ Dificultad para cubrir obligaciones de corto plazo.\n"
            "✔ Conclusión: posible estrés financiero."
        )

    if roe < 0:
        alerts.append(
            "🔥 Capital Destruction:\n"
            "→ ROE negativo.\n"
            "✔ Conclusión: destrucción de valor para el accionista."
        )

    if margin <= 0:
        alerts.append(
            "💀 No Profitability:\n"
            "→ Márgenes negativos.\n"
            "✔ Conclusión: negocio no rentable."
        )

    if roe < 0 and margin < 0 and rev_g < 0:
        alerts.append(
            "💀 Zombie Company:\n"
            "→ Sin crecimiento, sin márgenes, sin rentabilidad.\n"
            "✔ Conclusión: empresa no viable."
        )

    # --- RENDER ---
    if alerts:
        with st.expander("🔍 ORCA Intelligence", expanded=True):
            for a in alerts:
                if any(icon in a for icon in ["💎","🏭","📈","🛡️"]):
                    st.info(a)
                elif any(icon in a for icon in ["⚖️","🧪","🐢","🏢"]):
                    st.warning(a)
                else:
                    st.error(a)

    st.markdown("---")

    # --- VALUACIÓN ---
    st.subheader("🎯 Veredicto de Inversión")

    iv_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)
    factor_orca = 0.5 + (qs_sheets / 100) * 0.5
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
