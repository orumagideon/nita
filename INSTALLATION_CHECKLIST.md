# NITA Dashboard - Installation Verification Checklist

Use this checklist to verify your installation is complete and working correctly.

## ✅ Prerequisites Check

### System Requirements
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Node.js 14+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Git installed: `git --version`
- [ ] Internet connection available
- [ ] At least 2GB free disk space

### Operating System
- [ ] macOS 10.14+
- [ ] Windows 10+ (with WSL2 recommended)
- [ ] Linux (Ubuntu 18.04+, etc.)

---

## 📦 Backend Setup Verification

### Virtual Environment
- [ ] Virtual environment created: `ls backend/venv`
- [ ] Virtual environment activated: Check `(venv)` in terminal prompt
- [ ] Python version correct: `python --version` (should be 3.8+)

### Dependencies Installation
- [ ] fastapi installed: `pip show fastapi`
- [ ] uvicorn installed: `pip show uvicorn`
- [ ] gspread installed: `pip show gspread`
- [ ] python-dotenv installed: `pip show python-dotenv`
- [ ] oauth2client installed: `pip show oauth2client`

**Install all at once:**
```bash
cd backend
pip install -r requirements.txt
```

### Backend File Structure
- [ ] `backend/main.py` exists
- [ ] `backend/requirements.txt` exists
- [ ] `backend/.env.example` exists
- [ ] `backend/.gitignore` exists
- [ ] `backend/Dockerfile` exists

### Environment File
- [ ] `backend/.env` created: `cp backend/.env.example backend/.env`
- [ ] `SPREADSHEET_ID` set correctly
- [ ] `SERVICE_ACCOUNT_FILE` set to `service_account.json`

---

## 🔐 Google Cloud Credentials

### Service Account JSON
- [ ] `backend/service_account.json` exists
- [ ] File is valid JSON: `python3 -c "import json; json.load(open('backend/service_account.json'))"`
- [ ] File contains `client_email` field
- [ ] File contains `private_key` field

### Google Sheet Access
- [ ] Google Sheet is shared with service account email
- [ ] Service account has "Editor" access
- [ ] Sheet ID matches in code: `1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns`

**Test Google Sheets Connection:**
```bash
cd backend
source venv/bin/activate
python3 << 'EOF'
import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'service_account.json',
        ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets']
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns')
    records = sheet.sheet1.get_all_records()
    print(f"✅ Success! Found {len(records)} records")
    print(f"First record: {records[0] if records else 'No records'}")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

Expected output: `✅ Success! Found X records`

---

## 🖥️ Frontend Setup Verification

### Node Modules
- [ ] `frontend/node_modules` directory exists
- [ ] Dependencies installed: `cd frontend && npm ls --depth=0`

### Dependencies Installation
- [ ] react installed: `npm list react` (in frontend folder)
- [ ] react-dom installed: `npm list react-dom`
- [ ] axios installed: `npm list axios`
- [ ] plotly.js installed: `npm list plotly.js`
- [ ] react-router-dom installed: `npm list react-router-dom`
- [ ] tailwindcss installed: `npm list tailwindcss`

**Install all at once:**
```bash
cd frontend
npm install
```

### Frontend File Structure
- [ ] `frontend/public/index.html` exists
- [ ] `frontend/src/App.jsx` exists
- [ ] `frontend/src/index.js` exists
- [ ] `frontend/src/index.css` exists
- [ ] `frontend/src/components/` has 8 files:
  - [ ] `KPICard.jsx`
  - [ ] `GenderChart.jsx`
  - [ ] `EducationChart.jsx`
  - [ ] `CompaniesChart.jsx`
  - [ ] `CoursesChart.jsx`
  - [ ] `GeographicChart.jsx`
  - [ ] `Header.jsx`
  - [ ] `Sidebar.jsx`
- [ ] `frontend/src/pages/` has 2 files:
  - [ ] `Dashboard.jsx`
  - [ ] `NotFound.jsx`
- [ ] `frontend/src/services/api.js` exists

### Configuration Files
- [ ] `frontend/package.json` exists
- [ ] `frontend/tailwind.config.js` exists
- [ ] `frontend/postcss.config.js` exists
- [ ] `frontend/.env.example` exists
- [ ] `frontend/.env` created: `cp frontend/.env.example frontend/.env`
- [ ] `frontend/.gitignore` exists

### Environment File
- [ ] `frontend/.env` contains: `REACT_APP_API_URL=http://localhost:8000`

---

## 🚀 Backend Startup Verification

### Start Backend
```bash
cd backend
source venv/bin/activate  # or: .\venv\Scripts\activate (Windows)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Backend Running
- [ ] No errors in terminal
- [ ] Shows: `Uvicorn running on http://0.0.0.0:8000`
- [ ] Shows: `Application startup complete`

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","timestamp":"..."}
```

- [ ] Returns status code 200
- [ ] Response includes `"status": "healthy"`

### Test Data Endpoint
```bash
curl http://localhost:8000/data | jq .
```

- [ ] Returns status code 200
- [ ] Response includes `"total"` and `"data"` fields
- [ ] Data array contains records from Google Sheet

### Test Stats Endpoint
```bash
curl http://localhost:8000/stats | jq .
```

- [ ] Returns status code 200
- [ ] Response includes `"total_registrations"`
- [ ] Response includes `"gender_ratio"`
- [ ] Response includes `"education_breakdown"`
- [ ] Response includes `"top_courses"`
- [ ] Response includes `"geographic_distribution"`
- [ ] Response includes `"preferred_companies"`

### API Documentation
- [ ] Visit http://localhost:8000/docs
- [ ] Shows Swagger UI
- [ ] All endpoints listed
- [ ] Can test endpoints in browser

---

## 🎨 Frontend Startup Verification

### Start Frontend
```bash
cd frontend
npm start
```

### Verify Frontend Running
- [ ] No errors in terminal
- [ ] Shows: `Compiled successfully!`
- [ ] Browser opens http://localhost:3000
- [ ] Page loads without errors

### Check Page Content
- [ ] Page title: "NITA Dashboard"
- [ ] Header shows: "NITA Dashboard"
- [ ] Sidebar visible with filters
- [ ] 4 KPI cards visible at top
- [ ] At least 1 chart visible

### Check Browser Console
- [ ] No JavaScript errors (F12 → Console tab)
- [ ] No TypeScript errors
- [ ] No network errors

### Verify API Communication
- [ ] Browser DevTools (F12) → Network tab
- [ ] Click on `/stats` request
- [ ] Shows status 200
- [ ] Response has correct data

---

## 📊 Dashboard Features Verification

### KPI Cards
- [ ] "Total Applicants" card shows number
- [ ] "Placement Rate" card shows percentage
- [ ] "Male Applicants" card shows percentage
- [ ] "Female Applicants" card shows percentage

### Charts Visibility
- [ ] Gender distribution pie chart displays
- [ ] Education level bar chart displays
- [ ] Top courses bar chart displays
- [ ] Geographic distribution chart displays
- [ ] Companies horizontal bar chart displays

### Filters Working
- [ ] County dropdown opens
- [ ] County options display
- [ ] Selecting county updates charts
- [ ] Level dropdown opens
- [ ] Level options display
- [ ] Selecting level updates charts
- [ ] "Clear Filters" button removes selections

### Interactive Features
- [ ] Can hover over chart data points
- [ ] Tooltips show on hover
- [ ] Refresh button works
- [ ] Charts are responsive (resize browser)

---

## 🔄 Data Sync Verification

### Real-time Updates
- [ ] Modify data in Google Sheet
- [ ] Click "Refresh" in dashboard
- [ ] Charts update with new data
- [ ] Changes appear within 5 seconds

### Filter Results
- [ ] Select a county filter
- [ ] Total count updates
- [ ] Charts update accordingly
- [ ] Apply level filter
- [ ] Further filters the data

### Search Feature (Optional)
- [ ] API endpoint `/search?query=test` returns results
- [ ] Results include matching records

---

## 📱 Responsive Design Verification

### Desktop (1920x1080)
- [ ] Sidebar visible on left
- [ ] Charts in 2-column grid
- [ ] All content visible without scrolling

### Tablet (768x1024)
- [ ] Charts in single column
- [ ] Sidebar togglable
- [ ] Touch-friendly buttons

### Mobile (375x667)
- [ ] Hamburger menu visible
- [ ] Single column layout
- [ ] Charts stack vertically
- [ ] Text readable without zoom

---

## 🐳 Docker Verification (Optional)

### Docker Installation
- [ ] Docker installed: `docker --version`
- [ ] Docker running: `docker ps`
- [ ] Docker Compose installed: `docker-compose --version`

### Docker Build
```bash
docker-compose up --build
```

- [ ] Backend image builds successfully
- [ ] Frontend image builds successfully
- [ ] PostgreSQL container starts
- [ ] All containers healthy

### Docker Container Access
- [ ] Frontend at http://localhost:3000
- [ ] Backend at http://localhost:8000
- [ ] Backend health check passes: `curl http://localhost:8000/health`

---

## 📚 Documentation Verification

### README Files
- [ ] `README.md` exists and readable
- [ ] `QUICKSTART.md` exists and readable
- [ ] `DEVELOPMENT.md` exists and readable
- [ ] `API_DOCUMENTATION.md` exists and readable
- [ ] `PROJECT_SUMMARY.md` exists and readable

### Setup Scripts
- [ ] `setup.sh` is executable: `chmod +x setup.sh`
- [ ] `start.sh` is executable: `chmod +x start.sh`

---

## 🔒 Security Verification

### Git Configuration
- [ ] `service_account.json` in `.gitignore`
- [ ] `.env` files in `.gitignore`
- [ ] `node_modules/` in frontend `.gitignore`
- [ ] `venv/` in backend `.gitignore`

### Environment Files
- [ ] `.env.example` committed (not `.env`)
- [ ] No secrets in README files
- [ ] No credentials in code

### CORS Configuration
- [ ] CORS headers present in API responses
- [ ] Accessible from localhost

---

## ⚠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'gspread'"
```bash
cd backend
source venv/bin/activate
pip install gspread
```

### Issue: "Error: ENOENT: no such file or directory 'service_account.json'"
```bash
# Copy your credentials file
cp ~/Downloads/your-key-file.json backend/service_account.json
```

### Issue: "Port 8000 already in use"
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Issue: "Port 3000 already in use"
```bash
# Kill process on port 3000
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Issue: Charts not displaying
1. Check browser console (F12)
2. Verify API returns data: `curl http://localhost:8000/stats`
3. Check network tab for errors
4. Verify Plotly.js loaded from CDN

---

## ✅ Final Sign-Off

When all checks are complete:

- [ ] Backend running successfully
- [ ] Frontend running successfully  
- [ ] Google Sheets connected
- [ ] All 5 charts displaying
- [ ] Filters working correctly
- [ ] No errors in console
- [ ] Dashboard is responsive
- [ ] Documentation is complete

**Your dashboard is ready for use!** 🎉

---

## 📞 Support

If any check fails:
1. Read the error message carefully
2. Check [README.md](README.md#-troubleshooting)
3. Review [DEVELOPMENT.md](DEVELOPMENT.md) architecture section
4. Check browser console (F12)
5. Check terminal logs for API errors

---

**Created:** February 8, 2026  
**Last Updated:** February 8, 2026
