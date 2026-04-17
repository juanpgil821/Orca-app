import streamlit as st
from calculos import run_orca_logic

# Page Configuration
st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

# 💡 Optimization: Cache data for 10 minutes to avoid Yahoo Finance rate limits
@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

# Sidebar Configuration
st.sidebar.title("ORCA Settings")
st.sidebar.markdown("---")
disc_rate = st.sidebar.slider("Discount Rate (DCF)", 0.05, 0.25, 0.15, help="Hurdle rate for cash flow valuation.")

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
st.caption("Objective Risk & Capital Allocation System")

# Input with a clear instruction to avoid multiple rapid requests
ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT, GOOGL):", "").upper()

if ticker:
    # Use the cached function instead of calling run_orca_logic directly
    res = get_cached_orca_data(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
        st.info("Note: If you see frequent errors, Yahoo Finance might be rate-limiting your IP. Please wait a few minutes.")
    else:
        # Row 1: Key Metrics & Signaling
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        # Dynamic color logic for Signal
        if res['signal'].startswith("BUY"):
            color = "green"
        elif res['signal'] == "HOLD":
            color = "orange"
        else:
            color = "red"
            
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # Row 2: Valuation Models Breakdown
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold (+20%):** ${res['sell_threshold']:.2f}")
        
        st.caption("Intrinsic Value is the average of DCF and Mean Reversion models.")

        # Row 3: Quality Score, Analytics & Exposure
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.5, 1.5])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Asset Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            st.write(f"**FCF TTM:** ${res['fcf_ttm']:,.0f}")
            st.write(f"**CAGR (Growth):** {res.get('growth', 0):.2%}")
            st.write(f"**ROE:** {res['info'].get('returnOnEquity', 0):.2%}")
            st.write(f"**Operating Margins:** {res['info'].get('operatingMargins', 0):.2%}")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            st.markdown(f"**Max Weight per Position:** `{res['max_weight']}`")
            
            # Risk Management Info Box
            with st.container():
                # Logic to determine the tier limit text
                tier_limit = "50%" if res['category'] == "Core" else \
                             "30%" if res['category'] == "Standard" else \
                             "10%" if res['category'] == "Speculative" else "0%"
                
                st.info(f"""
                **Portfolio Allocation Limits ({res['category']}):**
                * Max Total {res['category']} Tier: {tier_limit}
                * Risk Profile: {res['category']} Asset
                """)

else:
    st.info("Please enter a ticker symbol to begin the analysis.")
