import yfinance as yf
import numpy as np

def get_row(df, names):
    for n in names:
        if n in df.index:
            return df.loc[n]
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
            return {"error": f"No se encontró información para {ticker_symbol}"}
    except Exception as e:
        return {"error": f"Error al conectar con Yahoo Finance: {str(e)}"}

    price = info.get("currentPrice")
    shares = info.get("sharesOutstanding")
    
    # --- MODELO 1: DCF (Celdas 5, 6, 7) ---
    cf = stock.cashflow
    growth = None
    if cf is not None and not cf.empty:
        op_h = get_row(cf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap_h = get_row(cf, ["Capital Expenditures", "Capital Expenditure"])
        if op_h is not None and cap_h is not None:
            fcf_hist = (op_h - cap_h).dropna()
            fcf_hist = fcf_hist[fcf_hist > 0]
            if len(fcf_hist) >= 2:
                growth = (fcf_hist.iloc[0] / fcf_hist.iloc[-1]) ** (1 / (len(fcf_hist)-1)) - 1

    qcf = stock.quarterly_cashflow
    fcf_ttm = None
    if not qcf.empty:
        op_q = get_row(qcf, ["Total Cash From Operating Activities", "Operating Cash Flow"])
        cap_q = get_row(qcf, ["Capital Expenditures", "Capital Expenditure"])
        if op_q is not None and cap_q is not None:
            fcf_ttm = op_q.iloc[:4].sum() + cap_q.iloc[:4].sum()

    intrinsic_dcf = None
    if fcf_ttm and growth is not None and shares:
        growth_capped = max(0.0, min(growth, 0.10))
        multiplier = 1 + growth_capped
        pfcf_current = price / (fcf_ttm / shares)
        pv_fcfs = sum([fcf_ttm * (multiplier ** t) / ((1 + discount_rate) ** t) for t in range(1, 6)])
        terminal_val = (fcf_ttm * (multiplier ** 5) * pfcf_current) / ((1 + discount_rate) ** 5)
        intrinsic_dcf = (pv_fcfs + terminal_val) / shares

    # --- MODELO 2: MEAN REVERSION (Celda 9) ---
    mr_intrinsic = None
    financial_sector = ["JPM", "BAC", "AXP", "ALL"]
    
    if ticker_symbol not in financial_sector:
        try:
            hist = stock.history(period="5y")["Close"]
            if not hist.empty:
                yearly_prices = hist.resample("YE").last().values
                financials = stock.financials
                ebit_row = get_row(financials, ["EBIT", "Ebit"])
                
                if ebit_row is not None and len(yearly_prices) > 0:
                    ebit_avg = ebit_row.dropna().mean()
                    current_ebit = ebit_row.iloc[0]
                    if current_ebit and ebit_avg:
                        mr_intrinsic = price * (ebit_avg / current_ebit)
        except:
            mr_intrinsic = None

    # --- QUALITY SCORE (Celda 11) ---
    fs = np.mean([scale(info.get("currentRatio", 0), 0.5, 3), scale(info.get("debtToEquity", 100), 200, 0)])
    pr = np.mean([scale(info.get("returnOnEquity", 0), 0, 0.30), scale(info.get("operatingMargins", 0), 0, 0.30)])
    gr = np.mean([scale(info.get("revenueGrowth", 0), -0.1, 0.3), scale(info.get("earningsGrowth", 0), -0.1, 0.3)])
    qs = (fs * 0.4) + (pr * 0.4) + (gr * 0.2)

    # --- FINAL SIGNAL (Celda 13) ---
    candidates = [v for v in [intrinsic_dcf, mr_intrinsic] if v is not None]
    final_intrinsic = np.mean(candidates) if candidates else None
    
    signal = "N/A"
    if final_intrinsic:
        margin_adj = 0.9 if qs > 85 else 0.8 if qs > 60 else 0.7
        if price <= (final_intrinsic * margin_adj): signal = "BUY"
        elif price <= final_intrinsic: signal = "HOLD"
        else: signal = "SELL"

    return {
        "symbol": ticker_symbol,
        "price": price,
        "intrinsic": final_intrinsic,
        "dcf": intrinsic_dcf,
        "mr": mr_intrinsic,
        "signal": signal,
        "qs": qs,
        "growth": growth,
        "info": info
    }


