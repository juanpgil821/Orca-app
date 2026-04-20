# database.py - Motor de Datos Completo del HTM-30 (Versión FCF Plus)

HTM_30_DATA = {
    # --- ANALIZADAS (Originales intactos) ---
    "ADBE": {
        "name": "Adobe Inc.",
        "fcf_yield": 10.3,
        "eps_growth": 15.0,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 306.00,
        "mr_val": 700.00,
        "fcf_ttm": 6200.0
    },
    "MSFT": {
        "name": "Microsoft Corp.",
        "fcf_yield": 2.47,
        "eps_growth": 12.5,
        "buyback_yield": 0.0,
        "quality_score": 79,
        "dcf_val": 385.00,
        "mr_val": 394.00,
        "fcf_ttm": 63000.0
    },
    "V": {
        "name": "Visa Inc.",
        "fcf_yield": 3.76,
        "eps_growth": 14.4,
        "buyback_yield": 0.0,
        "quality_score": 74,
        "dcf_val": 343.00,
        "mr_val": 311.00,
        "fcf_ttm": 19000.0
    },
    "ASML": {
        "name": "ASML Holding",
        "fcf_yield": 1.86,
        "eps_growth": 21.4,
        "buyback_yield": 0.0,
        "quality_score": 80,
        "dcf_val": 1557.00,
        "mr_val": 1170.00,
        "fcf_ttm": 3200.0
    },
    "NVO": {
        "name": "Novo Nordisk",
        "fcf_yield": 2.51,
        "eps_growth": 14.7,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 42.00,
        "mr_val": 46.00,
        "fcf_ttm": 12000.0
    },
    "DECK": {
        "name": "Deckers Outdoor",
        "fcf_yield": 5.82,
        "eps_growth": 14.8,
        "buyback_yield": 0.0,
        "quality_score": 89,
        "dcf_val": 118.00,
        "mr_val": 108.00,
        "fcf_ttm": 850.0
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "fcf_yield": 1.79,
        "eps_growth": 22.5,
        "buyback_yield": 0.0,
        "quality_score": 91,
        "dcf_val": 300.00,
        "mr_val": 234.50,
        "fcf_ttm": 73266.0
    },
    "COST": {
        "name": "Costco Wholesale",
        "fcf_yield": 2.05,
        "eps_growth": 11.7,
        "buyback_yield": 0.21,
        "quality_score": 83,
        "dcf_val": 802.00,
        "mr_val": 610.00,
        "fcf_ttm": 9099.0
    },
    "MCO": {
        "name": "Moody's Corp.",
        "fcf_yield": 3.18,
        "eps_growth": 20.4,
        "buyback_yield": 0.0,
        "quality_score": 78,
        "dcf_val": 407.00,
        "mr_val": 399.00,
        "fcf_ttm": 2575.0
    },
    "MA": {
        "name": "Mastercard Inc.",
        "fcf_yield": 3.55,
        "eps_growth": 16.9,
        "buyback_yield": 0.0,
        "quality_score": 68,
        "dcf_val": 502.00,
        "mr_val": 430.00,
        "fcf_ttm": 16433.0
    },
}

def get_ticker_data(ticker):
    """
    Recupera el diccionario de datos para un ticker específico.
    Si el ticker no existe, devuelve None.
    """
    return HTM_30_DATA.get(ticker.upper(), None)


