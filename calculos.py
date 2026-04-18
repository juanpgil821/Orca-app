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
    
    # --- MODELO 1: DCF (FLUJO DE CAJA) ---
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
        # Usamos el P/FCF actual pero limitado a un rango lógico para evitar distorsiones
        pfcf_curr = price / (fcf_ttm / shares) if (fcf_ttm / shares) != 0 else None
        
        if pfcf_curr:
            pv = sum([fcf_ttm * ((1 + g_capped)**t) / ((1 + discount_rate)**t) for t in range(1, 6)])
            tv = (fcf_ttm * ((1 + g_capped)**5) * pfcf_curr) / ((1 + discount_rate)**5)
            intrinsic_dcf = (pv + tv) / shares

    # --- MODELO 2: FUNDAMENTAL VALUATION (ANTI-VALS) ---
    # Usamos el Forward EPS (proyectado) y el Forward PE (múltiplo objetivo de analistas)
    # Estas métricas son mucho más estables que el precio por minuto.
    eps_fwd = info.get("forwardEps")
    pe_target = info.get("forwardPE")
    
    mr_intrinsic = None
    if eps_fwd and eps_fwd > 0 and pe_target and pe_target > 0:
        # El valor es lo que se espera que gane por lo que el mercado está dispuesto a pagar (Forward)
        mr_intrinsic = eps_fwd * pe_target

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
        final_intrinsic = price # Sin datos suficientes, no hay juicio

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

