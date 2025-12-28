from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import SensorReading, ControlAction, Alert
from app.schemas import SensorReadingCreate

def create_sensor_reading(db: Session, reading: SensorReadingCreate) -> SensorReading:
    """Create new sensor reading"""
    db_reading = SensorReading(**reading.model_dump())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_latest_sensor_reading(db: Session) -> Optional[SensorReading]:
    """Get most recent sensor reading"""
    return db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()

def get_sensor_readings_by_range(db: Session, hours: int = 1, limit: int = 1000) -> List[SensorReading]:
    """Get sensor readings within time range"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(SensorReading)\
        .filter(SensorReading.timestamp >= cutoff_time)\
        .order_by(desc(SensorReading.timestamp))\
        .limit(limit)\
        .all()

def create_control_action(db: Session, action_type: str, action_value: str, user: str = "system") -> ControlAction:
    """Create control action record"""
    action = ControlAction(
        action_type=action_type,
        action_value=action_value,
        user=user
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action

def get_recent_control_actions(db: Session, limit: int = 50) -> List[ControlAction]:
    """Get recent control actions"""
    return db.query(ControlAction)\
        .order_by(desc(ControlAction.timestamp))\
        .limit(limit)\
        .all()

def create_alert(db: Session, alert_type: str, severity: str, message: str,
                tds_value: Optional[float] = None,
                temp_value: Optional[float] = None,
                water_level_value: Optional[float] = None) -> Alert:
    """Create new alert"""
    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        message=message,
        tds_value=tds_value,
        temp_value=temp_value,
        water_level_value=water_level_value
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_active_alerts(db: Session) -> List[Alert]:
    """Get all active alerts"""
    return db.query(Alert)\
        .filter(Alert.is_active == True)\
        .order_by(desc(Alert.timestamp))\
        .all()

def get_alert_history(db: Session, limit: int = 100) -> List[Alert]:
    """Get alert history"""
    return db.query(Alert)\
        .order_by(desc(Alert.timestamp))\
        .limit(limit)\
        .all()

def resolve_alerts_by_type(db: Session, alert_type: str):
    """Resolve all active alerts of a specific type"""
    db.query(Alert)\
        .filter(and_(Alert.alert_type == alert_type, Alert.is_active == True))\
        .update({
            "is_active": False,
            "resolved_at": datetime.utcnow()
        })
    db.commit()

def get_db_statistics(db: Session) -> dict:
    """Get database statistics for reporting"""
    total_readings = db.query(SensorReading).count()
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
    total_actions = db.query(ControlAction).count()

    # Get latest reading
    latest = get_latest_sensor_reading(db)

    # Get average values from last 24h
    cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_readings = db.query(SensorReading)\
        .filter(SensorReading.timestamp >= cutoff)\
        .all()

    avg_tds = sum(r.tds_ppm for r in recent_readings) / len(recent_readings) if recent_readings else 0
    avg_temp = sum(r.temperature_c for r in recent_readings) / len(recent_readings) if recent_readings else 0
    avg_water = sum(r.water_level_cm for r in recent_readings) / len(recent_readings) if recent_readings else 0

    return {
        "total_readings": total_readings,
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "total_actions": total_actions,
        "latest_tds": latest.tds_ppm if latest else 0,
        "latest_temp": latest.temperature_c if latest else 0,
        "latest_water_level": latest.water_level_cm if latest else 0,
        "avg_tds_24h": round(avg_tds, 2),
        "avg_temp_24h": round(avg_temp, 2),
        "avg_water_level_24h": round(avg_water, 2),
        "recent_readings_count": len(recent_readings)
    }
