from __future__ import annotations

from backend.agents.base import AgentContext, BaseAgent

COMMANDS = {
    "GPU/CUDA": ["nvidia-smi", "watch -n 1 nvidia-smi", "ps -ef | grep python", "kill -9 <PID>"],
    "Autograd": ["torch.autograd.set_detect_anomaly(True)", "grep -R \"+=\\|relu_\\|masked_fill_\" -n models/"],
    "Environment": ["which python", "python --version", "python -m pip check", "conda list | grep torch"],
    "File/Path": ["pwd", "ls -lh", "find . -name '<filename>'", "realpath <path>"],
    "IO/Checkpoint": ["df -h", "du -sh <output_dir>", "ls -ld <output_dir>"],
    "Network": ["ping mirrors.tuna.tsinghua.edu.cn", "pip config list", "conda config --show channels"],
}


class SolutionAgent(BaseAgent):
    name = "SolutionAgent-解决方案智能体"

    def run(self, ctx: AgentContext) -> AgentContext:
        solutions = []
        for f in ctx.findings:
            commands = COMMANDS.get(f["category"], [])
            solution = {
                "problem": f["name"],
                "priority": f["severity"],
                "actions": [
                    f["suggestion"],
                    "先做最小复现实验：只运行 1 个 batch 或 1 个 epoch，确认问题是否稳定复现。",
                    "保留完整 Traceback 和运行命令，方便后续定位。",
                ],
                "commands": commands,
            }
            solutions.append(solution)
        ctx.solutions = solutions
        ctx.trace(self.name, f"为 {len(solutions)} 个问题生成了排查步骤和命令建议。")
        return ctx
