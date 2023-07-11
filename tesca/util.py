from r5py import TransportMode


transit_mode = {
    "TRANSIT": {
        "r5": TransportMode.TRANSIT,
        "name": "All transit modes",
        "description": "All possible modes of transit",
    },
    "AIR": {
        "r5": TransportMode.AIR,
        "name": "Air",
        "description": "Travel by airplane",
    },
    "TRAM": {
        "r5": TransportMode.TRAM,
        "name": "Tram",
        "description": "Modes classifeid as trams",
    },
    "SUBWAY": {
        "r5": TransportMode.SUBWAY,
        "name": "Subway",
        "description": "Modes classified as subways",
    },
    "RAIL": {
        "r5": TransportMode.RAIL,
        "name": "Rail",
        "description": "Modes classified as rail",
    },
    "BUS": {
        "r5": TransportMode.BUS,
        "name": "Bus",
        "description": "Modes classified as buses",
    },
    "FERRY": {
        "r5": TransportMode.FERRY,
        "name": "Ferry",
        "description": "Modes classified as ferries",
    },
    "CABLE_CAR": {
        "r5": TransportMode.CABLE_CAR,
        "name": "Cable car",
        "description": "Modes classified as cable cars",
    },
    "GONDOLA": {
        "r5": TransportMode.GONDOLA,
        "name": "Gondola",
        "description": "Modes classfied as gondolas",
    },
    "FUNICULAR": {"r5": TransportMode.FUNICULAR, "name": "Funicular"},
}

demographic_categories = {
    "B03002_001E": "Everyone",
    "B03002_003E": "White People",
    "B03002_004E": "Black People",
    "B03002_006E": "Asian",
    "B03002_012E": "Hispanic or Latino",
    "C17002_003E": "In Poverty",
}
