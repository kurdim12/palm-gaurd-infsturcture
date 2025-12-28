from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

# Sensor Schemas
class SensorReadingCreate(BaseModel):
    tds_ppm: float = Field(..., ge=0, le=5000)
    temperature_c: float = Field(..., ge=-10, le=60)
    water_level_cm: float = Field(..., ge=0, le=200)
    pump_state: Literal["ON", "OFF"]
    source: Literal["simulated", "manual"] = "manual"

class SensorReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    tds_ppm: float
    temperature_c: float
    water_level_cm: float
    pump_state: str
    source: str

    class Config:
        from_attributes = True

# Control Schemas
class PumpControlRequest(BaseModel):
    state: Literal["ON", "OFF"]
    user: str = "operator"

class DoseControlRequest(BaseModel):
    amount_ml: float = Field(..., ge=0, le=1000)
    user: str = "operator"

class ControlActionResponse(BaseModel):
    id: int
    timestamp: datetime
    action_type: str
    action_value: str
    user: str

    class Config:
        from_attributes = True

# Alert Schemas
class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    alert_type: str
    severity: str
    message: str
    is_active: bool
    resolved_at: Optional[datetime]
    tds_value: Optional[float]
    temp_value: Optional[float]
    water_level_value: Optional[float]

    class Config:
        from_attributes = True

# Simulator Schemas
class SimulatorStatusResponse(BaseModel):
    running: bool
    message: str
