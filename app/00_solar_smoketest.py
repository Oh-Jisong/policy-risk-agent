import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1",
)

resp = client.chat.completions.create(
    model="solar-pro2",
    messages=[{"role": "user", "content": "Say 'Solar connected' in one short sentence."}],
    temperature=0,
    stream=False,
)

print(resp.choices[0].message.content)