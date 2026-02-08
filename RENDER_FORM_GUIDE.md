# Render Deployment - Field Filling Guide

## Step 1: Get Your Service Account as Base64

Run this command in your terminal:
```bash
chmod +x scripts/encode_service_account.sh
./scripts/encode_service_account.sh
```

This will output a long base64 string. **Copy this entire string** - you'll need it for the backend deployment.

---

## Step 2: Deploy Frontend (Static Site)

**Go to Render Dashboard → New → Static Site**

### Form Filling:

```
┌─────────────────────────────────────────────────────┐
│ Source Code                                          │
│ ✓ orumagideon/nita (connected)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Name                                                 │
│ │ nita-dashboard-frontend                          │
└─────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────┐
│ Project (Optional)   │ Environment                  │
│ │ nita              │ │ Production                 │
└──────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Branch                                               │
│ │ main                                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Root Directory                                       │
│ │ frontend                                          │
│ (The React app folder)                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Build Command                                        │
│ │ npm install && npm run build                      │
│ (Build the React app)                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Publish Directory                                    │
│ │ build                                             │
│ (The output folder from npm build)                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Environment Variables (Optional)                     │
│                                                      │
│ NAME: REACT_APP_API_URL                             │
│ VALUE: (Leave empty for now - update after          │
│        backend is deployed)                         │
│                                                      │
│ Click "+ Add Environment Variable"                  │
└─────────────────────────────────────────────────────┘
```

Then click **"Create Static Site"** and wait for deployment (2-5 minutes)

---

## Step 3: Deploy Backend (Web Service)

**Go to Render Dashboard → New → Web Service**

### Form Filling:

```
┌─────────────────────────────────────────────────────┐
│ Source Code                                          │
│ ✓ orumagideon/nita (connected)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Name                                                 │
│ │ nita-dashboard-backend                           │
└─────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────┐
│ Project (Optional)   │ Environment                  │
│ │ nita              │ │ Production                 │
└──────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Branch                                               │
│ │ main                                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Root Directory                                       │
│ │ backend                                           │
│ (The FastAPI app folder)                            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Build Command                                        │
│ │ pip install -r requirements.txt                   │
│ (Install Python dependencies)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Start Command                                        │
│ │ uvicorn main:app --host 0.0.0.0 --port 8000      │
│ (Run the FastAPI server)                            │
└─────────────────────────────────────────────────────┘
```

### IMPORTANT: Environment Variables for Backend

**Add these 2 environment variables:**

#### Variable 1: Service Account JSON (from base64 encoding)
```
NAME: SERVICE_ACCOUNT_JSON
VALUE: [Paste the entire base64 string from Step 1]
```

#### Variable 2: Spreadsheet ID
```
NAME: SPREADSHEET_ID
VALUE: 1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns
```

Then click **"Create Web Service"** and wait for deployment (3-5 minutes)

---

## Step 4: Update Frontend with Backend URL

1. **Copy your backend URL** from Render (looks like: `https://nita-dashboard-backend.onrender.com`)

2. **Go back to your frontend service settings**
   - Navigate to Environment
   - Update `REACT_APP_API_URL` with your backend URL

3. **Trigger a redeploy:**
   - Go to Deployments
   - Click "Trigger Deploy"

---

## Final URLs

Once both are deployed:

- **Frontend**: `https://nita-dashboard-frontend.onrender.com`
- **Backend API**: `https://nita-dashboard-backend.onrender.com`
- **API Endpoints**:
  - Stats: `https://nita-dashboard-backend.onrender.com/stats`
  - Data: `https://nita-dashboard-backend.onrender.com/data`
  - Counties: `https://nita-dashboard-backend.onrender.com/counties`
  - Health: `https://nita-dashboard-backend.onrender.com/health`

---

## Troubleshooting

### Build fails on frontend?
```bash
# Make sure package.json exists in frontend/
# And npm dependencies are correct
```

### Build fails on backend?
```bash
# Make sure requirements.txt exists in backend/
# All Python packages are available
```

### API not responding?
- Check Environment Variables are set correctly
- Check the backend service is running (visit `/health` endpoint)
- Check CORS is enabled (it should be)

### Service account error?
- Verify the base64 string is complete (no line breaks)
- Try re-encoding: `./scripts/encode_service_account.sh`

### Frontend can't reach backend?
- Verify `REACT_APP_API_URL` is set correctly
- Ensure backend service is running
- Check browser console (F12) for CORS errors
