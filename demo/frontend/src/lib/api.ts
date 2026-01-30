import type { RiskReport } from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

/**
 * PDF 분석 요청
 * - risk: 화면에 보여줄 리스크 리포트
 * - has_md: MD 파일 존재 여부
 * - analysis_id: 이번 분석 결과를 식별하는 ID (다운로드용)
 */
export async function analyzePdf(
  file: File
): Promise<{
  risk: RiskReport;
  has_md: boolean;
  analysis_id: string;
}> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Analyze failed: ${res.status} ${text}`);
  }

  const data = await res.json();

  if (!data?.ok) {
    throw new Error("Invalid response: ok=false");
  }

  if (!data?.risk) {
    throw new Error("Invalid response: missing risk");
  }

  if (!data?.analysis_id) {
    throw new Error("Invalid response: missing analysis_id");
  }

  return {
    risk: data.risk as RiskReport,
    has_md: !!data.has_md,
    analysis_id: data.analysis_id as string,
  };
}

/**
 * Risk JSON 다운로드
 * (analysis_id 기준)
 */
export function downloadRiskJson(analysisId: string) {
  if (!analysisId) {
    console.warn("downloadRiskJson called without analysisId");
    return;
  }

  window.open(
    `${API_BASE}/api/download/risk?analysis_id=${analysisId}`,
    "_blank"
  );
}

/**
 * Markdown 리포트 다운로드
 * (analysis_id 기준)
 */
export function downloadMd(analysisId: string) {
  if (!analysisId) {
    console.warn("downloadMd called without analysisId");
    return;
  }

  window.open(
    `${API_BASE}/api/download/md?analysis_id=${analysisId}`,
    "_blank"
  );
}