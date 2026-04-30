# 科研训练日志自动诊断 Agent 系统

这是一个完整的课程/科研训练项目示例，包含：

- FastAPI 后端 API
- Multi-Agent 协同诊断流程
- SQLite 数据库存储
- Streamlit 前端控制台
- 飞书风格报告页面
- 可选飞书群机器人 Webhook 推送
- 示例训练日志

## 1. 项目结构

```text
research_log_agent/
├── backend/
│   ├── main.py                     # FastAPI 入口
│   ├── api/                        # API 路由与数据结构
│   ├── agents/                     # 多 Agent 协同模块
│   │   ├── coordinator.py          # 调度智能体
│   │   ├── parser_agent.py         # 日志解析智能体
│   │   ├── diagnosis_agent.py      # 错误诊断智能体
│   │   ├── solution_agent.py       # 解决方案智能体
│   │   └── report_agent.py         # 报告生成智能体
│   ├── database/                   # SQLite 操作
│   ├── services/                   # 飞书服务
│   └── templates/                  # 飞书风格 HTML 页面
├── frontend/
│   └── streamlit_app.py            # 前端控制台
├── sample_data/
│   └── sample_error.log            # 示例训练日志
├── scripts/
│   ├── run_backend.sh
│   └── run_frontend.sh
├── requirements.txt
└── README.md
```

## 2. 安装环境

建议 Python 3.10 或 3.11。

```bash
cd research_log_agent
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. 启动后端 API

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

## 4. 启动前端控制台

新开一个终端：

```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

访问：

```text
http://127.0.0.1:8501
```

## 5. 使用流程

1. 打开 Streamlit 控制台。
2. 粘贴训练日志，或上传 `sample_data/sample_error.log`。
3. 点击“开始诊断”。
4. 系统调用后端 Multi-Agent 流程：
   - Coordinator 调度智能体
   - ParserAgent 日志解析
   - DiagnosisAgent 错误诊断
   - SolutionAgent 解决方案生成
   - ReportAgent 报告生成
5. 诊断结果保存到 SQLite。
6. 点击“打开飞书风格报告页面”。

## 6. API 示例

```bash
curl -X POST http://127.0.0.1:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "log_name":"test.log",
    "raw_text":"RuntimeError: CUDA out of memory"
  }'
```

## 7. SQLite 数据库

默认数据库位置：

```text
data/research_log_agent.db
```

包含三张表：

- `logs`：原始日志
- `diagnosis_reports`：诊断报告
- `agent_traces`：多 Agent 推理轨迹

## 8. 飞书报告页面

每次诊断完成后，系统会生成类似下面的页面：

```text
http://127.0.0.1:8000/feishu/report/{report_id}
```

这是一个“飞书风格”的本地报告页面，适合课堂展示。

## 9. 可选：飞书群机器人推送

如果你有飞书机器人 Webhook，可以设置环境变量：

```bash
export FEISHU_WEBHOOK_URL="你的飞书机器人Webhook"
```

然后调用：

```bash
curl -X POST http://127.0.0.1:8000/api/feishu/send/1
```

## 10. 后续可扩展方向

- 接入 OpenAI / Qwen / DeepSeek API，让 DiagnosisAgent 从规则诊断升级为 LLM 诊断。
- 增加 Slurm 日志诊断规则。
- 增加 PyTorch Distributed/NCCL 错误规则。
- 增加训练曲线可视化。
- 增加用户登录与项目管理。
- 增加 RAG 知识库，把历史错误案例作为诊断依据。
