# database.py - Motor de Datos Completo del HTM-30

HTM_30_DATA = {
    # --- ANALIZADAS (Ejemplos con data real discutida) ---
    "ADBE": {
        "name": "Adobe Inc.",
        "fcf_yield": 10.3,
        "eps_growth": 15.0,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 306.00,  # Tu valoración por flujos descontados
        "mr_val": 700.00    # Valoración por múltiplos históricos (P/E, P/FCF, EV/EBIT)
    },
    "MSFT": {
        "name": "Microsoft Corp.",
        "fcf_yield": 2.47,
        "eps_growth": 12.5,
        "buyback_yield": 0.0,
        "quality_score": 79,
        "dcf_val": 385.00,
        "mr_val": 394.00
    },
    "V": {
        "name": "Visa Inc.",
        "fcf_yield": 3.76,
        "eps_growth": 14.4,
        "buyback_yield": 0.0,
        "quality_score": 74,
        "dcf_val": 343.00,
        "mr_val": 311.00
    },
}

def get_ticker_data(ticker):
    return HTM_30_DATA.get(ticker.upper(), None)


