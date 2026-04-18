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
    
    # --- MODELO 1: DCF (FLUJO DE CAJA DESCONTADO) ---
    cf = stock.cashflow
    growth, fcf_ttm, buyback_yield = 0, 0, 0
    if cf is not None and not cf.empty:
        op = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        repro = get_row(cf, ["Repurchase Of Capital Stock", "Repurchase Of Stock"])
        
        if op is not None and cap is not None:
            fcf_h = (op + cap).dropna()
            if len(fcf_h) >= 2:
                try:
                    # Lógica robusta para crecimiento: evita errores con FCF negativos
                    if fcf_h.iloc[-1] > 0 and fcf_h.iloc[0] > 0:
                        growth = (fcf_h.iloc[0] / fcf_h.iloc[-1]) ** (1 / (len(fcf_h)-1)) - 1
                    else:
                        growth = -0.50 # Penalización si el historial es inconsistente
                except:
                    growth = 0
            fcf_ttm = fcf_h.iloc[:4].sum() if len(fcf_h) >= 1 else 0

        # Cálculo de Buyback Yield (Necesario para el escenario "Cannibal")
        if repro is not None and price and shares:
            last_repro = abs(repro.iloc[0]) if not repro.empty else 0
            mkt_cap = price * shares
            buyback_yield = last_repro / mkt_cap if mkt_cap > 0 else 0

    # --- MODELO 2: MEAN REVERSION ---
    eps_ttm = info.get("trailingEps", 0)
    pe_curr = info.get("trailingPE", 20)
    pe_fwd = info.get("forwardPE", 15)
    pe_avg = (pe_curr + pe_fwd) / 2 if (pe_curr and pe_fwd) else 20
    mr_intrinsic = eps_ttm * pe_avg if eps_ttm and eps_ttm > 0 else 0

    # --- MÉTRICAS DE LIMPIEZA ---
    def safe_num(key):
        val = info.get(key, 0)
        return val if isinstance(val, (int, float, np.number)) and val is not None else 0

    res_metrics = {
        "curr_ratio": safe_num("currentRatio"),
        "debt_to_equity": safe_num("debtToEquity"),
        "roe": safe_num("returnOnEquity"),
        "margins": safe_num("operatingMargins"),
        "rev_growth": safe_num("revenueGrowth"),
        "earn_growth": safe_num("earningsGrowth")
    }

    # --- QUALITY SCORE (QS) ---
    fs = np.mean([scale(res_metrics['curr_ratio'], 0.5, 3), scale(res_metrics['debt_to_equity'], 200, 0)])
    pr = np.mean([scale(res_metrics['roe'], 0, 0.35), scale(res_metrics['margins'], 0, 0.35)])
    gr = np.mean([scale(res_metrics['rev_growth'], -0.1, 0.3), scale(res_metrics['earn_growth'], -0.1, 0.3)])
    
    qs_value = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)
    qs_category = classify_qs(qs_value)

    # --- VALUACIÓN FINAL ---
    # Si DCF es inviable (Zombies), usamos MR o un descuento agresivo sobre precio
    intrinsic_dcf = None
    if fcf_ttm and shares and shares > 0:
        g_capped = max(0.0, min(growth if growth else 0, 0.10))
        fcf_share = fcf_ttm / shares
        pfcf_curr = price / fcf_share if fcf_share != 0 else 20
        pv = sum([fcf_ttm * ((1 + g_capped)**t) / ((1 + discount_rate)**t) for t in range(1, 6)])
        tv = (fcf_ttm * ((1 + g_capped)**5) * pfcf_curr) / ((1 + discount_rate)**5)
        intrinsic_dcf = (pv + tv) / shares

    valid_models = [v for v in [intrinsic_dcf, mr_intrinsic] if v is not None and v > 0]
    final_intrinsic = np.mean(valid_models) if valid_models else (price * 0.7 if res_metrics['roe'] > 0 else price * 0.3)

    # --- SEÑAL ---
    sell_threshold = final_intrinsic * 1.20
    if price < final_intrinsic:
        signal = "REJECTED" if qs_value < 30 or res_metrics['roe'] < 0 else f"BUY ({qs_category})"
    elif price < sell_threshold:
        signal = "HOLD"
    else:
        signal = "SELL"

    return {
        "price": price, 
        "intrinsic": final_intrinsic, 
        "signal": signal,
        "dcf": intrinsic_dcf if intrinsic_dcf else 0, 
        "mr": mr_intrinsic, 
        "sell_threshold": sell_threshold,
        "qs": qs_value, 
        "category": qs_category,
        "fcf_ttm": fcf_ttm, 
        "growth": growth, 
        "buyback_yield": buyback_yield,
        **res_metrics # Desglosa curr_ratio, debt_to_equity, roe, margins, rev_growth, earn_growth
    }


