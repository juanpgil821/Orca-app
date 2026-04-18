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
    if qs >= 90: return "Gem 💎"
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
    
    # --- MODELO 1: DCF (Detección de FCF Crítico) ---
    cf = stock.cashflow
    growth, fcf_ttm = 0, 0
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        if op is not None and cap is not None:
            fcf_h = (op + cap).dropna()
            if len(fcf_h) >= 2:
                try:
                    # Si el FCF inicial es <= 0, el CAGR no es calculable linealmente
                    if fcf_h.iloc[-1] > 0:
                        growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1
                    else:
                        growth = -0.50 # Penalización por histórico negativo
                except:
                    growth = 0
            fcf_ttm = fcf_h.iloc[:4].sum() if len(fcf_h) >= 1 else 0

    # --- MODELO 2: MEAN REVERSION ---
    eps_ttm = info.get("trailingEps", 0)
    pe_curr = info.get("trailingPE", 20)
    pe_fwd = info.get("forwardPE", 15)
    pe_avg = (pe_curr + pe_fwd) / 2 if (pe_curr and pe_fwd) else 20
    mr_intrinsic = eps_ttm * pe_avg if eps_ttm and eps_ttm > 0 else 0

    # --- MÉTRICAS DE SALUD FINANCIERA ---
    def safe_num(key):
        val = info.get(key, 0)
        return val if isinstance(val, (int, float, np.number)) and val is not None else 0

    curr_ratio = safe_num("currentRatio")
    debt_to_equity = safe_num("debtToEquity")
    roe = safe_num("returnOnEquity")
    margins = safe_num("operatingMargins")
    rev_growth = safe_num("revenueGrowth")
    earn_growth = safe_num("earningsGrowth")

    # --- QUALITY SCORE (QS) ---
    fs = np.mean([scale(curr_ratio, 0.5, 3), scale(debt_to_equity, 200, 0)])
    pr = np.mean([scale(roe, 0, 0.3), scale(margins, 0, 0.3)])
    gr = np.mean([scale(rev_growth, -0.1, 0.3), scale(earn_growth, -0.1, 0.3)])
    
    qs_value = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)
    qs_category = classify_qs(qs_value)

    # --- VALUACIÓN FINAL ---
    valid_models = [v for v in [intrinsic_dcf if 'intrinsic_dcf' in locals() else None, mr_intrinsic] if v is not None and v > 0]
    final_intrinsic = np.mean(valid_models) if valid_models else (price * 0.5 if roe < 0 else price)

    sell_threshold = final_intrinsic * 1.20
    signal = "REJECTED" if qs_value < 30 or roe < 0 else ("BUY" if price < final_intrinsic else "HOLD")

    return {
        "price": price, "intrinsic": final_intrinsic, "signal": signal,
        "dcf": intrinsic_dcf if 'intrinsic_dcf' in locals() else 0, 
        "mr": mr_intrinsic, "sell_threshold": sell_threshold,
        "qs": qs_value, "category": qs_category,
        "roe": roe, "margins": margins, "debt_to_equity": debt_to_equity,
        "curr_ratio": curr_ratio, "fcf_ttm": fcf_ttm, "growth": growth,
        "rev_growth": rev_growth, "earn_growth": earn_growth
    }


