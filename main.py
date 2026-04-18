import streamlit as st
from calculos import run_orca_logic

# Configuración de la página
st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

# Sidebar
st.sidebar.title("ORCA Settings")
disc_rate = st.sidebar.slider("Discount Rate (DCF)", 0.05, 0.25, 0.15)
st.sidebar.caption("Higher rate = more conservative valuation.")

# Encabezado
st.title("🚢 ORCA: Advanced Intrinsic Analytics")
st.caption("Objective Risk & Capital Allocation System")

ticker = st.text_input("Enter Ticker Symbol:", "").upper()

if ticker:
    res = get_cached_orca_data(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
    else:
        # Fila 1: Estado de Mercado
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        color = "red" if "REJECTED" in res['signal'] else "green" if "BUY" in res['signal'] else "orange" if res['signal'] == "HOLD" else "red"
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # --- ORCA INTELLIGENCE ---
        alerts = []
        if res['margins'] > 0.30 and res['roe'] > 0.30:
            alerts.append("💎 **Wide Moat Gem:** Márgenes y ROE de élite.")
        if res['buyback_yield'] > 0.05:
            alerts.append(f"🐂 **Shareholder Yield Alpha:** Recompra masiva ({res['buyback_yield']:.1%}).")
        if res['fcf_ttm'] <= 0 and res['margins'] <= 0:
            alerts.append("💀 **Zombie Company Alert:** Negocio inviable sin flujo ni margen.")
        if res['roe'] < 0:
            alerts.append(f"🚨 **Capital Destroyer:** ROE negativo ({res['roe']:.1%}).")
        if res['roe'] > 0.50 and res['debt_to_equity'] > 250:
            alerts.append("🧪 **Leveraged ROE:** Rentabilidad inflada por deuda.")
        if res['curr_ratio'] < 0.9:
            if res['fcf_ttm'] > 2_000_000_000:
                alerts.append(f"🔄 **Negative Working Capital King:** FCF masivo compensa CR bajo.")
            else:
                alerts.append(f"📉 **Liquidity Trap:** Riesgo de insolvencia a corto plazo.")

        if alerts:
            with st.expander("🔍 ORCA Intelligence: Risk & Quality Diagnosis", expanded=True):
                for a in alerts:
                    if any(icon in a for icon in ["💎", "✨", "🐂", "🔄", "✂️"]): st.info(a)
                    elif any(icon in a for icon in ["⚠️", "🧪", "🚀", "🌫️"]): st.warning(a)
                    else: st.error(a)

        # Fila 2: Modelos de Valuación
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold:** ${res['sell_threshold']:.2f}")

        # Fila 3: Métricas, Value Drivers y Exposición
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.8, 1.2])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Asset Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            ma1, ma2, ma3 = st.columns(3)
            with ma1:
                st.write("**Solvency & Efficiency**")
                st.write(f"Current Ratio: `{res['curr_ratio']:.2f}`")
                st.write(f"Debt to Equity: `{res['debt_to_equity']:.2f}%`")
                st.write(f"ROE: `{res['roe']:.2%}`")
            with ma2:
                st.write("**Growth & Cash Flow**")
                st.write(f"Rev Growth: `{res['rev_growth']:.2%}`")
                st.write(f"FCF TTM: `${res['fcf_ttm']:,.0f}`")
                st.write(f"FCF CAGR: `{res['growth']:.2%}`")
            with ma3:
                st.write("**Value Drivers**")
                st.write(f"EPS TTM: `${res['eps_ttm']:.2f}`")
                st.write(f"FCF/SH: `${res['fcf_share']:.2f}`")
                st.write(f"Margins: `{res['margins']:.2%}`")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            weights = {"Gem 💎": "15%", "Core": "10%", "Standard": "5%", "Speculative": "2%", "Avoid": "0%"}
            max_w = weights.get(res['category'], "0%")
            st.markdown(f"**Max Weight:** `{max_w}`")
            st.info(f"**Portfolio Limit:** {res['category']}")

else:
    st.info("Enter a ticker symbol to start analysis.")




