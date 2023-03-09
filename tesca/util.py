from r5py import LegMode, TransitMode

transit_mode = {
    "TRANSIT": {
        "r5": TransitMode.TRANSIT,
        "name": "All transit modes",
        "description": "All possible modes of transit",
    },
    "AIR": {
        "r5": TransitMode.AIR,
        "name": "Air",
        "description": "Travel by airplane",
    },
    "TRAM": {
        "r5": TransitMode.TRAM,
        "name": "Tram",
        "description": "Modes classifeid as trams",
    },
    "SUBWAY": {
        "r5": TransitMode.SUBWAY,
        "name": "Subway",
        "description": "Modes classified as subways",
    },
    "RAIL": {
        "r5": TransitMode.RAIL,
        "name": "Rail",
        "description": "Modes classified as rail",
    },
    "BUS": {
        "r5": TransitMode.BUS,
        "name": "Bus",
        "description": "Modes classified as buses",
    },
    "FERRY": {
        "r5": TransitMode.FERRY,
        "name": "Ferry",
        "description": "Modes classified as ferries",
    },
    "CABLE_CAR": {
        "r5": TransitMode.CABLE_CAR,
        "name": "Cable car",
        "description": "Modes classified as cable cars",
    },
    "GONDOLA": {
        "r5": TransitMode.GONDOLA,
        "name": "Gondola",
        "description": "Modes classfied as gondolas",
    },
    "FUNICULAR": {
        "r5": TransitMode.FUNICULAR,
        "name": "Funicular",
        "description": "Modes classified as funiculars",
    },
}
