import streamlit as st
from calculos import run_orca_logic

# Page Configuration
st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

# Sidebar Configuration
st.sidebar.title("ORCA Settings")
st.sidebar.markdown("---")
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
        
        # Color logic for Signal
        sig = res['signal']
        if "REJECTED" in sig: color = "red"
        elif "BUY" in sig: color = "green"
        elif sig == "HOLD": color = "orange"
        else: color = "red"
            
        c3.markdown(f"### Signal: :{color}[{sig}]")

        # Row 2: Models
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold (+20%):** ${res['sell_threshold']:.2f}")

        # Row 3: Quality & Exposure
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.5, 1.5])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Asset Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            st.write(f"**FCF TTM:** ${res.get('fcf_ttm', 0):,.0f}")
            st.write(f"**CAGR (Growth):** {res.get('growth', 0):.2%}")
            st.write(f"**ROE:** {res.get('roe', 0):.2%}")
            st.write(f"**Margins:** {res.get('margins', 0):.2%}")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            weights = {"Gem 💎": "15%", "Core": "10%", "Standard": "5%", "Speculative": "2%", "Avoid": "0% (Avoid)"}
            max_w = weights.get(res['category'], "0%")
            st.markdown(f"**Max Weight per Position:** `{max_w}`")
            
            with st.container():
                tier_limit = {"Gem 💎": "60%", "Core": "50%", "Standard": "30%", "Speculative": "10%", "Avoid": "0%"}
                limit = tier_limit.get(res['category'], "0%")
                st.info(f"""
                **Portfolio Allocation Limits ({res['category']}):**
                * Max Total {res['category']} Tier: {limit}
                * Risk Profile: {res['category']} Asset
                """)
else:
    st.info("Please enter a ticker symbol to begin.")


