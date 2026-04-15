import streamlit as st
from calculos import run_orca_logic

# Configuración para que se vea bien en móviles
st.set_page_config(page_title="ORCA Finder", layout="centered")

st.title("🚢 ORCA Intrinsic System")
st.markdown("Introduce un ticker y presiona **Enter** para analizar.")

# Campo de entrada
ticker_input = st.text_input("Ticker de la empresa (ej: TSLA, AAPL, MSFT)", "").upper()

# Lógica de la App
if ticker_input:
    with st.spinner(f"Calculando valor de {ticker_input}..."):
        res = run_orca_logic(ticker_input)
        
        if "error" in res:
            st.error(res["error"])
        else:
            # --- RESUMEN VISUAL ---
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Precio de Mercado", f"${res['price']:.2f}")
                st.write(f"**Sector:** {res['info'].get('sector', 'N/A')}")

            with col2:
                if res['intrinsic']:
                    st.metric("Valor Intrínseco", f"${res['intrinsic']:.2f}")
                else:
                    st.write("Valor Intrínseco: N/A (Faltan datos)")

            # --- SEÑAL Y CALIDAD ---
            color = "green" if res['signal'] == "BUY" else "orange" if res['signal'] == "HOLD" else "red"
            st.subheader(f"Señal sugerida: :{color}[{res['signal']}]")
            
            st.divider()
            st.write(f"**ORCA Quality Score:** {res['qs']:.1f} / 100")
            st.progress(res['qs'] / 100)
            
            # --- DETALLES EXTRA ---
            with st.expander("Ver métricas de salud financiera"):
                st.write(f"Debt to Equity: {res['info'].get('debtToEquity')}")
                st.write(f"ROE: {res['info'].get('returnOnEquity')}")
                st.write(f"Current Ratio: {res['info'].get('currentRatio')}")

