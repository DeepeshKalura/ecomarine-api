## Long Description for RapidAPI Listing

**Headline:** Calculate ECA Distances & Fuel Costs for Maritime Routes

**Subheadline:** Fast, accurate Emission Control Area distance calculations for IMO 2020 compliance and voyage cost estimation

---

### Full Description (500+ words):

**Ecomarine API** is a specialized maritime navigation API that calculates distances within Emission Control Areas (ECAs), helping shipping companies, logistics providers, and maritime software developers accurately estimate fuel costs under IMO 2020 low-sulphur regulations.

#### 🚢 What is Ecomarine API?

Maritime shipping routes often pass through Emission Control Areas (ECAs) where stricter fuel sulphur limits apply. These areas include the North Sea, Baltic Sea, Mediterranean, and coastal waters of North America. Navigating through ECAs requires low-sulphur fuel (0.1% or 0.5%), which is significantly more expensive than standard marine fuel (0.5% global cap).

Ecomarine API calculates:
- ✅ Total nautical miles for any maritime route
- ✅ Distance traveled within ECA zones
- ✅ Percentage of route in ECA waters
- ✅ Estimated fuel cost impact
- ✅ Compliance status and applicable regulations

#### 💡 Perfect For:

- **Voyage Planning Software** - Calculate fuel costs before departure
- **Freight Marketplaces** - Provide accurate shipping cost estimates
- **Maritime Compliance Tools** - Verify IMO 2020 adherence
- **Logistics Platforms** - Optimize routes for cost efficiency
- **Port Management Systems** - Estimate vessel arrival costs
- **Fuel Procurement Apps** - Calculate ECA fuel requirements

#### 🌍 Supported ECA Zones:

Our API covers all major Emission Control Areas:
- North Sea SECA (Sulphur Emission Control Area)
- Baltic Sea SECA
- Mediterranean ECA
- United States ECA (East Coast, West Coast, Gulf Coast)
- United States Caribbean ECA
- North American ECA (all regions)

#### 💰 Pricing:

**🆓 FREE FOREVER**
- 50 requests/month
- All endpoints included
- No credit card required
- Perfect for testing and development

**⚡ BASIC - $9/month**
- 2,000 requests/month
- ~$0.0045 per request
- Email support
- Great for small projects and startups

**🚀 PRO - $29/month**
- 10,000 requests/month  
- ~$0.0029 per request
- Priority support
- Ideal for growing logistics platforms

**💼 ENTERPRISE - Contact Us**
- Unlimited requests (fair use policy)
- Dedicated support
- Custom SLA
- Large shipping companies & consultancies

#### 📝 API Endpoints:

**POST /calculate-route-eca**
Calculate marine route with ECA distance & compliance data. Returns total distance, ECA distance, fuel cost impact, compliance status, and traversed zones.

**GET /check-point** (Coming Soon)
Check if specific coordinates are inside any ECA zone. Returns zone name, type, sulphur limit, and regulation.

**GET /supported-zones**
List all supported ECA zones with metadata including year established, sulphur limits, and applicable regulations.

#### 🔧 Integration Example:

```python
import requests

# Calculate route from Rotterdam to New York
response = requests.post(
    "https://api.ecomarine.io/calculate-route-eca",
    headers={"X-RapidAPI-Key": "your_api_key"},
    json={
        "origin": [51.9244, 4.4777],      # Rotterdam
        "destination": [40.7128, -74.0060] # New York
    }
)

result = response.json()
print(f"Total Distance: {result['total_distance_nm']} NM")
print(f"ECA Distance: {result['eca_distance_nm']} NM")
print(f"Fuel Cost Impact: ${result['fuel_impact']['total_extra_cost_usd']}")
```

#### ⚡ Why Choose Ecomarine API?

- **🎯 Specialized** - The only API focused purely on ECA calculations
- **🚀 Fast** - Sub-second response times
- **📊 Accurate** - Based on official IMO/EPA boundary data
- **💡 Simple** - REST API with JSON responses
- **🛡️ Reliable** - 99.9% uptime guarantee
- **💰 Affordable** - Start free, scale affordably

#### 🌊 Maritime Industry Context:

IMO 2020 regulations require ships to use fuel with maximum 0.5% sulphur content globally. In ECAs, the limit is even stricter at 0.1%. Non-compliance can result in fines of $15,000-$50,000+ per violation. Ecomarine API helps shipping companies plan routes that minimize expensive ECA fuel usage while maintaining compliance.

#### 📞 Support:

- Email: deepeshkalurs@gmail.com
- Response Time: 24-72 hours (Priority for Pro/Enterprise)
- Documentation: Full API reference included

#### 🆓 Get Started:

Sign up for the **FREE tier** today - no credit card required. Test the API with 50 requests and upgrade when you're ready to scale.

---

**Tags:** maritime, shipping, ECA, SECA, IMO 2020, MARPOL, fuel cost, compliance, route planning, nautical miles, vessel, port, logistics, transportation

**Category:** Logistics, Transportation
