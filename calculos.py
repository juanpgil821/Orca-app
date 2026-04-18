import yfinance as yf
import numpy as np

def get_row(df, names):
    for n in names:
        if n in df.index: return df.loc[n]
    return None

def scale(value, min_val, max_val):
    try:
        if value is None or not isinstance(value, (int, float, np.number)): 
            return 0
        if min_val == max_val: return 0
        score = (value - min_val) / (max_val - min_val)
        return max(0, min(score * 100, 100))
    except:
        return 0

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
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

    price = info.get("currentPrice", 0)
    shares = info.get("sharesOutstanding", 0)
    
    # --- MODELO 1: DCF (FLUJO DE CAJA DESCONTADO) ---
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
    if fcf_ttm and shares and shares > 0:
        g_capped = max(0.0, min(growth if growth else 0, 0.10))
        pfcf_curr = price / (fcf_ttm / shares) if (fcf_ttm / shares) != 0 else 20
        pv = sum([fcf_ttm * ((1 + g_capped)**t) / ((1 + discount_rate)**t) for t in range(1, 6)])
        tv = (fcf_ttm * ((1 + g_capped)**5) * pfcf_curr) / ((1 + discount_rate)**5)
        intrinsic_dcf = (pv + tv) / shares

    # --- MODELO 2: MEAN REVERSION (DINÁMICO Y ESTABILIZADO) ---
    eps_ttm = info.get("trailingEps")
    pe_curr = info.get("trailingPE")
    pe_fwd = info.get("forwardPE")

    # Validación real de datos: Evitamos promedios arbitrarios (15/20)
    pe_avg = None
    if pe_curr and pe_fwd:
        pe_avg = (pe_curr + pe_fwd) / 2
    elif pe_curr:
        pe_avg = pe_curr
    elif pe_fwd:
        pe_avg = pe_fwd

    # Cálculo basado puramente en Earnings (Independiente del precio actual)
    mr_intrinsic = None
    if eps_ttm and eps_ttm > 0 and pe_avg:
        mr_intrinsic = eps_ttm * pe_avg

    # --- PROTECCIÓN Y LIMPIEZA DE MÉTRICAS ---
    def safe_num(key):
        val = info.get(key, 0)
        return val if isinstance(val, (int, float, np.number)) and val is not None else 0

    curr_ratio = safe_num("currentRatio")
    d_to_e = safe_num("debtToEquity")
    roe = safe_num("returnOnEquity")
    op_margins = safe_num("operatingMargins")
    rev_growth = safe_num("revenueGrowth")
    earn_growth = safe_num("earningsGrowth")

    # --- QUALITY SCORE (QS) ---
    def safe_mean(values):
        clean = [v for v in values if v is not None]
        return np.mean(clean) if clean else 0

    fs = safe_mean([scale(curr_ratio, 0.5, 3), scale(d_to_e, 200, 0)])
    pr = safe_mean([scale(roe, 0, 0.3), scale(op_margins, 0, 0.3)])
    gr = safe_mean([scale(rev_growth, -0.1, 0.3), scale(earn_growth, -0.1, 0.3)])
    
    qs_value = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)
    qs_category = classify_qs(qs_value)

    # --- VALUACIÓN FINAL (PROMEDIO DE MODELOS VÁLIDOS) ---
    valid_models = [v for v in [intrinsic_dcf, mr_intrinsic] if v is not None and v > 0]
    
    if valid_models:
        final_intrinsic = np.mean(valid_models)
    else:
        # Si no hay modelos válidos, usamos el precio como base neutral
        final_intrinsic = price

    # --- SEÑAL DE ACCIÓN ---
    sell_threshold = final_intrinsic * 1.20
    if price < final_intrinsic:
        signal = "REJECTED (Avoid)" if qs_value < 30 else f"BUY ({qs_category})"
    elif price < sell_threshold:
        signal = "HOLD"
    else:
        signal = "SELL"

    return {
        "price": price, "intrinsic": final_intrinsic, "dcf": intrinsic_dcf,
        "mr": mr_intrinsic, "qs": qs_value, "category": qs_category,
        "signal": signal, "sell_threshold": sell_threshold, 
        "fcf_ttm": fcf_ttm, "growth": growth, 
        "curr_ratio": curr_ratio, "debt_to_equity": d_to_e,
        "rev_growth": rev_growth, "earn_growth": earn_growth,
        "roe": roe, "margins": op_margins
    }

