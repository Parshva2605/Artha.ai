import type {
  ExportFormat,
  GenerateDatasetRequest,
  GenerateDatasetResponse,
  JobStatusResponse,
  QualityReport,
} from "./types";
import { getAuthHeaders } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function buildError(response: Response): Promise<ApiError> {
  let message = `Request failed with status ${response.status}`;
  try {
    const payload = (await response.json()) as { detail?: string; message?: string };
    message = payload.detail || payload.message || message;
  } catch {
  }

  return new ApiError(response.status, message);
}

// ==================== Authentication ====================

export interface AuthResponse {
  user_id: string;
  email: string;
  full_name: string | null;
  access_token: string;
}

export interface UserResponse {
  user_id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
}

export async function register(
  email: string,
  password: string,
  full_name?: string,
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name }),
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return (await response.json()) as AuthResponse;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return (await response.json()) as AuthResponse;
}

export async function getCurrentUser(): Promise<UserResponse> {
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return (await response.json()) as UserResponse;
}

export async function logout(): Promise<void> {
  await fetch(`${API_BASE}/api/auth/logout`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
}

// ==================== Dataset Generation ====================

export async function generateDataset(request: GenerateDatasetRequest): Promise<GenerateDatasetResponse> {
  const response = await fetch(`${API_BASE}/api/generate-dataset`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      ...getAuthHeaders(),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return (await response.json()) as GenerateDatasetResponse;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/api/job-status/${jobId}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw await buildError(response);
  }
  return (await response.json()) as JobStatusResponse;
}

export interface JobResponse {
  job_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export async function getMyJobs(): Promise<JobResponse[]> {
  const response = await fetch(`${API_BASE}/api/my-jobs`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw await buildError(response);
  }

  return (await response.json()) as JobResponse[];
}

export async function deleteJob(jobId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw await buildError(response);
  }
}

export async function getQualityReport(jobId: string): Promise<QualityReport> {
  const response = await fetch(`${API_BASE}/api/quality-report/${jobId}`);
  if (!response.ok) {
    throw await buildError(response);
  }

  const raw = (await response.json()) as {
    overall_quality_score: number;
    per_language_quality: Record<string, number>;
    label_distribution: Record<string, number>;
    shortfall_warnings: string[];
    low_quality_warning: string | null;
    total_labeled: number;
    total_needs_review: number;
    claude_count: number;
    openai_count: number;
    ollama_count: number;
    balance_result?: { is_balanced?: boolean };
    is_balanced?: boolean;
  };

  return {
    overall_quality_score: raw.overall_quality_score,
    per_language_quality: raw.per_language_quality,
    label_distribution: raw.label_distribution,
    is_balanced: raw.is_balanced ?? raw.balance_result?.is_balanced ?? true,
    shortfall_warnings: raw.shortfall_warnings,
    low_quality_warning: raw.low_quality_warning,
    total_labeled: raw.total_labeled,
    total_needs_review: raw.total_needs_review,
    claude_count: raw.claude_count,
    openai_count: raw.openai_count,
    ollama_count: raw.ollama_count,
  };
}

export function getDownloadUrl(jobId: string, format: ExportFormat): string {
  return `${API_BASE}/api/download/${jobId}/${format}`;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    return response.status === 200;
  } catch {
    return false;
  }
}
