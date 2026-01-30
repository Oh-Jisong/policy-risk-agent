export type Finding = {
  title: string;
  why_it_matters: string;
  evidence_quotes: string[];
  recommendations: string[];
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  CRITICAL: "bg-red-600 text-white border-red-600",
};

export type RiskReport = {
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  top_findings: Finding[];
  quick_checklist?: string[];
  assumptions_and_limits?: string[];
};