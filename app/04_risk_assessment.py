import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("UPSTAGE_API_KEY")
assert API_KEY, "UPSTAGE_API_KEY not loaded (.env 확인)"

# pipeline에서 넘겨준 OUTPUT_DIR 사용 (없으면 기존 data/outputs)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join("data", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

IE_PATH = os.path.join(OUTPUT_DIR, "ie_result.json")
TXT_PATH = os.path.join(OUTPUT_DIR, "plain_text.txt")

assert os.path.exists(IE_PATH), f"ie_result.json not found: {IE_PATH}"
assert os.path.exists(TXT_PATH), f"plain_text.txt not found: {TXT_PATH}"

with open(IE_PATH, "r", encoding="utf-8") as f:
    ie = json.load(f)

with open(TXT_PATH, "r", encoding="utf-8") as f:
    plain_text = f.read()

# 원문이 길면 Solar 입력 길이 때문에 컷
plain_text = plain_text[:16000]

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.upstage.ai/v1",
)

system = """You are a 'Policy Risk Agent' specialized in privacy/personal-data policy review.
Your job is to assess risk and provide actionable recommendations.
You must:
- Use the extracted JSON as primary evidence
- Quote supporting snippets from the provided policy text (Korean) for each finding when possible
- Be conservative and avoid hallucinating missing details
- When explaining why each issue matters, include both legal risk and service/operational risk.
- Write all fields in Korean.

HARD RULES:
- Output must include exactly 5 items in top_findings (not 3, not 4).
  - If you find fewer than 5 major issues, fill remaining items with lower-severity "improvement opportunities" (e.g., clarity, transparency, user rights UX),
    but they must still be grounded in the provided policy_text_excerpt or extracted_structured_data.
- evidence_quotes must contain ONLY human-readable quotes from the provided policy text excerpt (Korean).
  - Do NOT include internal field names or structured signals like "retention_period 필드가 비어 있음", "null", "missing field", or any schema key names.

Return STRICT JSON only (no markdown, no commentary)."""

user = {
    "task": "Assess privacy policy risk and produce an actionable report.",
    "inputs": {
        "extracted_structured_data": ie,
        "policy_text_excerpt": plain_text
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "risk_score": {"type": "integer", "description": "0~100 (higher = riskier)"},
            "risk_level": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
            "top_findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "why_it_matters": {"type": "string"},
                        "evidence_quotes": {"type": "array", "items": {"type": "string"}},
                        "recommendations": {"type": "array", "items": {"type": "string"}},
                        "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}
                    },
                    "required": ["title", "why_it_matters", "recommendations", "severity"]
                }
            },
            "quick_checklist": {"type": "array", "items": {"type": "string"}},
            "assumptions_and_limits": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["risk_score", "risk_level", "top_findings", "quick_checklist", "assumptions_and_limits"]
    }
}

resp = client.chat.completions.create(
    model="solar-pro2",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
    ],
)

raw = resp.choices[0].message.content


def _extract_json_object(text: str) -> str | None:
    """
    LLM 출력이 깨지는 경우가 있어 가장 바깥쪽 { ... } 블록만 뽑아서 파싱 재시도한다.
    """
    if not isinstance(text, str):
        return None

    t = text.strip()
    t = t.replace("```json", "").replace("```", "").strip()
    t = re.sub(r"^\s*json\s*", "", t, flags=re.IGNORECASE).strip()

    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    return t[start:end + 1]


# 저장: OUTPUT_DIR/risk_report.json
OUT_PATH = os.path.join(OUTPUT_DIR, "risk_report.json")

try:
    parsed = json.loads(raw)
except Exception:
    candidate = _extract_json_object(raw)
    if candidate:
        try:
            parsed = json.loads(candidate)
        except Exception:
            parsed = {
                "raw_text": raw,
                "note": "Model output was not valid JSON. See raw_text."
            }
    else:
        parsed = {
            "raw_text": raw,
            "note": "Model output was not valid JSON. See raw_text."
        }

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print("saved:", OUT_PATH)
print("\n--- preview ---")
print(json.dumps(parsed, ensure_ascii=False, indent=2)[:1000])