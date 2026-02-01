"use client";

import { useMemo, useRef, useState } from "react";
import type { RiskReport, Finding } from "@/types";
import { analyzePdf, downloadMd, downloadRiskJson } from "@/lib/api";

function levelBadge(level: RiskReport["risk_level"]) {
  const map: Record<string, string> = {
    LOW: "bg-green-100 text-green-700 border-green-200",
    MEDIUM: "bg-yellow-100 text-yellow-800 border-yellow-200",
    HIGH: "bg-red-100 text-red-700 border-red-200",
  };
  return map[level] ?? "bg-gray-100 text-gray-700 border-gray-200";
}

function severityPill(sev: Finding["severity"]) {
  const map: Record<string, string> = {
    LOW: "bg-green-50 text-green-700 border-green-200",
    MEDIUM: "bg-yellow-50 text-yellow-800 border-yellow-200",
    HIGH: "bg-red-50 text-red-700 border-red-200",
    CRITICAL: "bg-red-600 text-white border-red-600",
  };
  return map[sev] ?? "bg-gray-50 text-gray-700 border-gray-200";
}

function levelMessage(level: RiskReport["risk_level"]) {
  const map: Record<string, string> = {
    LOW: "현재 기준에서는 큰 위험 신호가 적습니다.",
    MEDIUM: "개선 권장: 누락/모호 조항을 우선 정리하세요.",
    HIGH: "즉시 개선 필요: 핵심 조항 누락 가능성이 높습니다.",
  };
  return map[level] ?? "리스크 수준을 확인하세요.";
}

function filterEvidenceQuotes(quotes: string[] = []) {
  const badPatterns: RegExp[] = [
    /필드가\s*(비어|없|누락|null)/i,
    /\bnull\b/i,
    /\bmissing\b/i,
    /\bfield\b/i,

    // 내부 키/스키마 느낌
    /retention_period/i,
    /third_party/i,
    /data_subject/i,
    /video_/i,

    // snake_case 키가 들어간 문장
    /\b[a-z]+_[a-z_]+\b/i,
  ];

  return quotes
    .map((q) => (q ?? "").trim())
    .filter((q) => q.length > 0)
    .filter((q) => q.length >= 12)
    .filter((q) => !badPatterns.some((re) => re.test(q)));
}

function isLegalCitation(text: string) {
  return /제\s*\d+\s*조|제\s*\d+\s*항|개인정보\s*보호법|시행령|시행규칙|고시/i.test(text);
}

export default function Page() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RiskReport | null>(null);
  const [hasMd, setHasMd] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ✅ Step 1: analysis_id 저장
  const [analysisId, setAnalysisId] = useState<string | null>(null);

  const top5 = useMemo(() => {
    if (!result?.top_findings) return [];
    return result.top_findings.slice(0, 5);
  }, [result]);

  async function onAnalyze() {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      // ✅ analyzePdf 응답 전체에서 analysis_id를 꺼내서 state로 저장
      const res = await analyzePdf(file);
      // res: { ok, analysis_id, has_md, risk, ...flatten }
      setAnalysisId(res.analysis_id ?? null);

      // 기존 UI는 risk 객체를 사용
      setResult(res.risk ?? null);
      setHasMd(Boolean(res.has_md));
    } catch (e: any) {
      setError(e?.message ?? "Unknown error");
      setResult(null);
      setHasMd(false);
      setAnalysisId(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="mx-auto max-w-5xl px-6 py-12">
        <header className="mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight">PolicyRisk Agent</h1>
          <p className="mt-3 text-neutral-600">
            PDF를 업로드하면 Agent가 개인정보/약관 리스크를 점검하고 근거 기반으로 결과를 제공합니다.
          </p>
        </header>

        {/* Upload Card */}
        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex-1">
              <label className="block text-sm font-medium text-neutral-700">PDF 업로드</label>

              <div className="mt-2 flex items-center gap-3">
                <input
                  ref={fileInputRef}
                  className="hidden"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />

                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="rounded-xl border bg-white px-4 py-3 text-sm font-medium hover:bg-neutral-50"
                >
                  파일 선택
                </button>

                <div className="flex-1 rounded-xl border bg-white px-4 py-3 text-sm text-neutral-700">
                  {file ? file.name : "선택된 파일 없음"}
                </div>
              </div>

              <p className="mt-2 text-xs text-neutral-500">
                개인정보처리방침/이용약관/공지문 PDF를 넣어보세요.
              </p>

              {/* ✅ 디버그/확인용: analysis_id 표시 (원하면 나중에 지워도 됨) */}
              {analysisId && (
                <p className="mt-2 text-xs text-neutral-400">
                  analysis_id: <span className="font-mono">{analysisId}</span>
                </p>
              )}
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <button
                onClick={onAnalyze}
                disabled={!file || loading}
                className="rounded-xl bg-neutral-900 px-5 py-3 text-white disabled:opacity-40"
              >
                {loading ? "Analyzing..." : "Analyze"}
              </button>

              {/* ✅ analysisId 없으면 다운로드 막기 */}
              <button
                onClick={() => analysisId && downloadRiskJson(analysisId)}
                disabled={!analysisId}
                className="rounded-xl border px-5 py-3 disabled:opacity-40"
              >
                JSON
              </button>

              <button
                onClick={() => analysisId && downloadMd(analysisId)}
                disabled={!analysisId || !hasMd}
                className="rounded-xl border px-5 py-3 disabled:opacity-40"
              >
                MD
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}
        </section>

        {/* Summary */}
        {result && (
          <>
            <section className="mt-8 grid gap-4 md:grid-cols-3">
              {/* Risk Score */}
              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-sm text-neutral-500">Risk Score</div>
                <div className="mt-2 text-4xl font-bold">{result.risk_score}</div>
                <div className="mt-3 text-xs text-neutral-500">0~100 (높을수록 위험)</div>

                <div
                  className={`mt-4 rounded-xl border p-3 text-sm font-medium ${
                    result.risk_level === "HIGH"
                      ? "border-red-200 bg-red-50 text-red-800"
                      : result.risk_level === "MEDIUM"
                      ? "border-yellow-200 bg-yellow-50 text-yellow-900"
                      : "border-green-200 bg-green-50 text-green-800"
                  }`}
                >
                  {levelMessage(result.risk_level)}
                </div>
              </div>

              {/* Risk Level */}
              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-sm text-neutral-500">Risk Level</div>
                <div className="mt-3 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold">
                  <span className={`rounded-full border px-3 py-1 ${levelBadge(result.risk_level)}`}>
                    {result.risk_level}
                  </span>
                </div>
                <div className="mt-3 text-xs text-neutral-500">
                  Agent가 주요 조항 누락/모호성/민감정보 처리 등을 종합 평가
                </div>
              </div>

              {/* Findings */}
              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-sm text-neutral-500">Findings</div>
                <div className="mt-2 text-4xl font-bold">{result.top_findings?.length ?? 0}</div>
                <div className="mt-3 text-xs text-neutral-500">우선순위 기반 이슈 목록</div>
              </div>
            </section>

            {/* Findings list */}
            <section className="mt-8 rounded-2xl border bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-bold">Top Findings</h2>
                <span className="text-sm text-neutral-500">클릭해서 근거/조치 확인</span>
              </div>

              <div className="space-y-3">
                {top5.map((f, idx) => {
                  const urgent = f.severity === "HIGH" || f.severity === "CRITICAL";
                  const isCritical = f.severity === "CRITICAL";

                  return (
                    <details
                      key={idx}
                      className={`group rounded-xl border p-4 ${
                        urgent
                          ? isCritical
                            ? "border-red-300 bg-red-50"
                            : "border-red-200 bg-red-50/30"
                          : "bg-white"
                      }`}
                    >
                      <div className="relative">
                        {urgent && <div className="absolute left-0 top-0 h-full w-1 rounded-full bg-red-500" />}

                        <summary className="flex cursor-pointer list-none items-center justify-between gap-3 pl-3">
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-semibold text-neutral-500">#{idx + 1}</span>
                            <span className={`font-semibold ${urgent ? "text-neutral-900" : ""}`}>
                              {f.title}
                            </span>
                            <span className={`rounded-full border px-2 py-1 text-xs ${severityPill(f.severity)}`}>
                              {f.severity}
                            </span>
                          </div>
                          <span className="text-neutral-400 group-open:rotate-180">▾</span>
                        </summary>

                        <div className="mt-4 grid gap-4 md:grid-cols-2 pl-3">
                          <div>
                            <div className="text-sm font-semibold text-neutral-700">왜 중요한가</div>
                            <p className="mt-2 text-sm text-neutral-700 leading-relaxed">{f.why_it_matters}</p>
                          </div>

                          <div>
                            <div className="text-sm font-semibold text-neutral-700">권고 조치</div>
                            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-neutral-700">
                              {f.recommendations?.map((r, i) => (
                                <li key={i}>{r}</li>
                              ))}
                            </ul>
                          </div>

                          <div className="md:col-span-2">
                            <div className="text-sm font-semibold text-neutral-700">근거 문구</div>

                            {(() => {
                              const filtered = filterEvidenceQuotes(f.evidence_quotes ?? []);

                              if (filtered.length === 0) {
                                return (
                                  <div className="mt-2 rounded-lg border bg-neutral-50 p-3 text-sm text-neutral-600">
                                    근거 문구를 충분히 추출하지 못했습니다. (원문/JSON에서 확인 가능)
                                  </div>
                                );
                              }

                              return (
                                <details className="mt-2 rounded-xl border bg-white p-3">
                                  <summary className="cursor-pointer text-sm font-medium text-neutral-800">
                                    근거 문구 보기 ({filtered.length}개)
                                    <span className="ml-2 text-neutral-400">▾</span>
                                  </summary>

                                  <div className="mt-3 space-y-2">
                                    {filtered.map((q, i) => {
                                      const legal = isLegalCitation(q);
                                      return (
                                        <div
                                          key={i}
                                          className={`rounded-lg p-3 text-sm leading-relaxed ${
                                            legal
                                              ? "border border-indigo-200 bg-indigo-50 text-indigo-900"
                                              : "bg-neutral-50 text-neutral-700"
                                          }`}
                                        >
                                          “{q}”
                                        </div>
                                      );
                                    })}
                                  </div>
                                </details>
                              );
                            })()}
                          </div>
                        </div>
                      </div>
                    </details>
                  );
                })}
              </div>
            </section>

            {/* Quick Checklist */}
            <section className="mt-6 rounded-2xl border bg-white p-6 shadow-sm">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-bold">Quick Checklist</h2>
                <p className="checklist-note"> ※ 아래 항목은 정책 문서를 검토·개선하는 담당자를 위한 점검 기준입니다. </p>
                <span className="text-sm text-neutral-500">바로 점검할 항목</span>
              </div>

              {result.quick_checklist && result.quick_checklist.length > 0 ? (
                <ul className="space-y-2">
                  {result.quick_checklist.map((item, i) => (
                    <li key={i} className="flex items-start gap-3 rounded-xl border bg-neutral-50 p-3">
                      <input type="checkbox" className="mt-1 h-4 w-4" />
                      <span className="text-sm text-neutral-800">{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="rounded-xl border bg-neutral-50 p-3 text-sm text-neutral-600">
                  체크리스트 항목이 없습니다.
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
