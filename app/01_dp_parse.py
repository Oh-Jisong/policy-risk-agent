import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("UPSTAGE_API_KEY")
assert API_KEY, "UPSTAGE_API_KEY not loaded (.env 확인)"

PDF_PATH = os.path.join("data", "samples", "policy.pdf")
assert os.path.exists(PDF_PATH), f"PDF not found: {PDF_PATH}"

# pipeline에서 넘겨준 OUTPUT_DIR이 있으면 그쪽에 저장, 없으면 기존 data/outputs
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join("data", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)
out_path = os.path.join(OUTPUT_DIR, "dp_result.json")

# Upstage Document Parse endpoint
url = "https://api.upstage.ai/v1/document-digitization"
headers = {"Authorization": f"Bearer {API_KEY}"}

files = {"document": open(PDF_PATH, "rb")}

data = {
    "model": "document-parse",
    "ocr": "auto",
}

resp = requests.post(url, headers=headers, files=files, data=data, timeout=90)

print("status:", resp.status_code)

try:
    result = resp.json()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("saved:", out_path)

    preview = json.dumps(result, ensure_ascii=False)[:800]
    print("preview:", preview)

except Exception:
    print(resp.text[:1000])