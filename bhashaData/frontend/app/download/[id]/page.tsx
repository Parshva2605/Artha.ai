"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { ApiError, getQualityReport } from "../../../lib/api";
import type { ExportFormat, QualityReport as QualityReportType } from "../../../lib/types";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import DownloadCard from "../../../components/DownloadCard";
import QualityReport from "../../../components/QualityReport";

const defaultExportFormats: ExportFormat[] = ["csv"];

function totalDistribution(report: QualityReportType): number {
  return Object.values(report.label_distribution).reduce((sum, value) => sum + value, 0);
}

export default function DownloadPage() {
  const params = useParams<{ id: string }>();
  const jobId = params.id;

  const reportQuery = useQuery({
    queryKey: ["quality-report", jobId],
    queryFn: () => getQualityReport(jobId),
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

  const report = reportQuery.data;
  const exportFormats = report.export_formats?.length ? report.export_formats : defaultExportFormats;
  const distributionTotal = Math.max(1, totalDistribution(report));

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold text-[#0F172A]">Download Dataset</h1>
      <p className="mt-2 text-sm text-slate-600">Job ID: {jobId}</p>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-3">
          <QualityReport report={report} />
        </div>
      </div>

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Label Distribution</p>
        <div className="mt-4 space-y-3">
          {Object.entries(report.label_distribution).map(([label, count]) => {
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
        {!report.is_balanced && (
          <p className="mt-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
            Warning: Label distribution is not balanced.
          </p>
        )}
      </Card>

      {(report.shortfall_warnings.length > 0 || report.low_quality_warning) && (
        <Card className="mt-6 p-6">
          <p className="text-lg font-semibold text-slate-900">Warnings</p>
          <div className="mt-4 space-y-3">
            {report.shortfall_warnings.map((warning) => (
              <p key={warning} className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
                {warning}
              </p>
            ))}
            {report.low_quality_warning && (
              <p className="rounded-md border border-orange-300 bg-orange-50 p-3 text-sm text-orange-800">
                {report.low_quality_warning}
              </p>
            )}
            {report.overall_quality_score < 78 && (
              <p className="rounded-md border border-red-300 bg-red-50 p-3 text-sm font-semibold text-red-700">
                Quality below production threshold. Manual review recommended.
              </p>
            )}
          </div>
        </Card>
      )}

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Download</p>
        <p className="mt-1 text-sm text-slate-600">Total labeled rows: {report.total_labeled}</p>
        <div className="mt-4">
          <DownloadCard jobId={jobId} formats={exportFormats} />
        </div>
      </Card>

      <Card className="mt-6 p-6">
        <p className="text-lg font-semibold text-slate-900">Stats</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Total Labeled</p>
            <p className="text-xl font-semibold">{report.total_labeled}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Needs Review</p>
            <p className="text-xl font-semibold">{report.total_needs_review}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">Claude / OpenAI</p>
            <p className="text-xl font-semibold">{report.claude_count} / {report.openai_count}</p>
          </div>
          <div className="rounded-lg border p-3">
            <p className="text-sm text-slate-600">OpenRouter</p>
            <p className="text-xl font-semibold">{report.openrouter_count ?? report.ollama_count}</p>
          </div>
        </div>
      </Card>

      <Button asChild className="mt-6 bg-[#E8690A] text-white hover:bg-[#d45e07]">
        <Link href="/generate">Generate New Dataset</Link>
      </Button>
    </main>
  );
}
