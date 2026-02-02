# 🚢 Ecomarine API

**ECA Distance & Compliance API for Maritime Routes**

[![RapidAPI](https://img.shields.io/badge/RapidAPI-Available%20Soon-green)](https://rapidapi.com/studio/api_7bd483b9-3862-4fab-97b7-7c1e0f58e408/publish/docs)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-teal)](https://fastapi.tiangolo.com/)

Calculate marine routes with **Emission Control Area (ECA)** distance tracking for **IMO 2020** compliance and fuel cost optimization.

---

## 🎯 Keywords

`shipping` `maritime` `transportation` `logistics` `ECA` `SECA` `IMO 2020` `MARPOL` `fuel cost` `compliance` `vessel routing` `sea freight` `nautical miles` `marine navigation` `port management` `shipping API` `maritime compliance` `route planning` `ocean freight` `commercial shipping` `sulphur emissions` `environmental compliance`

---

## 💡 What is Ecomarine?

Maritime shipping routes pass through **Emission Control Areas (ECAs)** where stricter fuel sulphur limits apply. Ecomarine API helps shipping companies, logistics providers, and maritime software developers:

- ✅ Calculate total nautical miles for any route
- ✅ Track distance traveled inside ECA zones
- ✅ Estimate fuel cost impact
- ✅ Verify **IMO 2020** / **MARPOL** compliance
- ✅ Plan cost-efficient voyages

---

## 🎮 Live Demo

Try the **interactive demo** to see the API in action:

🌐 **[View Interactive Demo](./demo/)** (Open `demo/index.html` in your browser)

### Demo Features:
- 🗺️ **Route Calculator** - Visual map-based route planning with ECA tracking
- 📍 **ECA Zone Checker** - Click on the map to check if coordinates are in ECA zones  
- 🌍 **Supported Zones** - Browse all ECA zones with interactive map visualization
- 📡 **Live API Testing** - Test all 3 endpoints with your RapidAPI key
- 🗺️ **OpenStreetMap Integration** - Free, no API key required for maps

**Perfect for RapidAPI showcase!** Deploy the `demo/` folder to GitHub Pages, Vercel, or Netlify.

---

## 🔄 CI/CD & Pre-commit

### Automated Testing
Tests run automatically on every push via GitHub Actions:
```bash
# Run locally before committing
pytest tests/integration/ -v
```

### Pre-commit Hooks
**All RapidAPI artifacts are auto-generated via pre-commit:**
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually before commit
pre-commit run --all-files
```

**Generated files (auto-staged):**
- `openapi.json` - API specification
- `openapi.yaml` - YAML format
- `.rapidapi/tests/test_suite.json` - Test definitions
- `.rapidapi/tests/test_cases.md` - Test documentation
- `.rapidapi/tests/curl_commands.json` - API examples

### Manual RapidAPI Deployment
Since auto-deployment requires RapidAPI paid tier:

1. **Run pre-commit** to generate all files
2. **Go to RapidAPI Studio** → Your API
3. **Upload** `openapi.json` to Definitions tab
4. **Copy** `.rapidapi/tests/test_cases.md` to Docs tab
5. **Publish** your changes

**Or trigger manual workflow:**
```bash
# Go to GitHub → Actions → "Manual Deploy to RapidAPI"
# Click "Run workflow" and type "deploy" to confirm
```

---

## 🌍 Perfect For

- **Voyage Planning Software** - Pre-departure fuel calculations
- **Freight Marketplaces** - Accurate shipping cost estimates
- **Logistics Platforms** - Route optimization for cost efficiency
- **Maritime Compliance Tools** - IMO 2020 adherence verification
- **Port Management Systems** - Vessel arrival cost estimation
- **Fuel Procurement Apps** - ECA fuel requirement calculations
- **Commercial Shipping Companies** - Fleet route optimization

---

## 🚀 Quick Start

### Try the API

```bash
# Health check
curl https://your-api-domain.com/

# Check if coordinates are in ECA zone
curl "https://your-api-domain.com/check-point?latitude=58.5&longitude=3.2"

# Calculate route (Rotterdam to New York)
curl -X POST "https://your-api-domain.com/calculate_route" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": [51.9244, 4.4777],
    "destination": [40.7128, -74.0060],
    "restrictions": []
  }'
```

### Run Locally

```bash
# Clone repository
git clone <repo-url>
cd ecomarine

# Install dependencies (using uv)
uv pip install -e ".[dev]"

# Run the server
uvicorn main:app --reload
```

---

## 📡 API Endpoints

### `POST /calculate_route`

Calculate marine route with ECA distance & compliance data.

**Request:**
```json
{
  "origin": [51.9244, 4.4777],
  "destination": [40.7128, -74.0060],
  "restrictions": ["suez"],
  "include_explanation": false
}
```

**Response:**
```json
{
  "origin": [51.9244, 4.4777],
  "destination": [40.7128, -74.0060],
  "restrictions": ["suez"],
  "traversed_passage": "suez",
  "distance_nm": 3824.56,
  "eca_distance_nm": 892.34,
  "waypoints": [[51.9244, 4.4777], ...]
}
```

### `GET /check-point`

Check if coordinates are inside any ECA zone.

**Parameters:**
- `latitude` (-90 to 90)
- `longitude` (-180 to 180)

**Response:**
```json
{
  "inside_eca": true,
  "zone_name": "North Sea SECA",
  "zone_type": "seca",
  "required_sulphur": "0.1%",
  "regulation": "IMO 2020",
  "territory": "EU + UK"
}
```

### `GET /supported-zones`

List all supported ECA zones with metadata.

---

## 🗺️ Supported ECA Zones

- **North Sea SECA** - EU + UK waters
- **Baltic Sea SECA** - Northern European waters  
- **Mediterranean ECA** - Southern European waters
- **United States ECA** - East Coast, West Coast, Gulf Coast
- **United States Caribbean ECA** - Caribbean region
- **North American ECA** - All coastal regions

---

## 🔧 Tech Stack

- **Framework:** FastAPI (Python 3.12+)
- **Geospatial:** Shapely, GeoJSON
- **Routing:** SeaRoute integration
- **Deployment:** Serverless (Leapcell)
- **Documentation:** OpenAPI / Swagger UI

---

## 🎯 Why Ecomarine?

- **🎯 Specialized** - Only API focused on ECA distance calculations
- **⚡ Fast** - Sub-second response times
- **📊 Accurate** - Based on official IMO/EPA boundary data
- **💡 Simple** - REST API with JSON responses
- **🛡️ Reliable** - Production-ready architecture
- **💰 Cost-Effective** - Optimize routes, save fuel costs

---

## 🌊 Industry Context

**IMO 2020 regulations** require ships to use fuel with maximum 0.5% sulphur content globally. In ECAs, the limit is stricter at **0.1%**. Non-compliance fines range from **$15,000-$50,000+** per violation.

Ecomarine API helps shipping companies plan routes that minimize expensive ECA fuel usage while maintaining full compliance.

---

## 📝 RapidAPI Integration

This API is available on **RapidAPI** - the world's largest API marketplace.

🔗 **[View on RapidAPI](https://rapidapi.com/studio/api_7bd483b9-3862-4fab-97b7-7c1e0f58e408/publish/docs)**

Categories: `Logistics` `Transportation` `Shipping` `Maritime`

---

## 📊 Pricing (Coming Soon on RapidAPI)

| Plan | Requests | Price |
|------|----------|-------|
| 🆓 **Free** | 50/month | $0 |
| ⚡ **Basic** | 2,000/month | $9 |
| 🚀 **Pro** | 10,000/month | $29 |
| 💼 **Enterprise** | Unlimited | Contact Us |

---

## 🤝 Connect With Me

Need help with maritime API integration? Have questions about ECA compliance?

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Deepesh%20Kalura-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/deepeshkalura/)

**📧 Email:** deepeshkalurs@gmail.com

**⏱️ Response Time:** 24-72 hours

---

## 🚧 Status

**In Development** - See [Issues](../../issues) for current roadmap and improvements

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

Built for the maritime shipping and logistics community. Making ECA compliance easier, one route at a time.

---

*Made with 🌊 for the shipping industry*
