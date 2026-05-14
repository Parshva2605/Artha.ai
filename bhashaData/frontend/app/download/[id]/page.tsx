"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { ApiError, getDownloadUrl } from "../../../lib/api";
import type { ExportFormat, QualityReport as QualityReportType } from "../../../lib/types";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import DownloadCard from "../../../components/DownloadCard";
import { LANGUAGE_LABELS } from "../../../lib/types";

const defaultExportFormats: ExportFormat[] = ["csv"];
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type DownloadReport = Partial<QualityReportType> & {
  source?: string;
  is_uploaded_job?: boolean;
  total_rows?: number;
  labeled_rows?: number;
  skipped_rows?: number;
  label_type?: string;
  custom_labels?: string[] | null;
};

function totalDistribution(labelDistribution: Record<string, number> | undefined): number {
  if (!labelDistribution) {
    return 0;
  }
  return Object.values(labelDistribution).reduce((sum, value) => sum + value, 0);
}

async function getRawQualityReport(jobId: string): Promise<DownloadReport> {
  const response = await fetch(`${API_BASE}/api/quality-report/${jobId}`);
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string; message?: string };
      message = payload.detail || payload.message || message;
    } catch {
    }
    throw new ApiError(response.status, message);
  }
  return (await response.json()) as DownloadReport;
}

export default function DownloadPage() {
  const params = useParams<{ id: string }>();
  const jobId = params.id;

  const reportQuery = useQuery({
    queryKey: ["quality-report", jobId],
    queryFn: () => getRawQualityReport(jobId),
    enabled: Boolean(jobId),
    retry: (failureCount, error) => error instanceof ApiError && error.status === 404 && failureCount < 10,
    retryDelay: 2000,
  });

  if (reportQuery.isLoading) {
    return <main className="mx-auto max-w-6xl px-4 py-12">Loading quality report...</main>;
  }

  if (reportQuery.isError || !reportQuery.data) {
    const isNotReady = reportQuery.error instanceof ApiError && reportQuery.error.status === 404;

    return (
      <main className="mx-auto max-w-6xl px-4 py-12">
        <Card className="border-red-200 p-6">
          <p className="text-lg font-semibold text-red-700">Unable to load quality report</p>
          <p className="mt-2 text-sm text-red-600">
            {isNotReady
              ? "The report is not ready yet. Wait a few seconds and refresh this page."
              : reportQuery.error instanceof Error
                ? reportQuery.error.message
                : "Unknown error"}
          </p>
          <Button asChild className="mt-4 bg-[#E8690A] text-white hover:bg-[#d45e07]">
            <Link href="/generate">Generate New Dataset</Link>
          </Button>
        </Card>
      </main>
    );
  }

  const report = reportQuery.data as DownloadReport;
  const isUploadedJob = report?.source === "uploaded" || report?.is_uploaded_job === true;
  const qualityScore = report?.overall_quality_score ?? 0;
  const perLanguageQuality = report?.per_language_quality ?? {};
  const labelDistribution = report?.label_distribution ?? {};
  const shortfallWarnings = report?.shortfall_warnings ?? [];
  const lowQualityWarning = report?.low_quality_warning ?? null;
  const downloadFormats = report?.export_formats ?? {};
  const safeDownloadFormats = Array.isArray(downloadFormats)
    ? downloadFormats
    : defaultExportFormats;
  const distributionTotal = Math.max(1, totalDistribution(labelDistribution));

  if (isUploadedJob) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-10">
        <h1 className="text-3xl font-bold text-[#0F172A]">Your Labeled Dataset is Ready</h1>
        <p className="mt-2 text-sm text-slate-600">Job ID: {jobId}</p>

        <Card className="mt-6 p-6">
          <p className="text-lg font-semibold text-slate-900">Summary</p>
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="rounded-lg border p-3">
              <p className="text-sm text-slate-600">Total rows</p>
              <p className="text-xl font-semibold">{report?.total_rows ?? 0}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-sm text-slate-600">Labeled rows</p>
              <p className="text-xl font-semibold">{report?.labeled_rows ?? 0}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-sm text-slate-600">Skipped rows</p>
              <p className="text-xl font-semibold">{report?.skipped_rows ?? 0}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-sm text-slate-600">Label type</p>
              <p className="text-xl font-semibold capitalize">{report?.label_type ?? "unknown"}</p>
            </div>
          </div>
        </Card>

        <Card className="mt-6 p-6">
          <p className="text-lg font-semibold text-slate-900">Download</p>
          <p className="mt-1 text-sm text-slate-600">Download your labeled CSV file.</p>
          <Button asChild className="mt-4 bg-[#E8690A] text-white hover:bg-[#d45e07]">
            <Link href={getDownloadUrl(jobId, "csv")}>Download Labeled CSV</Link>
          </Button>
        </Card>

        <Button asChild className="mt-6 bg-[#E8690A] text-white hover:bg-[#d45e07]">
          <Link href="/generate">Generate New Dataset</Link>
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold text-[#0F172A]">Download Dataset</h1>
      <p className="mt-2 text-sm text-slate-600">Job ID: {jobId}</p>

      <Card className="mt-6 p-6">
        <p className="text-sm text-slate-600">Quality Score</p>
        <p className="text-6xl sm:text-8xl font-black text-[#0F172A]">{qualityScore.toFixed(1)}</p>
      </Card>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {Object.entries(perLanguageQuality).map(([language, score]) => (
          <Card key={language} className="p-4">
            <p className="text-sm text-slate-600">{LANGUAGE_LABELS[language as keyof typeof LANGUAGE_LABELS] ?? language}</p>
            <p className="text-2xl font-bold text-slate-900">{score.toFixed(1)}</p>
          </Card>
        ))}
      </div>

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Label Distribution</p>
        <div className="mt-4 space-y-3">
          {Object.entries(labelDistribution).map(([label, count]) => {
            const percentage = Math.round((count / distributionTotal) * 100);
            return (
              <div key={label}>
                <div className="flex justify-between text-sm text-slate-700">
                  <span className="capitalize">{label}</span>
                  <span>{count} ({percentage}%)</span>
                </div>
                <div className="mt-1 h-3 overflow-hidden rounded-full bg-slate-200">
                  <div className="h-full bg-[#E8690A]" style={{ width: `${percentage}%` } as React.CSSProperties} />
                </div>
              </div>
            );
          })}
        </div>
        {report?.is_balanced === false && (
          <p className="mt-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
            Warning: Label distribution is not balanced.
          </p>
        )}
      </Card>

      {(shortfallWarnings.length > 0 || lowQualityWarning) && (
        <Card className="mt-6 p-6">
          <p className="text-lg font-semibold text-slate-900">Warnings</p>
          <div className="mt-4 space-y-3">
            {shortfallWarnings.map((warning) => (
              <p key={warning} className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
                {warning}
              </p>
            ))}
            {lowQualityWarning && (
              <p className="rounded-md border border-orange-300 bg-orange-50 p-3 text-sm text-orange-800">
                {lowQualityWarning}
              </p>
            )}
            {qualityScore < 78 && (
              <p className="rounded-md border border-red-300 bg-red-50 p-3 text-sm font-semibold text-red-700">
                Quality below production threshold. Manual review recommended.
              </p>
            )}
          </div>
        </Card>
      )}

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Download</p>
        <p className="mt-1 text-sm text-slate-600">Total labeled rows: {report?.total_labeled ?? 0}</p>
        <div className="mt-4">
          {safeDownloadFormats.length > 0 ? (
            <DownloadCard jobId={jobId} formats={safeDownloadFormats} />
          ) : (
            <p className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
              Download not available.
            </p>
          )}
          <Link
            href={`/report?job_id=${jobId}`}
            className="mt-4 block text-center text-sm text-gray-400 underline transition-colors hover:text-[#E8690A]"
          >
            🚩 Report a data quality issue
          </Link>
        </div>
      </Card>

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Stats</p>
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Total Labeled</p>
            <p className="text-xl font-semibold">{report?.total_labeled ?? 0}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Needs Review</p>
            <p className="text-xl font-semibold">{report?.total_needs_review ?? 0}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Claude / OpenAI</p>
            <p className="text-xl font-semibold">{report?.claude_count ?? 0} / {report?.openai_count ?? 0}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">OpenRouter</p>
            <p className="text-xl font-semibold">{report?.openrouter_count ?? report?.ollama_count ?? 0}</p>
          </div>
        </div>
      </Card>

      <Button asChild className="mt-6 bg-[#E8690A] text-white hover:bg-[#d45e07]">
        <Link href="/generate">Generate New Dataset</Link>
      </Button>
    </main>
  );
}
