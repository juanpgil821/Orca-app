import streamlit as st
from calculos import run_orca_logic

st.set_page_config(page_title="ORCA Intrinsic System", layout="wide")

# --- SIDEBAR AJUSTABLE ---
st.sidebar.header("🛠️ Parámetros de Modelo")
st.sidebar.markdown("Ajusta las variables de riesgo:")

discount_rate = st.sidebar.slider("Tasa de Descuento (Exigencia)", 0.05, 0.25, 0.15, 0.01)
manual_mos = st.sidebar.slider("Margen de Seguridad (Manual)", 0.05, 0.50, 0.25, 0.05)

st.sidebar.divider()
st.sidebar.caption("ORCA v2.0 - Basado en análisis fundamental TTM.")

# --- CUERPO PRINCIPAL ---
st.title("🚢 ORCA Intrinsic System")
ticker_input = st.text_input("Ticker de la empresa (Presiona Enter):", "").upper()

if ticker_input:
    with st.spinner(f"Procesando {ticker_input}..."):
        res = run_orca_logic(ticker_input, discount_rate=discount_rate, mos=manual_mos)
        
        if "error" in res:
            st.error(res["error"])
        else:
            # --- SECCIÓN 1: MÉTRICAS CLAVE ---
            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"${res['price']:.2f}")
            c2.metric("Intrínseco", f"${res['intrinsic']:.2f}" if res['intrinsic'] else "N/A")
            c3.metric("Precio MOS", f"${res['mos_price']:.2f}" if res['mos_price'] else "N/A")
            
            color = "green" if res['signal'] == "BUY" else "orange" if res['signal'] == "HOLD" else "red"
            c4.subheader(f"Señal: :{color}[{res['signal']}]")

            # --- SECCIÓN 2: VARIABLES DEL CÁLCULO ---
            st.subheader("📊 Variables Utilizadas en DCF")
            v1, v2, v3, v4 = st.columns(4)
            
            with v1:
                st.write("**FCF TTM**")
                st.write(f"${res['fcf_ttm']:,.0f}" if res['fcf_ttm'] else "N/A")
            with v2:
                st.write("**CAGR (FCF)**")
                st.write(f"{res['growth']:.2%}" if res['growth'] else "N/A")
            with v3:
                st.write("**Multiplicador**")
                st.write(f"{res['multiplier']:.3f}" if res['multiplier'] else "N/A")
            with v4:
                st.write("**P/FCF Actual**")
                st.write(f"{res['pfcf']:.2f}" if res['pfcf'] else "N/A")

            # --- SECCIÓN 3: CALIDAD Y SALUD ---
            st.divider()
            st.subheader(f"🛡️ Quality Score: {res['qs']:.1f} / 100")
            st.progress(res['qs'] / 100)
            
            with st.expander("Métricas de Salud y Rentabilidad (Info Extra)"):
                e1, e2, e3 = st.columns(3)
                e1.write(f"**Debt to Equity:** {res['info'].get('debtToEquity', 'N/A')}")
                e1.write(f"**Current Ratio:** {res['info'].get('currentRatio', 'N/A')}")
                
                e2.write(f"**ROE:** {res['info'].get('returnOnEquity', 'N/A')}")
                e2.write(f"**Op. Margins:** {res['info'].get('operatingMargins', 'N/A')}")
                
                e3.write(f"**Sector:** {res['info'].get('sector', 'N/A')}")
                e3.write(f"**Shares Out:** {res['shares']:,.0f}" if res['shares'] else "N/A")
