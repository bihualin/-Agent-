from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.agents.coordinator import MultiAgentCoordinator
from backend.api.schemas import DiagnoseRequest, DiagnoseResponse
from backend.database.db import get_report, insert_log, insert_report, insert_trace, list_reports
from backend.services.feishu_service import send_feishu_webhook

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")


@router.post("/diagnose", response_model=DiagnoseResponse)
def diagnose(req: DiagnoseRequest, request: Request):
    if not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="日志内容不能为空")
    ctx = MultiAgentCoordinator().run(req.log_name, req.raw_text)
    log_id = insert_log(req.log_name, req.raw_text)
    result = {
        "parsed": ctx.parsed,
        "findings": ctx.findings,
        "solutions": ctx.solutions,
        "report": ctx.report,
    }
    report_id = insert_report(log_id, ctx.report["summary"], ctx.report["severity"], result, ctx.report["markdown"])
    for i, t in enumerate(ctx.traces, 1):
        insert_trace(report_id, t["agent"], i, t["content"])
    base = str(request.base_url).rstrip("/")
    return DiagnoseResponse(
        report_id=report_id,
        log_id=log_id,
        summary=ctx.report["summary"],
        severity=ctx.report["severity"],
        feishu_page_url=f"{base}/feishu/report/{report_id}",
    )


@router.post("/diagnose_file", response_model=DiagnoseResponse)
async def diagnose_file(request: Request, file: UploadFile = File(...)):
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("gbk", errors="ignore")
    return diagnose(DiagnoseRequest(log_name=file.filename, raw_text=text), request)


@router.get("/reports")
def reports():
    return {"items": list_reports()}


@router.get("/reports/{report_id}")
def report_detail(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@router.get("/feishu/report/{report_id}", response_class=HTMLResponse)
def feishu_report(request: Request, report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return templates.TemplateResponse("feishu_report.html", {"request": request, "report": report})


@router.post("/feishu/send/{report_id}")
def feishu_send(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    result = send_feishu_webhook(f"科研训练日志诊断：{report['summary']}", report["markdown_report"])
    return result
