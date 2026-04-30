from __future__ import annotations
from pydantic import BaseModel


class DiagnoseRequest(BaseModel):
    log_name: str = "manual_log.txt"
    raw_text: str


class DiagnoseResponse(BaseModel):
    report_id: int
    log_id: int
    summary: str
    severity: str
    feishu_page_url: str
