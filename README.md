# NITA Dynamic Dashboard

A production-ready Full-Stack Dashboard with **FastAPI** backend and **React** frontend, synced with Google Sheets in real-time. Features interactive Plotly charts, responsive design, and advanced filtering capabilities.

## 🎯 Features

- **Real-time Google Sheets Integration** - Automatic sync with your Google Sheet using gspread
- **FastAPI Backend** - RESTful API with CORS support and comprehensive endpoints
- **React Frontend** - Modern, responsive UI with Tailwind CSS
- **Interactive Visualizations** - Plotly charts for:
  - Gender distribution (Pie chart)
  - Education level breakdown (Bar chart)
  - Top 5 courses of study (Bar chart)
  - Geographic distribution (Bar chart)
  - Top 10 preferred companies (Horizontal bar chart)
  - KPI cards for quick insights
- **Smart Filtering** - Filter by County and Level of Training with live updates
- **Mobile Responsive** - Works seamlessly on desktop, tablet, and mobile
- **Production Ready** - Docker support, environment configuration, error handling

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ and npm
- Google Cloud Console access
- Git

## 🚀 Quick Start

### Part 1: Google Cloud Setup (Required for Data Sync)

This is the most critical step. Follow carefully:

#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Name it "NITA Dashboard" and click "CREATE"
5. Wait for the project to be created

#### Step 2: Enable Google Sheets API

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "ENABLE"
4. Go back and search for "Google Drive API"
5. Click on it and press "ENABLE"

#### Step 3: Create a Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "Service Account"
3. Fill in the service account name (e.g., "nita-dashboard")
4. Click "CREATE AND CONTINUE"
5. Grant the service account "Editor" role
6. Click "CONTINUE" and then "DONE"

#### Step 4: Create and Download the Key

1. In the Credentials page, click on the service account you just created
2. Go to the "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON" format
5. Click "CREATE" - the JSON file will download automatically

#### Step 5: Move the JSON File to the Backend

1. In the downloaded JSON file, you'll find a `client_email` (looks like: `service-account-name@project-id.iam.gserviceaccount.com`)
2. Copy the entire downloaded JSON file to `/backend/service_account.json`

```bash
# After downloading the JSON file:
mv ~/Downloads/your-key-file.json /path/to/nita/backend/service_account.json
```

#### Step 6: Share Your Google Sheet

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns/edit
2. Click the "Share" button
3. Paste the `client_email` from your service account JSON
4. Give it "Editor" access
5. Click "Share" (don't send notifications)

**⚠️ IMPORTANT:** The dashboard will NOT work without completing these Google Cloud steps. The API will fail if the service account doesn't have access to the sheet.

### Part 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, for future configuration)
cp .env.example .env

# Run the FastAPI server (CORRECT COMMAND - use 'main:app' not 'app.main:app')
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **Important:** Use `uvicorn main:app` - NOT `uvicorn app.main:app`. The file is `main.py`, not in an `app/` folder.

The API will be available at: http://localhost:8000

**Test the API:**
```bash
# Check if API is running
curl http://localhost:8000/health

# Get all data
curl http://localhost:8000/data

# Get statistics
curl http://localhost:8000/stats
```

### Part 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start the development server
npm start
```

The dashboard will open at: http://localhost:3000

## 📊 API Endpoints

### Health Check
```
GET /health
```
Returns API status and connection to Google Sheets.

### Get All Data
```
GET /data?limit=50&offset=0
```
Fetches all records from the Google Sheet.

### Get Statistics
```
GET /stats?county=optional_county&level=optional_level
```
Returns aggregated statistics:
- `total_registrations`: Total count of records
- `placement_rate`: Percentage of placed applicants
- `gender_ratio`: Breakdown by gender
- `education_breakdown`: Count by education level
- `top_courses`: Top 5 courses by count
- `geographic_distribution`: Top 5 counties
- `preferred_companies`: Top 10 companies

### Get Filter Options
```
GET /counties
GET /levels
```
Returns available counties and training levels for filtering.

### Search
```
GET /search?query=search_term&field=optional_field
```
Search records across the sheet.

## 🎨 Frontend Features

### Dashboard Components

1. **Header**
   - Title and description
   - Last updated timestamp
   - Refresh button
   - Error indicator

2. **Sidebar**
   - County filter with dropdown
   - Level of Training filter
   - Clear filters button
   - Mobile-responsive

3. **KPI Row**
   - Total Applicants
   - Placement Rate
   - Male Applicants %
   - Female Applicants %

4. **Charts**
   - Gender distribution (Pie)
   - Education level (Bar)
   - Top courses (Bar)
   - Geographic distribution (Bar)
   - Preferred companies (Horizontal Bar)

### Mobile Responsiveness

The dashboard is fully responsive with:
- Mobile sidebar toggle
- Touch-friendly buttons
- Optimized chart layouts
- Adaptive grid system

## 🐳 Docker Deployment (Optional)

### Using Docker Compose

```bash
# From the root directory
docker-compose up --build
```

This will:
- Start the FastAPI backend on port 8000
- Start the React frontend on port 3000
- Enable auto-reload during development

### Using Docker Individually

**Backend:**
```bash
cd backend
docker build -t nita-backend .
docker run -p 8000:8000 -v $(pwd)/service_account.json:/app/service_account.json nita-backend
```

**Frontend:**
```bash
cd frontend
docker build -t nita-frontend .
docker run -p 3000:3000 nita-frontend
```

## 📁 Project Structure

```
nita/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── service_account.json    # Google credentials (add after setup)
│   ├── .env.example            # Environment variables template
│   ├── Dockerfile              # Docker configuration
│   └── __pycache__/
├── frontend/
│   ├── public/
│   │   └── index.html          # HTML entry point
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── KPICard.jsx
│   │   │   ├── GenderChart.jsx
│   │   │   ├── EducationChart.jsx
│   │   │   ├── CompaniesChart.jsx
│   │   │   ├── CoursesChart.jsx
│   │   │   ├── GeographicChart.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   └── NotFound.jsx
│   │   ├── services/           # API services
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env                    # Add after setup
│   ├── Dockerfile
│   └── .gitignore
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # This file
└── .gitignore
```

## 🔧 Environment Variables

### Backend (.env)

Create `/backend/.env`:
```
# FastAPI Configuration
FASTAPI_ENV=development
FASTAPI_DEBUG=true

# Google Sheets Configuration
SPREADSHEET_ID=1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns
SERVICE_ACCOUNT_FILE=service_account.json
```

### Frontend (.env)

Create `/frontend/.env`:
```
# API Configuration
REACT_APP_API_URL=http://localhost:8000
```

For production, change to your deployed backend URL.

## 🚨 Troubleshooting

### "service_account.json not found"
**Solution:** Follow the Google Cloud setup steps again. Make sure the JSON file is in `/backend/service_account.json`.

### "Permission denied" error from Google Sheets
**Solution:** 
1. Check the `client_email` in your service_account.json
2. Go to your Google Sheet and share it with that email
3. Grant "Editor" access

### Frontend can't connect to backend
**Solution:**
1. Make sure backend is running: `http://localhost:8000/health`
2. Check that `REACT_APP_API_URL` in frontend/.env points to the correct backend URL
3. Restart the frontend: `npm start`

### Charts not displaying
**Solution:**
1. Open browser DevTools (F12)
2. Check the Console for errors
3. Verify the API is returning data: `curl http://localhost:8000/stats`

### Port already in use
**Solution:**
```bash
# Kill process on port 8000 (backend)
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

## 🔐 Security Considerations

1. **Never commit `service_account.json`** to version control
2. **Keep credentials private** - use environment variables in production
3. **Use HTTPS** in production
4. **Restrict CORS** - change `allow_origins=["*"]` in `main.py` to your domain
5. **Add authentication** if deploying publicly
6. **Use secrets management** tools (AWS Secrets Manager, Azure Key Vault, etc.)

## 📦 Production Deployment

### For AWS/Heroku/DigitalOcean:

1. Set environment variables in your hosting platform:
   - Upload `service_account.json` securely
   - Set `SPREADSHEET_ID`

2. Update CORS in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Use `gunicorn` for production:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

4. Deploy frontend:
```bash
npm run build
# Upload build/ folder to your CDN or server
```

## 📚 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **gspread** - Google Sheets API client
- **python-dotenv** - Environment configuration
- **uvicorn** - ASGI server

### Frontend
- **React 18** - UI framework
- **Plotly.js** - Interactive charts
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💡 Tips & Best Practices

1. **Auto-refresh**: The dashboard fetches fresh data every time you change filters
2. **Mobile-first**: Design changes work across all devices
3. **Performance**: Charts are memoized to prevent unnecessary re-renders
4. **Accessibility**: Use keyboard navigation (Tab) in filters
5. **Caching**: Backend automatically caches worksheet connections

## 🆘 Support

For issues or questions:
1. Check this README's troubleshooting section
2. Review the API documentation at `http://localhost:8000/docs`
3. Check browser console for frontend errors (F12)
4. Review backend logs in the terminal

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Google Sheets API](https://developers.google.com/sheets/api)

---

**Built with ❤️ for the NITA community**
