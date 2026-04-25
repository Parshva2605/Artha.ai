export type Language = "en" | "hi" | "gu" | "mr" | "ta";

export type Domain = "app_reviews" | "social_media" | "news" | "mixed";

export type LabelType = "sentiment" | "topic" | "ner" | "all";

export type ExportFormat = "csv" | "json" | "excel" | "parquet" | "huggingface";

export type JobStatus =
  | "queued"
  | "scraping"
  | "cleaning"
  | "labeling"
  | "quality_check"
  | "exporting"
  | "complete"
  | "failed"
  | "cancelled";

export interface GenerateDatasetRequest {
  languages: Language[];
  domain: Domain;
  label_type: LabelType;
  quantity_per_language: number;
  export_formats: ExportFormat[];
  email?: string;
}

export interface GenerateDatasetResponse {
  job_id: string;
  estimated_minutes: number;
  message: string;
}

export interface PerLanguageStatus {
  step: string;
  rows_collected: number;
  rows_clean: number;
  rows_labeled: number;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress_percent: number;
  current_step: string;
  per_language_status: Record<string, PerLanguageStatus>;
  eta_seconds: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface QualityReport {
  overall_quality_score: number;
  per_language_quality: Record<string, number>;
  label_distribution: Record<string, number>;
  is_balanced: boolean;
  shortfall_warnings: string[];
  low_quality_warning: string | null;
  total_labeled: number;
  total_needs_review: number;
  claude_count: number;
  openai_count: number;
  openrouter_count: number;
  ollama_count: number;
  export_formats: ExportFormat[];
}

export interface DownloadFile {
  format: ExportFormat;
  url: string;
  label: string;
}

export const LANGUAGE_LABELS: Record<Language, string> = {
  en: "English",
  hi: "Hindi",
  gu: "Gujarati",
  mr: "Marathi",
  ta: "Tamil",
};

export const LANGUAGE_FLAGS: Record<Language, string> = {
  en: "🇬🇧",
  hi: "🇮🇳",
  gu: "🇮🇳",
  mr: "🇮🇳",
  ta: "🇮🇳",
};

export const FORMAT_LABELS: Record<ExportFormat, string> = {
  csv: "CSV",
  json: "JSON",
  excel: "Excel (.xlsx)",
  parquet: "Parquet",
  huggingface: "HuggingFace Dataset",
};
