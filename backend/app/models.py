from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    tds_ppm = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    water_level_cm = Column(Float, nullable=False)
    pump_state = Column(String, nullable=False)  # ON / OFF
    source = Column(String, nullable=False)  # simulated / manual

class ControlAction(Base):
    __tablename__ = "control_actions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    action_type = Column(String, nullable=False)  # pump / dose
    action_value = Column(String, nullable=False)  # ON/OFF or amount_ml
    user = Column(String, default="system")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # warning / critical
    message = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    tds_value = Column(Float, nullable=True)
    temp_value = Column(Float, nullable=True)
    water_level_value = Column(Float, nullable=True)
