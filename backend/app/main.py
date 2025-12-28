from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List
import io
import csv

from app.database import init_db, get_db
from app.schemas import (
    SensorReadingCreate, SensorReadingResponse,
    PumpControlRequest, DoseControlRequest, ControlActionResponse,
    AlertResponse, SimulatorStatusResponse
)
from app.crud import (
    create_sensor_reading, get_latest_sensor_reading, get_sensor_readings_by_range,
    create_control_action, get_recent_control_actions,
    get_active_alerts, get_alert_history, get_db_statistics
)
from app.services.alert_engine import AlertEngine
from app.services.simulator import simulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    init_db()
    print("[OK] Database initialized")
    yield
    # Shutdown
    print("[OK] Application shutdown")

app = FastAPI(
    title="DualFarm API",
    description="AI-Assisted Smart Farming System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DualFarm API v1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Sensor endpoints
@app.post("/api/sensors/ingest", response_model=SensorReadingResponse, tags=["Sensors"])
async def ingest_sensor_data(reading: SensorReadingCreate, db: Session = Depends(get_db)):
    """Ingest new sensor reading and trigger alert engine"""
    db_reading = create_sensor_reading(db, reading)
    AlertEngine.check_alerts(db, db_reading)
    return db_reading

@app.get("/api/sensors/latest", response_model=SensorReadingResponse, tags=["Sensors"])
async def get_latest_reading(db: Session = Depends(get_db)):
    """Get most recent sensor reading"""
    reading = get_latest_sensor_reading(db)
    if not reading:
        raise HTTPException(status_code=404, detail="No sensor readings found")
    return reading

@app.get("/api/sensors/history", response_model=List[SensorReadingResponse], tags=["Sensors"])
async def get_reading_history(range: str = Query("1h", regex="^(1h|24h|7d)$"), db: Session = Depends(get_db)):
    """Get sensor reading history by time range"""
    range_map = {"1h": 1, "24h": 24, "7d": 168}
    hours = range_map.get(range, 1)
    readings = get_sensor_readings_by_range(db, hours=hours)
    return readings

# Control endpoints
@app.post("/api/control/pump", response_model=ControlActionResponse, tags=["Control"])
async def control_pump(request: PumpControlRequest, db: Session = Depends(get_db)):
    """Control water pump (ON/OFF)"""
    action = create_control_action(db=db, action_type="pump", action_value=request.state, user=request.user)
    return action

@app.post("/api/control/dose", response_model=ControlActionResponse, tags=["Control"])
async def dose_nutrients(request: DoseControlRequest, db: Session = Depends(get_db)):
    """Trigger nutrient dosing"""
    action = create_control_action(db=db, action_type="dose", action_value=f"{request.amount_ml}ml", user=request.user)
    return action

@app.get("/api/control/history", response_model=List[ControlActionResponse], tags=["Control"])
async def get_control_history(db: Session = Depends(get_db)):
    """Get recent control actions"""
    actions = get_recent_control_actions(db, limit=50)
    return actions

# Alert endpoints
@app.get("/api/alerts/latest", response_model=List[AlertResponse], tags=["Alerts"])
async def get_latest_alerts(db: Session = Depends(get_db)):
    """Get all active alerts"""
    alerts = get_active_alerts(db)
    return alerts

@app.get("/api/alerts/history", response_model=List[AlertResponse], tags=["Alerts"])
async def get_alerts_history(db: Session = Depends(get_db)):
    """Get alert history"""
    alerts = get_alert_history(db, limit=100)
    return alerts

# Simulator endpoints
@app.post("/api/simulate/start", response_model=SimulatorStatusResponse, tags=["Simulator"])
async def start_simulator():
    """Start sensor data simulation"""
    result = await simulator.start()
    return SimulatorStatusResponse(
        running=simulator.is_running(),
        message="Simulator started successfully" if result["status"] == "started" else "Simulator already running"
    )

@app.post("/api/simulate/stop", response_model=SimulatorStatusResponse, tags=["Simulator"])
async def stop_simulator():
    """Stop sensor data simulation"""
    result = await simulator.stop()
    return SimulatorStatusResponse(
        running=simulator.is_running(),
        message="Simulator stopped successfully" if result["status"] == "stopped" else "Simulator not running"
    )

@app.get("/api/simulate/status", response_model=SimulatorStatusResponse, tags=["Simulator"])
async def get_simulator_status():
    """Get simulator status"""
    return SimulatorStatusResponse(
        running=simulator.is_running(),
        message="Simulator is running" if simulator.is_running() else "Simulator is stopped"
    )

# Report endpoints
@app.get("/api/report/robocraft", tags=["Reports"])
async def get_robocraft_report(db: Session = Depends(get_db)):
    """Generate comprehensive RoboCraft competition report"""
    from datetime import datetime
    stats = get_db_statistics(db)

    report = f"""# DualFarm: AI-Assisted Smart Farming System
## RoboCraft Competition Technical Report

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

### System Statistics
- Total Sensor Readings: {stats['total_readings']:,}
- Active Alerts: {stats['active_alerts']}
- Total Alerts: {stats['total_alerts']}
- Control Actions: {stats['total_actions']}

### Latest Measurements
- TDS: {stats['latest_tds']:.2f} ppm
- Temperature: {stats['latest_temp']:.2f}°C
- Water Level: {stats['latest_water_level']:.2f} cm

### 24-Hour Averages
- Avg TDS: {stats['avg_tds_24h']:.2f} ppm
- Avg Temperature: {stats['avg_temp_24h']:.2f}°C
- Avg Water Level: {stats['avg_water_level_24h']:.2f} cm

For complete report, see README.md
"""

    return {
        "report_markdown": report,
        "statistics": stats,
        "generated_at": datetime.utcnow().isoformat(),
        "report_version": "1.0.0"
    }

@app.get("/api/report/export/csv", tags=["Reports"])
async def export_sensor_data_csv(db: Session = Depends(get_db)):
    """Export sensor readings to CSV"""
    readings = get_sensor_readings_by_range(db, hours=168, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'TDS (ppm)', 'Temperature (°C)', 'Water Level (cm)', 'Pump State', 'Source'])

    for reading in reversed(readings):
        writer.writerow([
            reading.timestamp.isoformat(),
            reading.tds_ppm,
            reading.temperature_c,
            reading.water_level_cm,
            reading.pump_state,
            reading.source
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=dualfarm_sensor_data.csv"}
    )
