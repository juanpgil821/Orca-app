import streamlit as st
from calculos import run_orca_logic

# Configuración de la página
st.set_page_config(page_title="ORCA System", layout="wide", page_icon="🚢")

@st.cache_data(ttl=600)
def get_cached_orca_data(ticker, disc_rate):
    return run_orca_logic(ticker, disc_rate)

# Sidebar
st.sidebar.title("ORCA Settings")
disc_rate = st.sidebar.slider("Discount Rate (DCF)", 0.05, 0.25, 0.15)
st.sidebar.caption("Higher rate = more conservative valuation.")

# Encabezado
st.title("🚢 ORCA: Advanced Intrinsic Analytics")
st.caption("Objective Risk & Capital Allocation System")

ticker = st.text_input("Enter Ticker Symbol:", "").upper()

if ticker:
    res = get_cached_orca_data(ticker, disc_rate)
    
    if "error" in res:
        st.error(res["error"])
    else:
        # Fila 1: Estado de Mercado
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Market Price", f"${res['price']:.2f}")
        c2.metric("Intrinsic Value", f"${res['intrinsic']:.2f}")
        
        color = "red" if "REJECTED" in res['signal'] else "green" if "BUY" in res['signal'] else "orange" if res['signal'] == "HOLD" else "red"
        c3.markdown(f"### Signal: :{color}[{res['signal']}]")

        # --- ORCA INTELLIGENCE: MATRIZ DE DIAGNÓSTICO ROBUSTA ---
        alerts = []
        
        # 1. ESCENARIOS DE EXCELENCIA (ELITE)
        if res['margins'] > 0.30 and res['roe'] > 0.30:
            if res['debt_to_equity'] < 100:
                alerts.append("💎 **Wide Moat Gem:** Márgenes y ROE de élite con deuda baja. Un negocio con ventajas competitivas estructurales.")
            else:
                alerts.append("✨ **High-Quality Compounder:** Retornos excepcionales sobre el capital. La deuda está totalmente justificada por la rentabilidad.")

        if res['buyback_yield'] > 0.05:
            alerts.append(f"🐂 **Shareholder Yield Alpha:** Recompra de acciones masiva ({res['buyback_yield']:.1%}). La directiva está canibalizando acciones a favor del accionista.")

        # 2. ESCENARIOS ZOMBIE Y DETERIORO (Caso LZMH y similares)
        if res['fcf_ttm'] <= 0 and res['margins'] <= 0:
            alerts.append("💀 **Zombie Company Alert:** Ni flujo de caja ni margen operativo. El negocio base está quemando dinero sin retorno.")
        
        if res['roe'] < 0:
            alerts.append(f"🚨 **Capital Destroyer:** ROE negativo ({res['roe']:.1%}). La empresa está diluyendo o consumiendo el patrimonio del accionista.")

        # 3. ESCENARIOS DE CONTRADICCIÓN (INGENIERÍA FINANCIERA)
        if res['roe'] > 0.50 and res['debt_to_equity'] > 250:
            alerts.append(f"🧪 **Leveraged ROE:** Este ROE tan alto no es eficiencia operativa, es el resultado de un balance sobreapalancado. Riesgo de fragilidad.")
        
        if res['rev_growth'] > 0.20 and res['fcf_ttm'] < 0:
            alerts.append("🚀 **Growth Burn:** Crecimiento agresivo de ingresos a costa de quemar caja masivamente. Típico de empresas que necesitan capital externo constante.")

        # 4. ESCENARIOS DE LIQUIDEZ Y EFICIENCIA (STRESS ANALYTICS)
        if res['curr_ratio'] < 0.9:
            if res['fcf_ttm'] > 2_000_000_000:
                alerts.append(f"🔄 **Negative Working Capital King:** CR bajo ({res['curr_ratio']:.2f}) pero con caja masiva. La empresa cobra antes de pagar a proveedores (Modelo Costco/Apple).")
            else:
                alerts.append(f"📉 **Liquidity Trap:** Ratio de liquidez peligroso ({res['curr_ratio']:.2f}). No hay flujo de caja suficiente para cubrir deudas de corto plazo.")

        if res['curr_ratio'] > 1.2 and res['fcf_ttm'] < 0:
            alerts.append("🌫️ **False Safety:** El ratio de liquidez se ve bien, pero la empresa está perdiendo caja operativa. Es una seguridad temporal.")

        # 5. ESCENARIOS DE DEUDA Y MÁRGENES
        if res['debt_to_equity'] > 200:
            if res['margins'] > 0.20:
                alerts.append(f"🏢 **Managed Leverage:** Deuda alta, pero los márgenes ({res['margins']:.1%}) son el escudo protector contra intereses.")
            else:
                alerts.append("🚨 **Extreme Debt Stress:** Alta deuda con márgenes pobres. La empresa es un esclavo de sus acreedores.")

        # 6. ESCENARIOS DE EFICIENCIA OPERATIVA
        if res['rev_growth'] < 0 and res['earn_growth'] > 0:
            alerts.append("✂️ **Margin Expansion Play:** Ganando más dinero con menos ventas. Indica un recorte de costos brutal o mayor eficiencia.")

        # Despliegue de Alertas
        if alerts:
            with st.expander("🔍 ORCA Intelligence: Risk & Quality Diagnosis", expanded=True):
                for a in alerts:
                    if any(icon in a for icon in ["💎", "✨", "🐂", "🔄", "✂️"]):
                        st.info(a)
                    elif any(icon in a for icon in ["⚠️", "🧪", "🚀", "🌫️"]):
                        st.warning(a)
                    else:
                        st.error(a)

        # Fila 2: Modelos de Valuación
        st.subheader("🛠️ Valuation Models")
        m1, m2, m3 = st.columns(3)
        m1.write(f"**DCF (Cash Flow):** ${res['dcf']:.2f}" if res['dcf'] else "**DCF:** N/A")
        m2.write(f"**MR (Mean Reversion):** ${res['mr']:.2f}")
        m3.write(f"**Hold/Sell Threshold:** ${res['sell_threshold']:.2f}")

        # Fila 3: Métricas y Exposición
        st.divider()
        col_qs, col_metrics, col_exposure = st.columns([1, 1.8, 1.2])
        
        with col_qs:
            st.subheader(f"🛡️ QS: {res['qs']:.1f}")
            st.progress(res['qs']/100)
            st.caption(f"Asset Tier: **{res['category']}**")

        with col_metrics:
            st.markdown("### 📊 Fundamental Analytics")
            ma1, ma2 = st.columns(2)
            with ma1:
                st.write("**Solvency & Efficiency**")
                st.write(f"Current Ratio: `{res['curr_ratio']:.2f}`")
                st.write(f"Debt to Equity: `{res['debt_to_equity']:.2f}%`")
                st.write(f"ROE: `{res['roe']:.2%}`")
                st.write(f"Op. Margins: `{res['margins']:.2%}`")
            with ma2:
                st.write("**Growth & Cash Flow**")
                st.write(f"Revenue Growth: `{res['rev_growth']:.2%}`")
                st.write(f"Earnings Growth: `{res['earn_growth']:.2%}`")
                st.write(f"FCF TTM: `${res['fcf_ttm']:,.0f}`")
                st.write(f"FCF CAGR: `{res['growth']:.2%}`")

        with col_exposure:
            st.markdown("### 🧱 Recommended Exposure")
            weights = {"Gem 💎": "15%", "Core": "10%", "Standard": "5%", "Speculative": "2%", "Avoid": "0%"}
            max_w = weights.get(res['category'], "0%")
            st.markdown(f"**Max Weight per Position:** `{max_w}`")
            
            tier_limit = {"Gem 💎": "60%", "Core": "50%", "Standard": "30%", "Speculative": "10%", "Avoid": "0%"}
            st.info(f"**Portfolio Limit ({res['category']}):** {tier_limit.get(res['category'], '0%')}")

else:
    st.info("Enter a ticker symbol to start analysis.")


