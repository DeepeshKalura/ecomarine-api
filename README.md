# Ecomarine API

ECA Distance & Compliance API for Maritime Routes

## Overview

Ecomarine API calculates distances within Emission Control Areas (ECAs), helping shipping companies, logistics providers, and maritime software accurately estimate fuel costs under IMO 2020 low-sulphur regulations.

## Features

- 🚢 Calculate marine routes with ECA distance calculations
- 📍 Check if coordinates are inside ECA zones
- 🌍 List all supported ECA zones (Baltic Sea, North Sea, Mediterranean, etc.)
- 💰 Fuel cost impact estimates
- ✅ IMO 2020 compliance data

## API Endpoints

### POST /calculate-route-eca
Calculate marine route with ECA distance & compliance data.

### GET /check-point
Check if coordinates are inside any ECA zone.

### GET /supported-zones
List all supported ECA zones.

## Deployment

Deployed on Leapcell - Serverless platform for Python FastAPI applications.

## Status

🚧 **In Development** - See [Issues](../../issues) for current bugs and improvements

## License

MIT
