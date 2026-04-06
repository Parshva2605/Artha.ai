import type { JobStatus, JobStatusResponse } from "../lib/types";
import { LANGUAGE_LABELS } from "../lib/types";

type ProgressTrackerProps = {
  jobStatus: JobStatusResponse;
};

const stages: Array<{ status: JobStatus; label: string }> = [
  { status: "scraping", label: "Scraping" },
  { status: "cleaning", label: "Cleaning" },
  { status: "labeling", label: "Labeling" },
  { status: "quality_check", label: "Quality Check" },
  { status: "exporting", label: "Exporting" },
  { status: "complete", label: "Complete" },
];

function getFailedStageIndex(currentStep: string): number {
  const normalized = currentStep.toLowerCase();
  if (normalized.includes("export")) return 4;
  if (normalized.includes("quality")) return 3;
  if (normalized.includes("label")) return 2;
  if (normalized.includes("clean")) return 1;
  if (normalized.includes("scrap")) return 0;
  return 0;
}

export default function ProgressTracker({ jobStatus }: ProgressTrackerProps) {
  const currentStageIndex = stages.findIndex((item) => item.status === jobStatus.status);
  const failedStageIndex = jobStatus.status === "failed" ? getFailedStageIndex(jobStatus.current_step) : -1;

  return (
    <div className="space-y-6">
      <div>
        {jobStatus.status === "queued" && (
          <p className="mb-2 text-sm text-slate-600">Waiting to start...</p>
        )}
        <div className="h-4 overflow-hidden rounded-full bg-slate-200">
          <div
            className="h-full bg-[#E8690A]"
            style={{ width: `${jobStatus.progress_percent}%` } as React.CSSProperties}
          />
        </div>
        <p className="mt-2 text-sm text-slate-700">{jobStatus.progress_percent}% - {jobStatus.current_step}</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {stages.map((stage, index) => {
          const stageDone = jobStatus.status === "complete" || index < currentStageIndex;
          const isCurrent = jobStatus.status !== "complete" && jobStatus.status !== "failed" && index === currentStageIndex;
          const isFailedStage = jobStatus.status === "failed" && index === failedStageIndex;
          return (
            <span
              key={stage.status}
              className={`rounded-full border px-3 py-1 text-xs ${
                isFailedStage
                  ? "border-red-300 bg-red-50 text-red-700"
                  : isCurrent
                  ? "border-[#E8690A] bg-[#E8690A] text-white"
                  : stageDone
                    ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                    : "border-slate-200 text-slate-500"
              } ${isCurrent ? "animate-pulse" : ""}`}
            >
              {stageDone ? "✓ " : ""}{stage.label}
            </span>
          );
        })}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-slate-600">
              <th className="px-2 py-2">Language</th>
              <th className="px-2 py-2">Step</th>
              <th className="px-2 py-2">Scraped</th>
              <th className="px-2 py-2">Cleaned</th>
              <th className="px-2 py-2">Labeled</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(jobStatus.per_language_status).map(([language, status]) => (
              <tr key={language} className="border-b border-slate-100">
                <td className="px-2 py-2 font-medium">{LANGUAGE_LABELS[language as keyof typeof LANGUAGE_LABELS] ?? language}</td>
                <td className="px-2 py-2">{status.step}</td>
                <td className="px-2 py-2">{status.rows_collected}</td>
                <td className="px-2 py-2">{status.rows_clean}</td>
                <td className="px-2 py-2">{status.rows_labeled}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
