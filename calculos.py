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

def classify_qs(qs):
    if qs is None: return "Unknown"
    elif qs >= 90: return "Gem 💎"
    elif qs >= 70: return "Core"
    elif qs >= 40: return "Standard"
    elif qs >= 30: return "Speculative"
    else: return "Avoid"

def run_orca_logic(ticker_symbol, discount_rate=0.15):
    stock = yf.Ticker(ticker_symbol)
    try:
        info = stock.info
        if not info or 'currentPrice' not in info:
            return {"error": f"No data found for {ticker_symbol}"}
    except:
        return {"error": "Connection Error"}

    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    
    # --- MODEL 1: DCF ---
    cf = stock.cashflow
    growth, fcf_ttm = 0, 0
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
        m, pfcf_curr = 1 + g_capped, price / (fcf_ttm / shares) if shares > 0 else 20
        pv = sum([fcf_ttm * (m**t) / ((1+discount_rate)**t) for t in range(1, 6)])
        tv = (fcf_ttm * (m**5) * pfcf_curr) / ((1+discount_rate)**5)
        intrinsic_dcf = (pv + tv) / shares

    # --- MODEL 2: MEAN REVERSION ---
    pe_curr = info.get("trailingPE", 20)
    pe_fwd = info.get("forwardPE", 15)
    pe_avg = (pe_curr + pe_fwd) / 2
    mr_intrinsic = price * (pe_avg / pe_curr) if pe_curr else price

    # --- QUALITY SCORE (QS) ---
    fs = np.mean([scale(info.get("currentRatio", 0), 0.5, 3), scale(info.get("debtToEquity", 100), 200, 0)])
    pr = np.mean([scale(info.get("returnOnEquity", 0), 0, 0.3), scale(info.get("operatingMargins", 0), 0, 0.3)])
    gr = scale(info.get("revenueGrowth", 0), -0.1, 0.3)
    qs_value = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)
    
    qs_category = classify_qs(qs_value)

    # --- FINAL INTRINSIC VALUE ---
    final_intrinsic = np.mean([v for v in [intrinsic_dcf, mr_intrinsic] if v is not None])

    # --- SIGNAL LOGIC REFINED ---
    sell_threshold = final_intrinsic * 1.20
    
    if price < final_intrinsic:
        if qs_value < 30:
            signal = "REJECTED (Avoid)"
        else:
            signal = f"BUY ({qs_category})"
    elif price < sell_threshold:
        signal = "HOLD"
    else:
        signal = "SELL"

    return {
        "price": price, "intrinsic": final_intrinsic, "dcf": intrinsic_dcf,
        "mr": mr_intrinsic, "qs": qs_value, "category": qs_category,
        "signal": signal, "sell_threshold": sell_threshold, 
        "fcf_ttm": fcf_ttm, "growth": growth, "info": info
    }
