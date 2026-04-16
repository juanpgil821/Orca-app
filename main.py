import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA Advanced", layout="wide", initial_sidebar_state="expanded")

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Parámetros")
    disc_rate = st.slider("Tasa de Descuento", 0.05, 0.25, 0.15, 0.01)
    min_mos = st.slider("Mínimo MOS", 0.05, 0.50, 0.20, 0.05)
    st.divider()
    st.caption("Fórmula MR: (Acción 70% | Sector 30%)")

# --- APP ---
st.title("🚢 ORCA Intrinsic System")
ticker = st.text_input("Ingrese Ticker:", placeholder="AAPL").upper()

if ticker:
    with st.spinner("Analizando fundamentos..."):
        res = run_orca_logic(ticker, disc_rate, min_mos)
        
        if "error" in res:
            st.error(res["error"])
        else:
            # Resumen Superior
            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"${res['price']:.2f}")
            c2.metric("Intrínseco Final", f"${res['intrinsic']:.2f}")
            c3.metric("Precio de Compra", f"${res['mos_price']:.2f}", help="Incluye Margen de Seguridad")
            
            sig_color = {"BUY": "green", "HOLD": "orange", "SELL": "red"}[res['signal']]
            c4.markdown(f"### Señal: :{sig_color}[{res['signal']}]")

            # Desglose de Modelos
            st.subheader("🛠️ Modelos de Valoración")
            m1, m2 = st.columns(2)
            
            with m1:
                st.info(f"**DCF (Flujo de Caja):** ${res['dcf']:.2f}")
                st.write(f"FCF TTM: ${res['fcf_ttm']:,.0f}")
                st.write(f"CAGR Estimado: {res['growth']:.2%}")
                
            with m2:
                st.info(f"**MR (Reversión):** ${res['mr']:.2f}")
                st.write(f"B12 (Acción 70%): ${res['mr_stock']:.2f}")
                st.write(f"D12 (Sector 30%): ${res['mr_sector']:.2f}")

            # Calidad
            st.divider()
            q_col1, q_col2 = st.columns([1, 2])
            with q_col1:
                st.subheader(f"🛡️ Quality Score: {res['qs']:.1f}")
                st.progress(res['qs']/100)
            with q_col2:
                st.write("**Datos de Salud Financiera**")
                st.write(f"ROE: {res['info'].get('returnOnEquity', 0):.2%} | Margen Op: {res['info'].get('operatingMargins', 0):.2%}")
                st.write(f"MOS Aplicado: {res['used_mos']:.0%}")


