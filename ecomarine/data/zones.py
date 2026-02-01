"""ECA Zones data loader and metadata module.

This module loads ECA zone polygons from the shapefile and provides
metadata for each zone including sulphur limits, regulations, and bounding boxes.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import shapefile

from ..classes.area_feature import AreaFeature

logger = logging.getLogger(__name__)

# Zone metadata mapping based on shapefile area names
# Format: area_name -> {type, sulphur_limit, regulation, year_established, territory}
ZONE_METADATA: dict[str, dict[str, Any]] = {
    "Baltic Sea area": {
        "name": "Baltic Sea SECA",
        "type": "seca",
        "year_established": 2006,
        "required_sulphur": "0.1%",
        "regulation": "IMO 2020",
        "territory": "EU",
        "status": "active",
    },
    "United States Caribbean sea area": {
        "name": "United States Caribbean ECA",
        "type": "eca",
        "year_established": 2014,
        "required_sulphur": "0.1%",
        "regulation": "EPA",
        "territory": "US Caribbean",
        "status": "active",
    },
    "North American area 1": {
        "name": "North American ECA 1 (East Coast)",
        "type": "eca",
        "year_established": 2014,
        "required_sulphur": "0.1%",
        "regulation": "EPA",
        "territory": "US East Coast & Canada",
        "status": "active",
    },
    "North American area 2": {
        "name": "North American ECA 2 (West Coast)",
        "type": "eca",
        "year_established": 2014,
        "required_sulphur": "0.1%",
        "regulation": "EPA",
        "territory": "US West Coast & Canada",
        "status": "active",
    },
    "North American area 3": {
        "name": "North American ECA 3 (Gulf Coast)",
        "type": "eca",
        "year_established": 2014,
        "required_sulphur": "0.1%",
        "regulation": "EPA",
        "territory": "US Gulf Coast & Mexico",
        "status": "active",
    },
    "North Sea area": {
        "name": "North Sea SECA",
        "type": "seca",
        "year_established": 2007,
        "required_sulphur": "0.1%",
        "regulation": "IMO 2020",
        "territory": "EU + UK",
        "status": "active",
    },
    "2513586.274558733": {  # Mediterranean has a numeric area field
        "name": "Mediterranean ECA",
        "type": "eca",
        "year_established": 2025,
        "required_sulphur": "0.5%",
        "regulation": "MARPOL Annex VI",
        "territory": "Mediterranean",
        "status": "active",
    },
}


@dataclass(frozen=True)
class ECAZone:
    """Represents an ECA zone with polygon and metadata.

    Attributes:
        area_feature: AreaFeature with polygon geometry
        metadata: Dictionary with zone metadata (name, type, sulphur limit, etc.)
    """

    area_feature: AreaFeature
    metadata: dict[str, Any]

    @property
    def name(self) -> str:
        """Return zone name."""
        return self.metadata.get("name", "Unknown")

    @property
    def zone_type(self) -> str:
        """Return zone type (seca or eca)."""
        return self.metadata.get("type", "unknown")

    @property
    def required_sulphur(self) -> str:
        """Return required sulphur limit."""
        return self.metadata.get("required_sulphur", "unknown")

    @property
    def regulation(self) -> str:
        """Return applicable regulation."""
        return self.metadata.get("regulation", "unknown")

    @property
    def territory(self) -> str:
        """Return zone territory."""
        return self.metadata.get("territory", "unknown")

    def contains(self, longitude: float, latitude: float) -> bool:
        """Check if point is inside this zone polygon.

        Args:
            longitude: Longitude in degrees (-180 to 180)
            latitude: Latitude in degrees (-90 to 90)

        Returns:
            True if point is inside zone, False otherwise
        """
        return self.area_feature.contains(longitude, latitude)

    def to_dict(self) -> dict[str, Any]:
        """Convert zone to dictionary representation."""
        return {
            "name": self.name,
            "type": self.zone_type,
            "year_established": self.metadata.get("year_established"),
            "required_sulphur": self.required_sulphur,
            "regulation": self.regulation,
            "territory": self.territory,
            "status": self.metadata.get("status", "active"),
            "bounding_box": self.metadata.get("bounding_box"),
        }


def _get_shapefile_path() -> Path:
    """Get path to ECA shapefile."""
    # Try multiple possible locations
    possible_paths = [
        Path("data/merged_eca.shp"),
        Path(__file__).parent.parent.parent / "data" / "merged_eca.shp",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Could not find merged_eca.shp. Searched in: " + ", ".join(str(p) for p in possible_paths)
    )


def _extract_polygons_from_shape(shape) -> list[list[list[float]]]:
    """Extract polygons from a shapefile shape.

    Shapefile polygons can have multiple parts (rings).
    Returns list of polygons, where each polygon is a list of [lon, lat] coordinates.
    """
    if not shape.parts:
        # Single polygon
        return [[list(point) for point in shape.points]]

    # Multiple parts - extract each ring
    polygons = []
    parts = list(shape.parts) + [len(shape.points)]

    for i in range(len(shape.parts)):
        start_idx = parts[i]
        end_idx = parts[i + 1]
        ring_points = shape.points[start_idx:end_idx]
        polygons.append([list(point) for point in ring_points])

    return polygons


def _calculate_bounding_box(points: list[tuple[float, float]]) -> dict[str, float]:
    """Calculate bounding box from list of (lon, lat) points."""
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    return {
        "min_lon": min(lons),
        "max_lon": max(lons),
        "min_lat": min(lats),
        "max_lat": max(lats),
    }


def load_eca_zones() -> list[ECAZone]:
    """Load ECA zones from shapefile.

    Returns:
        List of ECAZone objects with polygons and metadata

    Raises:
        FileNotFoundError: If shapefile cannot be found
    """
    shapefile_path = _get_shapefile_path()
    logger.info(f"Loading ECA zones from {shapefile_path}")

    sf = shapefile.Reader(str(shapefile_path))
    zones = []

    for _i, (shape, record) in enumerate(zip(sf.shapes(), sf.records(), strict=False)):
        area_name = record.area
        regulation = record.regulation

        # Get metadata for this zone
        metadata = ZONE_METADATA.get(area_name, {}).copy()
        if not metadata:
            logger.warning(f"No metadata found for zone: {area_name}")
            metadata = {
                "name": area_name,
                "type": "unknown",
                "required_sulphur": "unknown",
                "regulation": regulation,
                "territory": "unknown",
                "status": "active",
            }

        # Add regulation from shapefile if not in metadata
        if "regulation" not in metadata or metadata["regulation"] == "unknown":
            metadata["regulation"] = regulation

        # Calculate bounding box
        bbox = _calculate_bounding_box(shape.points)
        metadata["bounding_box"] = bbox

        # Extract polygons from shape
        polygons = _extract_polygons_from_shape(shape)

        # For point-in-polygon, we use the first (main) polygon
        # Multi-part polygons can be handled if needed
        if polygons:
            main_polygon = polygons[0]
            # Ensure polygon is closed
            if main_polygon[0] != main_polygon[-1]:
                main_polygon.append(main_polygon[0])

            # Create AreaFeature with the polygon
            area_feature = AreaFeature(
                coordinates=[main_polygon],  # GeoJSON Polygon format
                name=metadata["name"],
                preferred_ports=[],
                zone_type=metadata["type"],
                sulphur_limit=metadata["required_sulphur"],
                regulation=metadata["regulation"],
                territory=metadata["territory"],
            )

            zone = ECAZone(area_feature=area_feature, metadata=metadata)
            zones.append(zone)
            logger.debug(f"Loaded zone: {zone.name} with {len(main_polygon)} points")

    logger.info(f"Loaded {len(zones)} ECA zones")
    return zones


# Module-level cache for zones
_zones_cache: list[ECAZone] | None = None


def get_eca_zones() -> list[ECAZone]:
    """Get list of all ECA zones.

    Returns cached zones on subsequent calls.

    Returns:
        List of ECAZone objects
    """
    global _zones_cache  # noqa: PLW0603

    if _zones_cache is None:
        _zones_cache = load_eca_zones()

    return _zones_cache


def get_eca_zones_metadata() -> list[dict[str, Any]]:
    """Get metadata for all ECA zones (without polygon geometry).

    Returns:
        List of zone metadata dictionaries
    """
    zones = get_eca_zones()
    return [zone.to_dict() for zone in zones]


def check_point_in_zones(longitude: float, latitude: float) -> ECAZone | None:
    """Check if a point is inside any ECA zone.

    Args:
        longitude: Longitude in degrees (-180 to 180)
        latitude: Latitude in degrees (-90 to 90)

    Returns:
        ECAZone if point is inside a zone, None otherwise
    """
    zones = get_eca_zones()

    for zone in zones:
        # Quick bbox check first for performance
        bbox = zone.metadata.get("bounding_box")
        if bbox and not (
            bbox["min_lon"] <= longitude <= bbox["max_lon"]
            and bbox["min_lat"] <= latitude <= bbox["max_lat"]
        ):
            continue

        # Detailed point-in-polygon check
        if zone.contains(longitude, latitude):
            return zone

    return None


# Export for backward compatibility
ECA_ZONES = get_eca_zones_metadata

if __name__ == "__main__":
    # Test loading zones
    logging.basicConfig(level=logging.DEBUG)
    zones = get_eca_zones()
    print(f"\nLoaded {len(zones)} ECA zones:\n")
    for zone in zones:
        print(f"  - {zone.name} ({zone.zone_type})")
        print(f"    Sulphur limit: {zone.required_sulphur}")
        print(f"    Regulation: {zone.regulation}")
        print(f"    Territory: {zone.territory}")
        bbox = zone.metadata.get("bounding_box")
        if bbox:
            print(
                f"    Bounding box: "
                f"lon({bbox['min_lon']:.2f} to {bbox['max_lon']:.2f}), "
                f"lat({bbox['min_lat']:.2f} to {bbox['max_lat']:.2f})"
            )
        print()
