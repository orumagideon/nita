# NITA Dashboard - Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites Check

```bash
# Check Python
python3 --version  # Should be 3.8+

# Check Node.js
node --version     # Should be 14+
npm --version
```

### 1. Clone Repository (Skip if you have it)

```bash
git clone <repository-url>
cd nita
```

### 2. Run Automated Setup

```bash
bash setup.sh
```

If that doesn't work, follow manual setup below.

## 📖 Manual Setup

### Backend Setup (5 minutes)

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (choose your OS)
# macOS/Linux:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Go back to root
cd ..
```

### Frontend Setup (3 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file (if using custom API URL)
cp .env.example .env

# Go back to root
cd ..
```

## 🔐 Google Cloud Setup (Critical)

This is required for the dashboard to work. **Do not skip this!**

### Quick Path (If you have credentials already):

```bash
# Place your JSON file here
mv ~/Downloads/your-key-file.json backend/service_account.json
```

Then:
1. Open the JSON file and copy the `client_email` value
2. Go to https://docs.google.com/spreadsheets/d/1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns
3. Click Share → Paste the email → Give Editor access → Click Share

### Full Path (If you don't have credentials):

See the **"Google Cloud Setup"** section in [README.md](README.md#-google-cloud-setup-required-for-data-sync)

## 🚀 Run the Dashboard

### Option A: Using Startup Script

```bash
bash start.sh
```

This starts both backend and frontend. The dashboard opens at:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

### Option B: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or: .\venv\Scripts\activate (Windows)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** Do NOT use `uvicorn app.main:app` - the correct command is `uvicorn main:app`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Option C: Docker

```bash
docker-compose up --build
```

Then open http://localhost:3000

## ✅ Verify It's Working

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy",...}`

### Frontend Loading

Open http://localhost:3000 in your browser. You should see:
- NITA Dashboard title
- County and Level filters on the left
- 4 KPI cards at the top
- 5 charts below

### If Something's Wrong

**"Cannot connect to backend"**
- ✓ Is backend running? Check Terminal 1
- ✓ Is it on port 8000? `curl http://localhost:8000/health`
- ✓ Check frontend `.env` file has correct `REACT_APP_API_URL`

**"No data showing in charts"**
- ✓ Is `service_account.json` in `backend/` folder?
- ✓ Is the service account email shared with the Google Sheet?
- ✓ Check browser console (F12) for errors

**"Permission denied from Google Sheets"**
- ✓ Did you share the sheet with the service account email?
- ✓ Did you give it "Editor" access?
- ✓ Did you wait a minute for permissions to sync?

## 🎨 Customization

### Change API URL (Production)

Edit `frontend/.env`:
```
REACT_APP_API_URL=https://your-api-domain.com
```

### Change Google Sheet

Edit `backend/main.py`:
```python
SPREADSHEET_ID = "your-new-sheet-id"
```

Get sheet ID from URL: `docs.google.com/spreadsheets/d/**SHEET_ID**/edit`

### Customize Port Numbers

**Backend:** Edit `start.sh` or run:
```bash
uvicorn main:app --port 9000
```

**Frontend:** Create `.env`:
```
PORT=3001
```

## 📱 Responsive Design

The dashboard works on all devices:
- **Desktop:** Full sidebar visible, grid layout
- **Tablet:** Sidebar hidden, mobile toggle
- **Mobile:** Hamburger menu, single-column layout

## 🛑 Stop the Dashboard

**If using `start.sh`:**
Press `Ctrl + C` in the terminal

**If using separate terminals:**
Press `Ctrl + C` in each terminal

**If using Docker:**
```bash
docker-compose down
```

## 🔄 Common Tasks

### Update Sheet Data Without Restarting

Just refresh the browser! The API fetches latest data on each request.

### Add New Filter Option

1. **Add column to Google Sheet**
2. **Update backend endpoint** in `main.py`
3. **Add to sidebar** in `frontend/src/components/Sidebar.jsx`

### Deploy to Production

See [DEVELOPMENT.md](DEVELOPMENT.md#deployment) for AWS/Heroku/DigitalOcean instructions

## 📚 Next Steps

1. **Explore the code**: Start with `frontend/src/pages/Dashboard.jsx`
2. **Read full docs**: See [README.md](README.md) and [DEVELOPMENT.md](DEVELOPMENT.md)
3. **Test API**: Visit http://localhost:8000/docs for interactive testing
4. **Customize charts**: Edit components in `frontend/src/components/`

## 💡 Pro Tips

- **Live reload**: Backend and frontend both auto-reload on file changes
- **Console logging**: Add `console.log()` to debug components
- **API testing**: Use http://localhost:8000/docs (Swagger UI)
- **Network tab**: Use browser DevTools (F12) → Network to see API calls
- **Performance**: Check React DevTools extension for component re-renders

## 🆘 Getting Help

If something doesn't work:

1. **Check logs**: Look at terminal output for error messages
2. **Check browser console**: F12 → Console tab
3. **Test API directly**: Use curl or http://localhost:8000/docs
4. **Review README.md**: Full troubleshooting section available
5. **Check DEVELOPMENT.md**: Architecture and debugging guide

## 🎉 You're Done!

Your dashboard is now running. Enjoy! 🚀

---

**Stuck?** Refer to the full [README.md](README.md#-troubleshooting) for detailed troubleshooting.
