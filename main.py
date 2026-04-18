import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

st.sidebar.title("ORCA Settings")
disc_rate = st.sidebar.slider("Discount Rate (DCF)", 0.05, 0.25, 0.15)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
st.caption("Objective Risk & Capital Allocation System")

ticker = st.text_input("Enter Ticker Symbol:", "").upper()

if ticker:
    res = get_cached_orca_data(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
    else:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        color = "red" if "REJECTED" in res['signal'] else "green" if "BUY" in res['signal'] else "orange"
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # --- ORCA INTELLIGENCE: DIAGNÓSTICO ROBUSTO ---
        alerts = []
        
        # 1. Escenario Zombie (Caso LZMH)
        if res['fcf_ttm'] <= 0 and res['margins'] <= 0:
            alerts.append("💀 **Zombie Company Alert:** Generación de caja nula y márgenes operativos negativos. Estructura de negocio no viable actualmente.")
        
        # 2. Análisis de ROE y Capital
        if res['roe'] < 0:
            alerts.append(f"🚨 **Capital Erosion:** ROE negativo ({res['roe']:.1%}). La empresa está consumiendo el patrimonio de los accionistas.")
        elif res['roe'] > 0.40 and res['debt_to_equity'] > 250:
            alerts.append(f"🧪 **Financial Engineering:** ROE de {res['roe']:.0%} inflado por deuda masiva. Riesgo de apalancamiento oculto.")

        # 3. Trampa de Liquidez
        if res['curr_ratio'] > 1.0 and res['fcf_ttm'] < 0:
            alerts.append(f"🌫️ **False Liquidity:** Current Ratio de {res['curr_ratio']:.2f} es estable, pero el flujo de caja negativo está drenando la caja operativa.")
        elif res['curr_ratio'] < 0.8:
            if res['fcf_ttm'] > 1e9:
                alerts.append(f"🔄 **Efficient Cash Machine:** Liquidez baja pero compensada por un FCF masivo. Común en empresas de alta rotación.")
            else:
                alerts.append(f"📉 **Liquidity Stress:** Riesgo de incumplimiento a corto plazo (CR < 1).")

        # 4. Escenario de Deuda
        if res['debt_to_equity'] > 300:
            if res['margins'] > 0.20:
                alerts.append(f"🏢 **Serviceable Debt:** Deuda alta pero protegida por márgenes operativos robustos.")
            else:
                alerts.append("🚨 **Extreme Leverage Risk:** Deuda insostenible frente a márgenes de beneficio mediocres.")

        if alerts:
            with st.expander("🔍 ORCA Intelligence: Risk & Quality Diagnosis", expanded=True):
                for a in alerts:
                    if any(icon in a for icon in ["💀", "🚨", "🧪"]): st.error(a)
                    elif any(icon in a for icon in ["🌫️", "📉"]): st.warning(a)
                    else: st.info(a)

        # Fila 2: Modelos
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res.get('dcf') else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold (+20%):** ${res['sell_threshold']:.2f}")

        # Fila 3: Métricas
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.8, 1.2])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Asset Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            ma1, ma2 = st.columns(2)
            with ma1:
                st.write(f"Current Ratio: `{res['curr_ratio']:.2f}`")
                st.write(f"Debt to Equity: `{res['debt_to_equity']:.1f}%`")
                st.write(f"ROE: `{res['roe']:.2%}`")
            with ma2:
                st.write(f"FCF TTM: `${res['fcf_ttm']:,.0f}`")
                st.write(f"Op. Margins: `{res['margins']:.2%}`")
                st.write(f"Revenue Growth: `{res['rev_growth']:.2%}`")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            weights = {"Gem 💎": "15%", "Core": "10%", "Standard": "5%", "Speculative": "2%", "Avoid": "0%"}
            st.markdown(f"**Max Weight:** `{weights.get(res['category'], '0%')}`")
            
            tier_limit = {"Gem 💎": "60%", "Core": "50%", "Standard": "30%", "Speculative": "10%", "Avoid": "0%"}
            st.info(f"**Tier Limit:** {tier_limit.get(res['category'], '0%')}")
else:
    st.info("Please enter a ticker symbol to begin.")


