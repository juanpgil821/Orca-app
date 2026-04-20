# database.py - Motor de Datos Completo del HTM-30 (Versión FCF Plus)

HTM_30_DATA = {
    # --- ANALIZADAS ---
    "ADBE": {
        "name": "Adobe Inc.",
        "fcf_yield": 10.3,
        "eps_growth": 15.0,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 306.00,
        "mr_val": 700.00,
        "fcf_ttm": 10317.0  # Ejemplo: FCF en millones $M
    },
    "MSFT": {
        "name": "Microsoft Corp.",
        "fcf_yield": 2.47,
        "eps_growth": 12.5,
        "buyback_yield": 0.0,
        "quality_score": 79,
        "dcf_val": 385.00,
        "mr_val": 394.00,
        "fcf_ttm": 77412.0
    },
    "V": {
        "name": "Visa Inc.",
        "fcf_yield": 3.76,
        "eps_growth": 14.4,
        "buyback_yield": 0.0,
        "quality_score": 74,
        "dcf_val": 343.00,
        "mr_val": 311.00,
        "fcf_ttm": 22928.0
    },
    "ASML": {
        "name": "ASML Holding",
        "fcf_yield": 1.86,
        "eps_growth": 21.4,
        "buyback_yield": 0.0,
        "quality_score": 80,
        "dcf_val": 1527.00,
        "mr_val": 1153.00,
        "fcf_ttm": 10494.0
    },
    "NVO": {
        "name": "Novo Nordisk",
        "fcf_yield": 2.51,
        "eps_growth": 14.7,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 42.00,
        "mr_val": 46.00,
        "fcf_ttm": 4388.0
    },
    "DECK": {
        "name": "Deckers Outdoor",
        "fcf_yield": 5.82,
        "eps_growth": 14.8,
        "buyback_yield": 0.0,
        "quality_score": 89,
        "dcf_val": 118.00,
        "mr_val": 108.00,
        "fcf_ttm": 929.0
    },
}

def get_ticker_data(ticker):
    """
    Recupera el diccionario de datos para un ticker específico.
    Si el ticker no existe, devuelve None.
    """
    return HTM_30_DATA.get(ticker.upper(), None)


