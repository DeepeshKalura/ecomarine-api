# Ecomarine API: Standardized Launch System

## Executive Summary

**Strategy:** Create a replicable system to launch multiple APIs quickly on Leapcell (free tier) → RapidAPI marketplace. Test which get traction, then double down on winners.

**Current API:** Ecomarine API (ECA Distance & Compliance)  
**Deployment:** Leapcell Free Tier (20 projects, 3 vCPUs, 4GB RAM)  
**Marketplace:** RapidAPI (first), then expand based on traction  
**Goal:** Standardized template for launching APIs fast, measuring market demand, scaling winners

---

## 1. WHY LEAPCELL IS PERFECT FOR YOU

### Free Tier Benefits:
- ✅ **20 projects** - Launch 20 different APIs
- ✅ **3 vCPUs + 4GB RAM** per project - More than enough for FastAPI
- ✅ **100,000 invocations/month** - Covers free + early paid users
- ✅ **Serverless** - $0 when idle, scales automatically
- ✅ **No credit card** - True $0 startup
- ✅ **Fast deploy** - Git push → Live in 2 minutes
- ✅ **Auto HTTPS** - SSL certificates included
- ✅ **Global CDN** - Fast worldwide

### Why Not Cloudflare Workers?
- ❌ Python support is experimental/complex
- ❌ Needs Wrangler CLI + WASM bindings
- ❌ Your dependencies (networkx, geojson) don't work in Workers
- ❌ More setup time (3-5 days vs 1 day)

**Winner:** Leapcell = FastAPI works natively, zero config

---

## 2. STANDARDIZED API TEMPLATE ARCHITECTURE

### Reusable Structure (Copy-Paste for Each New API):

```
ecomarine-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + endpoints
│   ├── models.py            # Pydantic models
│   ├── services.py          # Business logic
│   └── config.py            # Settings + env vars
├── data/
│   ├── __init__.py
│   └── zones.py             # ECA polygon data (you have this!)
├── tests/
│   └── test_api.py
├── requirements.txt
├── .env.example
├── .gitignore
├── leapcell.yaml            # Deployment config (optional)
└── README.md
```

### Core Files Template:

#### 1. `requirements.txt` (Standard for all APIs)
```txt
# Core FastAPI
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

# Data processing
networkx>=3.0
geojson>=3.0.0
shapely>=2.0.0

# HTTP client
httpx>=0.24.0

# Utilities
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Monitoring (optional)
sentry-sdk>=1.30.0
```

#### 2. `app/config.py` (Reusable config loader)
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Config
    API_NAME: str = "Ecomarine API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Pricing Tiers
    FREE_TIER_REQUESTS: int = 50
    SOLO_TIER_REQUESTS: int = 2000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

#### 3. `app/models.py` (Standardized request/response models)
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class VesselType(str, Enum):
    CONTAINER = "container"
    TANKER = "tanker"
    BULK = "bulk"
    CRUISE = "cruise"
    GENERAL = "general"

class Coordinates(BaseModel):
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")

class RouteRequest(BaseModel):
    origin: Coordinates
    destination: Coordinates
    vessel_type: VesselType = VesselType.GENERAL
    include_waypoints: bool = True
    fuel_price_low_sulfur_usd_per_tonne: Optional[float] = Field(None, ge=0)
    fuel_price_high_sulfur_usd_per_tonne: Optional[float] = Field(None, ge=0)

class ECAZoneInfo(BaseModel):
    name: str
    zone_type: Literal["seca", "eca"]
    required_sulphur: str
    regulation: str
    start_nm: float
    end_nm: float

class FuelImpact(BaseModel):
    price_difference_usd_per_tonne: float
    total_extra_cost_usd: float
    currency: str = "USD"
    low_sulfur_required_nm: float

class ComplianceInfo(BaseModel):
    status: Literal["seca", "eca", "none"]
    regulations: List[str]
    zones_traversed: List[ECAZoneInfo]
    imo_compliant: bool

class RouteResponse(BaseModel):
    total_distance_nm: float
    eca_distance_nm: float
    eca_percentage: float
    fuel_impact: FuelImpact
    compliance: ComplianceInfo
    route: dict
    calculations: dict
```

---

## 3. ECOMARINE API: SPECIFIC IMPLEMENTATION

### Endpoint 1: POST /calculate-route-eca

**What it does:** Calculate marine route with ECA distance & compliance

**Request:**
```json
{
  "origin": {"longitude": -0.1276, "latitude": 51.5074},
  "destination": {"longitude": -74.006, "latitude": 40.7128},
  "vessel_type": "container",
  "fuel_price_low_sulfur_usd_per_tonne": 850.0,
  "fuel_price_high_sulfur_usd_per_tonne": 650.0
}
```

**Response:**
```json
{
  "total_distance_nm": 3456.78,
  "eca_distance_nm": 892.34,
  "eca_percentage": 25.8,
  "fuel_impact": {
    "price_difference_usd_per_tonne": 200.0,
    "total_extra_cost_usd": 35118.0,
    "currency": "USD",
    "low_sulfur_required_nm": 892.34
  },
  "compliance": {
    "status": "seca",
    "regulations": ["IMO 2020", "EU_MRV"],
    "zones_traversed": [
      {
        "name": "North Sea SECA",
        "zone_type": "seca",
        "required_sulphur": "0.1%",
        "regulation": "IMO 2020",
        "start_nm": 156.2,
        "end_nm": 245.7
      }
    ],
    "imo_compliant": true
  },
  "route": {
    "origin": [-0.1276, 51.5074],
    "destination": [-74.006, 40.7128],
    "waypoints": [[...]]
  },
  "calculations": {
    "method": "Haversine over maritime network",
    "accuracy": "99%+ benchmarked"
  }
}
```

### Endpoint 2: GET /check-point

**What it does:** Check if coordinates are inside any ECA zone

**Request:** `GET /check-point?longitude=-1.5&latitude=52.0`

**Response:**
```json
{
  "inside_eca": true,
  "zone_name": "North Sea SECA",
  "zone_type": "seca",
  "required_sulphur": "0.1%",
  "regulation": "IMO 2020",
  "territory": "EU + UK",
  "year_established": 2015
}
```

**Implementation using your polygon data:**
```python
from shapely.geometry import Point, Polygon
from data.zones import ECA_ZONES_POLY  # You have this!

def check_point_in_eca(longitude: float, latitude: float):
    point = Point(longitude, latitude)
    
    for zone in ECA_ZONES_POLY:
        polygon = Polygon(zone['coordinates'])
        if polygon.contains(point):
            return {
                "inside_eca": True,
                "zone_name": zone['name'],
                "zone_type": zone['type'],
                "required_sulphur": zone['sulphur_limit'],
                "regulation": zone['regulation']
            }
    
    return {"inside_eca": False}
```

### Endpoint 3: GET /supported-zones

**What it does:** List all supported ECA zones

**Response:**
```json
{
  "zones": [
    {
      "name": "North Sea SECA",
      "type": "seca",
      "year_established": 2015,
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
    {
      "name": "Baltic Sea SECA",
      "type": "seca",
      "year_established": 2015,
      "required_sulphur": "0.1%",
      "regulation": "IMO 2020",
      "territory": "EU + Russia",
      "status": "active"
    },
    {
      "name": "Mediterranean ECA",
      "type": "eca",
      "year_established": 2020,
      "required_sulphur": "0.5%",
      "regulation": "IMO 2020",
      "territory": "Mediterranean coastal states",
      "status": "active"
    },
    {
      "name": "United States ECA",
      "type": "eca",
      "year_established": 2015,
      "required_sulphur": "0.1%",
      "regulation": "EPA",
      "territory": "USA East/West/Gulf coasts",
      "status": "active"
    }
  ],
  "count": 4,
  "last_updated": "2025-01-01"
}
```

---

## 4. RAPIDAPI INTEGRATION (Free Tier = Money Maker)

### Why RapidAPI + Your Strategy:

1. **Launch fast** - No marketing, just submit listing
2. **Test demand** - See which APIs get users
3. **Scale winners** - Invest time in APIs with traction
4. **Kill losers** - Abandon APIs with no demand
5. **Rinse & repeat** - Template makes new APIs easy

### RapidAPI Setup Checklist:

**Required for listing:**
- [ ] API Name: **Ecomarine API**
- [ ] Logo/Icon: 512x512px (ship + green leaf icon)
- [ ] Base URL: `https://your-app.leapcell.dev`
- [ ] Endpoints: 3 documented
- [ ] Pricing tiers configured
- [ ] Terms of Service
- [ ] Contact email
- [ ] Tags: maritime, shipping, ECA, compliance, distance

### Pricing Strategy (Solo Dev Optimized):

```
FREE TIER
⚡ 50 requests/month
- All endpoints
- No credit card
- Perfect for testing

SOLO ($19/month)
⚡ 2,000 requests/month  
- Fuel cost calculations
- Email support
- ~66 requests/day

GROWTH ($49/month)
⚡ 10,000 requests/month
- Bulk processing
- Priority support
- ~333 requests/day

SCALE ($149/month)
⚡ Unlimited requests
- Dedicated support
- Custom SLA
```

**Solo Dev Math:**
- Hosting (Leapcell free): $0
- At 10 customers @ $19: **$190/month profit**
- Time: ~2 hrs/week support
- Hourly rate: **$95/hour** (and grows!)

---

## 5. DEPLOYMENT: LEAPCELL STEP-BY-STEP

### Prerequisites:
- GitHub account
- Your API code ready

### Step 1: Prepare Code

**Structure:**
```
ecomarine-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── config.py
├── data/
│   └── zones.py          # Your ECA polygon data
├── requirements.txt
└── .gitignore
```

**`requirements.txt`:**
```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
networkx>=3.0
geojson>=3.0.0
shapely>=2.0.0
python-dotenv>=1.0.0
```

**`app/main.py`:**
```python
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.models import RouteRequest, RouteResponse
from app.services import calculate_route_eca, check_point_eca
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION,
    description="Calculate ECA distances & maritime compliance"
)

# CORS for web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": settings.API_NAME,
        "version": settings.API_VERSION,
        "endpoints": [
            "/calculate-route-eca",
            "/check-point", 
            "/supported-zones"
        ]
    }

@app.post("/calculate-route-eca", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    """Calculate marine route with ECA distance & compliance"""
    return calculate_route_eca(request)

@app.get("/check-point")
async def check_point(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90)
):
    """Check if coordinates are inside ECA zones"""
    return check_point_eca(longitude, latitude)

@app.get("/supported-zones")
async def get_supported_zones():
    """List all supported ECA zones"""
    from data.zones import ECA_ZONES
    return {"zones": ECA_ZONES, "count": len(ECA_ZONES)}
```

### Step 2: Push to GitHub

```bash
cd ecomarine-api
git init
git add .
git commit -m "Initial Ecomarine API"
git remote add origin https://github.com/YOUR_USERNAME/ecomarine-api.git
git push -u origin main
```

### Step 3: Deploy on Leapcell

1. **Sign up:** [leapcell.io](https://leapcell.io) (no credit card)
2. **Connect GitHub:** Dashboard → Connect GitHub
3. **New Service:**
   - Click "New Service"
   - Select `ecomarine-api` repo
   
4. **Configure:**
   
   | Field | Value |
   |-------|-------|
   | **Runtime** | Python 3.11 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port 8080` |
   | **Port** | `8080` |

5. **Click Deploy** → Wait 1-2 minutes

6. **Get URL:** `https://ecomarine-api-xxx.leapcell.dev`

### Step 4: Test Endpoints

```bash
# Test root
curl https://ecomarine-api-xxx.leapcell.dev/

# Test calculate route
curl -X POST https://ecomarine-api-xxx.leapcell.dev/calculate-route-eca \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"longitude": -0.1276, "latitude": 51.5074},
    "destination": {"longitude": -74.006, "latitude": 40.7128}
  }'

# Test check point
curl "https://ecomarine-api-xxx.leapcell.dev/check-point?longitude=-1.5&latitude=52.0"

# Test supported zones
curl https://ecomarine-api-xxx.leapcell.dev/supported-zones
```

### Step 5: Setup Monitoring (Free)

**UptimeRobot:**
- Free: 50 monitors
- Check every 5 minutes
- Alerts via email/Slack

**Sentry:**
- Free: 10k events/month
- Error tracking
- Performance monitoring

```python
# Add to app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

---

## 6. STANDARDIZED LAUNCH PROCESS (Copy for Each API)

### Template: Launch Any API in 1 Day

#### Day 1 Morning (4 hours):
**Hour 1:** Code the API
- Copy template structure
- Implement endpoints
- Add your data/logic
- Test locally

**Hour 2:** Deploy to Leapcell
- Push to GitHub
- Create Leapcell service
- Deploy
- Test live endpoints

**Hour 3:** RapidAPI listing
- Create RapidAPI account
- Write listing copy
- Set pricing tiers
- Submit for approval

**Hour 4:** Documentation
- Write README
- Add code examples (Python, JS, cURL)
- Create FAQ
- Set up monitoring

#### Day 1 Afternoon:
- Share on LinkedIn, Reddit r/shipping
- Email 3 potential users
- Fix any initial bugs
- Celebrate launch 🎉

### Multi-API Strategy:

**Month 1:** Launch 2-3 APIs
- Ecomarine API (ECA compliance)
- API #2 (port data? route optimization?)
- API #3 (fuel prices? weather?)

**Month 2-3:** Measure traction
- Which APIs get signups?
- Which get paid conversions?
- Which get support tickets?

**Month 4+:** Double down on winners
- Add features to successful APIs
- Market them more
- Sunset losers
- Launch 1-2 new APIs per month

---

## 7. INFRASTRUCTURE AS CODE (Optional but Smart)

### Why IaaS for Leapcell?

**Benefits:**
- ✅ Replicable deployments
- ✅ Version control for infrastructure
- ✅ Easy to clone API setups
- ✅ Terraform state tracks everything
- ✅ Migration path to AWS/GCP later

**Approach:** Python-based IaaS (easier than Terraform for solo dev)

### Python IaaS Setup:

**`deploy.py`:**
```python
import os
import requests
from typing import Dict, Any

LEAPCELL_API_KEY = os.getenv("LEAPCELL_API_KEY")

class LeapcellDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.leapcell.io/v1"
    
    def create_service(self, config: Dict[str, Any]):
        """Create new service from config"""
        endpoint = f"{self.base_url}/services"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(endpoint, json=config, headers=headers)
        return response.json()
    
    def deploy_from_github(self, repo_url: str, branch: str = "main"):
        """Deploy service from GitHub repo"""
        config = {
            "name": "ecomarine-api",
            "repo_url": repo_url,
            "branch": branch,
            "runtime": "python3.11",
            "build_command": "pip install -r requirements.txt",
            "start_command": "uvicorn app.main:app --host 0.0.0.0 --port 8080",
            "port": 8080,
            "env_vars": {
                "API_NAME": "Ecomarine API",
                "DEBUG": "false"
            }
        }
        return self.create_service(config)

# Usage
if __name__ == "__main__":
    deployer = LeapcellDeployer(os.getenv("LEAPCELL_API_KEY"))
    result = deployer.deploy_from_github(
        "https://github.com/YOUR_USERNAME/ecomarine-api"
    )
    print(f"Deployed: {result['url']}")
```

**Benefits of this approach:**
- Version controlled deployments
- Easy to replicate for new APIs
- Documented infrastructure
- Can migrate to Terraform later

---

## 8. MONEY-FOCUSED DECISION MATRIX

### Which APIs to Build? (Priority Order)

**High Value = Build First:**
1. **Compliance/Regulatory** - ECA zones, MARPOL, port state control
   - Businesses MUST comply (forced demand)
   - High willingness to pay
   - Example: Ecomarine API ✅

2. **Cost Optimization** - Fuel prices, route optimization, port costs
   - Saves companies money (clear ROI)
   - Easy to justify pricing
   - Example: Fuel cost API, Route optimizer

3. **Operational Efficiency** - Ship tracking, ETA, port schedules
   - Saves time and labor
   - Moderate pricing power
   - Example: Real-time tracking, Port queue API

4. **Data/Analytics** - Historical data, market analysis
   - Nice to have (lower urgency)
   - Lower pricing power
   - Example: Market reports, Analytics dashboards

**Decision Framework:**
```
IF (required_by_regulation OR saves_money):
    BUILD_FIRST = True
    PRICING_POWER = High
ELSE IF (saves_time OR operational_efficiency):
    BUILD_SECOND = True
    PRICING_POWER = Medium
ELSE:
    BUILD_LATER = True
    PRICING_POWER = Low
```

### API Ideas to Test (Ranked by Money Potential):

1. **Ecomarine API** (ECA compliance) - $$$ ✅
2. **FuelPrice API** (live bunker prices) - $$$
3. **PortCost API** (port fees calculator) - $$
4. **RouteOptimizer API** (shortest/cheapest route) - $$
5. **ETACalculator API** (ship arrival times) - $$
6. **MarketData API** (freight rates, indices) - $
7. **WeatherRouting API** (weather-optimized routes) - $

---

## 9. MCP (Model Context Protocol) FOR AI BOTS

### What is MCP?
MCP allows AI assistants (Claude, Cursor, etc.) to call your API directly. Users can say:
> "Claude, calculate the ECA distance from Rotterdam to New York"

And Claude will automatically call your API.

### Should You Build MCP?

**Current recommendation: NO** ❌

**Reasons:**
1. MCP is new - very few users know about it
2. Adds complexity (extra server to maintain)
3. RapidAPI is proven market with 3M users
4. You can add MCP later once profitable

**When to add MCP:**
- After you have 50+ paying customers
- When AI assistants become mainstream for business
- When you have bandwidth for extra support

**Future MCP Strategy:**
```
IF (paying_customers > 50 AND monthly_revenue > $2000):
    BUILD_MCP_SERVER = True
    OFFER_AS_PREMIUM_TIER = True
    PRICE_MCP_ACCESS = $99/month
```

---

## 10. EXECUTION ROADMAP

### Week 1: Ecomarine API Launch

**Day 1-2:** Code & Deploy
- [ ] Refactor current code to template structure
- [ ] Add /check-point endpoint (using your polygon data)
- [ ] Enhance /calculate-route-eca with compliance data
- [ ] Add /supported-zones endpoint
- [ ] Deploy to Leapcell
- [ ] Test all endpoints

**Day 3:** RapidAPI Listing
- [ ] Create RapidAPI account
- [ ] Write listing copy
- [ ] Set pricing tiers ($19/49/149)
- [ ] Submit for approval

**Day 4:** Documentation & Monitoring
- [ ] Write comprehensive README
- [ ] Add Python/JS/cURL examples
- [ ] Setup UptimeRobot (free)
- [ ] Setup Sentry (free)
- [ ] Create FAQ

**Day 5:** Launch & Promote
- [ ] Share on LinkedIn, Reddit r/maritime
- [ ] Email 5 potential beta users
- [ ] Post on Hacker News "Show HN"
- [ ] Fix any initial bugs

### Week 2-4: Validation
- [ ] Monitor RapidAPI analytics
- [ ] Track free tier usage
- [ ] Get first 3-5 paying customers
- [ ] Gather feedback
- [ ] Iterate based on demand

### Month 2: Second API
- [ ] Identify next high-value API (FuelPrice? PortCost?)
- [ ] Use same template, different data
- [ ] Launch in 1 week (template makes it fast)
- [ ] Cross-promote with Ecomarine API

### Month 3+: Scale Pattern
- [ ] Launch 1 new API per month
- [ ] Sunset APIs with no traction
- [ ] Double down on winners
- [ ] Build $500-1000/month MRR per API

---

## 11. SUCCESS METRICS (Solo Dev Edition)

### Month 1 Goals:
- [ ] 1 API live on RapidAPI
- [ ] 50+ free tier signups
- [ ] 3-5 paying customers
- [ ] $57-95 MRR
- [ ] Zero critical bugs

### Month 3 Goals:
- [ ] 3 APIs live
- [ ] 300+ total free users
- [ ] 30+ paying customers across all APIs
- [ ] $1,500+ total MRR
- [ ] <2% churn rate
- [ ] Self-sustainable (cover living expenses)

### Month 6 Goals:
- [ ] 6 APIs live
- [ ] 1,000+ total free users
- [ ] 100+ paying customers
- [ ] $5,000+ total MRR
- [ ] Quit day job option

---

## 12. CRITICAL DECISIONS NEEDED

Before I start coding, confirm:

### 1. **Polygon Data Format**
You said you have ECA zone data. What format?
- GeoJSON polygons?
- Shapefiles?
- Custom format?
- I need to know to write the /check-point endpoint

### 2. **Current Code State**
Can you share:
- Current main.py structure?
- Where ECA distance is calculated?
- What data files you have?

### 3. **Priority: Speed vs Perfection**
- **Option A:** Deploy FAST (1-2 days) with basic endpoints, iterate later
- **Option B:** Perfect architecture (1 week) with all features, then deploy

**My recommendation:** Option A (money first, perfection later)

### 4. **Terraform/IaaS**
- **Option A:** Manual deploy for now (faster to market)
- **Option B:** Set up Python IaaS (better long-term)

**My recommendation:** Option A now, add IaaS when you have 3+ APIs

---

## 13. NEXT IMMEDIATE ACTION

**Give me the green light to:**

1. **Restructure your code** to the template format
2. **Add the 3 endpoints** (/calculate-route-eca, /check-point, /supported-zones)
3. **Create Leapcell deployment** config
4. **Write RapidAPI listing** copy
5. **Setup monitoring** (UptimeRobot, Sentry)

**What I need from you:**
- ✅ Confirm: Use Leapcell (not Cloudflare Workers)
- ✅ Confirm: Ecomarine API name
- ✅ Confirm: Pricing tiers ($19/49/149)
- ✅ Share: Your ECA polygon data format
- ✅ Give: Green light to start coding

**Timeline from "Go":** 2-3 days to live on RapidAPI

---

*Plan created: 2025-02-01*  
*Status: Awaiting approval to execute*