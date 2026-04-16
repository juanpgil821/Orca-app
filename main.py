import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide")

st.sidebar.title("Configuración ORCA")
disc_rate = st.sidebar.slider("Discount Rate", 0.05, 0.25, 0.15)
manual_mos = st.sidebar.slider("Min. Margin of Safety (DCF)", 0.05, 0.50, 0.20)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
ticker = st.text_input("Ticker:", "AAPL").upper()

if ticker:
    res = run_orca_logic(ticker, disc_rate, manual_mos)
    
    if "error" in res:
        st.error(res["error"])
    else:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Precio Mercado", f"${res['price']:.2f}")
        c2.metric("Intrínseco Combinado", f"${res['intrinsic']:.2f}")
        
        if res['signal'].startswith("BUY"):
            color = "green"
        elif res['signal'] == "HOLD":
            color = "orange"
        else:
            color = "red"
            
        c3.markdown(f"### Señal: :{color}[{res['signal']}]")

        # Fila 2: Desglose de Modelos
        st.subheader("🛠️ Modelos de Valoración")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Compra (DCF w/MOS):** ${res['mos_price']:.2f}")
        
        st.caption(f"Límite para Venta (Intrínseco + 20%): ${res['sell_threshold']:.2f}")

        # Fila 3: Calidad y Exposición (Sección nueva a la derecha)
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.5, 1.5])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Clasificación: **{res['category']}**")

        with col_metrics:
            st.write("**Métricas de Apoyo**")
            st.write(f"FCF TTM: ${res['fcf_ttm']:,.0f}")
            st.write(f"CAGR: {res.get('growth', 0):.2%}")
            st.write(f"ROE: {res['info'].get('returnOnEquity', 0):.2%}")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            st.markdown(f"**Max. Weight per Position:** `{res['max_weight']}`")
            
            # Bloque de guía de portafolio
            with st.container():
                st.info(f"""
                **Portfolio Limits ({res['category']}):**
                * Max Total {res['category']}: {
                    '50%' if res['category'] == 'Core' else 
                    '30%' if res['category'] == 'Standard' else 
                    '10%' if res['category'] == 'Speculative' else '0%'
                }
                * Current Risk Tier: {res['category']}
                """)
