"""ECA Marine API - Main FastAPI Application.

Provides endpoints for:
- Marine route calculation between two points
- ECA zone point checking
- Supported ECA zones listing
"""

import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ecomarine import searoute
from ecomarine.classes.passages import Passage
from ecomarine.data.zones import check_point_in_zones, get_eca_zones_metadata

app = FastAPI(
    title="ECA Marine API",
    description="API for calculating marine routes and checking ECA zone compliance",
    version="0.1.0",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def suez_tool_calulator():
    pass


def panama_tool_calulator():
    pass


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "ECA Marine API", "version": "0.1.0"}


@app.get("/ping")
def ping():
    """Lightweight health check endpoint for monitoring services.

    Returns simple status for load balancers and health check services.
    """
    return {"status": "ok"}


# Define request model for route calculation
class RouteRequest(BaseModel):
    """Request model for route calculation.

    Coordinates are in [latitude, longitude] format for user-friendliness.
    These are converted internally to [longitude, latitude] for the searoute function.
    """

    origin: list[float] = Field(
        ...,
        description="Origin coordinates as [latitude, longitude]. Example: [51.9, 4.5] for Rotterdam",
        min_length=2,
        max_length=2,
    )
    destination: list[float] = Field(
        ...,
        description="Destination coordinates as [latitude, longitude]. Example: [40.7, -74.0] for New York",
        min_length=2,
        max_length=2,
    )
    restrictions: list[str] = Field(
        default=[],
        description="List of passage restrictions. Options: suez, panama, gibraltar, ormuz, northwest, babalmandab, bosporus, chili",
    )
    include_explanation: bool = Field(
        default=False,
        description="Include AI-generated route analysis (not implemented)",
    )


def validate_coordinates(lat: float, lon: float, field_name: str) -> None:
    """Validate latitude and longitude values.

    Args:
        lat: Latitude value
        lon: Longitude value
        field_name: Name of the field for error messages

    Raises:
        HTTPException: If coordinates are invalid
    """
    if not -90 <= lat <= 90:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} latitude: {lat}. Must be between -90 and 90.",
        )
    if not -180 <= lon <= 180:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} longitude: {lon}. Must be between -180 and 180.",
        )


def convert_to_lonlat(latlon: list[float]) -> tuple[float, float]:
    """Convert [lat, lon] to (lon, lat) format for internal processing.

    The API accepts [lat, lon] for user-friendliness, but searoute expects [lon, lat].

    Args:
        latlon: List in [latitude, longitude] format

    Returns:
        Tuple in (longitude, latitude) format
    """
    return (latlon[1], latlon[0])


async def get_marine_route(
    origin: list[float],
    destination: list[float],
    restrictions: list[str] | None = None,
    explanation: bool = False,
) -> dict:
    """Calculate marine route between two points with optional restrictions.

    Args:
        origin: Origin coordinates as [latitude, longitude]
        destination: Destination coordinates as [latitude, longitude]
        restrictions: List of passage restrictions
        explanation: Whether to include explanation (not implemented)

    Returns:
        Dictionary with route details including waypoints, distance, and ECA distance

    Raises:
        HTTPException: If coordinates are invalid or route calculation fails
    """
    restrictions = restrictions if restrictions else []

    # Validate coordinates
    validate_coordinates(origin[0], origin[1], "origin")
    validate_coordinates(destination[0], destination[1], "destination")

    # Convert from [lat, lon] to [lon, lat] for searoute
    origin_lonlat = list(convert_to_lonlat(origin))
    destination_lonlat = list(convert_to_lonlat(destination))

    try:
        # Fetch the sea route
        route = searoute(
            origin_lonlat,
            destination_lonlat,
            restrictions=restrictions,
            units="naut",
            include_ports=False,
            return_passages=True,
        )
    except Exception as e:
        logger.error(f"Route calculation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Route calculation failed: {str(e)}",
        ) from e

    # searoute returns coordinates in [lon, lat] format
    # Convert back to [lat, lon] for the API response
    coordinates = route["geometry"]["coordinates"]
    waypoints = [[lat, lon] for lon, lat in coordinates]

    # Extract route information
    distance = route["properties"]["length"]
    eca_distance = route["properties"].get("eca_distance", 0)
    all_traversed_passages = route["properties"].get("traversed_passages", [])

    # Determine primary traversed passage
    traversed_passage = None
    if Passage.suez in all_traversed_passages:
        traversed_passage = Passage.suez
    elif Passage.panama in all_traversed_passages:
        traversed_passage = Passage.panama

    return {
        "origin": origin,
        "destination": destination,
        "restrictions": restrictions,
        "traversed_passage": traversed_passage,
        "distance_nm": round(distance, 2),
        "eca_distance_nm": round(eca_distance, 2) if eca_distance else 0,
        "waypoints": waypoints,
    }


@app.post("/calculate_route")
async def calculate_route(request: RouteRequest) -> dict:
    """Calculate marine route between origin and destination.

    Coordinates should be provided as [latitude, longitude].
    The route avoids restricted passages if specified.

    Returns route details including:
    - waypoints: List of [lat, lon] coordinates along the route
    - distance_nm: Total distance in nautical miles
    - eca_distance_nm: Distance within ECA zones in nautical miles
    - traversed_passage: Primary passage used (suez, panama, or null)
    """
    return await get_marine_route(
        request.origin,
        request.destination,
        request.restrictions,
        request.include_explanation,
    )


@app.get("/check-point")
async def check_point(
    latitude: Annotated[
        float,
        Query(
            ...,
            ge=-90,
            le=90,
            description="Latitude in degrees (-90 to 90). Example: 58.5 for North Sea",
        ),
    ],
    longitude: Annotated[
        float,
        Query(
            ...,
            ge=-180,
            le=180,
            description="Longitude in degrees (-180 to 180). Example: 3.2 for North Sea",
        ),
    ],
) -> dict:
    """Check if coordinates are inside any ECA zone.

    Args:
        latitude: Latitude in degrees (-90 to 90)
        longitude: Longitude in degrees (-180 to 180)

    Returns:
        If inside ECA zone:
        {
            "inside_eca": true,
            "zone_name": "North Sea SECA",
            "zone_type": "seca",
            "required_sulphur": "0.1%",
            "regulation": "IMO 2020"
        }

        If outside all zones:
        {
            "inside_eca": false
        }
    """
    logger.info(f"Checking point: lat={latitude}, lon={longitude}")

    zone = check_point_in_zones(longitude, latitude)

    if zone:
        return {
            "inside_eca": True,
            "zone_name": zone.name,
            "zone_type": zone.zone_type,
            "required_sulphur": zone.required_sulphur,
            "regulation": zone.regulation,
            "territory": zone.territory,
        }

    return {"inside_eca": False}


@app.get("/supported-zones")
async def supported_zones() -> dict:
    """Get list of all supported ECA zones with metadata.

    Returns:
        {
            "zones": [
                {
                    "name": "North Sea SECA",
                    "type": "seca",
                    "year_established": 2007,
                    "required_sulphur": "0.1%",
                    "regulation": "IMO 2020",
                    "territory": "EU + UK",
                    "status": "active",
                    "bounding_box": {
                        "min_lon": -5.0,
                        "max_lon": 10.0,
                        "min_lat": 50.0,
                        "max_lat": 62.0
                    }
                },
                ...
            ],
            "count": 7,
            "last_updated": "2025-02-01"
        }
    """
    zones = get_eca_zones_metadata()

    return {
        "zones": zones,
        "count": len(zones),
    }
