# DualFarm - Quick Start Guide

## ✅ BACKEND IS RUNNING!

Your FastAPI backend is successfully running at:
**http://localhost:8000**

### Backend Status
- ✅ API Health: http://localhost:8000/health
- ✅ API Docs (Swagger): http://localhost:8000/docs
- ✅ All endpoints operational

## 🎯 How to Access the Application

### Option 1: API Documentation (Recommended - Works Now!)

1. Open your browser
2. Navigate to: **http://localhost:8000/docs**
3. You can test ALL features through Swagger UI:
   - Start/Stop simulator
   - Get latest sensor readings
   - Control pump
   - Dose nutrients
   - View alerts
   - Generate reports
   - Export CSV

### Option 2: Frontend Setup (Manual Steps Required)

The frontend has a Windows-specific npm dependency issue. To fix:

1. Open PowerShell or Command Prompt (as Administrator)
2. Navigate to frontend:
   ```powershell
   cd C:\Users\User\DualFarm\frontend
   ```

3. Remove node_modules:
   ```powershell
   Remove-Item -Path node_modules -Recurse -Force
   Remove-Item -Path package-lock.json -Force
   ```

4. Install dependencies:
   ```powershell
   npm install
   npm install @rollup/rollup-win32-x64-msvc --force
   ```

5. Start frontend:
   ```powershell
   npm run dev
   ```

6. Open browser to http://localhost:5173

## 🚀 TESTING THE SYSTEM NOW

### 1. Start the Simulator

Using curl or Swagger UI:
```bash
curl -X POST http://localhost:8000/api/simulate/start
```

### 2. Get Latest Sensor Reading

```bash
curl http://localhost:8000/api/sensors/latest
```

### 3. View Active Alerts

```bash
curl http://localhost:8000/api/alerts/latest
```

### 4. Control the Pump

```bash
curl -X POST http://localhost:8000/api/control/pump \
  -H "Content-Type: application/json" \
  -d '{"state":"ON","user":"operator"}'
```

### 5. Generate RoboCraft Report

```bash
curl http://localhost:8000/api/report/robocraft
```

### 6. Export CSV Data

Visit in browser:
http://localhost:8000/api/report/export/csv

## 📊 Full API Endpoints

### Sensors
- POST `/api/sensors/ingest` - Add sensor reading
- GET `/api/sensors/latest` - Latest reading
- GET `/api/sensors/history?range=1h` - History (1h|24h|7d)

### Control
- POST `/api/control/pump` - Pump ON/OFF
- POST `/api/control/dose` - Dose nutrients
- GET `/api/control/history` - Control history

### Alerts
- GET `/api/alerts/latest` - Active alerts
- GET `/api/alerts/history` - All alerts

### Simulator
- POST `/api/simulate/start` - Start simulation
- POST `/api/simulate/stop` - Stop simulation
- GET `/api/simulate/status` - Check status

### Reports
- GET `/api/report/robocraft` - Generate report
- GET `/api/report/export/csv` - Export CSV

## 🎓 For RoboCraft Competition

1. **Start Simulator** via Swagger UI or curl
2. Wait 30-60 seconds for data to accumulate
3. **Take Screenshots** of Swagger UI showing:
   - Sensor readings with realistic data
   - Active alerts (if any)
   - Control actions
   - Generated report

4. **Generate Report**:
   - Go to http://localhost:8000/api/report/robocraft
   - Copy the markdown content
   - Save as robocraft_report.md

5. **Export Data**:
   - Download CSV from http://localhost:8000/api/report/export/csv
   - Import into Excel/Google Sheets for charts

## 💡 Swagger UI Is Your Friend!

The Swagger UI at http://localhost:8000/docs provides:
- ✅ Interactive API testing
- ✅ No frontend needed
- ✅ All features accessible
- ✅ Request/response examples
- ✅ Perfect for demo screenshots

## 🎬 Demo Flow

1. Open http://localhost:8000/docs
2. Try POST `/api/simulate/start` → Click "Execute"
3. Try GET `/api/sensors/latest` → See real data
4. Try GET `/api/alerts/latest` → See alerts (if thresholds exceeded)
5. Try POST `/api/control/pump` → Control system
6. Try GET `/api/report/robocraft` → Get full report

## 📝 System Status

Backend Port: 8000 ✅ RUNNING
Frontend Port: 5173 ⏳ (Needs Windows PowerShell setup)
Database: SQLite ✅ AUTO-CREATED
Simulator: Ready ✅

---

**Your DualFarm backend is 100% functional!**
Use Swagger UI for full system access.
