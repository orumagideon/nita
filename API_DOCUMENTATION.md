# NITA Dashboard - API Documentation

## Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://your-api-domain.com`

## Interactive API Documentation

Visit `{BASE_URL}/docs` for an interactive Swagger UI where you can test all endpoints directly.

Example: http://localhost:8000/docs

## Authentication

Currently, no authentication is required. For production deployment, consider adding JWT tokens or API keys.

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "data": {},
  "timestamp": "2026-02-08T12:00:00",
  "error": null
}
```

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check API and Google Sheets connection status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-08T12:00:00.123456"
}
```

**Status Codes:**
- `200`: API is healthy
- `503`: Connection issue with Google Sheets

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Get All Data

**Endpoint:** `GET /data`

**Description:** Fetch all records from the Google Sheet with optional pagination.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum number of records to return |
| `offset` | integer | No | Number of records to skip (default: 0) |

**Response:**
```json
{
  "total": 150,
  "count": 50,
  "data": [
    {
      "Name": "John Doe",
      "Gender": "Male",
      "Your County": "Nairobi",
      "Level of Training": "Degree",
      "Course of Study": "Computer Science",
      "Preferred Companies": "Tech Corp, Google",
      "Placement": "Yes"
    }
  ],
  "timestamp": "2026-02-08T12:00:00.123456"
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error (check Google Sheets connection)

**Examples:**
```bash
# Get first 50 records
curl "http://localhost:8000/data?limit=50"

# Get records 100-150
curl "http://localhost:8000/data?limit=50&offset=100"

# Get all records (no limit)
curl "http://localhost:8000/data"
```

---

### 3. Get Statistics

**Endpoint:** `GET /stats`

**Description:** Get aggregated statistics with optional filtering by county or training level.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `county` | string | No | Filter by county name |
| `level` | string | No | Filter by level of training |

**Response:**
```json
{
  "total_registrations": 150,
  "placement_rate": 75.5,
  "gender_ratio": {
    "Male": 60.5,
    "Female": 35.2,
    "Other": 4.3
  },
  "education_breakdown": {
    "Degree": 85,
    "Diploma": 45,
    "Certificate": 20
  },
  "top_courses": [
    {
      "name": "Computer Science",
      "count": 25
    },
    {
      "name": "Business Administration",
      "count": 20
    }
  ],
  "geographic_distribution": [
    {
      "county": "Nairobi",
      "count": 45
    },
    {
      "county": "Kiambu",
      "count": 30
    }
  ],
  "preferred_companies": [
    {
      "name": "Tech Corp",
      "count": 40
    },
    {
      "name": "Google",
      "count": 35
    }
  ],
  "filtered": false,
  "timestamp": "2026-02-08T12:00:00.123456"
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `total_registrations` | integer | Total count of records in filtered dataset |
| `placement_rate` | float | Percentage of applicants with placement |
| `gender_ratio` | object | Percentage breakdown by gender |
| `education_breakdown` | object | Count of records by education level |
| `top_courses` | array | Top 5 courses by application count |
| `geographic_distribution` | array | Top 5 counties by applicant count |
| `preferred_companies` | array | Top 10 companies by preference count |
| `filtered` | boolean | Whether results are filtered |

**Status Codes:**
- `200`: Success
- `500`: Server error

**Examples:**
```bash
# Get all stats
curl "http://localhost:8000/stats"

# Filter by county
curl "http://localhost:8000/stats?county=Nairobi"

# Filter by level
curl "http://localhost:8000/stats?level=Degree"

# Filter by both
curl "http://localhost:8000/stats?county=Nairobi&level=Degree"
```

---

### 4. Get Counties

**Endpoint:** `GET /counties`

**Description:** Get list of all unique counties in the dataset.

**Response:**
```json
{
  "counties": [
    "Baringo",
    "Bomas of Kenya",
    "Bomet",
    "Bungoma",
    "Busia",
    "Kilifi",
    "Kiambu",
    "Kisii",
    "Kisumu",
    "Kitui",
    "Nairobi",
    "Nakuru"
  ]
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error

**Example:**
```bash
curl "http://localhost:8000/counties"
```

---

### 5. Get Training Levels

**Endpoint:** `GET /levels`

**Description:** Get list of all unique training levels in the dataset.

**Response:**
```json
{
  "levels": [
    "Certificate",
    "Degree",
    "Diploma"
  ]
}
```

**Status Codes:**
- `200`: Success
- `500`: Server error

**Example:**
```bash
curl "http://localhost:8000/levels"
```

---

### 6. Search

**Endpoint:** `GET /search`

**Description:** Search records by query string across all fields or specific field.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search term (minimum 1 character) |
| `field` | string | No | Specific field to search in |

**Response:**
```json
{
  "query": "John",
  "count": 5,
  "data": [
    {
      "Name": "John Doe",
      "Gender": "Male",
      "Your County": "Nairobi",
      "Level of Training": "Degree",
      "Course of Study": "Computer Science",
      "Preferred Companies": "Tech Corp",
      "Placement": "Yes"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid query (empty or too short)
- `500`: Server error

**Notes:**
- Search is case-insensitive
- Results limited to 50 records
- Search across all fields if `field` not specified

**Examples:**
```bash
# Search across all fields
curl "http://localhost:8000/search?query=John"

# Search in specific field
curl "http://localhost:8000/search?query=Nairobi&field=Your%20County"

# Search for companies
curl "http://localhost:8000/search?query=Google&field=Preferred%20Companies"
```

---

## Error Handling

All errors return appropriate HTTP status codes and descriptive messages:

```json
{
  "detail": "Descriptive error message"
}
```

**Common Error Codes:**

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request | Check query parameters |
| `404` | Not Found | Endpoint doesn't exist |
| `500` | Internal Server Error | Check API logs, Google Sheets connection |
| `503` | Service Unavailable | Google Sheets API unreachable |

**Example Error Response:**
```bash
$ curl "http://localhost:8000/stats"
# If service_account.json is missing:
{"detail": "service_account.json not found. Please create it via Google Cloud Console."}
```

---

## Rate Limiting

Currently, there is no rate limiting. For production, implement:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/stats")
@limiter.limit("10/minute")
async def get_stats():
    # ...
```

---

## CORS Headers

All responses include CORS headers allowing requests from any origin (customizable):

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

For production, restrict to specific domains:

```python
allow_origins=["https://yourdomain.com"]
```

---

## Data Schema

### Record Structure (from Google Sheet)

```typescript
interface Record {
  Name: string;
  Gender: "Male" | "Female" | "Other";
  "Your County": string;
  "Level of Training": "Degree" | "Diploma" | "Certificate";
  "Course of Study": string;
  "Preferred Companies": string; // Comma-separated
  Placement: "Yes" | "No";
  // ... other custom fields
}
```

---

## Performance Tips

1. **Use pagination**: Add `limit` and `offset` for large datasets
2. **Cache results**: Frontend caches stats until filter changes
3. **Batch requests**: Fetch multiple endpoints in parallel
4. **Monitor usage**: Check API logs for slow queries

---

## Testing Endpoints

### Using cURL

```bash
# Test health
curl -v http://localhost:8000/health

# Get stats with JSON pretty-print
curl http://localhost:8000/stats | jq .

# Save response to file
curl http://localhost:8000/data > data.json
```

### Using Python

```python
import requests

# Fetch stats
response = requests.get('http://localhost:8000/stats')
stats = response.json()
print(f"Total: {stats['total_registrations']}")

# Filter by county
response = requests.get('http://localhost:8000/stats', params={'county': 'Nairobi'})
filtered_stats = response.json()
```

### Using JavaScript

```javascript
// Fetch stats
const stats = await fetch('http://localhost:8000/stats').then(r => r.json());
console.log(stats);

// Filter by county
const filtered = await fetch('http://localhost:8000/stats?county=Nairobi').then(r => r.json());
```

---

## Webhook Support

Webhooks can be added for real-time updates. Example implementation:

```python
# Future enhancement
@app.post("/webhook/subscribe")
async def subscribe_webhook(url: str):
    # Store webhook URL
    # Send data updates to URL when sheet changes
    pass
```

---

## API Versioning

Current version: `v1`

For future versions, use URL paths:
```
/v1/stats
/v2/stats  # Future enhancement
```

---

## Documentation Links

- **OpenAPI (Swagger)**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

**Access locally:**
- http://localhost:8000/docs
- http://localhost:8000/redoc
- http://localhost:8000/openapi.json

---

## Changelog

**v1.0.0** (February 2026)
- Initial release
- 6 main endpoints
- Google Sheets integration
- Real-time statistics
- Filtering support

---

**Last Updated:** February 2026
**Version:** 1.0.0
