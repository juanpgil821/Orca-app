import streamlit as st
from calculos import run_orca_logic

# Configuración de página para móviles
st.set_page_config(page_title="ORCA System", layout="centered")

st.title("🚢 ORCA Intrinsic System")
st.markdown("Escribe un ticker y presiona **Enter**")

# Barra lateral para ajustes rápidos
with st.sidebar:
    st.header("Ajustes de Modelo")
    disc_rate = st.slider("Tasa de Descuento", 0.05, 0.20, 0.15)
    st.info("La tasa de descuento afecta principalmente al modelo DCF.")

# Entrada de usuario
ticker_input = st.text_input("Ticker (ej: AAPL, MSFT, GOOGL)", "").upper()

if ticker_input:
    with st.spinner(f"Analizando {ticker_input}..."):
        res = run_orca_logic(ticker_input, discount_rate=disc_rate)
        
        if "error" in res:
            st.error(res["error"])
        else:
            # --- SECCIÓN DE RESULTADOS ---
            st.subheader(f"Resultados para {ticker_input}")
            
            # Fila 1: Precio y Promedio Final
            col1, col2 = st.columns(2)
            col1.metric("Precio Mercado", f"${res['price']:.2f}")
            col2.metric("Intrínseco (Promedio)", f"${res['intrinsic']:.2f}" if res['intrinsic'] else "N/A")
            
            st.divider()
            
            # Fila 2: Comparación de Modelos
            st.write("**Desglose por Modelo:**")
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Valor DCF", f"${res['dcf']:.2f}" if res['dcf'] else "N/A")
            m_col2.metric("Valor Mean Reversion", f"${res['mr']:.2f}" if res['mr'] else "N/A")
            
            # --- SEÑAL FINAL ---
            color = "green" if res['signal'] == "BUY" else "orange" if res['signal'] == "HOLD" else "red"
            st.markdown(f"### Señal Sugerida: :{color}[{res['signal']}]")
            
            st.divider()
            
            # --- QUALITY SCORE ---
            st.write(f"**ORCA Quality Score:** {res['qs']:.1f} / 100")
            st.progress(res['qs'] / 100)
            
            # --- DATOS ADICIONALES ---
            with st.expander("Ver Detalles Financieros"):
                st.write(f"**Crecimiento FCF Estimado:** {res['growth']:.2%}" if res['growth'] else "N/A")
                st.write(f"**Sector:** {res['info'].get('sector', 'N/A')}")
                st.write(f"**ROE:** {res['info'].get('returnOnEquity', 0):.2%}")
                st.write(f"**Debt to Equity:** {res['info'].get('debtToEquity', 0)}")

