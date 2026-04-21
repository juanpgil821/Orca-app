# database.py - Motor de Datos Completo del HTM-30

HTM_30_DATA = {
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
        "quality_score": 74,
        "dcf_val": 321.00,
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
        "quality_score": 77,
        "dcf_val": 980.00,
        "mr_val": 1079.00,
        "fcf_ttm": 3200.0
    },
    "NVO": {
        "name": "Novo Nordisk",
        "fcf_yield": 2.51,
        "eps_growth": 14.7,
        "buyback_yield": 0.0,
        "quality_score": 71,
        "dcf_val": 32.00,
        "mr_val": 94.57,
        "fcf_ttm": 12000.0
    },
    "DECK": {
        "name": "Deckers Outdoor",
        "fcf_yield": 5.82,
        "eps_growth": 14.8,
        "buyback_yield": 0.0,
        "quality_score": 79,
        "dcf_val": 118.00,
        "mr_val": 127.00,
        "fcf_ttm": 850.0
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "fcf_yield": 1.79,
        "eps_growth": 22.5,
        "buyback_yield": 0.0,
        "quality_score": 77,
        "dcf_val": 300.00,
        "mr_val": 190,
        "fcf_ttm": 73266.0
    },
    "COST": {
        "name": "Costco Wholesale",
        "fcf_yield": 2.05,
        "eps_growth": 11.7,
        "buyback_yield": 0.21,
        "quality_score": 46,
        "dcf_val": 802.00,
        "mr_val": 610.00,
        "fcf_ttm": 9099.0
    },
    "MCO": {
        "name": "Moody's Corp.",
        "fcf_yield": 3.18,
        "eps_growth": 20.4,
        "buyback_yield": 0.0,
        "quality_score": 69,
        "dcf_val": 407.00,
        "mr_val": 399.00,
        "fcf_ttm": 2575.0
    },
    "MA": {
        "name": "Mastercard Inc.",
        "fcf_yield": 3.55,
        "eps_growth": 16.9,
        "buyback_yield": 0.0,
        "quality_score": 72,
        "dcf_val": 503.00,
        "mr_val": 523.00,
        "fcf_ttm": 16433.0
    },
    "NOW": {
        "name": "ServiceNow Inc.",
        "fcf_yield": 4.42,
        "eps_growth": 32.2,
        "buyback_yield": 1.84,
        "quality_score": 52,
        "dcf_val": 99.64,
        "mr_val": 231.27,
        "fcf_ttm": 4533.0
    },
    "CSGP": {
        "name": "CoStar Group Inc.",
        "fcf_yield": 0.24,
        "eps_growth": -11.8,
        "buyback_yield": 3,
        "quality_score": 47,
        "dcf_val": 35.24,
        "mr_val": 10.68,
        "fcf_ttm": 41.0
    },
    "SPGI": {
        "name": "S&P Global Inc.",
        "fcf_yield": 4.16,
        "eps_growth": 16.8,
        "buyback_yield": 0.0,
        "quality_score": 56, 
        "dcf_val": 365.00,
        "mr_val": 377.00,
        "fcf_ttm": 5456.0
    },
    "MSCI": {
        "name": "MSCI Inc.",
        "fcf_yield": 3.40,
        "eps_growth": 14.7,
        "buyback_yield": 0.0,
        "quality_score": 55,
        "dcf_val": 562.00,
        "mr_val": 481.00,
        "fcf_ttm": 1459.0
    }
}

def get_ticker_data(ticker):
    """
    Recupera el diccionario de datos para un ticker específico.
    Si el ticker no existe, devuelve None.
    """
    return HTM_30_DATA.get(ticker.upper(), None)


