# NITA Dashboard - Development Guide

## Architecture Overview

The NITA Dashboard is a modern full-stack application with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│  (localhost:3000)  Components, Charts, Filters          │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (Axios)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│  (localhost:8000)  REST API, Data Processing            │
└────────────────────────┬────────────────────────────────┘
                         │ gspread API
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Google Sheets                          │
│          Real-time Data Source (Read-only)              │
└─────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Main Modules

**main.py**
- FastAPI application entry point
- RESTful API endpoints
- Google Sheets integration via gspread
- CORS middleware for cross-origin requests
- Statistics calculation and aggregation
- Singleton pattern for Google Sheets client

### Key Components

#### GoogleSheetsClient (Singleton)
```python
client = GoogleSheetsClient()  # Always returns same instance
records = client.fetch_all_records()
```

**Benefits:**
- Single connection to Google Sheets
- Automatic credential caching
- Thread-safe operations
- Efficient resource usage

#### API Endpoints

1. **GET /health**
   - Purpose: Check API and Google Sheets connection
   - Use: Monitoring and debugging

2. **GET /data**
   - Purpose: Fetch raw records from sheet
   - Params: `limit`, `offset` for pagination
   - Returns: All worksheet data

3. **GET /stats**
   - Purpose: Get calculated statistics
   - Params: `county`, `level` for filtering
   - Returns: Aggregated data with charts information

4. **GET /counties** & **GET /levels**
   - Purpose: Get available filter options
   - Use: Populate sidebar dropdowns

5. **GET /search**
   - Purpose: Full-text search across data
   - Params: `query`, `field`
   - Returns: Matching records

### Data Processing Pipeline

```
Raw Sheet Data
      │
      ▼
Filter (by county/level)
      │
      ▼
Aggregate (count, group)
      │
      ▼
Calculate Statistics:
  - Total Registrations
  - Gender Ratio (percentage)
  - Education Breakdown
  - Top 5 Courses
  - Top 5 Geographic Distribution
  - Top 10 Companies
  - Placement Rate
      │
      ▼
Return JSON Response
```

## Frontend Architecture

### Component Structure

```
App
├── Dashboard (Page)
│   ├── Header
│   │   ├── Title & Description
│   │   ├── Last Updated Timestamp
│   │   ├── Refresh Button
│   │   └── Error Display
│   │
│   ├── Sidebar
│   │   ├── County Filter
│   │   ├── Level Filter
│   │   └── Clear Filters Button
│   │
│   └── Main Content
│       ├── KPIRow
│       │   ├── Total Applicants (KPI)
│       │   ├── Placement Rate (KPI)
│       │   ├── Male Percentage (KPI)
│       │   └── Female Percentage (KPI)
│       │
│       └── Charts Grid
│           ├── Gender Chart (Pie)
│           ├── Education Chart (Bar)
│           ├── Courses Chart (Bar)
│           ├── Geographic Chart (Bar)
│           └── Companies Chart (Horizontal Bar)
│
└── NotFound (404 Page)
```

### State Management

Uses React hooks:
- `useState`: Component-level state
- `useEffect`: Side effects (API calls)
- `useMemo`: Chart data memoization (performance)

### Key Features

#### Responsive Design
- Mobile-first approach
- Tailwind CSS grid system
- Sidebar toggle for mobile
- Touch-friendly interactions

#### Performance Optimizations
- Memoized chart data calculations
- Conditional rendering
- Lazy loading patterns
- Efficient re-renders with useEffect dependencies

#### Error Handling
- Try-catch blocks in API calls
- User-friendly error messages
- Retry functionality
- Connection status display

## Data Flow

### User Interaction Flow

```
User Opens Dashboard
        │
        ▼
App Component Mounts
        │
        ├─► Fetch Counties & Levels
        └─► Fetch Initial Stats
        │
        ▼
Dashboard Renders with Data
        │
User Selects Filter
        │
        ▼
State Updates (selectedCounty/selectedLevel)
        │
        ▼
useEffect Triggers
        │
        ▼
API Call to /stats with filters
        │
        ▼
Stats State Updates
        │
        ▼
Charts Re-render with New Data
```

### Real-time Data Sync

Currently, data refreshes when:
1. Page loads
2. Filter changes
3. User clicks refresh button

To implement true real-time sync:
```javascript
// Add WebSocket listener (future enhancement)
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onmessage = (event) => {
    const newStats = JSON.parse(event.data);
    setStats(newStats);
  };
  return () => ws.close();
}, []);
```

## File Organization

### Backend Files

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── service_account.json   # Google credentials (not in git)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker configuration
└── venv/                  # Virtual environment
```

### Frontend Files

```
frontend/
├── public/
│   └── index.html         # HTML template
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── KPICard.jsx
│   │   ├── GenderChart.jsx
│   │   ├── EducationChart.jsx
│   │   ├── CompaniesChart.jsx
│   │   ├── CoursesChart.jsx
│   │   ├── GeographicChart.jsx
│   │   ├── Header.jsx
│   │   └── Sidebar.jsx
│   ├── pages/             # Full-page components
│   │   ├── Dashboard.jsx
│   │   └── NotFound.jsx
│   ├── services/          # API and external services
│   │   └── api.js
│   ├── App.jsx            # Main app component
│   ├── index.js           # React DOM render
│   └── index.css          # Global styles
├── package.json           # Dependencies
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── Dockerfile             # Docker configuration
└── node_modules/          # Dependencies (not in git)
```

## Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm start
```

### Adding a New Feature

1. **Backend**: Add endpoint in `main.py`
2. **Backend**: Test with `curl` or API docs (`/docs`)
3. **Frontend**: Add API call in `services/api.js`
4. **Frontend**: Create/update component to use new data
5. **Frontend**: Test in browser

### Example: Adding a New Chart

```javascript
// 1. Create new component: src/components/NewChart.jsx
export const NewChart = ({ data }) => {
  const chartData = useMemo(() => {
    // Transform data for Plotly
    return [{ x: [...], y: [...], type: 'bar' }];
  }, [data]);

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <Plot data={chartData} layout={{...}} />
    </div>
  );
};

// 2. Add to Dashboard.jsx
<NewChart data={stats.new_data_field} />

// 3. Update backend stats endpoint
def calculate_statistics(records):
  # ... existing code ...
  new_data_field = calculate_new_data(records)
  return {
    # ... existing stats ...
    "new_data_field": new_data_field
  }
```

## Debugging

### Backend Debugging

```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing {len(records)} records")

# Use FastAPI docs
# Visit http://localhost:8000/docs for interactive API testing

# Check API responses
curl http://localhost:8000/stats | jq .
```

### Frontend Debugging

```javascript
// Browser DevTools (F12)
console.log(stats);  // Log state values
debugger;  // Set breakpoints

// Network tab: Monitor API calls
// Console tab: See JavaScript errors
// React DevTools extension: Inspect components
```

### Google Sheets Issues

```bash
# Test credentials
python3 -c "
import gspread
from oauth2client.service_account import ServiceAccountCredentials

creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', [...])
client = gspread.authorize(creds)
sheet = client.open_by_key('1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns')
print(sheet.sheet1.get_all_records()[:1])  # Print first record
"
```

## Performance Considerations

### Backend
- **Caching**: Implement redis for frequently accessed stats
- **Pagination**: Use limit/offset for large datasets
- **Async**: Use `async/await` for I/O operations
- **Connection pooling**: Reuse Sheets connections

### Frontend
- **Code splitting**: Lazy load pages with React Router
- **Bundle analysis**: Use webpack-bundle-analyzer
- **Image optimization**: Compress and cache charts
- **Virtual scrolling**: For large data tables

## Security Best Practices

### Implemented
✅ CORS configuration (customize for production)
✅ Input validation (gspread handles this)
✅ Read-only service account (for Google Sheets)
✅ Environment variables for secrets

### Recommended for Production
⚠️ Add authentication (JWT tokens)
⚠️ Rate limiting (prevent abuse)
⚠️ Input sanitization (SQL injection prevention)
⚠️ HTTPS only (force TLS)
⚠️ CORS whitelist (specific domains only)

## Deployment

### Docker Deployment

```bash
docker-compose up --build
```

### Cloud Platforms

**AWS (EC2)**
```bash
# Install Docker
sudo yum install docker -y
sudo systemctl start docker

# Clone and run
git clone <repo>
cd nita
docker-compose up -d
```

**Heroku**
```bash
# Create Procfile
web: gunicorn main:app

# Deploy
git push heroku main
```

**DigitalOcean App Platform**
- Connect GitHub repository
- Set environment variables
- Deploy automatically

## Testing

### Backend Testing

```python
# Create tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

# Run tests
pytest tests/
```

### Frontend Testing

```javascript
// Using React Testing Library
import { render, screen } from '@testing-library/react';
import Dashboard from './pages/Dashboard';

test('renders dashboard', () => {
  render(<Dashboard />);
  expect(screen.getByText(/NITA Dashboard/i)).toBeInTheDocument();
});

// Run tests
npm test
```

## Troubleshooting Guide

### "ModuleNotFoundError: No module named 'gspread'"
```bash
cd backend
source venv/bin/activate
pip install gspread
```

### "Connection refused" when accessing localhost:3000
```bash
# Check if frontend is running
ps aux | grep npm

# Restart frontend
cd frontend
npm start
```

### Charts not loading
```javascript
// Check browser console (F12)
// Verify API returns correct data format
curl http://localhost:8000/stats | jq .

// Check Plotly configuration in component
```

### Google Sheets authentication fails
```bash
# Verify service account has access
# 1. Check client_email in service_account.json
# 2. Share sheet with that email
# 3. Verify sheet ID matches in code
# 4. Test with Python:
python3 -c "import gspread; [...]"
```

## Next Steps & Enhancements

- [ ] Add user authentication
- [ ] Implement data caching with Redis
- [ ] Add real-time updates with WebSocket
- [ ] Create admin panel for data management
- [ ] Add export to CSV/PDF functionality
- [ ] Implement user preferences/saved filters
- [ ] Add data visualization customization
- [ ] Create API rate limiting
- [ ] Add comprehensive logging and monitoring
- [ ] Build mobile app version

---

**Last Updated:** February 2026
**Version:** 1.0.0
