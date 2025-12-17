from shapely.geometry import LineString, Polygon
from citygen.models import CityLayout



from shapely.geometry import mapping


def feature(geom, properties: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": properties or {},
    }


def city_layout_to_geojson(layout: CityLayout) -> dict:
    features = []

    # --- главная магистраль ---
    for road in layout.main_street_roads:
        features.append(feature(
            road,
            {"type": "main_road"}
        ))

    # --- все дороги ---
    for road in layout.all_roads:
        features.append(feature(
            road,
            {"type": "road"}
        ))

    # --- дома ---
    for block in layout.blocks:
        for house in block.houses:
            features.append(feature(
                house,
                {"type": "house"}
            ))

    # --- парк ---
    features.append(feature(
        layout.park_polygon,
        {"type": "park"}
    ))

    return {
        "type": "FeatureCollection",
        "features": features
    }
