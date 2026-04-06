"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { getJobStatus } from "../../../lib/api";
import type { JobStatusResponse } from "../../../lib/types";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import ProgressTracker from "../../../components/ProgressTracker";

function formatEta(seconds: number | null): string {
  if (seconds === null) return "Calculating...";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

export default function JobPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const jobId = params.id;

  const statusQuery = useQuery<JobStatusResponse>({
    queryKey: ["job-status", jobId],
    queryFn: () => getJobStatus(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "complete" || status === "failed") return false;
      return 3000;
    },
    enabled: Boolean(jobId),
  });

  useEffect(() => {
    if (statusQuery.data?.status === "complete") {
      const handle = setTimeout(() => {
        router.push(`/download/${jobId}`);
      }, 2000);
      return () => clearTimeout(handle);
    }
    return undefined;
  }, [jobId, router, statusQuery.data?.status]);

  if (statusQuery.isLoading) {
    return <main className="mx-auto max-w-5xl px-4 py-12">Loading job status...</main>;
  }

  if (statusQuery.isError || !statusQuery.data) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-12">
        <Card className="border-red-200 p-6">
          <h1 className="text-xl font-semibold text-red-700">Unable to load job</h1>
          <p className="mt-2 text-sm text-red-600">{statusQuery.error instanceof Error ? statusQuery.error.message : "Unknown error"}</p>
          <Button asChild className="mt-4 bg-[#E8690A] text-white hover:bg-[#d45e07]">
            <Link href="/generate">Try Again</Link>
          </Button>
        </Card>
      </main>
    );
  }

  const data = statusQuery.data;
  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold text-[#0F172A]">Job Progress</h1>
      <p className="mt-2 text-sm text-slate-600">Job ID: {data.job_id}</p>

      <Card className="mt-6 border-slate-200 p-6">
        <p className="text-lg font-semibold text-slate-900">Estimated time remaining: {formatEta(data.eta_seconds)}</p>
        <div className="mt-4">
          <ProgressTracker jobStatus={data} />
        </div>
      </Card>

      {data.status === "complete" && (
        <Card className="mt-6 border-emerald-200 bg-emerald-50 p-6">
          <p className="text-lg font-semibold text-emerald-700">Dataset generation complete</p>
          <p className="mt-1 text-sm text-emerald-700">Redirecting to download page...</p>
        </Card>
      )}

      {data.status === "failed" && (
        <Card className="mt-6 border-red-200 bg-red-50 p-6">
          <p className="text-lg font-semibold text-red-700">Dataset generation failed</p>
          <p className="mt-1 text-sm text-red-700">{data.error_message ?? "Unknown error"}</p>
          <Button asChild className="mt-4 bg-[#E8690A] text-white hover:bg-[#d45e07]">
            <Link href="/generate">Try Again</Link>
          </Button>
        </Card>
      )}
    </main>
  );
}
