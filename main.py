import streamlit as st

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="ORCA Command Center 2.0", layout="wide")

st.title("🚢 ORCA 2.0: Terminal de Ejecución")
st.info("Introduce los datos validados desde tu Google Sheets para obtener el veredicto de compra.")

# --- ENTRADA DE DATOS (INPUTS DE SHEETS) ---
with st.sidebar:
    st.header("📥 Datos de Sheets")
    ticker = st.text_input("Ticker", value="ADBE").upper()
    precio_mercado = st.number_input("Precio Actual de Mercado ($)", min_value=0.0, step=0.01)
    
    st.markdown("---")
    # Estos tres vienen directo de tus celdas en Sheets
    val_dcf = st.number_input("Valor DCF (Sheets)", min_value=0.0, step=0.01)
    val_mr = st.number_input("Valor Mean Reversion (Sheets)", min_value=0.0, step=0.01)
    qs_sheets = st.slider("Quality Score (Sheets)", 0, 100, 75)

# --- LÓGICA DE EJECUCIÓN (FÓRMULA B) ---
# Promedio simple de tus dos modelos de valoración
valor_intrinseco_base = (val_dcf + val_mr) / 2 if (val_dcf > 0 and val_mr > 0) else max(val_dcf, val_mr)

# Aplicación del Factor de Confianza Equilibrado (Opción B)
factor_orca = 0.5 + (qs_sheets / 100) * 0.5
precio_compra_orca = valor_intrinseco_base * factor_orca

# --- VISUALIZACIÓN DE RESULTADOS ---
if precio_mercado > 0 and valor_intrinseco_base > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Valor Intrínseco (Promedio)", f"${valor_intrinseco_base:.2f}")
    
    with col2:
        st.metric("Factor de Seguridad (B)", f"{factor_orca:.3f}", help="0.5 + (QS/100 * 0.5)")
        
    with col3:
        # El delta muestra qué tan lejos está el precio de compra del precio actual
        upside = ((precio_compra_orca / precio_mercado) - 1) * 100
        st.metric("Precio de Compra ORCA", f"${precio_compra_orca:.2f}", delta=f"{upside:.1f}% vs Mercado")

    st.markdown("---")

    # --- VEREDICTO FINAL ---
    st.subheader("📢 Veredicto de la Operación")
    
    if precio_mercado <= precio_compra_orca:
        st.success(f"💎 SEÑAL DE COMPRA: El precio actual (${precio_mercado}) está por debajo de tu zona de seguridad ajustada por calidad.")
    elif precio_mercado <= valor_intrinseco_base:
        st.warning(f"⚖️ ZONA DE ESPERA: Está por debajo del intrínseco, pero la calidad ({qs_sheets} QS) exige un descuento mayor para ser una compra segura.")
    else:
        st.error(f"🚫 SOBREVALORADA: El mercado está pagando un premium excesivo sobre el valor real de la empresa.")

else:
    st.warning("Faltan datos. Asegúrate de que el Precio de Mercado y al menos un modelo de valoración (DCF/MR) sean mayores a cero.")


