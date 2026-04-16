import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA System", layout="wide")

st.sidebar.title("Configuración ORCA")
disc_rate = st.sidebar.slider("Discount Rate", 0.05, 0.25, 0.15)
manual_mos = st.sidebar.slider("Min. Margin of Safety", 0.05, 0.50, 0.20)

st.title("🚢 ORCA: Advanced Intrinsic Analytics")
ticker = st.text_input("Ticker:", "AAPL").upper()

if ticker:
    res = run_orca_logic(ticker, disc_rate, manual_mos)
    
    if "error" in res:
        st.error(res["error"])
    else:
        # Fila 1: El Corazón del Sistema
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Precio Mercado", f"${res['price']:.2f}")
        c2.metric("Intrínseco Combinado", f"${res['intrinsic']:.2f}")
        
        color = "green" if res['signal'] == "BUY" else "orange" if res['signal'] == "HOLD" else "red"
        c3.markdown(f"### Señal: :{color}[{res['signal']}]")

        # Fila 2: Desglose de Modelos (Aquí se ve la diferencia)
        st.subheader("🛠️ Modelos de Valoración")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Precio de Compra (w/MOS):** ${res['mos_price']:.2f}")

        # Fila 3: El Quality Score en acción
        st.divider()
        col_qs, col_data = st.columns([1, 2])
        
        with col_qs:
            st.subheader(f"🛡️ Quality Score: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption("Determina el margen de seguridad dinámico.")

        with col_data:
            st.write("**Métricas de Apoyo**")
            st.write(f"FCF TTM: ${res['fcf_ttm']:,.0f} | CAGR: {res.get('growth', 0):.2%}")
            st.write(f"ROE: {res['info'].get('returnOnEquity', 0):.2%} | Margins: {res['info'].get('operatingMargins', 0):.2%}")


