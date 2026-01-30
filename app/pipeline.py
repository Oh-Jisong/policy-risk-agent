import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("UPSTAGE_API_KEY")
assert API_KEY, "UPSTAGE_API_KEY not loaded"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SAMPLES = DATA_DIR / "samples"
BASE_OUTPUTS = DATA_DIR / "outputs"
SAMPLES.mkdir(parents=True, exist_ok=True)
BASE_OUTPUTS.mkdir(parents=True, exist_ok=True)


def _run(script_name: str, env: dict) -> None:
    subprocess.check_call(
        [sys.executable, str(ROOT / "app" / script_name)],
        cwd=str(ROOT),
        env=env,
    )


def run_dp(pdf_path: Path, env: dict) -> Path:
    # 기존 방식 유지: samples/policy.pdf로 복사해서 01이 보도록 함
    target = SAMPLES / "policy.pdf"
    if pdf_path.resolve() != target.resolve():
        target.write_bytes(pdf_path.read_bytes())

    _run("01_dp_parse.py", env)
    return Path(env["OUTPUT_DIR"]) / "dp_result.json"


def run_text(env: dict) -> Path:
    _run("02_extract_plain_text.py", env)
    return Path(env["OUTPUT_DIR"]) / "plain_text.txt"


def run_ie(pdf_path: Path, env: dict) -> Path:
    target = SAMPLES / "policy.pdf"
    if pdf_path.resolve() != target.resolve():
        target.write_bytes(pdf_path.read_bytes())

    _run("03_information_extract_pdf_ie.py", env)
    return Path(env["OUTPUT_DIR"]) / "ie_result.json"


def run_risk(env: dict) -> Path:
    _run("04_risk_assessment.py", env)
    return Path(env["OUTPUT_DIR"]) / "risk_report.json"


def run_report_md(env: dict) -> Path:
    # report.md 생성(backend가 MD 버튼에서 다운로드 하는 파일)
    _run("05_make_report_md.py", env)
    return Path(env["OUTPUT_DIR"]) / "report.md"


def main(pdf: str, analysis_id: str | None = None):
    pdf_path = Path(pdf)
    assert pdf_path.exists(), f"File not found: {pdf_path}"

    # 분석 요청 단위로 outputs/{analysis_id} 폴더 분리
    if analysis_id:
        output_dir = BASE_OUTPUTS / analysis_id
    else:
        # analysis_id가 없으면 기존처럼 data/outputs에 저장 (호환)
        output_dir = BASE_OUTPUTS

    output_dir.mkdir(parents=True, exist_ok=True)

    # 하위 스크립트들에게 OUTPUT_DIR을 환경변수로 전달
    env = os.environ.copy()
    env["OUTPUT_DIR"] = str(output_dir)

    print(f"[pipeline] OUTPUT_DIR = {output_dir}")

    print("1) DP...")
    run_dp(pdf_path, env)

    print("2) Text refinement...")
    run_text(env)

    print("3) Universal IE...")
    run_ie(pdf_path, env)

    print("4) Solar risk assessment...")
    run_risk(env)

    print("5) Make report.md...")
    out = run_report_md(env)

    print("\nDONE:", out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app/pipeline.py <pdf_path> [analysis_id]")
        raise SystemExit(1)

    pdf = sys.argv[1]
    analysis_id = sys.argv[2] if len(sys.argv) >= 3 else None
    main(pdf, analysis_id)