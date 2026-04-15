import streamlit as st
from calculos import run_orca_logic

# 1. Configuración de la página (Optimizada para vista móvil)
st.set_page_config(
    page_title="ORCA Intrinsic System", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# 2. Encabezado principal
st.title("🚢 ORCA Intrinsic System")
st.markdown("Analizador de valor real basado en fundamentos.")

# 3. Barra lateral para ajustes técnicos
with st.sidebar:
    st.header("Configuración del Modelo")
    disc_rate = st.slider("Tasa de Descuento (DCF)", 0.05, 0.20, 0.15, step=0.01)
    st.info("Ajusta la tasa de retorno exigida. A mayor tasa, más conservador es el valor DCF.")

# 4. Entrada de Ticker
ticker_input = st.text_input("Ingresa el Ticker y presiona Enter:", placeholder="ej: AAPL, TSLA, MSFT").upper()

if ticker_input:
    with st.spinner(f"Extrayendo datos y procesando {ticker_input}..."):
        # Llamada a la lógica en calculos.py
        res = run_orca_logic(ticker_input, discount_rate=disc_rate)
        
        if "error" in res:
            st.error(res["error"])
        else:
            # --- SECCIÓN DE RESULTADOS PRINCIPALES ---
            st.subheader(f"Análisis de {ticker_input}")
            
            col1, col2 = st.columns(2)
            
            # Precio actual de mercado
            price = res.get('price')
            col1.metric("Precio Mercado", f"${price:.2f}" if price else "N/A")
            
            # Valor intrínseco promedio
            intrinsic = res.get('intrinsic')
            col2.metric("Valor Intrínseco", f"${intrinsic:.2f}" if intrinsic else "N/A")
            
            st.divider()

            # --- SECCIÓN DE MODELOS INDIVIDUALES ---
            st.write("**Desglose por Metodología:**")
            m_col1, m_col2 = st.columns(2)
            
            dcf_val = res.get('dcf')
            m_col1.metric("Modelo DCF", f"${dcf_val:.2f}" if dcf_val else "N/A")
            
            mr_val = res.get('mr')
            m_col2.metric("Modelo MR", f"${mr_val:.2f}" if mr_val else "N/A")

            # --- SEÑAL DE ACCIÓN ---
            signal = res.get('signal', 'N/A')
            color_map = {"BUY": "green", "HOLD": "orange", "SELL": "red"}
            signal_color = color_map.get(signal, "gray")
            
            st.markdown(f"### Señal Sugerida: :{signal_color}[{signal}]")
            
            st.divider()

            # --- QUALITY SCORE ---
            qs = res.get('qs', 0)
            st.write(f"**ORCA Quality Score:** {qs:.1f} / 100")
            st.progress(min(max(qs / 100, 0.0), 1.0))

            # --- DETALLES FINANCIEROS (CON VALIDACIÓN ANTI-ERROR) ---
            with st.expander("Ver Detalles y Salud Financiera"):
                # Validación segura para Crecimiento
                g_val = res.get('growth')
                g_text = f"{g_val:.2%}" if isinstance(g_val, (float, int)) else "N/A"
                
                # Validación segura para ROE
                roe_val = res.get('info', {}).get('returnOnEquity')
                roe_text = f"{roe_val:.2%}" if isinstance(roe_val, (float, int)) else "N/A"
                
                # Otros datos
                sector = res.get('info', {}).get('sector', 'N/A')
                debt_eq = res.get('info', {}).get('debtToEquity', 'N/A')
                
                st.write(f"**Sector:** {sector}")
                st.write(f"**Crecimiento FCF (CAGR):** {g_text}")
                st.write(f"**ROE:** {roe_text}")
                st.write(f"**Debt to Equity:** {debt_eq}")

# 5. Pie de página simple
st.caption("Datos provistos por Yahoo Finance vía yfinance.")
