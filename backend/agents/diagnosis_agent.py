from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from backend.agents.base import AgentContext, BaseAgent


RULES: List[Dict] = [
    {
        "name": "CUDA 显存不足",
        "category": "GPU/CUDA",
        "severity": "High",
        "patterns": [r"CUDA out of memory", r"out of memory", r"CUDNN_STATUS_ALLOC_FAILED"],
        "cause": "GPU 显存不足，通常由 batch size 过大、模型过大、输入尺寸过高或缓存未释放导致。",
        "suggestion": "减小 batch size，开启 AMP 混合精度，清理无关进程，并检查是否保存了过多中间张量。",
    },
    {
        "name": "Inplace Operation 梯度错误",
        "category": "Autograd",
        "severity": "High",
        "patterns": [r"modified by an inplace operation", r"inplace operation", r"expected version .* instead"],
        "cause": "反向传播需要的张量被原地修改，例如 +=、relu_、masked_fill_ 等。",
        "suggestion": "将原地操作改为非原地操作，开启 torch.autograd.set_detect_anomaly(True) 定位具体代码行。",
    },
    {
        "name": "缺少 Python 依赖包",
        "category": "Environment",
        "severity": "Medium",
        "patterns": [r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]", r"ImportError"],
        "cause": "当前环境缺少依赖，或者没有激活正确 conda 环境。",
        "suggestion": "确认 which python 和 python -m pip 指向同一环境，再安装缺失包。",
    },
    {
        "name": "文件路径不存在",
        "category": "File/Path",
        "severity": "Medium",
        "patterns": [r"No such file or directory", r"FileNotFoundError", r"can't open file"],
        "cause": "运行目录、数据集路径、checkpoint 路径或脚本路径配置错误。",
        "suggestion": "使用 pwd、ls、realpath 检查路径，建议在配置文件中使用绝对路径。",
    },
    {
        "name": "Checkpoint 保存失败",
        "category": "IO/Checkpoint",
        "severity": "High",
        "patterns": [r"PytorchStreamWriter failed writing file", r"inline_container\.cc", r"torch\.save"],
        "cause": "磁盘空间不足、目录无权限、网络文件系统异常，或分布式多进程同时保存。",
        "suggestion": "检查 df -h 和目录权限；分布式训练只允许 rank0 保存 checkpoint。",
    },
    {
        "name": "依赖版本冲突",
        "category": "Environment",
        "severity": "Medium",
        "patterns": [r"ResolutionImpossible", r"conflicting dependencies", r"requires .* but you have"],
        "cause": "requirements 中固定版本互相冲突，尤其是 torch/torchvision/torchaudio/python 版本。",
        "suggestion": "先固定 Python 和 PyTorch 主版本，再逐个安装依赖；移除不必要的严格版本号。",
    },
    {
        "name": "网络/DNS/镜像源失败",
        "category": "Network",
        "severity": "Low",
        "patterns": [r"Failed to resolve", r"NameResolutionError", r"Could not fetch URL"],
        "cause": "服务器 DNS、代理、镜像源或计算节点外网访问异常。",
        "suggestion": "检查 ping、pip config、conda channels；必要时换源或在登录节点下载依赖包。",
    },
]


class DiagnosisAgent(BaseAgent):
    name = "DiagnosisAgent-错误诊断智能体"

    def run(self, ctx: AgentContext) -> AgentContext:
        text = ctx.raw_text
        findings = []
        for rule in RULES:
            matched = self._match(text, rule["patterns"])
            if matched:
                findings.append({
                    "name": rule["name"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "cause": rule["cause"],
                    "suggestion": rule["suggestion"],
                    "matched_text": matched[0],
                    "confidence": matched[1],
                })
        severity_rank = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        findings.sort(key=lambda x: (severity_rank.get(x["severity"], 0), x["confidence"]), reverse=True)
        ctx.findings = findings
        if findings:
            ctx.trace(self.name, f"命中 {len(findings)} 类问题，最高优先级问题是：{findings[0]['name']}。")
        else:
            ctx.trace(self.name, "未命中内置规则库，建议提供更完整的 Traceback 或扩展规则。")
        return ctx

    def _match(self, text: str, patterns: List[str]) -> Optional[Tuple[str, float]]:
        hits = []
        for p in patterns:
            m = re.search(p, text, re.I | re.M)
            if m:
                s, e = max(0, m.start() - 160), min(len(text), m.end() + 260)
                hits.append(text[s:e].strip())
        if not hits:
            return None
        return hits[0], min(0.60 + 0.12 * len(hits), 0.98)
