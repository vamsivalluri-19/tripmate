# Airport data mapping cities to nearby airports
AIRPORT_INFO = {
    'Mumbai': {
        'main': 'Bombay Maharaja Sayajirao Gaekwad Airport (BOM)',
        'code': 'BOM',
        'nearby': [
            'Indore Airport (IDR) - 450 km',
            'Pune Airport (PNQ) - 190 km',
            'Nashik Airport (ISK) - 200 km'
        ]
    },
    'Delhi': {
        'main': 'Indira Gandhi International Airport (DEL)',
        'code': 'DEL',
        'nearby': [
            'Jaipur International Airport (JAI) - 240 km',
            'Lucknow Airport (LKO) - 400 km',
            'Chandigarh Airport (CHD) - 240 km'
        ]
    },
    'Bangalore': {
        'main': 'Kempegowda International Airport (BLR)',
        'code': 'BLR',
        'nearby': [
            'Mysore Airport (MYR) - 140 km',
            'Coimbatore Airport (CJB) - 280 km',
            'Hyderabad Airport (HYD) - 560 km'
        ]
    },
    'Dubai': {
        'main': 'Dubai International Airport (DXB)',
        'code': 'DXB',
        'nearby': [
            'Al Maktoum International Airport (DWC) - 70 km',
            'Sharjah International Airport (SHJ) - 35 km',
            'Ras Al Khaimah International Airport (RKT) - 100 km'
        ]
    },
    'London': {
        'main': 'London Heathrow Airport (LHR)',
        'code': 'LHR',
        'nearby': [
            'Gatwick Airport (LGW) - 46 km',
            'Stansted Airport (STN) - 60 km',
            'Luton Airport (LTN) - 56 km',
            'London City Airport (LCY) - 22 km'
        ]
    },
    'Paris': {
        'main': 'Charles de Gaulle Airport (CDG)',
        'code': 'CDG',
        'nearby': [
            'Orly Airport (ORY) - 18 km',
            'Le Bourget Airport (LBG) - 20 km',
            'Beauvais-Tillé Airport (BVA) - 80 km'
        ]
    },
    'New York': {
        'main': 'John F. Kennedy International Airport (JFK)',
        'code': 'JFK',
        'nearby': [
            'Newark Liberty International Airport (EWR) - 20 km',
            'LaGuardia Airport (LGA) - 14 km',
            'Westchester County Airport (HPN) - 50 km'
        ]
    },
    'Tokyo': {
        'main': 'Narita International Airport (NRT)',
        'code': 'NRT',
        'nearby': [
            'Haneda Airport (HND) - 20 km',
            'Komatsu Airport (KMQ) - 300 km',
            'Yokota Air Base (OKO) - 50 km'
        ]
    },
    'Singapore': {
        'main': 'Singapore Changi Airport (SIN)',
        'code': 'SIN',
        'nearby': [
            'Kuala Lumpur International Airport (KUL) - 400 km',
            'Johor Bahru International Airport (JHB) - 80 km',
            'Penang International Airport (PEN) - 380 km'
        ]
    },
    'Sydney': {
        'main': 'Sydney Kingsford Smith Airport (SYD)',
        'code': 'SYD',
        'nearby': [
            'Newcastle Airport (NWS) - 160 km',
            'Canberra International Airport (CBR) - 290 km',
            'Wollongong Airport (WOL) - 100 km'
        ]
    },
    'Bangkok': {
        'main': 'Suvarnabhumi Airport (BKK)',
        'code': 'BKK',
        'nearby': [
            'Don Mueang International Airport (DMK) - 25 km',
            'U-Tapao International Airport (UTP) - 160 km',
            'Hua Hin Airport (HHH) - 220 km'
        ]
    },
    'Hong Kong': {
        'main': 'Hong Kong International Airport (HKG)',
        'code': 'HKG',
        'nearby': [
            'Macau International Airport (MFM) - 70 km',
            'Shenzhen Bao\'an International Airport (SZX) - 35 km',
            'Zhuhai Jinwan Airport (ZUH) - 120 km'
        ]
    },
    'Istanbul': {
        'main': 'Istanbul Airport (IST)',
        'code': 'IST',
        'nearby': [
            'Sabiha Gokcen International Airport (SAW) - 40 km',
            'Bursa Yesil Airport (YEZ) - 100 km',
            'Ankara Esenboga Airport (ESB) - 450 km'
        ]
    },
    'Berlin': {
        'main': 'Berlin Tegel Airport (TXL)',
        'code': 'TXL',
        'nearby': [
            'Berlin Schönefeld Airport (SXF) - 20 km',
            'Potsdam Airport (BBG) - 50 km',
            'Leipzig/Halle Airport (LEJ) - 200 km'
        ]
    },
    'Rome': {
        'main': 'Leonardo da Vinci-Fiumicino Airport (FCO)',
        'code': 'FCO',
        'nearby': [
            'Ciampino Airport (CIA) - 30 km',
            'Perugia Airport (PEG) - 190 km',
            'Naples Airport (NAP) - 230 km'
        ]
    },
    'Seoul': {
        'main': 'Incheon International Airport (ICN)',
        'code': 'ICN',
        'nearby': [
            'Gimpo International Airport (GMP) - 50 km',
            'Daegu International Airport (TAE) - 300 km',
            'Busan Gimhae International Airport (PUS) - 400 km'
        ]
    },
    'Doha': {
        'main': 'Doha International Airport (DOH)',
        'code': 'DOH',
        'nearby': [
            'Al Udeid Air Base (MPS) - 30 km',
            'Abu Dhabi International Airport (AUH) - 150 km'
        ]
    },
    'Frankfurt': {
        'main': 'Frankfurt am Main Airport (FRA)',
        'code': 'FRA',
        'nearby': [
            'Wiesbaden Air Base (VSP) - 30 km',
            'Cologne/Bonn Airport (CGN) - 140 km',
            'Stuttgart Airport (STR) - 200 km'
        ]
    },
    'Melbourne': {
        'main': 'Melbourne Airport (MEL)',
        'code': 'MEL',
        'nearby': [
            'Avalon Airport (AVV) - 50 km',
            'Essendon Airport (ESS) - 25 km'
        ]
    },
    'Los Angeles': {
        'main': 'Los Angeles International Airport (LAX)',
        'code': 'LAX',
        'nearby': [
            'Burbank Airport (BUR) - 30 km',
            'Long Beach Airport (LGB) - 40 km',
            'Ontario International Airport (ONT) - 90 km'
        ]
    },
    'San Francisco': {
        'main': 'San Francisco International Airport (SFO)',
        'code': 'SFO',
        'nearby': [
            'Oakland International Airport (OAK) - 50 km',
            'San Jose Mineta International Airport (SJC) - 85 km'
        ]
    },
    'Chicago': {
        'main': 'Chicago O\'Hare International Airport (ORD)',
        'code': 'ORD',
        'nearby': [
            'Chicago Midway International Airport (MDW) - 20 km',
            'Gary/Chicago International Airport (GYY) - 40 km'
        ]
    }
}

def get_airport_info(city):
    """Get airport information for a city"""
    if not city:
        return None
    
    # Try exact match first
    if city in AIRPORT_INFO:
        return AIRPORT_INFO[city]
    
    # Try case-insensitive match
    for key, value in AIRPORT_INFO.items():
        if key.lower() == city.lower():
            return value
    
    # Try partial match
    for key, value in AIRPORT_INFO.items():
        if city.lower() in key.lower():
            return value
    
    return None
