from sqlalchemy.orm import Session
from app.models import SensorReading, Alert
from app.crud import create_alert, resolve_alerts_by_type, get_active_alerts
from typing import List

class AlertEngine:
    """Rules-based alert detection engine"""

    # Thresholds
    TDS_MIN = 500
    TDS_MAX = 1100
    TEMP_MIN = 15
    TEMP_MAX = 35
    WATER_LEVEL_MIN = 10

    @staticmethod
    def check_alerts(db: Session, reading: SensorReading) -> List[Alert]:
        """Check sensor reading against all rules and generate alerts"""
        alerts_generated = []

        # Rule 1: TDS Deficiency
        if reading.tds_ppm < AlertEngine.TDS_MIN:
            resolve_alerts_by_type(db, "nutrient_deficiency")
            alert = create_alert(
                db=db,
                alert_type="nutrient_deficiency",
                severity="warning",
                message=f"Nutrient Deficiency Detected: TDS {reading.tds_ppm} ppm is below minimum threshold of {AlertEngine.TDS_MIN} ppm",
                tds_value=reading.tds_ppm
            )
            alerts_generated.append(alert)
        else:
            resolve_alerts_by_type(db, "nutrient_deficiency")

        # Rule 2: TDS Over Concentration
        if reading.tds_ppm > AlertEngine.TDS_MAX:
            resolve_alerts_by_type(db, "over_concentration")
            alert = create_alert(
                db=db,
                alert_type="over_concentration",
                severity="critical",
                message=f"Over Concentration Detected: TDS {reading.tds_ppm} ppm exceeds maximum threshold of {AlertEngine.TDS_MAX} ppm",
                tds_value=reading.tds_ppm
            )
            alerts_generated.append(alert)
        else:
            resolve_alerts_by_type(db, "over_concentration")

        # Rule 3: Low Water Level
        if reading.water_level_cm < AlertEngine.WATER_LEVEL_MIN:
            resolve_alerts_by_type(db, "low_water_level")
            alert = create_alert(
                db=db,
                alert_type="low_water_level",
                severity="critical",
                message=f"Low Water Level: {reading.water_level_cm} cm is below minimum threshold of {AlertEngine.WATER_LEVEL_MIN} cm",
                water_level_value=reading.water_level_cm
            )
            alerts_generated.append(alert)
        else:
            resolve_alerts_by_type(db, "low_water_level")

        # Rule 4: Temperature Risk
        if reading.temperature_c < AlertEngine.TEMP_MIN:
            resolve_alerts_by_type(db, "temperature_low")
            alert = create_alert(
                db=db,
                alert_type="temperature_low",
                severity="warning",
                message=f"Temperature Too Low: {reading.temperature_c}°C is below minimum threshold of {AlertEngine.TEMP_MIN}°C",
                temp_value=reading.temperature_c
            )
            alerts_generated.append(alert)
        elif reading.temperature_c > AlertEngine.TEMP_MAX:
            resolve_alerts_by_type(db, "temperature_high")
            alert = create_alert(
                db=db,
                alert_type="temperature_high",
                severity="warning",
                message=f"Temperature Too High: {reading.temperature_c}°C exceeds maximum threshold of {AlertEngine.TEMP_MAX}°C",
                temp_value=reading.temperature_c
            )
            alerts_generated.append(alert)
        else:
            resolve_alerts_by_type(db, "temperature_low")
            resolve_alerts_by_type(db, "temperature_high")

        # Rule 5: Pump Runtime Risk
        if reading.pump_state == "ON":
            active_pump_alerts = [a for a in get_active_alerts(db) if a.alert_type == "pump_runtime_risk"]
            if not active_pump_alerts:
                alert = create_alert(
                    db=db,
                    alert_type="pump_runtime_risk",
                    severity="warning",
                    message="Pump Running: Monitor for extended runtime to prevent overheating"
                )
                alerts_generated.append(alert)
        else:
            resolve_alerts_by_type(db, "pump_runtime_risk")

        return alerts_generated
