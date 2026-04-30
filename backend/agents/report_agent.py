from __future__ import annotations

from datetime import datetime
from backend.agents.base import AgentContext, BaseAgent


class ReportAgent(BaseAgent):
    name = "ReportAgent-报告生成智能体"

    def run(self, ctx: AgentContext) -> AgentContext:
        severity = "Normal"
        if ctx.findings:
            severity = ctx.findings[0]["severity"]
        summary = ctx.findings[0]["name"] if ctx.findings else "未发现明显已知错误"
        md = self._build_markdown(ctx, summary, severity)
        ctx.report = {
            "summary": summary,
            "severity": severity,
            "markdown": md,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        }
        ctx.trace(self.name, "已生成 Markdown 诊断报告，可用于飞书页面或导出。")
        return ctx

    def _build_markdown(self, ctx: AgentContext, summary: str, severity: str) -> str:
        lines = [
            "# 科研训练日志自动诊断报告",
            "",
            f"- 日志名称：{ctx.log_name}",
            f"- 总体结论：{summary}",
            f"- 最高严重程度：{severity}",
            f"- 日志行数：{ctx.parsed.get('line_count', 0)}",
            "",
            "## 一、Multi-Agent 协同过程",
        ]
        for i, t in enumerate(ctx.traces, 1):
            lines.append(f"{i}. **{t['agent']}**：{t['content']}")
        lines += ["", "## 二、诊断问题"]
        if not ctx.findings:
            lines.append("未命中规则库中的常见问题。")
        for i, f in enumerate(ctx.findings, 1):
            lines += [
                f"### {i}. {f['name']}",
                f"- 类别：{f['category']}",
                f"- 严重程度：{f['severity']}",
                f"- 置信度：{f['confidence']:.2f}",
                f"- 可能原因：{f['cause']}",
                f"- 修复建议：{f['suggestion']}",
                "- 命中日志片段：",
                "```text",
                f["matched_text"][:1200],
                "```",
                "",
            ]
        lines += ["", "## 三、建议命令"]
        for s in ctx.solutions:
            lines.append(f"### {s['problem']}")
            for cmd in s["commands"]:
                lines.append(f"```bash\n{cmd}\n```")
        return "\n".join(lines)
