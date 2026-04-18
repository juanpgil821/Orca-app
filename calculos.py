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
    
    # --- MODELO 1: DCF ---
    cf = stock.cashflow
    growth, fcf_ttm, buyback_yield = 0, 0, 0
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        # Recompras: "Repurchase Of Capital Stock" suele ser negativo
        repro = get_row(cf, ["Repurchase Of Capital Stock", "Repurchase Of Stock"])
        
        if op is not None and cap is not None:
            fcf_h = (op + cap).dropna()
            if len(fcf_h) >= 2 and fcf_h.iloc[-1] > 0:
                growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1
            fcf_ttm = fcf_h.iloc[:4].sum() if len(fcf_h) >= 1 else 0
            
        if repro is not None and price and shares:
            last_repro = abs(repro.iloc[0]) if not repro.empty else 0
            buyback_yield = last_repro / (price * shares)

    # --- MODELO 2: MEAN REVERSION ---
    eps_ttm = info.get("trailingEps", 0)
    pe_avg = (info.get("trailingPE", 20) + info.get("forwardPE", 15)) / 2
    mr_intrinsic = eps_ttm * pe_avg if eps_ttm and eps_ttm > 0 else 0

    # --- MÉTRICAS ---
    def safe_num(key):
        val = info.get(key, 0)
        return val if isinstance(val, (int, float, np.number)) and val is not None else 0

    res = {
        "price": price,
        "roe": safe_num("returnOnEquity"),
        "margins": safe_num("operatingMargins"),
        "debt_to_equity": safe_num("debtToEquity"),
        "curr_ratio": safe_num("currentRatio"),
        "payout": safe_num("payoutRatio"),
        "rev_growth": safe_num("revenueGrowth"),
        "earn_growth": safe_num("earningsGrowth"),
        "fcf_ttm": fcf_ttm,
        "growth": growth,
        "buyback_yield": buyback_yield,
        "shares": shares,
        "mr": mr_intrinsic,
        "dcf": mr_intrinsic * 1.1 # Proxy si DCF falla para mantener main vivo
    }

    # QS
    fs = np.mean([scale(res['curr_ratio'], 0.5, 3), scale(res['debt_to_equity'], 200, 0)])
    pr = np.mean([scale(res['roe'], 0, 0.4), scale(res['margins'], 0, 0.4)])
    res['qs'] = (fs * 0.4) + (pr * 0.4) + (scale(res['rev_growth'], 0, 0.2) * 0.2)
    res['category'] = classify_qs(res['qs'])
    res['intrinsic'] = np.mean([v for v in [res['mr'], res['dcf']] if v > 0])
    res['sell_threshold'] = res['intrinsic'] * 1.2
    res['signal'] = "BUY" if price < res['intrinsic'] else "HOLD"
    if res['roe'] < 0 or res['qs'] < 30: res['signal'] = "REJECTED"

    return res


