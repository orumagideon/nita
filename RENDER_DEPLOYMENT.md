# NITA Dashboard Deployment on Render

## Overview
Your project has 2 components that require different Render services:
- **Frontend (React)** → Deploy as Static Site (FREE)
- **Backend (FastAPI)** → Deploy as Web Service (Free tier available)

---

## Part 1: Deploy Frontend as Static Site

### Form Fields to Fill:

| Field | Value | Notes |
|-------|-------|-------|
| **Source Code** | `orumagideon/nita` | Already connected to your GitHub |
| **Name** | `nita-dashboard` | Unique name for your site |
| **Project** | `nita` (or new) | Optional - for organization |
| **Branch** | `main` | The branch to deploy from |
| **Root Directory** | `frontend` | Where the React app is located |
| **Build Command** | `npm install && npm run build` | Build the React app |
| **Publish Directory** | `build` | Output folder from npm build |

### Step-by-Step:
1. **Name**: Enter `nita-dashboard-frontend`
2. **Root Directory**: Type `frontend`
3. **Build Command**: Type `npm install && npm run build`
4. **Publish Directory**: Type `build`
5. **Environment Variables**: Add if needed (see below)

### Frontend Environment Variables (Optional):
```
REACT_APP_API_URL = https://your-backend-url.onrender.com
```
(You'll create the backend URL next)

---

## Part 2: Deploy Backend as Web Service

After deploying the frontend, you'll need to deploy the backend:

1. Go to Render Dashboard → New → Web Service
2. Connect to the same GitHub repo

### Web Service Form Fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `nita-dashboard-backend` | Unique name |
| **Root Directory** | `backend` | Where FastAPI app is |
| **Build Command** | `pip install -r requirements.txt` | Install Python dependencies |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port 8000` | Run FastAPI server |
| **Environment Variables** | See below | Important! |

### Backend Environment Variables (REQUIRED):

1. Encode your `service_account.json` as base64:
```bash
cat backend/service_account.json | base64
```

2. Add these environment variables in Render:
```
SERVICE_ACCOUNT_JSON = [paste the base64 string here]
SPREADSHEET_ID = 1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns
```

3. In your `backend/main.py`, add code to read from env var:
```python
import os
import json
import base64

# Read service account from environment variable
if os.getenv('SERVICE_ACCOUNT_JSON'):
    service_account_json = base64.b64decode(os.getenv('SERVICE_ACCOUNT_JSON')).decode()
    with open('service_account.json', 'w') as f:
        f.write(service_account_json)
```

---

## Summary of Render URLs

Once deployed:
- **Frontend**: https://nita-dashboard-frontend.onrender.com
- **Backend API**: https://nita-dashboard-backend.onrender.com
- **API Endpoints**: https://nita-dashboard-backend.onrender.com/stats, /counties, /data, etc.

---

## Quick Checklist

- [ ] Frontend deployed as Static Site
- [ ] Backend deployed as Web Service
- [ ] Environment variables set for backend
- [ ] Frontend `.env` updated with backend URL
- [ ] GitHub repository is public (or add Render's SSH key)
- [ ] Test API endpoints are accessible

---

## Troubleshooting

**404 on frontend?** Check Root Directory is `frontend` and Publish Directory is `build`

**Backend not starting?** Check environment variables are properly set

**API not connecting?** Ensure CORS is enabled in FastAPI (it is in your code)

**Service account error?** Verify the base64 encoding is correct
