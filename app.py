import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ORCA Terminal", page_icon="🐋", layout="wide")

# Estilo visual
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE DESCARGA ROBUSTA ---
@st.cache_data(ttl=3600)
def fetch_orca_data(symbol):
    try:
        # Usamos una sesión con un "User-Agent" de navegador real
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        ticker = yf.Ticker(symbol, session=session)
        
        # Intentamos obtener el precio de varias formas
        info = ticker.info
        hist_1d = ticker.history(period="1d")
        
        if hist_1d.empty and (not info or 'currentPrice' not in info):
            return None
            
        price = info.get("currentPrice") if info and 'currentPrice' in info else hist_1d['Close'].iloc[-1]
        name = info.get("shortName", symbol) if info else symbol
        
        # Obtener fundamentales
        financials = ticker.financials
        cashflow = ticker.cashflow
        hist_5y = ticker.history(period="5y")

        # --- LÓGICA QUALITY SCORE (Celda 11) ---
        roe = info.get("returnOnEquity", 0.1) if info else 0.1
        margin = info.get("operatingMargins", 0.1) if info else 0.1
        debt = (info.get("debtToEquity", 100) / 100) if info else 1.0
        
        def scale_val(v, mi, ma):
            return max(0, min((v - mi) / (ma - mi), 1)) * 100

        qs = round((scale_val(roe, 0, 0.3)*0.4 + scale_val(margin, 0, 0.3)*0.4 + scale_val(3-debt, 0, 3)*0.2), 2)

        # --- LÓGICA VALOR INTRÍNSECO (Simplificada para estabilidad) ---
        shares = info.get("sharesOutstanding") if info else None
        
        # Si no hay flujos de caja o acciones, hacemos una estimación basada en múltiplos
        intrinsic_base = price * 1.2 
        
        if shares and not cashflow.empty:
            try:
                # Intentamos buscar OCF y CapEx
                ocf = None
                for k in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                    if k in cashflow.index: ocf = cashflow.loc[k].iloc[0]; break
                
                capex = None
                for k in ["Capital Expenditure", "Capital Expenditures"]:
                    if k in cashflow.index: capex = cashflow.loc[k].iloc[0]; break
                
                if ocf is not None and capex is not None:
                    fcf = ocf + capex
                    # DCF a 5 años
                    intrinsic_base = ((fcf * 1.05 * 5) + (fcf * 15)) / shares
            except:
                pass

        return {
            "name": name,
            "price": price,
            "intrinsic": intrinsic_base,
            "qs": qs,
            "history": hist_5y,
            "info": info if info else {}
        }
    except Exception as e:
        return None

# --- INTERFAZ ---
st.title("🐋 ORCA: Intrinsic Intelligence")

with st.sidebar:
    st.header("Control")
    ticker_input = st.text_input("Ticker", "AAPL").upper()
    disc_rate = st.slider("Tasa Descuento (%)", 5, 20, 15)
    st.warning("Si da error, espera 10 segundos y vuelve a intentar. Yahoo limita las peticiones.")

if ticker_input:
    data = fetch_orca_data(ticker_input)
    
    if data:
        col1, col2, col3 = st.columns(3)
        col1.metric("Precio Actual", f"${data['price']:.2f}")
        
        # Margen de seguridad dinámico
        margin_adj = 0.9 if data['qs'] > 75 else 0.75
        val_final = data['intrinsic'] * margin_adj
        upside = ((val_final / data['price']) - 1) * 100
        
        col2.metric("Valor Intrínseco", f"${val_final:.2f}", f"{upside:.2f}%")
        
        if upside > 10:
            status, color = "COMPRA", "#00ff88"
        elif upside < -10: status, color = "VENTA", "#ff4b4b"
        else: status, color = "HOLD", "#ffaa00"
            
        col3.markdown(f"<h3 style='text-align:center;'>Señal:<br><span style='color:{color}'>{status}</span></h3>", unsafe_allow_html=True)

        st.write(f"**ORCA Quality Score: {data['qs']}/100**")
        st.progress(data['qs'] / 100)
        st.area_chart(data['history']['Close'])
    else:
        st.error(f"Yahoo Finance bloqueó la conexión para {ticker_input}. Esto es normal en servidores gratuitos. Intenta de nuevo en unos segundos.")
