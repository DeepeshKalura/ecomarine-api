# Ecomarine API Test Cases

This document contains all test cases extracted from Python integration tests.

## Test Summary

- **Total Tests**: 14
- **Endpoints Covered**: 5

## Tests by Endpoint

### /

1. **Root Endpoint (GET /)**
   - Description: Test root health check endpoint.
   - Method: GET
   - Expected Status: 200

2. **Endpoint Response Times (GET /)**
   - Description: Test that endpoints respond within reasonable time.

This is a basic smoke test to catch major performance regressions.
   - Method: GET
   - Expected Status: 200
   - Params: `{
  "latitude": 54.5,
  "longitude": 3.0
}`

### /ping

1. **Ping Endpoint (GET /ping)**
   - Description: Test lightweight /ping health check endpoint for monitoring.
   - Method: GET
   - Expected Status: 200

### /calculate_route

1. **Calculate Route Rotterdam To New York (POST /calculate_route)**
   - Description: Test route calculation from Rotterdam to New York.

This is a classic Atlantic route that should go through:
- English Channel
- Atlantic Ocean
- Past Nova Scotia
- Into New York

Expected to use no major passages (Suez/Panama) for Atlantic crossing.
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    51.9244,
    4.4777
  ],
  "destination": [
    40.7128,
    -74.006
  ],
  "restrictions": [],
  "include_explanation": false
}`

2. **Calculate Route Singapore To Rotterdam Via Suez (POST /calculate_route)**
   - Description: Test route from Singapore to Rotterdam via Suez Canal.

This is a major East-West route that should traverse:
- Strait of Malacca
- Indian Ocean
- Red Sea
- Suez Canal
- Mediterranean
- Into Rotterdam
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    1.3521,
    103.8198
  ],
  "destination": [
    51.9244,
    4.4777
  ],
  "restrictions": [],
  "include_explanation": false
}`

3. **Calculate Route With Suez Restriction (POST /calculate_route)**
   - Description: Test route from Singapore to Rotterdam with Suez restricted.

Should force route around Cape of Good Hope (South Africa).
This should result in a longer distance.
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    1.3521,
    103.8198
  ],
  "destination": [
    51.9244,
    4.4777
  ],
  "restrictions": [
    "suez"
  ],
  "include_explanation": false
}`

4. **Calculate Route Us West To Asia (POST /calculate_route)**
   - Description: Test route from Los Angeles to Singapore.

Should cross Pacific Ocean.
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    34.0522,
    -118.2437
  ],
  "destination": [
    1.3521,
    103.8198
  ],
  "restrictions": [],
  "include_explanation": false
}`

5. **Calculate Route Invalid Coordinates (POST /calculate_route)**
   - Description: Test route calculation with invalid coordinates.

Should return 400 Bad Request for out-of-bounds coordinates.
   - Method: POST
   - Expected Status: 400
   - Payload: `{
  "origin": "[95.0",
  "destination": [
    40.7128,
    -74.006
  ]
}`

6. **Route With Multiple Restrictions (POST /calculate_route)**
   - Description: Test route with multiple passage restrictions.
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    1.3521,
    103.8198
  ],
  "destination": [
    51.5074,
    -0.1278
  ],
  "restrictions": "[\"suez\"",
  "include_explanation": false
}`

7. **Route Coordinate Format (POST /calculate_route)**
   - Description: Test that API accepts [lat, lon] and returns waypoints in [lat, lon].
   - Method: POST
   - Expected Status: 200
   - Payload: `{
  "origin": [
    51.9244,
    4.4777
  ],
  "destination": [
    51.5074,
    -0.1278
  ]
}`

### /check-point

1. **Check Point Invalid Coordinates (GET /check-point)**
   - Description: Test check-point with invalid coordinates.

FastAPI should auto-validate bounds and return 422.
   - Method: GET
   - Expected Status: 422

### /supported-zones

1. **Supported Zones Endpoint (GET /supported-zones)**
   - Description: Test /supported-zones endpoint returns all ECA zones.
   - Method: GET
   - Expected Status: 200

2. **Supported Zones Sulphur Limits (GET /supported-zones)**
   - Description: Test that zones have correct sulphur limits.
   - Method: GET
   - Expected Status: 200

3. **Supported Zones Bounding Boxes (GET /supported-zones)**
   - Description: Test that all zones have valid bounding boxes.
   - Method: GET
   - Expected Status: 200

