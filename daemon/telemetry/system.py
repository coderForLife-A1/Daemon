"""System hardware and resource telemetry sensor."""

import os
import psutil
from pydantic import BaseModel


class SystemMetrics(BaseModel):
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    process_count: int = 0
    thermal_stress_index: float = 0.0  # Synthetic score 0.0 - 1.0 based on CPU & RAM load


class SystemSensor:
    def __init__(self):
        # Initial prime call for psutil
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

    def read(self) -> SystemMetrics:
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            pids = len(psutil.pids())
            ram_used_gb = round(mem.used / (1024 ** 3), 2)
            ram_total_gb = round(mem.total / (1024 ** 3), 2)

            # Thermal stress estimation: combination of CPU load and memory pressure
            stress = min(1.0, max(0.0, (cpu * 0.7 + mem.percent * 0.3) / 100.0))

            return SystemMetrics(
                cpu_percent=cpu,
                ram_percent=mem.percent,
                ram_used_gb=ram_used_gb,
                ram_total_gb=ram_total_gb,
                process_count=pids,
                thermal_stress_index=round(stress, 3)
            )
        except Exception:
            return SystemMetrics()

