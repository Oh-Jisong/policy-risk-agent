# Policy Risk Agent
**AI Agent for Privacy & Compliance Risk Assessment in Policy Documents**

**프로젝트 정리 글 (Velog)**  
[![Velog](https://img.shields.io/badge/Velog-Project%20Write--up-20C997?logo=velog&logoColor=white)](https://velog.io/@songing/Policy-Risk-Agent-Upstage-AI-Ambassador-%EC%A7%80%EC%9B%90-%EA%B3%BC%EC%A0%9C%EB%A1%9C-%EC%A7%84%ED%96%89%ED%95%9C-%EB%AC%B8%EC%84%9C-%EB%A6%AC%EC%8A%A4%ED%81%AC-%EC%A0%90%EA%B2%80-AI-Agent)

---

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-18_LTS-339933?logo=node.js&logoColor=white)

![Upstage](https://img.shields.io/badge/Upstage-AI%20Ambassador%20(Assignment)-5B2EFF)
![LLM](https://img.shields.io/badge/AI-LLM%20Agent-blueviolet)
![Solar](https://img.shields.io/badge/Upstage-Solar_LLM-6F4CFF)
![Document%20Parse](https://img.shields.io/badge/Upstage-Document_Parse-6F4CFF)
![Information%20Extract](https://img.shields.io/badge/Upstage-Information_Extract-6F4CFF)

---

## Table of Contents

- [프로젝트 개요](#프로젝트-개요)
- [문제 정의 (Problem)](#문제-정의-problem)
- [해결 방안 (Solution)](#해결-방안-solution)
- [핵심 기술 (Core Technologies)](#핵심-기술-core-technologies)
- [전체 파이프라인 (Architecture)](#전체-파이프라인-architecture)
- [Architecture Improvement: Analysis Session Isolation](#architecture-improvement-analysis-session-isolation)
- [Architecture Diagram Description](#architecture-diagram-description)
- [Frontend / Backend 구조](#frontend--backend-구조)
- [데모 기능 (Features)](#데모-기능-features)
- [실행 방법 (How to Run)](#실행-방법-how-to-run)
- [Node.js Version Requirement](#nodejs-version-requirement)
- [CORS 설정 및 주의사항](#cors-설정-및-주의사항)
- [기대 효과 (Expected Impact)](#기대-효과-expected-impact)
- [향후 개선 방향 (Future Work)](#향후-개선-방향-future-work)
- [참고](#참고)

---

## 프로젝트 개요

**Policy Risk Agent**는 개인정보처리방침, 이용약관, 공지문과 같은  
정책 문서(PDF)를 입력하면 **Upstage의 Solar, Document Parse, Information Extract API**를 활용해  
문서를 구조적으로 분석하고 **개인정보·컴플라이언스 관점의 리스크를 점검하는 AI Agent 프로토타입**입니다.

단순 요약이나 질의응답이 아니라  
> **문서 이해 → 구조화 → 판단 → 행동 제안**  
의 흐름을 갖춘 *Agent 형태의 서비스*를 목표로 합니다.

> 본 레포는 **Upstage AI Ambassador 지원 과제**로 진행한 프로젝트이며,  
> 실제 Ambassador 선발 여부와는 무관합니다.

---

## 문제 정의 (Problem)

대부분의 서비스 약관·개인정보처리방침은 다음과 같은 문제를 갖고 있습니다.

- 문서 분량이 길고 구조가 복잡해 **일반 사용자가 이해하기 어려움**
- 개인정보 수집·보관·제3자 제공 등 **핵심 리스크가 흩어져 있음**
- 책임 회피, 모호한 표현 등 **사용자에게 불리한 조항을 직접 식별하기 어려움**
- 기존 AI 서비스는 요약이나 QA에 집중되어 있어  
  **“이 문서가 위험한가?”라는 판단을 직접 제공하지 못함**

즉,  
**문서를 읽어주는 AI는 많지만,**  
**문서를 점검하고 판단해주는 AI Agent는 부족한 상황**입니다.

---

## 해결 방안 (Solution)

Policy Risk Agent는 다음과 같은 접근으로 문제를 해결합니다.

1. **Document Parse**로 PDF 문서를 정밀하게 파싱
2. HTML 기반 텍스트를 정제하여 분석 가능한 형태로 변환
3. **Information Extract**를 활용해  
   개인정보 처리 관련 핵심 항목을 **스키마 기반으로 구조화**
4. **Solar LLM**이 구조화된 정보와 원문 근거를 바탕으로  
   개인정보·컴플라이언스 리스크를 **판단 기준에 따라 평가**
5. 결과를 다음 형태로 제공
   - 리스크 요약
   - 체크리스트
   - JSON 리포트 (기계 판독용)
   - Markdown 리포트 (사람 판독용)

> 단순 요약이 아니라  
> **판단(Risk Assessment) + 근거(Evidence) + 행동 제안(Actionable Output)** 을 제공하는 것이 핵심입니다.

---

## 핵심 기술 (Core Technologies)

### Upstage Document Parse
- PDF 문서를 HTML 포함 구조화 JSON으로 변환
- 복잡한 정책 문서를 기계가 이해할 수 있는 형태로 전처리

### Text Refinement Pipeline
- HTML에서 의미 있는 태그(h1, h2, h3, p)만 추출
- LLM 분석에 적합한 텍스트로 정제

### Upstage Information Extract
- 개인정보 처리방침 핵심 항목을 스키마 기반으로 구조화
  - 수집 항목
  - 이용 목적
  - 보관 및 파기 기준
  - 제3자 제공/위탁 여부
  - 정보주체 권리

### Upstage Solar (solar-pro2)
- 구조화 데이터 + 원문 근거를 기반으로 리스크 판단
- 환각 방지를 위해 **근거 문구 인용 강제**
- 출력 JSON 형식 엄격 검증 로직 포함

### FastAPI + Next.js 기반
- PDF 업로드 → 분석 → 결과 시각화까지 end-to-end 구현

---

## 전체 파이프라인 (Architecture)
```
PDF Upload
↓
Document Parse (PDF → HTML/JSON)
↓
Text Refinement
↓
Information Extract (Structured JSON)
↓
Solar Risk Assessment
↓
Risk Report (JSON / Markdown)
↓
Web Dashboard Output
```


---

## Architecture Improvement: Analysis Session Isolation

본 프로젝트에서는 **분석 요청 단위의 결과 충돌과 재현성 문제**를 해결하기 위해  
`analysis_id` 기반의 **분석 세션 분리 구조**를 도입했습니다.

### 문제점 (초기 구조)

초기 파이프라인은 모든 분석 결과를 단일 디렉토리(`data/outputs/`)에 저장했습니다.  
이 구조는 다음과 같은 한계를 가졌습니다.

- 여러 PDF를 연속 분석할 경우 **이전 결과가 덮어써짐**
- 프론트엔드에서 JSON / MD 다운로드 시  
  **어떤 분석 결과인지 식별 불가능**
- 비동기 요청 또는 다중 사용자 환경에서  
  **결과 충돌 및 레이스 컨디션 발생 가능**

### 개선 방식

FastAPI의 `/api/analyze` 요청마다 **고유한 `analysis_id (UUID)`를 발급**하고  
해당 ID를 파이프라인 전체에 전달하여 **출력 디렉토리를 요청 단위로 분리**했습니다.

```
data/outputs/
├─ {analysis_id}/
│ ├─ dp_result.json
│ ├─ plain_text.txt
│ ├─ ie_result.json
│ ├─ risk_report.json
│ └─ report.md
```


이를 위해 다음과 같은 구조를 적용했습니다.

- Backend에서 요청 단위 `analysis_id` 생성
- `pipeline.py` 실행 시 `analysis_id`를 인자로 전달
- `OUTPUT_DIR`을 환경변수로 하위 파이프라인 스크립트에 전파
- 다운로드 API에서 `analysis_id` 기준으로 결과 조회

### 효과

- 분석 결과의 **완전한 요청 단위 격리**
- 프론트엔드에서 **정확한 결과(JSON / Markdown) 다운로드 보장**
- 분석 이력 추적 및 재현 가능
- 향후 **멀티 유저 / 비동기 Agent 서비스 확장에 유리한 구조**

> 이 구조는 단순 데모를 넘어  
> **실제 AI Agent 서비스 운영을 고려한 아키텍처 설계**를 반영합니다.

---

## Architecture Diagram Description

본 아키텍처는 **Frontend(UI)** 와 **Backend(AI Agent Pipeline)** 의 역할을 명확히 분리한 구조입니다.

- **Frontend (Next.js)**  
  - PDF 업로드
  - 분석 결과 시각화
  - JSON / Markdown 리포트 다운로드  
  → 사용자 인터페이스 및 상호작용에 집중

- **Backend (FastAPI)**  
  - PDF 수신 및 분석 요청 관리
  - 분석 요청마다 `analysis_id` 발급
  - Document Parse → Information Extract → Solar LLM으로 이어지는  
    단계적 AI Agent 파이프라인 실행
  - 분석 결과 파일 관리 및 API 제공  
  → 문서 처리 및 판단 로직 전담

Backend 내부에서는 LLM을 단발성 호출이 아닌  
**문서 이해 → 구조화 → 리스크 판단 → 행동 제안**의  
Agent 파이프라인 형태로 구성하여 실질적인 의사결정을 수행합니다.

---

## Frontend / Backend 구조

### 간단 버전
```text
┌───────────────────────────────┐
│          User / Browser        │
└───────────────┬───────────────┘
                │  Upload PDF
                ▼
┌───────────────────────────────┐
│     Next.js Frontend (3000)    │
│  - Upload / View / Download    │
└───────────────┬───────────────┘
                │  POST /api/analyze
                ▼
┌───────────────────────────────┐
│     FastAPI Backend (8000)     │
│  - issues analysis_id          │
│  - runs pipeline               │
└───────────────┬───────────────┘
                │  OUTPUT_DIR = data/outputs/{analysis_id}
                ▼
┌───────────────────────────────┐
│     Policy Risk Pipeline       │
│  1) Document Parse (PDF→HTML)  │
│  2) Text Refinement            │
│  3) Information Extract (JSON) │
│  4) Solar Risk Assessment      │
│  5) Report (JSON/MD)           │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│  data/outputs/{analysis_id}/   │
│  - dp_result.json              │
│  - plain_text.txt              │
│  - ie_result.json              │
│  - risk_report.json            │
│  - report.md                   │
└───────────────┬───────────────┘
                │  GET /api/download/{risk|md}?analysis_id=...
                ▼
┌───────────────────────────────┐
│     Next.js renders results     │
└───────────────────────────────┘
```

### 상세 버전
```
+----------------------------------------------------------------------------------+
|                                  Frontend (Next.js)                             |
|                              http://localhost:3000                               |
|                                                                                  |
|   [UI] Upload PDF  ───────────────►  POST http://127.0.0.1:8000/api/analyze      |
|   [UI] View Score/Findings  ◄──────  JSON { analysis_id, risk, has_md }          |
|   [UI] Download JSON/MD ───────────►  GET /api/download/risk?analysis_id=...     |
|                                     GET /api/download/md?analysis_id=...        |
+----------------------------------------------------------------------------------+
                                         │
                                         │ REST
                                         ▼
+----------------------------------------------------------------------------------+
|                                  Backend (FastAPI)                              |
|                              http://127.0.0.1:8000                               |
|                                                                                  |
|  1) Receive PDF (multipart/form-data)                                            |
|  2) Issue analysis_id (UUID)                                                     |
|  3) Run pipeline: python app/pipeline.py <pdf_path> <analysis_id>                |
|  4) Serve outputs by analysis_id                                                 |
+----------------------------------------------------------------------------------+
                                         │
                                         │ OUTPUT_DIR = data/outputs/{analysis_id}
                                         ▼
+----------------------------------------------------------------------------------+
|                             Policy Risk Agent Pipeline                           |
|                                                                                  |
|  [01] Upstage Document Parse        : PDF -> HTML(JSON)                          |
|  [02] Text Refinement               : HTML -> plain_text.txt                     |
|  [03] Upstage Information Extract   : PDF -> structured IE JSON                  |
|  [04] Upstage Solar Risk Assessment : (IE JSON + text) -> risk_report.json       |
|  [05] Report Generator              : risk_report.json -> report.md              |
|                                                                                  |
|  Outputs: data/outputs/{analysis_id}/                                            |
|   - dp_result.json / plain_text.txt / ie_result.json / risk_report.json / report.md |
+----------------------------------------------------------------------------------+

```

---

## 데모 기능 (Features)

- PDF 정책 문서 업로드
- Risk Score & Risk Level 시각화
- Top Risk Findings (5개 고정)
- Quick Checklist 제공
- JSON / Markdown 리포트 다운로드
- Health Check API 제공

---

## 실행 방법 (How to Run)

### 1) 환경 설정
```
git clone https://github.com/Oh-Jisong/policy-risk-agent.git
cd policy-risk-agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) 환경 변수 설정
```
cp .env.example .env

```

- `.env` 파일에 Upstage API key 입력:
```
UPSTAGE_API_KEY=your_upstage_api_key
```

### 3) 파이프라인 단독 실행
```
python app/pipeline.py data/samples/policy.pdf
```

### 4) 결과물
- data/outputs/{analysis_id}/dp_result.json
- data/outputs/{analysis_id}/plain_text.txt
- data/outputs/{analysis_id}/ie_result.json
- data/outputs/{analysis_id}/risk_report.json
- data/outputs/{analysis_id}/report.md

> 파이프라인은 실행 시 analysis_id가 존재하면
> 자동으로 data/outputs/{analysis_id} 아래에 결과를 저장합니다.

### 5) 웹 데모 실행

#### 5-1) Backend 실행 : FastAPI
- 위치
```
policy-risk-agent/
└─ demo/
   └─ backend/
```

- 실행
```
uvicorn demo.backend.main:app --reload --port 8000

```

- 확인
```
- Backend: http://127.0.0.1:8000
- Health Check: GET /api/health => http://127.0.0.1:8000/api/health
- PDF 분석: POST /api/analyze => http://127.0.0.1:8000/api/analyze

```

#### 5-2) Frontend 실행 : Next.js
- 위치
```
policy-risk-agent/
└─ demo/
   └─ frontend/

```

- 최초 1회 의존성 설치
```
cd demo/frontend
npm install
```

- 실행
```
npm run dev
```

- 접속
```
Frontend: http://localhost:3000
```

---

## Node.js Version Requirement

Frontend는 **Next.js(App Router 기반)** 를 사용합니다.
```
Node.js >= 18.17.0 (LTS)
```
> Node 16 이하에서는 Next.js 실행 중 오류가 발생할 수 있습니다.

---

## CORS 설정 및 주의사항

### 로컬 개발 환경
서로 다른 포트에서 실행되므로 Backend(FastAPI)에서 CORS 허용 필요
- Frontend: http://localhost:3000
- Backend: http://127.0.0.1:8000
 
- 예시
```
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 배포 시 주의점
- Frontend 배포 도메인이 바뀌면 allow_origins도 함께 업데이트해야 합니다.
- .env의 UPSTAGE_API_KEY는 절대 프론트로 노출되지 않도록 Backend에서만 관리해야 합니다.
- multi-user 운영을 고려한다면 data/outputs/{analysis_id} 폴더의 보관 정책(만료/정리)도 함께 설계하는 것이 좋습니다.

---

## 기대 효과 (Expected Impact)
- 일반 사용자도 정책 문서의 위험 요소를 빠르게 인지
- 서비스 운영자는 사전 컴플라이언스 점검 도구로 활용 가능
- 보안·법무·정책 검토 영역에서 AI Agent 활용 가능성 제시
- 단순 LLM 활용을 넘어 “판단하는 AI Agent” 의 실질적 예시 제공

---

## 향후 개선 방향 (Future Work)
- [ ] 다중 문서 동시 분석 지원
- [ ] 국가/산업별 개인정보 규정 기준 적용
- [ ]  Risk Score 산정 로직 고도화
- [ ]  사용자 피드백 기반 리스크 학습
- [ ]  실제 법률·보안 전문가 룰셋 연계
- [ ]  outputs 보관 정책(만료/정리) 및 사용자별 접근 제어

---

## 참고

본 프로젝트는 Upstage AI Ambassador 지원 과제로 제작된
AI Agent 서비스 프로토타입입니다.
