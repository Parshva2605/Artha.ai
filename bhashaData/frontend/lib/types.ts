export type LabelType = "sentiment" | "topic" | "ner" | "all";
export type DomainType = "app_reviews" | "social_media" | "news" | "mixed";
export type ExportFormat = "csv" | "json" | "huggingface" | "excel" | "parquet";

export type GenerateDatasetRequest = {
  languages: string[];
  domain: DomainType;
  label_type: LabelType;
  quantity_per_language: number;
  export_formats: ExportFormat[];
  email?: string;
};

export type GenerateDatasetResponse = {
  job_id: string;
  estimated_minutes: number;
};
