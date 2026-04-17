import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

st.sidebar.title("ORCA Settings")
disc_rate = st.sidebar.slider("Discount Rate (DCF)", 0.05, 0.25, 0.15)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
ticker = st.text_input("Enter Ticker Symbol:", "").upper()

if ticker:
    res = get_cached_orca_data(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
    else:
        # Row 1: Metrics & Signal
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        color = "red" if "REJECTED" in res['signal'] else "green" if "BUY" in res['signal'] else "orange" if res['signal'] == "HOLD" else "red"
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # --- NEW: SYSTEM ALERTS ---
        alerts = []
        if res['roe'] > 1.0:
            alerts.append(f"⚠️ **High ROE ({res['roe']:.0%}):** This may be distorted by negative equity or massive share buybacks.")
        if res['debt_to_equity'] > 200:
            alerts.append(f"🚩 **Extreme Leverage:** Debt to Equity is `{res['debt_to_equity']:.0f}%`. Ensure interest coverage is stable.")
        if res['curr_ratio'] < 0.8:
            alerts.append("📉 **Liquidity Risk:** Current Ratio is below 0.8. Check short-term solvency.")
            
        if alerts:
            with st.expander("🔍 Risk Management Alerts", expanded=True):
                for a in alerts:
                    st.warning(a)

        # Row 2: Models
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold:** ${res['sell_threshold']:.2f}")

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
                st.write("**Solvency & Efficiency**")
                st.write(f"Current Ratio: `{res['curr_ratio']:.2f}`")
                st.write(f"Debt to Equity: `{res['debt_to_equity']:.2f}%`")
                st.write(f"ROE: `{res['roe']:.2%}`")
                st.write(f"Op. Margins: `{res['margins']:.2%}`")
            with ma2:
                st.write("**Growth & Cash Flow**")
                st.write(f"Revenue Growth: `{res['rev_growth']:.2%}`")
                st.write(f"Earnings Growth: `{res['earn_growth']:.2%}`")
                st.write(f"FCF TTM: `${res['fcf_ttm']:,.0f}`")
                st.write(f"FCF CAGR: `{res['growth']:.2%}`")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            weights = {"Gem 💎": "15%", "Core": "10%", "Standard": "5%", "Speculative": "2%", "Avoid": "0%"}
            max_w = weights.get(res['category'], "0%")
            st.markdown(f"**Max Weight per Position:** `{max_w}`")
            
            tier_limit = {"Gem 💎": "60%", "Core": "50%", "Standard": "30%", "Speculative": "10%", "Avoid": "0%"}
            st.info(f"**Portfolio Limit ({res['category']}):** {tier_limit.get(res['category'], '0%')}")

else:
    st.info("Please enter a ticker symbol.")
