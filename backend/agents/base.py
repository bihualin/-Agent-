from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AgentContext:
    log_name: str
    raw_text: str
    parsed: Dict[str, Any] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    solutions: List[Dict[str, Any]] = field(default_factory=list)
    report: Dict[str, Any] = field(default_factory=dict)
    traces: List[Dict[str, str]] = field(default_factory=list)

    def trace(self, agent: str, content: str) -> None:
        self.traces.append({"agent": agent, "content": content})


class BaseAgent:
    name = "BaseAgent"

    def run(self, ctx: AgentContext) -> AgentContext:
        raise NotImplementedError
