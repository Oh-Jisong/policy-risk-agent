import json
import shutil
import subprocess
import sys
import uuid
import os
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

print("BACKEND LOADED: demo/backend/main.py v9")

ROOT = Path(__file__).resolve().parents[2]  # policy-risk-agent 루트
OUTPUTS = ROOT / "data" / "outputs"
SAMPLES = ROOT / "data" / "samples"

app = FastAPI()

# CORS (프론트 Next.js: localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_risk_payload(risk):
    """
    risk_report.json이 {"raw_text": "...json string..."} 형태면 파싱해서 risk 객체로 정리
    """
    if isinstance(risk, dict) and "raw_text" in risk and isinstance(risk["raw_text"], str):
        try:
            return json.loads(risk["raw_text"])
        except Exception:
            return risk
    return risk


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    analysis_id = str(uuid.uuid4())

    # 1) 업로드 받은 PDF 저장 (samples)
    SAMPLES.mkdir(parents=True, exist_ok=True)
    pdf_path = SAMPLES / file.filename
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 2) pipeline 실행
    # 핵심: analysis_id에 해당하는 출력 폴더를 ENV로 전달
    out_dir = OUTPUTS / analysis_id
    out_dir.mkdir(parents=True, exist_ok=True)

    env = dict(**{k: v for k, v in (dict(Path.cwd().drive, ) if False else {}).items()})  # dummy (keep lint calm)
    env = dict(**(os.environ if "os" in globals() else __import__("os").environ))
    env["OUTPUT_DIR"] = str(out_dir)

    cmd = [sys.executable, str(ROOT / "app" / "pipeline.py"), str(pdf_path), analysis_id]
    try:
        subprocess.check_call(cmd, cwd=str(ROOT), env=env)
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            {"ok": False, "analysis_id": analysis_id, "error": f"pipeline failed: {e}"},
            status_code=500,
        )

    # 3) 결과 파일 읽기 (analysis_id 폴더 기준)
    risk_json = out_dir / "risk_report.json"
    md_path = out_dir / "report.md"

    if not risk_json.exists():
        return JSONResponse(
            {"ok": False, "analysis_id": analysis_id, "error": f"risk_report.json not found: {risk_json}"},
            status_code=500,
        )

    risk = _normalize_risk_payload(_load_json(risk_json))

    # 가장 안전한 응답: flatten 하지 말고 risk만 내려준다
    return JSONResponse(
        content={
            "ok": True,
            "analysis_id": analysis_id,
            "has_md": md_path.exists(),
            "risk": risk,
        }
    )


@app.get("/api/download/risk")
def download_risk(analysis_id: str = Query(..., description="analysis_id returned from /api/analyze")):
    path = OUTPUTS / analysis_id / "risk_report.json"

    if not path.exists():
        return JSONResponse(
            {"ok": False, "error": f"risk_report.json not found for analysis_id={analysis_id}"},
            status_code=404,
        )

    data = _load_json(path)
    risk = _normalize_risk_payload(data)

    # 프론트가 쓰기 좋은 형태로: risk 객체만 내려주기
    return JSONResponse(content=risk)


@app.get("/api/download/md")
def download_md(analysis_id: str = Query(..., description="analysis_id returned from /api/analyze")):
    path = OUTPUTS / analysis_id / "report.md"

    if not path.exists():
        return JSONResponse(
            {"ok": False, "error": f"report.md not found for analysis_id={analysis_id}"},
            status_code=404,
        )

    return FileResponse(
        path,
        filename=f"policy-risk-report-{analysis_id}.md",
        media_type="text/markdown",
    )


@app.get("/api/health")
def health():
    return {"ok": True, "from": "demo/backend/main.py v9"}