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
    },
       # --- BLOQUE SEMICONDUCTORES & ESPECIALIZADOS (Data Refinada) ---
    "NVDA": {
        "name": "NVIDIA Corporation",
        "fcf_yield": 1.92,
        "eps_growth": 142.6,
        "buyback_yield": 0,
        "quality_score": 100,
        "dcf_val": 176.70,
        "mr_val": 191,
        "fcf_ttm": 96676.0
    },
    "AVGO": {
        "name": "Broadcom Inc.",
        "fcf_yield": 1.53,
        "eps_growth": 9,
        "buyback_yield": 0.63,
        "quality_score": 72,
        "dcf_val": 271.24,
        "mr_val": 220.65,
        "fcf_ttm": 28911.0
    },
    "LRCX": {
        "name": "Lam Research Corporation",
        "fcf_yield": 1.89,
        "eps_growth": 8.4,
        "buyback_yield": 0,
        "quality_score": 77,
        "dcf_val": 221.11,
        "mr_val": 213.63,
        "fcf_ttm": 6216.0
    },
    "KLAC": {
        "name": "KLA Corporation",
        "fcf_yield": 1.85,
        "eps_growth": 16.3,
        "buyback_yield": 0,
        "quality_score": 84,
        "dcf_val": 1483.00,
        "mr_val": 1672.20,
        "fcf_ttm": 4377.0
    },
       # --- BLOQUE INDUSTRIALES & DATOS DE MOAT ANCHO (Data Refinada) ---
    "ODFL": {
        "name": "Old Dominion Freight Line",
        "fcf_yield": 2.05,
        "eps_growth": 18.4,
        "buyback_yield": 0,
        "quality_score": 50,
        "dcf_val": 168.25,
        "mr_val": 130.00,
        "fcf_ttm": 955.0
    },
    "CP": {
        "name": "Canadian Pacific Kansas City",
        "fcf_yield": 2.13,
        "eps_growth": 8.6,
        "buyback_yield": 0.0,
        "quality_score": 51,
        "dcf_val": 41.65,
        "mr_val": 53.62,
        "fcf_ttm": 1563.0
    },
    "RSG": {
        "name": "Republic Services Inc.",
        "fcf_yield": 3.74,
        "eps_growth": 12.5,
        "buyback_yield": 0.0,
        "quality_score": 41,
        "dcf_val": 19.00,
        "mr_val": 163.50,
        "fcf_ttm": 2409.0
    },
    "FICO": {
        "name": "Fair Isaac Corporation",
        "fcf_yield": 2.85,
        "eps_growth": 20.2,
        "buyback_yield": 0,
        "quality_score": 57,
        "dcf_val": 1041.50,
        "mr_val": 1062.50,
        "fcf_ttm": 718.5
    },
       # --- BLOQUE CONSUMO & LIFESTYLE (Early Morning) ---
    "LVMUY": {
        "name": "LVMH Moet Hennessy Louis Vuitton",
        "fcf_yield": 5.79,
        "eps_growth": -8.7,
        "buyback_yield": 0.0,
        "quality_score": 45,
        "dcf_val": 135.14,
        "mr_val": 104.08,
        "fcf_ttm": 16536.0
    },
    "EL": {
        "name": "Estée Lauder Companies Inc.",
        "fcf_yield": 4.04,
        "eps_growth": -40.7, # Recuperación tras ciclo de inventario
        "buyback_yield": 0.24,
        "quality_score": 26,
        "dcf_val": 49.60,
        "mr_val": 34.78,
        "fcf_ttm": 1137.0
    },
    "ORLY": {
        "name": "O'Reilly Automotive Inc.",
        "fcf_yield": 2.05,
        "eps_growth": 10,
        "buyback_yield": 0,
        "quality_score": 49,
        "dcf_val": 53.71,
        "mr_val": 34.74,
        "fcf_ttm": 1593.0
    },

    # --- BLOQUE SALUD & BIOTECNOLOGÍA (Late Morning) ---
    "LLY": {
        "name": "Eli Lilly and Co.",
        "fcf_yield": 0.73,
        "eps_growth": 45,
        "buyback_yield": 0.0,
        "quality_score": 78,
        "dcf_val": 728,
        "mr_val": 649,
        "fcf_ttm": 5964.0
    },
    "ISRG": {
        "name": "Intuitive Surgical Inc.",
        "fcf_yield": 1.51,
        "eps_growth": 24,
        "buyback_yield": 1.39,
        "quality_score": 78,
        "dcf_val": 377.70,
        "mr_val": 393.12,
        "fcf_ttm": 2491.0
    },
    "IDXX": {
        "name": "IDEXX Laboratories Inc.",
        "fcf_yield": 2.25,
        "eps_growth": 15.7,
        "buyback_yield": 0,
        "quality_score": 68,
        "dcf_val": 742.20,
        "mr_val": 628.70,
        "fcf_ttm": 1044.0
    },
    "TMO": {
        "name": "Thermo Fisher Scientific Inc.",
        "fcf_yield": 3.22,
        "eps_growth": -0.5,
        "buyback_yield": 0,
        "quality_score": 47,
        "dcf_val": 320.00,
        "mr_val": 515.84,
        "fcf_ttm": 6293.0
    },

    # --- EL CANDADO (Market Infrastructure) ---
    "ICE": {
        "name": "Intercontinental Exchange Inc.",
        "fcf_yield": 4.24,
        "eps_growth": 9.5,
        "buyback_yield": 1.54,
        "quality_score": 65,
        "dcf_val": 156.0,
        "mr_val": 128.63,
        "fcf_ttm": 3871.0
    },
}

def get_ticker_data(ticker):
    """
    Recupera el diccionario de datos para un ticker específico.
    Si el ticker no existe, devuelve None.
    """
    return HTM_30_DATA.get(ticker.upper(), None)


