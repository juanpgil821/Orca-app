import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
ticker = st.text_input("Enter Ticker Symbol:", "").upper()
disc_rate = st.sidebar.slider("Discount Rate", 0.05, 0.25, 0.15)

if ticker:
    res = get_cached_orca_data(ticker, disc_rate)
    if "error" in res:
        st.error(res["error"])
    else:
        # Fila 1: Métricas principales (Mismo formato que el anterior)
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        sig_col = "red" if "REJECTED" in res['signal'] else "green" if "BUY" in res['signal'] else "orange"
        c3.markdown(f"### Signal: :{sig_col}[{res['signal']}]")

        # --- ORCA INTELLIGENCE 3.0: ANALISTA SENIOR ---
        alerts = []
        
        # A. SECCIÓN DE EXCELENCIA (GEMAS Y FOSOS)
        if res['margins'] > 0.35 and res['roe'] > 0.25:
            alerts.append("💎 **Wide Moat Gem:** Márgenes de élite (>35%) y ROE alto. Esta empresa tiene un poder de fijación de precios masivo.")
        
        if res['buyback_yield'] > 0.04:
            alerts.append(f"🐂 **Aggressive Cannibal:** Recompra de acciones masiva ({res['buyback_yield']:.1%}). La directiva cree que la acción está barata y está concentrando tu valor.")

        # B. SECCIÓN DE RIESGOS Y ESTRÉS
        if res['curr_ratio'] < 0.85:
            if res['fcf_ttm'] > 5e9: # Flujo de caja masivo (Ej: Apple, Walmart)
                alerts.append(f"🔄 **Controlled Liquidity:** CR bajo ({res['curr_ratio']:.2f}) pero compensado por FCF masivo. Es una estrategia de eficiencia en gigantes.")
            else:
                alerts.append(f"🚨 **Liquidity Asphyxia:** CR de {res['curr_ratio']:.2f} sin suficiente FCF. Riesgo inminente de necesitar deuda o ampliar capital.")

        if res['payout'] > 0.90 and res['fcf_ttm'] > 0:
            alerts.append("⚠️ **Dividend Trap?** Payout ratio extremo (>90%). El dividendo podría ser insostenible si el FCF flaquea un solo trimestre.")

        if res['debt_to_equity'] > 250:
            if res['margins'] > 0.15:
                alerts.append(f"🏢 **High Leverage (Serviceable):** Deuda del {res['debt_to_equity']:.0f}%, pero los márgenes permiten el pago de intereses por ahora.")
            else:
                alerts.append(f"🚩 **Debt Death Trap:** Deuda alta con márgenes pobres. La empresa trabaja para el banco, no para ti.")

        # C. EL ESCENARIO "ZOMBIE / LZMH"
        if res['roe'] < 0 or res['fcf_ttm'] <= 0:
            if res['rev_growth'] > 0.20:
                alerts.append("🔥 **Cash Burner:** Crecimiento alto pero quemando caja. ¿Cuándo llegará la rentabilidad?")
            else:
                alerts.append("💀 **Structural Decay:** Sin beneficios, sin caja y sin crecimiento. Evitar a toda costa.")

        if alerts:
            with st.expander("🔍 ORCA Intelligence: Deep Risk & Quality Analysis", expanded=True):
                for a in alerts:
                    if any(icon in a for icon in ["💎", "🐂", "✨"]): st.info(a)
                    elif any(icon in a for icon in ["⚠️", "🔄", "🏢"]): st.warning(a)
                    else: st.error(a)

        # Fila 2: Modelos y Datos Fundamentales (Resto del código igual para mantener consistencia)
        st.divider()
        st.subheader("📊 Fundamental Analytics")
        ma1, ma2, ma3 = st.columns(3)
        with ma1:
            st.write(f"**QS:** {res['qs']:.1f} ({res['category']})")
            st.write(f"ROE: `{res['roe']:.2%}`")
            st.write(f"Op. Margins: `{res['margins']:.2%}`")
        with ma2:
            st.write(f"Current Ratio: `{res['curr_ratio']:.2f}`")
            st.write(f"Debt to Equity: `{res['debt_to_equity']:.1f}%`")
            st.write(f"Buyback Yield: `{res['buyback_yield']:.2%}`")
        with ma3:
            st.write(f"FCF TTM: `${res['fcf_ttm']:,.0f}`")
            st.write(f"Rev. Growth: `{res['rev_growth']:.2%}`")
            st.write(f"Payout Ratio: `{res['payout']:.2%}`")
else:
    st.info("Enter ticker to perform Deep Analysis.")


