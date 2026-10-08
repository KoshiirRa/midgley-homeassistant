"""Client-side spatial location & ZIP code resolver for Midgley integration."""
from __future__ import annotations

import math
from typing import Dict, Any, Optional

CALIBRATION_HUBS: Dict[str, Dict[str, Any]] = {
    "tulsa": {
        "name": "Tulsa Metro Area, OK",
        "region_id": "Tulsa_OK",
        "lat": 36.1540, "lon": -95.9928,
        "state": "OK", "padd": "PADD 2", "padd_name": "Midwest",
        "state_tax": 0.190, "max_radius_miles": 150.0
    },
    "cincinnati": {
        "name": "Cincinnati Tri-State Hub, OH/KY/IN",
        "region_id": "Cincinnati_OH",
        "lat": 39.1031, "lon": -84.5120,
        "state": "OH", "padd": "PADD 2", "padd_name": "Midwest",
        "state_tax": 0.385, "max_radius_miles": 150.0
    },
    "newark": {
        "name": "Newark Metro Area, NJ / NY Harbor",
        "region_id": "Newark_DE",
        "lat": 39.5743, "lon": -75.5908,
        "state": "NJ", "padd": "PADD 1B", "padd_name": "Central Atlantic",
        "state_tax": 0.423, "max_radius_miles": 150.0
    },
    "oakland": {
        "name": "Oakland / East Bay, CA",
        "region_id": "Oakland_CA",
        "lat": 37.8044, "lon": -122.2712,
        "state": "CA", "padd": "PADD 5", "padd_name": "West Coast",
        "state_tax": 0.596, "max_radius_miles": 75.0
    },
    "bayarea": {
        "name": "San Francisco Bay Area, CA",
        "region_id": "BayArea_CA",
        "lat": 37.7749, "lon": -122.4194,
        "state": "CA", "padd": "PADD 5", "padd_name": "West Coast",
        "state_tax": 0.596, "max_radius_miles": 100.0
    },
    "charlotte": {
        "name": "Charlotte Metro Area, NC",
        "region_id": "Charlotte_NC",
        "lat": 35.2271, "lon": -80.8431,
        "state": "NC", "padd": "PADD 1C", "padd_name": "Lower Atlantic",
        "state_tax": 0.404, "max_radius_miles": 120.0
    },
    "greenville": {
        "name": "Greenville-Spartanburg, SC (Colonial Pipeline)",
        "region_id": "Greenville_NC",
        "lat": 35.6127, "lon": -77.3664,
        "state": "NC", "padd": "PADD 1C", "padd_name": "Lower Atlantic",
        "state_tax": 0.404, "max_radius_miles": 120.0
    },
    "port_st_lucie": {
        "name": "Port St. Lucie / Treasure Coast, FL",
        "region_id": "Port_St_Lucie_FL",
        "lat": 27.2730, "lon": -80.3582,
        "state": "FL", "padd": "PADD 1C", "padd_name": "Lower Atlantic",
        "state_tax": 0.362, "max_radius_miles": 120.0
    },
}

ZIP_METRO_PREFIX_MAP: Dict[str, str] = {
    "740": "tulsa", "741": "tulsa", "742": "tulsa", "743": "tulsa",
    "197": "newark", "198": "newark", "199": "newark",
    "450": "cincinnati", "451": "cincinnati", "452": "cincinnati",
    "278": "greenville", "279": "greenville",
    "280": "charlotte", "281": "charlotte", "282": "charlotte",
    "945": "oakland", "946": "oakland",
    "349": "port_st_lucie",
    "940": "bayarea", "941": "bayarea", "942": "bayarea", "943": "bayarea", "944": "bayarea"
}


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two GPS coordinates in statute miles."""
    r_miles = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2.0) ** 2
    return r_miles * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def resolve_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """Resolve GPS coordinates to closest refining hub."""
    try:
        f_lat, f_lon = float(lat), float(lon)
    except (ValueError, TypeError):
        return {"locale_code": "national", "name": "National Wholesale", "distance_miles": None}

    best_key = "national"
    best_dist = float("inf")
    best_meta = None

    for key, meta in CALIBRATION_HUBS.items():
        dist = haversine_miles(f_lat, f_lon, meta["lat"], meta["lon"])
        if dist < best_dist:
            best_dist, best_key, best_meta = dist, key, meta

    if best_meta:
        is_metro = best_dist <= best_meta.get("max_radius_miles", 120.0)
        return {
            "locale_code": best_key,
            "region_id": best_meta["region_id"],
            "name": best_meta["name"],
            "distance_miles": round(best_dist, 1),
            "is_metro_cluster_hit": is_metro,
            "padd_region": best_meta["padd"],
            "state": best_meta["state"]
        }
    return {"locale_code": "national", "name": "National Wholesale", "distance_miles": None}


def resolve_zip(zip_code: str) -> Dict[str, Any]:
    """Resolve 5-digit US ZIP code to matching metro hub."""
    clean = str(zip_code).strip().split("-")[0].zfill(5)[:5]
    prefix = clean[:3]
    if prefix in ZIP_METRO_PREFIX_MAP:
        loc = ZIP_METRO_PREFIX_MAP[prefix]
        meta = CALIBRATION_HUBS.get(loc, {})
        return {
            "locale_code": loc,
            "region_id": meta.get("region_id", loc.capitalize()),
            "name": meta.get("name", loc.capitalize()),
            "is_metro_cluster_hit": True,
            "zip_code": clean
        }
    return {"locale_code": "national", "name": f"US Average (Zip {clean})", "is_metro_cluster_hit": False, "zip_code": clean}
