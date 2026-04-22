from dataclasses import dataclass
from typing import Dict


@dataclass
class HealthCheckResponse:
    status: str


@dataclass
class ReadinessCheckResponse:
    status: str
    checks: Dict[str, bool]
    http_status_code: int
