import yfinance as yf
import numpy as np
import pandas as pd

def get_row(df, names):
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    if value is None: return 0
    score = (value - min_val) / (max_val - min_val)
    return max(0, min(score * 100, 100))

def run_orca_logic(ticker_symbol, discount_rate=0.15, mos=0.25):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info or 'currentPrice' not in info:
            return {"error": f"No hay datos para {ticker_symbol}"}
    except:
        return {"error": "Error de conexión"}

    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    
    # --- MODELO 1: DCF ---
    cf = stock.cashflow
    growth = None
    fcf_ttm = None
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        if op is not None and cap is not None:
            fcf_h = (op - cap).dropna()
            fcf_h = fcf_h[fcf_h > 0]
            if len(fcf_h) >= 2:
                growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1
    
    qcf = stock.quarterly_cashflow
    if not qcf.empty:
        op_q = get_row(qcf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap_q = get_row(qcf, ["Capital Expenditures", "Capital Expenditure"])
        if op_q is not None and cap_q is not None:
            fcf_ttm = op_q.iloc[:4].sum() + cap_q.iloc[:4].sum()

    intrinsic_dcf = None
    if fcf_ttm and growth is not None and shares:
        g_capped = max(0.0, min(growth, 0.10))
        m = 1 + g_capped
        pfcf_curr = price / (fcf_ttm / shares) if (fcf_ttm/shares) != 0 else 0
        pv = sum([fcf_ttm * (m**t) / ((1+discount_rate)**t) for t in range(1, 6)])
        tv = (fcf_ttm * (m**5) * pfcf_curr) / ((1+discount_rate)**5)
        intrinsic_dcf = (pv + tv) / shares

    # --- MODELO 2: MEAN REVERSION (RESTAURADO) ---
    mr_intrinsic = None
    mr_values = []
    
    # 1. Reversión por P/E
    curr_pe = info.get("trailingPE")
    # Estimamos un PE promedio histórico (yfinance no da el historial de PE directo, 
    # pero usamos el forward vs trailing como proxy de reversión)
    fwd_pe = info.get("forwardPE")
    if curr_pe and fwd_pe:
        pe_avg = (curr_pe + fwd_pe) / 2
        mr_values.append(price * (pe_avg / curr_pe))

    # 2. Reversión por FCF (P/FCF)
    if fcf_ttm and shares:
        current_pfcf = price / (fcf_ttm / shares)
        # Usamos 20 como un P/FCF estándar de mercado para promediar si no hay historial
        mr_values.append(price * (15.0 / current_pfcf) if current_pfcf != 0 else price)

    if mr_values:
        mr_intrinsic = np.mean(mr_values)

    # --- QUALITY SCORE ---
    fs = np.mean([scale(info.get("currentRatio", 0), 0.5, 3), scale(info.get("debtToEquity", 100), 200, 0)])
    pr = np.mean([scale(info.get("returnOnEquity", 0), 0, 0.3), scale(info.get("operatingMargins", 0), 0, 0.3)])
    qs = (fs * 0.4) + (pr * 0.4) + (scale(info.get("revenueGrowth", 0), -0.1, 0.3) * 0.2)

    # --- FINAL SIGNAL ---
    candidates = [v for v in [intrinsic_dcf, mr_intrinsic] if v is not None]
    final_intrinsic = np.mean(candidates) if candidates else None
    
    signal = "N/A"
    if final_intrinsic:
        # Margen de seguridad dinámico basado en tu Celda 13
        margin = 0.90 if qs > 95 else 0.80 if qs >= 80 else 0.70
        adjusted_intrinsic = final_intrinsic * margin
        
        if adjusted_intrinsic >= price * 1.10: signal = "BUY"
        elif adjusted_intrinsic <= price * 0.80: signal = "SELL"
        else: signal = "HOLD"

    return {
        "symbol": ticker_symbol, "price": price, "intrinsic": final_intrinsic,
        "dcf": intrinsic_dcf, "mr": mr_intrinsic, "signal": signal,
        "qs": qs, "growth": growth, "info": info
    }

