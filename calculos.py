import yfinance as yf
import numpy as np

def get_row(df, names):
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    if value is None: return 0
    score = (value - min_val) / (max_val - min_val)
    return max(0, min(score * 100, 100))

def run_orca_logic(ticker_symbol, discount_rate=0.15, mos=0.25):
    stock = yf.Ticker(ticker_symbol)
    try:
        info = stock.info
        if not info or 'currentPrice' not in info:
            return {"error": f"No se encontró información para {ticker_symbol}"}
    except:
        return {"error": "Error de conexión con Yahoo Finance"}

    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    
    # --- FCF Growth ---
    cf = stock.cashflow
    growth = None
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        if op is not None and cap is not None:
            fcf_h = (op - cap).dropna()
            fcf_h = fcf_h[fcf_h > 0]
            if len(fcf_h) >= 2:
                growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1

    # --- FCF TTM ---
    qcf = stock.quarterly_cashflow
    fcf_ttm = None
    if not qcf.empty:
        op_q = get_row(qcf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap_q = get_row(qcf, ["Capital Expenditures", "Capital Expenditure"])
        if op_q is not None and cap_q is not None:
            fcf_ttm = op_q.iloc[:4].sum() + cap_q.iloc[:4].sum()

    # --- DCF ---
    intrinsic_dcf = None
    multiplier = None
    pfcf_used = None

    if fcf_ttm and growth is not None and shares:
        g_capped = max(0.0, min(growth, 0.10))
        multiplier = 1 + g_capped
        pfcf_used = price / (fcf_ttm / shares) if (fcf_ttm/shares) != 0 else 0
        
        pv = sum([fcf_ttm * (multiplier ** t) / ((1 + discount_rate) ** t) for t in range(1, 6)])
        terminal_value = (fcf_ttm * (multiplier ** 5) * pfcf_used) / ((1 + discount_rate) ** 5)
        intrinsic_dcf = (pv + terminal_value) / shares

    # --- Quality Score ---
    fs = np.mean([scale(info.get("currentRatio", 0), 0.5, 3), scale(info.get("debtToEquity", 100), 200, 0)])
    pr = np.mean([scale(info.get("returnOnEquity", 0), 0, 0.3), scale(info.get("operatingMargins", 0), 0, 0.3)])
    qs = (fs * 0.4) + (pr * 0.4) + (scale(info.get("revenueGrowth", 0), -0.1, 0.3) * 0.2)

    # --- Señal ---
    intrinsic = intrinsic_dcf
    signal = "N/A"
    mos_price = None

    if intrinsic:
        mos_price = intrinsic * (1 - mos)
        if price < mos_price: signal = "BUY"
        elif price < intrinsic: signal = "HOLD"
        else: signal = "SELL"

    return {
        "symbol": ticker_symbol,
        "price": price,
        "intrinsic": intrinsic,
        "mos_price": mos_price,
        "signal": signal,
        "qs": qs,
        "fcf_ttm": fcf_ttm,
        "growth": growth,
        "multiplier": multiplier,
        "pfcf": pfcf_used,
        "shares": shares,
        "info": info
    }


