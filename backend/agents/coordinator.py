from __future__ import annotations

from backend.agents.base import AgentContext
from backend.agents.parser_agent import ParserAgent
from backend.agents.diagnosis_agent import DiagnosisAgent
from backend.agents.solution_agent import SolutionAgent
from backend.agents.report_agent import ReportAgent


class MultiAgentCoordinator:
    """多 Agent 调度器：日志解析 -> 错误诊断 -> 解决方案 -> 报告生成"""

    def __init__(self):
        self.agents = [ParserAgent(), DiagnosisAgent(), SolutionAgent(), ReportAgent()]

    def run(self, log_name: str, raw_text: str) -> AgentContext:
        ctx = AgentContext(log_name=log_name, raw_text=raw_text)
        ctx.trace("Coordinator-调度智能体", "接收日志任务，开始串行调度多个智能体协同分析。")
        for agent in self.agents:
            ctx = agent.run(ctx)
        ctx.trace("Coordinator-调度智能体", "所有智能体执行完毕，返回结构化诊断结果。")
        return ctx
