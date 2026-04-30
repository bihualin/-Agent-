from __future__ import annotations

import requests
import streamlit as st

API_BASE = st.sidebar.text_input("后端 API 地址", value="http://127.0.0.1:8000")

st.set_page_config(page_title="科研训练日志诊断控制台", page_icon="🧠", layout="wide")
st.title("🧠 科研训练日志自动诊断 Agent 控制台")
st.caption("FastAPI + SQLite + Multi-Agent + 飞书风格报告页面")

mode = st.radio("输入方式", ["粘贴日志", "上传日志文件"], horizontal=True)
log_name = "manual_log.txt"
raw_text = ""

if mode == "粘贴日志":
    log_name = st.text_input("日志名称", value="manual_log.txt")
    raw_text = st.text_area("粘贴训练日志 / Traceback", height=320)
    if st.button("开始诊断", type="primary"):
        if not raw_text.strip():
            st.warning("请先输入日志内容")
        else:
            resp = requests.post(f"{API_BASE}/api/diagnose", json={"log_name": log_name, "raw_text": raw_text}, timeout=30)
            if resp.ok:
                data = resp.json()
                st.success(f"诊断完成：{data['summary']} ｜ 严重程度：{data['severity']}")
                st.link_button("打开飞书风格报告页面", data["feishu_page_url"])
                st.session_state["last_report_id"] = data["report_id"]
            else:
                st.error(resp.text)
else:
    file = st.file_uploader("上传 .log / .txt / .out", type=["log", "txt", "out"])
    if st.button("上传并诊断", type="primary") and file is not None:
        resp = requests.post(f"{API_BASE}/api/diagnose_file", files={"file": (file.name, file.getvalue())}, timeout=30)
        if resp.ok:
            data = resp.json()
            st.success(f"诊断完成：{data['summary']} ｜ 严重程度：{data['severity']}")
            st.link_button("打开飞书风格报告页面", data["feishu_page_url"])
            st.session_state["last_report_id"] = data["report_id"]
        else:
            st.error(resp.text)

st.divider()
st.subheader("历史诊断报告")
try:
    resp = requests.get(f"{API_BASE}/api/reports", timeout=10)
    if resp.ok:
        reports = resp.json()["items"]
        for r in reports:
            with st.expander(f"#{r['id']} {r['log_name']} | {r['summary']} | {r['severity']}"):
                st.write(r)
                st.link_button("查看飞书报告", f"{API_BASE}/feishu/report/{r['id']}")
                detail = requests.get(f"{API_BASE}/api/reports/{r['id']}", timeout=10).json()
                st.markdown(detail["markdown_report"])
    else:
        st.info("后端尚未启动或没有报告。")
except Exception as e:
    st.warning(f"无法连接后端：{e}")
