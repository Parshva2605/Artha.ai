import { GenerateDatasetRequest, GenerateDatasetResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function generateDataset(payload: GenerateDatasetRequest): Promise<GenerateDatasetResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate-dataset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to start dataset generation job");
  }

  return response.json() as Promise<GenerateDatasetResponse>;
}
