from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

APP_NAME = os.getenv("APP_NAME", "科研训练日志自动诊断Agent系统")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "research_log_agent.db"))
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL", "")
