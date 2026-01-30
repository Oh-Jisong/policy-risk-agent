import os
import json
from bs4 import BeautifulSoup

# pipeline에서 넘겨준 OUTPUT_DIR 사용 (없으면 기존 data/outputs)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join("data", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 입력: dp_result.json (같은 OUTPUT_DIR 안에 있어야 함)
DP_PATH = os.path.join(OUTPUT_DIR, "dp_result.json")
assert os.path.exists(DP_PATH), "dp_result.json not found. 먼저 01_dp_parse.py 실행하세요."

with open(DP_PATH, "r", encoding="utf-8") as f:
    dp = json.load(f)

html = dp["content"]["html"]

# HTML → 텍스트
soup = BeautifulSoup(html, "html.parser")

texts = []
for tag in soup.find_all(["h1", "h2", "h3", "p"]):
    text = tag.get_text(strip=True)
    if text:
        texts.append(text)

plain_text = "\n".join(texts)

# 출력: plain_text.txt (같은 OUTPUT_DIR)
OUT_PATH = os.path.join(OUTPUT_DIR, "plain_text.txt")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(plain_text)

print("saved:", OUT_PATH)
print("\n--- preview ---")
print(plain_text[:800])