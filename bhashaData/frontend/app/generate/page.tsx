"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { generateDataset } from "../../lib/api";
import type { Domain, ExportFormat, GenerateDatasetRequest, LabelType, Language } from "../../lib/types";
import { FORMAT_LABELS, LANGUAGE_FLAGS, LANGUAGE_LABELS } from "../../lib/types";
import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";

const steps = ["Languages", "Domain", "Label Type", "Configure", "Review"];

const scripts: Record<Language, string> = {
  en: "Latin",
  hi: "Devanagari",
  gu: "Gujarati",
  mr: "Devanagari",
  ta: "Tamil",
};

const domainOptions: Array<{ value: Domain; title: string; description: string }> = [
  { value: "app_reviews", title: "App Reviews", description: "User feedback from application stores" },
  { value: "social_media", title: "Social Media", description: "Public discussions from social platforms" },
  { value: "news", title: "News", description: "News comments and opinion streams" },
  { value: "mixed", title: "Mixed", description: "Balanced multi-source collection" },
];

const labelOptions: Array<{ value: LabelType; title: string; example: string }> = [
  { value: "sentiment", title: "Sentiment", example: "positive / negative / neutral" },
  { value: "topic", title: "Topic Classification", example: "politics / sports / entertainment..." },
  { value: "ner", title: "NER", example: "PERSON / LOCATION / ORGANIZATION..." },
  { value: "all", title: "All Types", example: "all of the above" },
];

const exportOptions: ExportFormat[] = ["csv", "json", "excel", "parquet", "huggingface"];

export default function GeneratePage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<GenerateDatasetRequest>({
    languages: [],
    domain: "social_media",
    label_type: "sentiment",
    quantity_per_language: 100,
    export_formats: ["csv"],
    email: "",
  });

  const estimatedMinutes = useMemo(
    () => Math.max(2, Math.floor((form.quantity_per_language * Math.max(form.languages.length, 1)) / 100)),
    [form.languages.length, form.quantity_per_language]
  );

  const mutation = useMutation({
    mutationFn: (payload: GenerateDatasetRequest) => generateDataset(payload),
    onSuccess: (result) => {
      router.push(`/job/${result.job_id}`);
    },
    onError: (mutationError: Error) => {
      setError(mutationError.message);
    },
  });

  const validateStep = (index: number): string | null => {
    if (index === 0 && form.languages.length < 1) {
      return "Please select at least one language";
    }
    if (index === 1 && !domainOptions.some((option) => option.value === form.domain)) {
      return "Please select a domain";
    }
    if (index === 2 && !labelOptions.some((option) => option.value === form.label_type)) {
      return "Please select a label type";
    }
    if (index === 3) {
      if (form.quantity_per_language < 100 || form.quantity_per_language > 300) {
        return "Quantity must be between 100 and 300";
      }
      if (form.export_formats.length < 1) {
        return "Please select at least one export format";
      }
    }
    return null;
  };

  const toggleLanguage = (language: Language) => {
    const selected = form.languages.includes(language);
    setForm((previous) => ({
      ...previous,
      languages: selected
        ? previous.languages.filter((item) => item !== language)
        : [...previous.languages, language],
    }));
  };

  const toggleFormat = (format: ExportFormat) => {
    const selected = form.export_formats.includes(format);
    setForm((previous) => ({
      ...previous,
      export_formats: selected
        ? previous.export_formats.filter((item) => item !== format)
        : [...previous.export_formats, format],
    }));
  };

  const goNext = () => {
    const validationError = validateStep(step);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    setStep((previous) => Math.min(previous + 1, steps.length - 1));
  };

  const goPrevious = () => {
    setError(null);
    setStep((previous) => Math.max(previous - 1, 0));
  };

  const submit = () => {
    const validationError = validateStep(step);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    const payload: GenerateDatasetRequest = {
      ...form,
      email: form.email?.trim() ? form.email.trim() : undefined,
    };
    mutation.mutate(payload);
  };

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-bold tracking-tight text-[#0F172A]">Artha AI Dataset Generator</h1>
      <p className="mt-2 text-slate-600">Configure your dataset in five guided steps.</p>

      <div className="mt-8 grid grid-cols-5 gap-2">
        {steps.map((item, index) => (
          <div key={item} className="rounded-lg border p-2 text-center text-xs sm:text-sm">
            <p className={index <= step ? "font-semibold text-[#E8690A]" : "text-slate-500"}>{index + 1}. {item}</p>
          </div>
        ))}
      </div>

      <Card className="mt-6 border-slate-200 p-5 sm:p-6">
        {step === 0 && (
          <section>
            <h2 className="text-xl font-semibold">Step 1 - Select Languages</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {(["en", "hi", "gu", "mr", "ta"] as Language[]).map((language) => {
                const selected = form.languages.includes(language);
                const checkboxId = `language-${language}`;
                return (
                  <label
                    key={language}
                    htmlFor={checkboxId}
                    className={`block cursor-pointer rounded-xl border p-4 text-left transition ${
                      selected ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-lg">{LANGUAGE_FLAGS[language]} {LANGUAGE_LABELS[language]}</p>
                        <p className="text-sm text-slate-600">Script: {scripts[language]}</p>
                      </div>
                      <input
                        id={checkboxId}
                        type="checkbox"
                        checked={selected}
                        onChange={() => toggleLanguage(language)}
                        className="h-4 w-4 accent-[#E8690A]"
                      />
                    </div>
                  </label>
                );
              })}
            </div>
          </section>
        )}

        {step === 1 && (
          <section>
            <h2 className="text-xl font-semibold">Step 2 - Select Domain</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {domainOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setForm((previous) => ({ ...previous, domain: option.value }))}
                  className={`rounded-xl border p-4 text-left transition ${
                    form.domain === option.value ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
                  }`}
                >
                  <p className="font-semibold text-slate-900">{option.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{option.description}</p>
                </button>
              ))}
            </div>
          </section>
        )}

        {step === 2 && (
          <section>
            <h2 className="text-xl font-semibold">Step 3 - Select Label Type</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {labelOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setForm((previous) => ({ ...previous, label_type: option.value }))}
                  className={`rounded-xl border p-4 text-left transition ${
                    form.label_type === option.value ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
                  }`}
                >
                  <p className="font-semibold text-slate-900">{option.title}</p>
                  <p className="mt-1 text-sm text-slate-600">{option.example}</p>
                </button>
              ))}
            </div>
          </section>
        )}

        {step === 3 && (
          <section>
            <h2 className="text-xl font-semibold">Step 4 - Configure</h2>
            <div className="mt-4 space-y-6">
              <div>
                <Label htmlFor="quantity">Quantity per language: {form.quantity_per_language}</Label>
                <input
                  id="quantity"
                  className="mt-2 w-full"
                  type="range"
                  min={100}
                  max={300}
                  step={100}
                  value={form.quantity_per_language}
                  onChange={(event) =>
                    setForm((previous) => ({ ...previous, quantity_per_language: Number(event.target.value) }))
                  }
                />
                <p className="mt-2 text-sm text-slate-600">Estimated time: ~{estimatedMinutes} minutes</p>
                <p className="text-sm text-gray-500 mt-1">
                  Demo limit: 300 rows per language. Full access coming soon.
                </p>
              </div>

              <div>
                <p className="text-sm font-medium">Export formats</p>
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  {exportOptions.map((format) => {
                    const selected = form.export_formats.includes(format);
                    return (
                      <button
                        key={format}
                        type="button"
                        onClick={() => toggleFormat(format)}
                        className={`rounded-xl border p-3 text-left ${
                          selected ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
                        }`}
                      >
                        <p className="font-semibold">{FORMAT_LABELS[format]}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <Label htmlFor="email">Email (optional)</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={form.email ?? ""}
                  onChange={(event) => setForm((previous) => ({ ...previous, email: event.target.value }))}
                />
              </div>
            </div>
          </section>
        )}

        {step === 4 && (
          <section>
            <h2 className="text-xl font-semibold">Step 5 - Review and Submit</h2>
            <div className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p><span className="font-semibold">Languages:</span> {form.languages.map((item) => LANGUAGE_LABELS[item]).join(", ") || "-"}</p>
              <p><span className="font-semibold">Domain:</span> {form.domain}</p>
              <p><span className="font-semibold">Label type:</span> {form.label_type}</p>
              <p><span className="font-semibold">Quantity per language:</span> {form.quantity_per_language}</p>
              <p><span className="font-semibold">Export formats:</span> {form.export_formats.map((item) => FORMAT_LABELS[item]).join(", ")}</p>
              <p><span className="font-semibold">Estimated time:</span> {estimatedMinutes} minutes</p>
              <p><span className="font-semibold">Email:</span> {form.email?.trim() || "Not provided"}</p>
            </div>
          </section>
        )}

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

        <div className="mt-8 flex items-center justify-between">
          <Button type="button" variant="outline" onClick={goPrevious} disabled={step === 0 || mutation.isPending}>
            Previous
          </Button>
          {step < steps.length - 1 ? (
            <Button type="button" className="bg-[#E8690A] text-white hover:bg-[#d45e07]" onClick={goNext}>
              Next
            </Button>
          ) : (
            <Button
              type="button"
              className="bg-[#E8690A] text-white hover:bg-[#d45e07]"
              onClick={submit}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Generating..." : "Generate Dataset"}
            </Button>
          )}
        </div>
      </Card>
    </main>
  );
}
