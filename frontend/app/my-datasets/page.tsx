"use client";

import { useEffect, useState } from "react";
import { deleteJob, getMyJobs, getDownloadUrl, JobResponse } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

const RUNNING_STATUSES = new Set([
  "queued",
  "scraping",
  "cleaning",
  "labeling",
  "quality_check",
  "exporting",
]);

export default function MyDatasetsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);

  useEffect(() => {
    async function loadJobs() {
      try {
        const data = await getMyJobs();
        setJobs(data);
      } catch (err) {
        if (err instanceof Error && err.message.includes("401")) {
          router.push("/login");
        } else {
          setError(err instanceof Error ? err.message : "Failed to load datasets");
        }
      } finally {
        setLoading(false);
      }
    }

    loadJobs();
  }, [router]);

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function getStatusBadgeColor(status: string): string {
    switch (status) {
      case "complete":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "queued":
      case "scraping":
      case "cleaning":
      case "labeling":
      case "quality_check":
      case "exporting":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  }

  function formatStatus(status: string): string {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  async function handleDelete(job: JobResponse): Promise<void> {
    const isRunning = RUNNING_STATUSES.has(job.status);
    const confirmed = window.confirm(
      isRunning
        ? "This job is still running. Cancel it now?"
        : "Delete this dataset job permanently?",
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setDeletingJobId(job.job_id);
    try {
      await deleteJob(job.job_id);
      setJobs((previous) => previous.filter((item) => item.job_id !== job.job_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete job");
    } finally {
      setDeletingJobId(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">My Datasets</h1>
          <div className="text-center py-12">
            <p className="text-gray-600">Loading datasets...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold">My Datasets</h1>
          <Link
            href="/generate"
            className="w-full sm:w-auto text-center bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition"
          >
            Generate New Dataset
          </Link>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {jobs.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 text-lg mb-4">No datasets yet</p>
            <p className="text-gray-500 mb-6">
              Generate your first dataset to get started
            </p>
            <Link
              href="/generate"
              className="inline-block bg-orange-600 text-white px-6 py-2 rounded hover:bg-orange-700 transition"
            >
              Create Dataset
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px]">
                <thead className="bg-gray-100 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Job ID
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.job_id} className="border-b hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-700">
                        {formatDate(job.created_at)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-700 font-mono">
                        {job.job_id.substring(0, 8)}...
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(
                            job.status,
                          )}`}
                        >
                          {formatStatus(job.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex gap-2">
                          <Link
                            href={`/job/${job.job_id}`}
                            className="text-orange-600 hover:text-orange-700 font-medium"
                          >
                            View
                          </Link>
                          {job.status === "complete" && (
                            <a
                              href={getDownloadUrl(job.job_id, "csv")}
                              className="text-blue-600 hover:text-blue-700 font-medium"
                              download
                            >
                              Download
                            </a>
                          )}
                          <button
                            type="button"
                            className="text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
                            disabled={deletingJobId === job.job_id}
                            onClick={() => void handleDelete(job)}
                          >
                            {deletingJobId === job.job_id
                              ? "Working..."
                              : RUNNING_STATUSES.has(job.status)
                                ? "Cancel"
                                : "Delete"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
