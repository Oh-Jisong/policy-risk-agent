import os
import json

# pipeline에서 넘겨준 OUTPUT_DIR 사용 (없으면 기존 data/outputs)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join("data", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

RISK_PATH = os.path.join(OUTPUT_DIR, "risk_report.json")
OUT_PATH = os.path.join(OUTPUT_DIR, "report.md")

with open(RISK_PATH, "r", encoding="utf-8") as f:
    risk = json.load(f)

# risk가 {"raw_text": "...json string..."} 형태면 파싱해서 사용
if isinstance(risk, dict) and "raw_text" in risk and isinstance(risk["raw_text"], str):
    try:
        parsed = json.loads(risk["raw_text"])
        risk = parsed
    except Exception:
        pass

lines = []
lines.append("# Policy Risk Report\n")
lines.append("> 본 리포트는 정책 문서를 기반으로 개인정보 처리 리스크를 구조적으로 식별하고, 법적·운영상 개선 포인트를 제안합니다.\n")
lines.append(f"- Risk Score: **{risk.get('risk_score', 'N/A')}**")
lines.append(f"- Risk Level: **{risk.get('risk_level', 'N/A')}**\n")

lines.append("## Top Findings\n")
for i, fnd in enumerate(risk.get("top_findings", []), 1):
    lines.append(f"### {i}. {fnd.get('title', '')} ({fnd.get('severity', '')})\n")
    lines.append(f"**Why it matters**: {fnd.get('why_it_matters', '')}\n")

    if fnd.get("evidence_quotes"):
        lines.append("**Evidence quotes**:")
        for q in fnd["evidence_quotes"]:
            lines.append(f"- {q}")
        lines.append("")

    lines.append("**Recommendations**:")
    for r in fnd.get("recommendations", []):
        lines.append(f"- {r}")
    lines.append("")

lines.append("## Quick Checklist\n")
for c in risk.get("quick_checklist", []):
    lines.append(f"- {c}")
lines.append("")

lines.append("## Assumptions & Limits\n")
for a in risk.get("assumptions_and_limits", []):
    lines.append(f"- {a}")
lines.append("")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("saved:", OUT_PATH)