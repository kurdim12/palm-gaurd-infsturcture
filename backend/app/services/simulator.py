import asyncio
import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas import SensorReadingCreate
from app.crud import create_sensor_reading
from app.services.alert_engine import AlertEngine

class SensorSimulator:
    """Simulates realistic sensor data with drift"""

    def __init__(self):
        self.running = False
        self.task = None

        # Initial state
        self.tds = 800.0
        self.temperature = 24.0
        self.water_level = 50.0
        self.pump_state = "OFF"

    async def start(self):
        """Start the simulator"""
        if self.running:
            return {"status": "already_running"}

        self.running = True
        self.task = asyncio.create_task(self._simulate_loop())
        return {"status": "started"}

    async def stop(self):
        """Stop the simulator"""
        if not self.running:
            return {"status": "not_running"}

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        return {"status": "stopped"}

    def is_running(self) -> bool:
        """Check if simulator is running"""
        return self.running

    async def _simulate_loop(self):
        """Main simulation loop"""
        try:
            while self.running:
                # Generate realistic sensor drift
                self._update_values()

                # Create reading
                db = SessionLocal()
                try:
                    reading_data = SensorReadingCreate(
                        tds_ppm=round(self.tds, 2),
                        temperature_c=round(self.temperature, 2),
                        water_level_cm=round(self.water_level, 2),
                        pump_state=self.pump_state,
                        source="simulated"
                    )

                    reading = create_sensor_reading(db, reading_data)

                    # Run alert engine
                    AlertEngine.check_alerts(db, reading)

                finally:
                    db.close()

                # Wait 3 seconds
                await asyncio.sleep(3)

        except asyncio.CancelledError:
            self.running = False
            raise

    def _update_values(self):
        """Update sensor values with realistic drift"""
        # TDS drift (±5 ppm per reading)
        self.tds += random.uniform(-5, 5)
        self.tds = max(200, min(1500, self.tds))  # Clamp between 200-1500

        # Random events
        if random.random() < 0.02:  # 2% chance
            # Simulate nutrient deficiency
            self.tds = random.uniform(300, 490)
        elif random.random() < 0.02:  # 2% chance
            # Simulate over concentration
            self.tds = random.uniform(1110, 1400)

        # Temperature drift (±0.5°C per reading)
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(10, min(40, self.temperature))  # Clamp between 10-40

        # Water level drift (slow decrease when pump is off, increase when on)
        if self.pump_state == "ON":
            self.water_level += random.uniform(0.5, 1.5)  # Filling
        else:
            self.water_level -= random.uniform(0.1, 0.3)  # Evaporation

        self.water_level = max(5, min(100, self.water_level))  # Clamp between 5-100

        # Random pump state change
        if random.random() < 0.05:  # 5% chance to toggle
            self.pump_state = "OFF" if self.pump_state == "ON" else "ON"

# Global simulator instance
simulator = SensorSimulator()
