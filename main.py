import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide")

st.sidebar.title("ORCA Settings")
disc_rate = st.sidebar.slider("Discount Rate", 0.05, 0.25, 0.15)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
ticker = st.text_input("Ticker Symbol:", "AAPL").upper()

if ticker:
    res = run_orca_logic(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
    else:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        color = "green" if res['signal'].startswith("BUY") else "orange" if res['signal'] == "HOLD" else "red"
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # Row 2: Valuation Models
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
            st.caption(f"Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            st.write(f"**FCF TTM:** ${res['fcf_ttm']:,.0f}")
            st.write(f"**CAGR:** {res.get('growth', 0):.2%}")
            st.write(f"**ROE:** {res['info'].get('returnOnEquity', 0):.2%}")
            st.write(f"**Margins:** {res['info'].get('operatingMargins', 0):.2%}")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            st.markdown(f"**Max Weight per Position:** `{res['max_weight']}`")
            
            with st.container():
                st.info(f"""
                **Portfolio Allocation Limits ({res['category']}):**
                * Max Total {res['category']} Tier: {
                    '50%' if res['category'] == 'Core' else 
                    '30%' if res['category'] == 'Standard' else 
                    '10%' if res['category'] == 'Speculative' else '0%'
                }
                * Risk Profile: {res['category']} Asset
                """)
