from __future__ import annotations

import requests
from backend.core.config import FEISHU_WEBHOOK_URL


def send_feishu_webhook(title: str, markdown: str) -> dict:
    """
    可选：发送飞书群机器人通知。
    使用方法：在 .env 或环境变量中配置 FEISHU_WEBHOOK_URL。
    """
    if not FEISHU_WEBHOOK_URL:
        return {"ok": False, "message": "未配置 FEISHU_WEBHOOK_URL，仅生成本地飞书风格报告页面。"}
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"},
            "elements": [
                {"tag": "markdown", "content": markdown[:6000]},
            ],
        },
    }
    resp = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
    return {"ok": resp.ok, "status_code": resp.status_code, "text": resp.text[:500]}
