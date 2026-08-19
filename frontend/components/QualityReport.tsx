import type { QualityReport as QualityReportType } from "../lib/types";
import { LANGUAGE_LABELS } from "../lib/types";

type QualityReportProps = {
  report: QualityReportType;
};

function scoreColor(score: number): string {
  if (score >= 85) return "text-emerald-700";
  if (score >= 70) return "text-amber-600";
  return "text-red-600";
}

export default function QualityReport({ report }: QualityReportProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border p-5">
        <p className="text-sm text-slate-600">Quality Score</p>
        <p className={`text-4xl font-black ${scoreColor(report.overall_quality_score)}`}>{report.overall_quality_score.toFixed(1)}</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(report.per_language_quality).map(([language, score]) => (
          <div key={language} className="rounded-xl border p-4">
            <p className="text-sm text-slate-600">{LANGUAGE_LABELS[language as keyof typeof LANGUAGE_LABELS] ?? language}</p>
            <p className={`text-2xl font-bold ${scoreColor(score)}`}>{score.toFixed(1)}</p>
          </div>
        ))}
      </div>

      {report.shortfall_warnings.length > 0 && (
        <div className="space-y-2 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800">
          {report.shortfall_warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      )}

      {report.low_quality_warning && (
        <div className="rounded-xl border border-orange-300 bg-orange-50 p-4 text-sm text-orange-800">
          {report.low_quality_warning}
        </div>
      )}
    </div>
  );
}
