"""Integration tests for ECA Marine API.

These are system/integration tests that test the entire API stack without mocking.
Tests use real data files and actual route calculations.

All tests can be run with: pytest tests/integration/ -v
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# =============================================================================
# Test Data - Real coordinates for known locations
# =============================================================================

# Port coordinates [latitude, longitude] - user-friendly format
ROTTERDAM = [51.9244, 4.4777]  # Netherlands
NEW_YORK = [40.7128, -74.0060]  # USA
SINGAPORE = [1.3521, 103.8198]  # Singapore
LONDON = [51.5074, -0.1278]  # UK
BARCELONA = [41.3851, 2.1734]  # Spain (Mediterranean)
STOCKHOLM = [59.3293, 18.0686]  # Sweden (Baltic Sea)
MIAMI = [25.7617, -80.1918]  # USA (Caribbean area)
LOS_ANGELES = [34.0522, -118.2437]  # USA (West Coast)
HOUSTON = [29.7604, -95.3698]  # USA (Gulf Coast)
DUBAI = [25.2048, 55.2708]  # UAE (outside ECA)
SYDNEY = [-33.8688, 151.2093]  # Australia (outside ECA)

# ECA test points [latitude, longitude]
NORTH_SEA_POINT = [54.5, 3.0]  # Inside North Sea SECA
BALTIC_SEA_POINT = [58.5, 20.0]  # Inside Baltic Sea SECA
MEDITERRANEAN_POINT = [40.0, 10.0]  # Inside Mediterranean ECA
CARIBBEAN_POINT = [18.0, -65.0]  # Inside US Caribbean ECA
# North American ECA zones from shapefile:
# Area 1: -154 to -117 lon (Gulf of Alaska/West Coast offshore waters)
# Area 2: -97 to -47 lon (Texas to Nova Scotia - East Coast & Gulf)
# Area 3: -163 to -151 lon (Aleutians/Hawaii)
# Note: ECA zones are in offshore waters, not directly at coastal cities
US_WEST_COAST_POINT = [55.0, -135.0]  # Gulf of Alaska - Inside North American ECA 1
US_EAST_COAST_POINT = [38.0, -75.0]  # Delaware coast - Inside North American ECA 2 (East/Gulf)
US_GULF_COAST_POINT = [28.0, -90.0]  # Gulf of Mexico - Inside North American ECA 2 (East/Gulf)
OUTSIDE_ECA_POINT = [25.0, 55.0]  # Dubai area - outside ECA


# =============================================================================
# Health Check Tests
# =============================================================================


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Test root health check endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ECA Marine API"
    assert "version" in data


# =============================================================================
# Route Calculation Tests
# =============================================================================


@pytest.mark.asyncio
async def test_calculate_route_rotterdam_to_new_york(client: AsyncClient) -> None:
    """Test route calculation from Rotterdam to New York.

    This is a classic Atlantic route that should go through:
    - English Channel
    - Atlantic Ocean
    - Past Nova Scotia
    - Into New York

    Expected to use no major passages (Suez/Panama) for Atlantic crossing.
    """
    payload = {
        "origin": ROTTERDAM,
        "destination": NEW_YORK,
        "restrictions": [],
        "include_explanation": False,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["origin"] == ROTTERDAM
    assert data["destination"] == NEW_YORK
    assert data["restrictions"] == []
    assert "distance_nm" in data
    assert "eca_distance_nm" in data
    assert "waypoints" in data
    assert isinstance(data["waypoints"], list)
    assert len(data["waypoints"]) > 0

    # Rotterdam to New York is ~3500-4000 nautical miles
    assert 3000 < data["distance_nm"] < 5000

    # Check waypoints are in [lat, lon] format
    first_waypoint = data["waypoints"][0]
    assert len(first_waypoint) == 2
    # First waypoint should be near Rotterdam
    assert 51 < first_waypoint[0] < 52  # latitude
    assert 4 < first_waypoint[1] < 5  # longitude


@pytest.mark.asyncio
async def test_calculate_route_singapore_to_rotterdam_via_suez(client: AsyncClient) -> None:
    """Test route from Singapore to Rotterdam via Suez Canal.

    This is a major East-West route that should traverse:
    - Strait of Malacca
    - Indian Ocean
    - Red Sea
    - Suez Canal
    - Mediterranean
    - Into Rotterdam
    """
    payload = {
        "origin": SINGAPORE,
        "destination": ROTTERDAM,
        "restrictions": [],
        "include_explanation": False,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["traversed_passage"] == "suez"
    assert data["distance_nm"] > 8000  # Long route


@pytest.mark.asyncio
async def test_calculate_route_with_suez_restriction(client: AsyncClient) -> None:
    """Test route from Singapore to Rotterdam with Suez restricted.

    Should force route around Cape of Good Hope (South Africa).
    This should result in a longer distance.
    """
    payload = {
        "origin": SINGAPORE,
        "destination": ROTTERDAM,
        "restrictions": ["suez"],
        "include_explanation": False,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    # Without Suez, traversed_passage should be null or different
    assert data["traversed_passage"] != "suez"
    # Route around Africa should be longer
    assert data["distance_nm"] > 10000


@pytest.mark.asyncio
async def test_calculate_route_us_west_to_asia(client: AsyncClient) -> None:
    """Test route from Los Angeles to Singapore.

    Should cross Pacific Ocean.
    """
    payload = {
        "origin": LOS_ANGELES,
        "destination": SINGAPORE,
        "restrictions": [],
        "include_explanation": False,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["distance_nm"] > 7000  # Pacific crossing


@pytest.mark.asyncio
async def test_calculate_route_invalid_coordinates(client: AsyncClient) -> None:
    """Test route calculation with invalid coordinates.

    Should return 400 Bad Request for out-of-bounds coordinates.
    """
    # Test invalid latitude (>90)
    payload = {
        "origin": [95.0, 0.0],  # Invalid latitude
        "destination": NEW_YORK,
    }
    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 400
    assert "latitude" in response.json()["detail"].lower()

    # Test invalid longitude (>180)
    payload = {
        "origin": ROTTERDAM,
        "destination": [0.0, 200.0],  # Invalid longitude
    }
    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 400
    assert "longitude" in response.json()["detail"].lower()


# =============================================================================
# ECA Zone Point Checking Tests
# =============================================================================


@pytest.mark.asyncio
async def test_check_point_inside_north_sea_eca(client: AsyncClient) -> None:
    """Test checking a point inside North Sea SECA."""
    response = await client.get(
        "/check-point",
        params={"latitude": NORTH_SEA_POINT[0], "longitude": NORTH_SEA_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    assert "North Sea" in data["zone_name"]
    assert data["zone_type"] == "seca"
    assert data["required_sulphur"] == "0.1%"
    assert data["regulation"] == "IMO 2020"


@pytest.mark.asyncio
async def test_check_point_inside_baltic_sea_eca(client: AsyncClient) -> None:
    """Test checking a point inside Baltic Sea SECA."""
    response = await client.get(
        "/check-point",
        params={"latitude": BALTIC_SEA_POINT[0], "longitude": BALTIC_SEA_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    assert "Baltic" in data["zone_name"]
    assert data["zone_type"] == "seca"


@pytest.mark.asyncio
async def test_check_point_inside_mediterranean_eca(client: AsyncClient) -> None:
    """Test checking a point inside Mediterranean ECA."""
    response = await client.get(
        "/check-point",
        params={"latitude": MEDITERRANEAN_POINT[0], "longitude": MEDITERRANEAN_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    assert "Mediterranean" in data["zone_name"]
    assert data["zone_type"] == "eca"
    assert data["required_sulphur"] == "0.5%"


@pytest.mark.asyncio
async def test_check_point_inside_caribbean_eca(client: AsyncClient) -> None:
    """Test checking a point inside US Caribbean ECA."""
    response = await client.get(
        "/check-point",
        params={"latitude": CARIBBEAN_POINT[0], "longitude": CARIBBEAN_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    assert "Caribbean" in data["zone_name"]
    assert data["regulation"] == "EPA"


@pytest.mark.asyncio
async def test_check_point_inside_us_west_coast_eca(client: AsyncClient) -> None:
    """Test checking a point inside North American ECA 1 (West Coast).

    Note: Shapefile Area 1 covers Alaska to Washington (West Coast).
    """
    response = await client.get(
        "/check-point",
        params={"latitude": US_WEST_COAST_POINT[0], "longitude": US_WEST_COAST_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    assert "North American ECA 1" in data["zone_name"] or "West Coast" in data["zone_name"]


@pytest.mark.asyncio
async def test_check_point_inside_us_east_coast_eca(client: AsyncClient) -> None:
    """Test checking a point inside North American ECA 2 (East Coast & Gulf).

    Note: Shapefile Area 2 covers East Coast and Gulf of Mexico.
    """
    response = await client.get(
        "/check-point",
        params={"latitude": US_EAST_COAST_POINT[0], "longitude": US_EAST_COAST_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    # ECA 2 covers both East Coast and Gulf
    assert "North American ECA 2" in data["zone_name"]


@pytest.mark.asyncio
async def test_check_point_inside_us_gulf_coast_eca(client: AsyncClient) -> None:
    """Test checking a point inside North American ECA 2 (Gulf Coast).

    Note: Shapefile Area 2 covers both East Coast and Gulf of Mexico.
    Gulf Coast points will match ECA 2, not ECA 3.
    """
    response = await client.get(
        "/check-point",
        params={"latitude": US_GULF_COAST_POINT[0], "longitude": US_GULF_COAST_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is True
    # Gulf Coast is covered by ECA 2 in the shapefile
    assert "North American ECA 2" in data["zone_name"]


@pytest.mark.asyncio
async def test_check_point_outside_all_eca_zones(client: AsyncClient) -> None:
    """Test checking a point outside all ECA zones (Dubai area)."""
    response = await client.get(
        "/check-point",
        params={"latitude": OUTSIDE_ECA_POINT[0], "longitude": OUTSIDE_ECA_POINT[1]},
    )
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert data["inside_eca"] is False
    assert "zone_name" not in data


@pytest.mark.asyncio
async def test_check_point_invalid_coordinates(client: AsyncClient) -> None:
    """Test check-point with invalid coordinates.

    FastAPI should auto-validate bounds and return 422.
    """
    # Invalid latitude > 90
    response = await client.get("/check-point", params={"latitude": 95.0, "longitude": 0.0})
    assert response.status_code == 422

    # Invalid latitude < -90
    response = await client.get("/check-point", params={"latitude": -95.0, "longitude": 0.0})
    assert response.status_code == 422

    # Invalid longitude > 180
    response = await client.get("/check-point", params={"latitude": 0.0, "longitude": 200.0})
    assert response.status_code == 422

    # Invalid longitude < -180
    response = await client.get("/check-point", params={"latitude": 0.0, "longitude": -200.0})
    assert response.status_code == 422


# =============================================================================
# Supported Zones Tests
# =============================================================================


@pytest.mark.asyncio
async def test_supported_zones_endpoint(client: AsyncClient) -> None:
    """Test /supported-zones endpoint returns all ECA zones."""
    response = await client.get("/supported-zones")
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    assert "zones" in data
    assert "count" in data
    assert data["count"] == 7
    assert len(data["zones"]) == 7

    # Check each zone has required fields
    zone_names = []
    for zone in data["zones"]:
        assert "name" in zone
        assert "type" in zone
        assert "required_sulphur" in zone
        assert "regulation" in zone
        assert "territory" in zone
        assert "status" in zone
        assert "bounding_box" in zone
        zone_names.append(zone["name"])

    # Verify all expected zones are present
    expected_zones = [
        "Baltic Sea SECA",
        "United States Caribbean ECA",
        "North American ECA 1",
        "North American ECA 2",
        "North American ECA 3",
        "North Sea SECA",
        "Mediterranean ECA",
    ]
    for expected in expected_zones:
        assert any(expected in name for name in zone_names), f"Missing zone: {expected}"


@pytest.mark.asyncio
async def test_supported_zones_sulphur_limits(client: AsyncClient) -> None:
    """Test that zones have correct sulphur limits."""
    response = await client.get("/supported-zones")
    data: dict[str, Any] = response.json()

    zones_by_name = {z["name"]: z for z in data["zones"]}

    # Check specific sulphur limits
    assert zones_by_name["Baltic Sea SECA"]["required_sulphur"] == "0.1%"
    assert zones_by_name["North Sea SECA"]["required_sulphur"] == "0.1%"
    assert zones_by_name["Mediterranean ECA"]["required_sulphur"] == "0.5%"

    # All North American ECAs should be 0.1%
    assert zones_by_name["United States Caribbean ECA"]["required_sulphur"] == "0.1%"


@pytest.mark.asyncio
async def test_supported_zones_bounding_boxes(client: AsyncClient) -> None:
    """Test that all zones have valid bounding boxes."""
    response = await client.get("/supported-zones")
    data: dict[str, Any] = response.json()

    for zone in data["zones"]:
        bbox = zone["bounding_box"]
        assert bbox is not None
        assert "min_lon" in bbox
        assert "max_lon" in bbox
        assert "min_lat" in bbox
        assert "max_lat" in bbox

        # Verify bounds are valid
        assert -180 <= bbox["min_lon"] <= 180
        assert -180 <= bbox["max_lon"] <= 180
        assert -90 <= bbox["min_lat"] <= 90
        assert -90 <= bbox["max_lat"] <= 90
        assert bbox["min_lon"] <= bbox["max_lon"]
        assert bbox["min_lat"] <= bbox["max_lat"]


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================


@pytest.mark.asyncio
async def test_route_with_multiple_restrictions(client: AsyncClient) -> None:
    """Test route with multiple passage restrictions."""
    payload = {
        "origin": SINGAPORE,
        "destination": LONDON,
        "restrictions": ["suez", "panama"],  # Block both major canals
        "include_explanation": False,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()
    # Route should not use Suez or Panama
    assert data["traversed_passage"] not in ["suez", "panama"]


@pytest.mark.asyncio
async def test_route_coordinate_format(client: AsyncClient) -> None:
    """Test that API accepts [lat, lon] and returns waypoints in [lat, lon]."""
    payload = {
        "origin": ROTTERDAM,
        "destination": LONDON,
    }

    response = await client.post("/calculate_route", json=payload)
    assert response.status_code == 200

    data: dict[str, Any] = response.json()

    # Verify origin/destination are returned as provided ([lat, lon])
    assert data["origin"] == ROTTERDAM
    assert data["destination"] == LONDON

    # Verify waypoints are in [lat, lon] format
    # First waypoint should have reasonable latitude for North Sea
    first_waypoint = data["waypoints"][0]
    assert 45 < first_waypoint[0] < 60  # Latitude range
    assert -10 < first_waypoint[1] < 10  # Longitude range (Europe)


@pytest.mark.asyncio
async def test_round_trip_route_symmetry(client: AsyncClient) -> None:
    """Test that route distance is similar in both directions."""
    # Rotterdam to New York
    payload_fwd = {"origin": ROTTERDAM, "destination": NEW_YORK}
    response_fwd = await client.post("/calculate_route", json=payload_fwd)
    data_fwd = response_fwd.json()

    # New York to Rotterdam (reverse)
    payload_rev = {"origin": NEW_YORK, "destination": ROTTERDAM}
    response_rev = await client.post("/calculate_route", json=payload_rev)
    data_rev = response_rev.json()

    # Distances should be very close (within 1%)
    assert abs(data_fwd["distance_nm"] - data_rev["distance_nm"]) / data_fwd["distance_nm"] < 0.01


# =============================================================================
# Performance Tests (Basic)
# =============================================================================


@pytest.mark.asyncio
async def test_endpoint_response_times(client: AsyncClient) -> None:
    """Test that endpoints respond within reasonable time.

    This is a basic smoke test to catch major performance regressions.
    """
    import time

    # Test health endpoint
    start = time.time()
    response = await client.get("/")
    health_time = time.time() - start
    assert response.status_code == 200
    assert health_time < 1.0  # Should be instant

    # Test supported zones (cached)
    start = time.time()
    response = await client.get("/supported-zones")
    zones_time = time.time() - start
    assert response.status_code == 200
    assert zones_time < 1.0  # Should be fast after initial load

    # Test check-point
    start = time.time()
    response = await client.get(
        "/check-point",
        params={"latitude": NORTH_SEA_POINT[0], "longitude": NORTH_SEA_POINT[1]},
    )
    check_time = time.time() - start
    assert response.status_code == 200
    assert check_time < 2.0  # Point-in-polygon should be reasonably fast
