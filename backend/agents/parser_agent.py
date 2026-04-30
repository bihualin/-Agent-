from __future__ import annotations

import re
from backend.agents.base import AgentContext, BaseAgent


class ParserAgent(BaseAgent):
    name = "ParserAgent-日志解析智能体"

    def run(self, ctx: AgentContext) -> AgentContext:
        text = ctx.raw_text
        lines = text.splitlines()
        traceback_blocks = re.findall(r"Traceback \(most recent call last\):[\s\S]*?(?=\n\S|\Z)", text)
        levels = {
            "ERROR": len(re.findall(r"\bERROR\b|RuntimeError|Exception|Traceback", text, re.I)),
            "WARNING": len(re.findall(r"\bWARNING\b|UserWarning|FutureWarning", text, re.I)),
            "INFO": len(re.findall(r"\bINFO\b|Epoch|Start training", text, re.I)),
        }
        metrics = []
        for no, line in enumerate(lines, start=1):
            if any(k in line.lower() for k in ["loss", "acc", "accuracy", "epoch", "lr"]):
                metrics.append({"line": no, "text": line[:300]})
        ctx.parsed = {
            "line_count": len(lines),
            "char_count": len(text),
            "levels": levels,
            "traceback_count": len(traceback_blocks),
            "metrics_preview": metrics[:30],
        }
        ctx.trace(self.name, f"完成日志解析：共 {len(lines)} 行，Traceback 数量 {len(traceback_blocks)}，ERROR 信号 {levels['ERROR']} 个。")
        return ctx
