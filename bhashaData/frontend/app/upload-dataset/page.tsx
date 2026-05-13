"use client";

import { useRef, useState } from "react";
import type { DragEvent } from "react";
import { useRouter } from "next/navigation";
import { Upload } from "lucide-react";

import { labelUploadedCsv, uploadCsv } from "../../lib/api";
import type { LabelType, UploadPreviewResponse } from "../../lib/types";
import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import LabelTypeSelector from "../../components/LabelTypeSelector";

const uploadLabelOptions = [
  { value: "sentiment" as const, title: "Sentiment", example: "positive / negative / neutral" },
  { value: "topic" as const, title: "Topic Classification", example: "politics / sports / entertainment..." },
  { value: "ner" as const, title: "NER", example: "PERSON / LOCATION / ORGANIZATION..." },
  { value: "custom" as const, title: "Custom Labels", example: "Define your own categories" },
];

export default function UploadDatasetPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [uploadPreview, setUploadPreview] = useState<UploadPreviewResponse | null>(null);
  const [selectedColumn, setSelectedColumn] = useState("");
  const [labelType, setLabelType] = useState<LabelType>("sentiment");
  const [customLabels, setCustomLabels] = useState<string[]>([]);
  const [labelInput, setLabelInput] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const previewColumns = uploadPreview?.column_names.slice(0, 4) ?? [];

  const pickFile = () => {
    fileInputRef.current?.click();
  };

  const handleFile = async (file: File | null | undefined) => {
    if (!file) {
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const preview = await uploadCsv(file);
      setUploadPreview(preview);
      setSelectedColumn(preview.detected_text_column);
      setStep(2);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = async (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    await handleFile(file);
  };

  const handleSubmit = async () => {
    if (!uploadPreview) {
      return;
    }
    if (labelType === "custom" && customLabels.length < 2) {
      setError("Add at least 2 custom labels before labeling your data");
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      const result = await labelUploadedCsv({
        upload_id: uploadPreview.upload_id,
        text_column: selectedColumn,
        label_type: labelType,
        custom_labels: labelType === "custom" ? customLabels : undefined,
        export_formats: ["csv"],
        language: "en",
      });
      router.push(`/job/${result.job_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to start labeling");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-[#0F172A]">Label Your Own Data</h1>
      <p className="mt-2 text-slate-600">Upload a CSV, choose your labels, download labeled data.</p>

      <div className="mt-8 grid grid-cols-3 gap-2">
        {[
          { stepNumber: 1, title: "Upload" },
          { stepNumber: 2, title: "Configure" },
          { stepNumber: 3, title: "Label" },
        ].map((item) => (
          <div key={item.title} className="rounded-lg border p-2 text-center text-xs sm:text-sm">
            <p className={item.stepNumber <= step ? "font-semibold text-[#E8690A]" : "text-slate-500"}>
              <span>{item.stepNumber}.</span> <span className="hidden sm:inline">{item.title}</span>
            </p>
          </div>
        ))}
      </div>

      <Card className="mt-6 border-slate-200 p-5 sm:p-6">
        {step === 1 && (
          <section>
            <div
              onDragOver={(event) => event.preventDefault()}
              onDrop={handleDrop}
              onClick={pickFile}
              className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center transition hover:border-[#E8690A] hover:bg-[#E8690A]/5"
            >
              <Upload className="h-10 w-10 text-[#E8690A]" />
              <p className="mt-4 text-lg font-semibold text-slate-900">Drop your CSV here or click to browse</p>
              <p className="mt-2 text-sm text-slate-500">Max 5MB · Max 5000 rows · CSV only</p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                hidden
                onChange={async (event) => {
                  await handleFile(event.target.files?.[0]);
                  event.currentTarget.value = "";
                }}
              />
            </div>
            {isUploading && <p className="mt-4 text-sm text-slate-600">Uploading...</p>}
            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
          </section>
        )}

        {step === 2 && uploadPreview && (
          <section>
            <h2 className="text-xl font-semibold">Step 2 - Configure</h2>
            <p className="mt-2 text-sm text-slate-600">
              File: {uploadPreview.filename} · {uploadPreview.total_rows} rows
            </p>

            <div className="mt-6 space-y-6">
              <div>
                <Label htmlFor="text-column">Which column contains your text?</Label>
                <select
                  id="text-column"
                  value={selectedColumn}
                  onChange={(event) => setSelectedColumn(event.target.value)}
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                >
                  {uploadPreview.column_names.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-900">Preview</p>
                <div className="mt-3 overflow-x-auto rounded-xl border border-slate-200">
                  <table className="min-w-full border-collapse text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        {previewColumns.map((column) => (
                          <th
                            key={column}
                            className={`border-b border-slate-200 px-3 py-2 text-left font-medium text-slate-700 ${
                              column === selectedColumn ? "bg-[#E8690A]/10 text-[#B34F03]" : ""
                            }`}
                          >
                            {column}
                          </th>
                        ))}
                        {uploadPreview.column_names.length > 4 && (
                          <th className="border-b border-slate-200 px-3 py-2 text-left font-medium text-slate-400">…</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {uploadPreview.preview_rows.map((row, index) => (
                        <tr key={index} className="odd:bg-white even:bg-slate-50">
                          {previewColumns.map((column) => (
                            <td key={column} className="border-b border-slate-100 px-3 py-2 align-top text-slate-700">
                              <div className="max-w-[240px] break-words">{String(row[column] ?? "")}</div>
                            </td>
                          ))}
                          {uploadPreview.column_names.length > 4 && (
                            <td className="border-b border-slate-100 px-3 py-2 text-slate-400">…</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-900">What kind of labels do you want?</p>
                <div className="mt-3">
                  <LabelTypeSelector
                    selected={labelType}
                    onChange={setLabelType}
                    options={uploadLabelOptions}
                  />
                </div>

                {labelType === "custom" && (
                  <div className="mt-6 rounded-xl border border-slate-200 p-4">
                    <label className="block text-sm font-medium text-slate-900">Your Labels (2–10)</label>
                    <div className="mb-3 mt-3 flex flex-wrap gap-2">
                      {customLabels.map((label) => (
                        <div
                          key={label}
                          className="inline-flex items-center gap-2 rounded-full border border-[#E8690A]/20 bg-[#E8690A]/10 px-3 py-1 text-sm text-slate-900"
                        >
                          <span>{label}</span>
                          <button
                            type="button"
                            onClick={() => setCustomLabels((previous) => previous.filter((item) => item !== label))}
                            className="ml-1 font-semibold text-[#E8690A] hover:text-[#d45e07]"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <Input
                      value={labelInput}
                      onChange={(event) => setLabelInput(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === ",") {
                          event.preventDefault();
                          const trimmed = labelInput.trim().replace(",", "");
                          if (trimmed && customLabels.length < 10 && !customLabels.includes(trimmed)) {
                            setCustomLabels([...customLabels, trimmed]);
                            setLabelInput("");
                          }
                        }
                      }}
                      placeholder="Type a label and press Enter"
                      disabled={customLabels.length >= 10}
                    />
                    <p className="mt-2 text-sm text-slate-600">{customLabels.length}/10 labels</p>
                    {customLabels.length < 2 && labelType === "custom" && (
                      <p className="mt-2 text-sm text-red-600">Add at least 2 labels</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-between">
              <Button type="button" variant="outline" onClick={() => setStep(1)} className="w-full sm:w-auto">
                Back
              </Button>
              <Button type="button" onClick={() => setStep(3)} className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]">
                Review
              </Button>
            </div>

            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
          </section>
        )}

        {step === 3 && uploadPreview && (
          <section>
            <h2 className="text-xl font-semibold">Step 3 - Label</h2>
            <div className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <p><span className="font-semibold text-slate-900">File:</span> {uploadPreview.filename}</p>
              <p><span className="font-semibold text-slate-900">Text column:</span> {selectedColumn}</p>
              <p><span className="font-semibold text-slate-900">Label type:</span> {labelType}</p>
              {labelType === "custom" && <p><span className="font-semibold text-slate-900">Custom labels:</span> {customLabels.join(", ")}</p>}
              <p><span className="font-semibold text-slate-900">Rows:</span> {uploadPreview.total_rows}</p>
            </div>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-between">
              <Button type="button" variant="outline" onClick={() => setStep(2)} className="w-full sm:w-auto">
                Back
              </Button>
              <Button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting || (labelType === "custom" && customLabels.length < 2)}
                className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]"
              >
                {isSubmitting ? "Labeling..." : "Label My Data"}
              </Button>
            </div>

            {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
          </section>
        )}
      </Card>
    </main>
  );
}