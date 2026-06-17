from datetime import datetime

from pydantic import BaseModel


class ScanResult(BaseModel):
    scan_id: str
    label: str
    confidence: float
    raw_score: float
    filename: str
    scanned_at: datetime


class ScanHistoryItem(BaseModel):
    scan_id: str
    label: str
    confidence: float
    filename: str
    scanned_at: datetime


class ScanHistoryResponse(BaseModel):
    scans: list[ScanHistoryItem]
    total: int
