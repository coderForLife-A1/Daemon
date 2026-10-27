"""Base class for visual overlay anomalies."""

import time
from abc import ABC, abstractmethod
from PySide6.QtGui import QPainter


class BaseEffect(ABC):
    """Abstract base class for a rendered anomaly on the overlay."""

    def __init__(self, duration: float = 6.0):
        self.duration = duration
        self.start_time = time.time()
        self.age = 0.0
        self.is_alive = True

    def tick(self, dt: float) -> bool:
        """Update anomaly state. Returns True if still alive, False if expired."""
        self.age += dt
        if self.age >= self.duration:
            self.is_alive = False
        return self.is_alive

    @abstractmethod
    def render(self, painter: QPainter, width: int, height: int) -> None:
        """Render the effect onto the QPainter canvas."""
        pass

