import os
import json
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("UPSTAGE_API_KEY")
assert API_KEY, "UPSTAGE_API_KEY not loaded (.env 확인)"

PDF_PATH = os.path.join("data", "samples", "policy.pdf")
assert os.path.exists(PDF_PATH), f"policy.pdf not found: {PDF_PATH}"

# pipeline에서 넘겨준 OUTPUT_DIR 사용 (없으면 기존 data/outputs)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join("data", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUTPUT_DIR, "ie_result.json")


def encode_file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


b64_data = encode_file_to_base64(PDF_PATH)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.upstage.ai/v1/information-extraction",
)

schema = {
    "type": "object",
    "properties": {
        "collected_personal_data": {
            "type": "array",
            "items": {"type": "string"},
            "description": "수집하는 개인정보 항목"
        },
        "collection_purpose": {
            "type": "array",
            "items": {"type": "string"},
            "description": "수집 목적"
        },
        "retention_period": {
            "type": "string",
            "description": "보관/이용 기간"
        },
        "third_party_sharing_or_outsourcing": {
            "type": "array",
            "items": {"type": "string"},
            "description": "제3자 제공 또는 처리위탁"
        },
        "user_rights": {
            "type": "array",
            "items": {"type": "string"},
            "description": "정보주체 권리(열람/정정/삭제 등)"
        }
    }
}

resp = client.chat.completions.create(
    model="information-extract",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:application/octet-stream;base64,{b64_data}"}
                }
            ],
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "privacy_policy_schema",
            "schema": schema
        }
    }
)

# 보통 message.content에 JSON 문자열
raw = resp.choices[0].message.content

try:
    parsed = json.loads(raw)
except Exception:
    parsed = {"raw": raw}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print("saved:", OUT_PATH)
print(json.dumps(parsed, ensure_ascii=False, indent=2)[:800])