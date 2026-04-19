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
    "ASML": {
        "name": "ASML Holding",
        "fcf_yield": 1.86,
        "eps_growth": 21.4,
        "buyback_yield": 0.0,  # Ratio 0.8 (Dilución neta)
        "quality_score": 80,
        "dcf_val": 1557.00,
        "mr_val": 1170.00
    },
    "NVO": {
        "name": "Novo Nordisk",
        "fcf_yield": 2.51,
        "eps_growth": 14.7,
        "buyback_yield": 0.0,  # Ratio 0.40 (Dilución neta)
        "quality_score": 71,
        "dcf_val": 42.00,
        "mr_val": 46.00
    },
    "DECK": {
        "name": "Deckers Outdoor",
        "fcf_yield": 5.82,
        "eps_growth": 14.8,
        "buyback_yield": 0.0,  # Ratio 2.5 (Dilución neta alta)
        "quality_score": 89,
        "dcf_val": 118.00,
        "mr_val": 108.00
    },
}

def get_ticker_data(ticker):
    return HTM_30_DATA.get(ticker.upper(), None)


