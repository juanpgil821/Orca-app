import yfinance as yf
import numpy as np
import pandas as pd

def get_row(df, names):
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    if value is None or np.isnan(value): return 0
    score = (value - min_val) / (max_val - min_val)
    return max(0, min(score * 100, 100))

def run_orca_logic(ticker_symbol, discount_rate=0.15, manual_mos=0.25):
    stock = yf.Ticker(ticker_symbol)
    try:
        info = stock.info
        if not info or 'currentPrice' not in info:
            return {"error": f"No hay datos para {ticker_symbol}"}
    except:
        return {"error": "Error de conexión con Yahoo Finance"}

    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    
    # --- MODELO 1: DCF (FLUJO DE CAJA DESCONTADO) ---
    cf = stock.cashflow
    fin = stock.financials
    growth = 0
    fcf_ttm = 0
    
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        if op is not None and cap is not None:
            fcf_h = (op - cap).dropna()
            if len(fcf_h) >= 2:
                growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1
    
    qcf = stock.quarterly_cashflow
    if not qcf.empty:
        op_q = get_row(qcf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap_q = get_row(qcf, ["Capital Expenditures", "Capital Expenditure"])
        if op_q is not None and cap_q is not None:
            fcf_ttm = op_q.iloc[:4].sum() + cap_q.iloc[:4].sum()

    intrinsic_dcf = None
    if fcf_ttm and shares:
        g_capped = max(0.0, min(growth if growth else 0, 0.10))
        m = 1 + g_capped
        pfcf_curr = price / (fcf_ttm / shares) if shares > 0 else 20
        pv = sum([fcf_ttm * (m**t) / ((1+discount_rate)**t) for t in range(1, 6)])
        tv = (fcf_ttm * (m**5) * pfcf_curr) / ((1+discount_rate)**5)
        intrinsic_dcf = (pv + tv) / shares

    # --- MODELO 2: MEAN REVERSION (MR) - LÓGICA SHEETS ---
    # B12: Promedios de la Acción (Triple Métrica)
    pe_curr = info.get("trailingPE")
    pfcf_curr = price / (fcf_ttm / shares) if (fcf_ttm and shares) else None
    evebit_curr = info.get("enterpriseValue", 0) / info.get("ebitda", 1) # Proxy de EBIT
    
    # Promedios históricos (Proxy 5 años usando forward/actual/industria)
    pe_avg = (info.get("trailingPE", 15) + info.get("forwardPE", 15)) / 2
    pfcf_avg = 18.0 # Promedio estándar si no hay historial
    evebit_avg = 12.0 # Promedio estándar si no hay historial

    mr_pe = price * (pe_avg / pe_curr) if pe_curr else price
    mr_pfcf = price * (pfcf_avg / pfcf_curr) if pfcf_curr else price
    mr_evebit = price * (evebit_avg / evebit_curr) if evebit_curr else price
    
    b12_stock_mr = np.mean([mr_pe, mr_pfcf, mr_evebit])
    
    # D12: Promedio del Sector
    sector_pe = info.get("industryTrailingPE", pe_avg)
    d12_sector_mr = price * (sector_pe / pe_curr) if pe_curr else price
    
    # Fórmula Final MR: (B12 * 0.7) + (D12 * 0.3)
    final_mr = (b12_stock_mr * 0.7) + (d12_sector_mr * 0.3)

    # --- QUALITY SCORE (QS) ---
    fs = np.mean([scale(info.get("currentRatio", 0), 0.5, 3), scale(info.get("debtToEquity", 100), 200, 0)])
    pr = np.mean([scale(info.get("returnOnEquity", 0), 0, 0.3), scale(info.get("operatingMargins", 0), 0, 0.3)])
    gr = scale(info.get("revenueGrowth", 0), -0.1, 0.3)
    qs = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)

    # --- SELECCIÓN FINAL ---
    final_intrinsic = np.mean([v for v in [intrinsic_dcf, final_mr] if v is not None])
    
    # MOS Dinámico basado en QS
    dynamic_mos = 0.10 if qs > 85 else 0.20 if qs > 65 else 0.30
    used_mos = max(dynamic_mos, manual_mos)
    mos_price = final_intrinsic * (1 - used_mos)
    
    signal = "SELL"
    if price < mos_price: signal = "BUY"
    elif price < final_intrinsic: signal = "HOLD"

    return {
        "price": price, "intrinsic": final_intrinsic, "dcf": intrinsic_dcf,
        "mr": final_mr, "mr_stock": b12_stock_mr, "mr_sector": d12_sector_mr,
        "qs": qs, "signal": signal, "mos_price": mos_price, "used_mos": used_mos,
        "fcf_ttm": fcf_ttm, "growth": growth, "info": info
    }


