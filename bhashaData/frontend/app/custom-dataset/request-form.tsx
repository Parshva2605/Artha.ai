"use client";

import { useState } from "react";

const accessKey = "39142af4-75ee-4065-8839-755ad0f2a411";
const subject = "New Custom Dataset Request - Artha AI";

const languageOptions = ["Hindi", "Gujarati", "Marathi", "Tamil", "Telugu", "Bengali", "English", "Other"];
const outputOptions = ["CSV", "JSON", "COCO (images)", "YOLO (images)", "HuggingFace", "Excel", "Other"];

const initialForm = {
  fullName: "",
  email: "",
  organization: "",
  datasetType: "",
  domain: "",
  languages: [] as string[],
  datasetSize: "",
  labelTypes: "",
  outputFormats: [] as string[],
  deadline: "",
  budgetRange: "",
  additionalDetails: "",
};

export default function CustomDatasetRequestForm() {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleItem = (field: "languages" | "outputFormats", value: string) => {
    setForm((previous) => {
      const selected = previous[field].includes(value);
      return {
        ...previous,
        [field]: selected
          ? previous[field].filter((item) => item !== value)
          : [...previous[field], value],
      };
    });
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      const formData = new FormData();
      formData.append("access_key", accessKey);
      formData.append("subject", subject);
      formData.append("from_name", form.fullName);
      formData.append("name", form.fullName);
      formData.append("email", form.email);
      formData.append("organization", form.organization);
      formData.append("dataset_type", form.datasetType);
      formData.append("domain", form.domain);
      formData.append("languages_required", form.languages.join(", "));
      formData.append("dataset_size", form.datasetSize);
      formData.append("label_types_required", form.labelTypes);
      formData.append("output_format", form.outputFormats.join(", "));
      formData.append("deadline", form.deadline);
      formData.append("budget_range", form.budgetRange);
      formData.append("additional_details", form.additionalDetails);

      const response = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || "Submission failed");
      }

      setSuccessMessage(
        `✅ Request received! We will contact you at ${form.email} within 24 hours. For urgent requests email us directly at arthaai.dev@gmail.com`,
      );
      setForm(initialForm);
    } catch {
      setErrorMessage("Something went wrong. Please email us directly at arthaai.dev@gmail.com");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
      <form className="space-y-6" onSubmit={handleSubmit}>
        <input type="hidden" name="subject" value={subject} />
        <input type="hidden" name="access_key" value={accessKey} />

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Full Name</span>
            <input
              type="text"
              required
              placeholder="Your full name"
              value={form.fullName}
              onChange={(event) => setForm((previous) => ({ ...previous, fullName: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input
              type="email"
              required
              placeholder="your@email.com"
              value={form.email}
              onChange={(event) => setForm((previous) => ({ ...previous, email: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            />
          </label>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Organization / College</span>
            <input
              type="text"
              required
              placeholder="Company or college name"
              value={form.organization}
              onChange={(event) => setForm((previous) => ({ ...previous, organization: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Dataset Type</span>
            <select
              required
              value={form.datasetType}
              onChange={(event) => setForm((previous) => ({ ...previous, datasetType: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            >
              <option value="">Select dataset type</option>
              <option>Text / NLP</option>
              <option>Computer Vision / Images</option>
              <option>Audio / Speech</option>
              <option>Document / PDF</option>
              <option>Medical / Healthcare</option>
              <option>Agriculture</option>
              <option>Other (specify below)</option>
            </select>
          </label>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Domain / Industry</span>
            <input
              type="text"
              required
              placeholder="e.g. E-commerce, Healthcare, Education"
              value={form.domain}
              onChange={(event) => setForm((previous) => ({ ...previous, domain: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Dataset Size</span>
            <select
              required
              value={form.datasetSize}
              onChange={(event) => setForm((previous) => ({ ...previous, datasetSize: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            >
              <option value="">Select dataset size</option>
              <option>Small (under 1,000 rows/images)</option>
              <option>Medium (1,000 - 10,000)</option>
              <option>Large (10,000 - 1,00,000)</option>
              <option>Enterprise (1,00,000+)</option>
            </select>
          </label>
        </div>

        <div>
          <span className="text-sm font-medium text-slate-700">Languages Required</span>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
            {languageOptions.map((language) => (
              <label key={language} className="flex items-center gap-3 rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.languages.includes(language)}
                  onChange={() => toggleItem("languages", language)}
                  className="h-4 w-4 accent-[#E8690A]"
                />
                {language}
              </label>
            ))}
          </div>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Label Types Required</span>
          <textarea
            required
            rows={4}
            placeholder="Describe the labels you need. Example: Detect and label doors, windows, and walls in building images"
            value={form.labelTypes}
            onChange={(event) => setForm((previous) => ({ ...previous, labelTypes: event.target.value }))}
            className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
          />
        </label>

        <div>
          <span className="text-sm font-medium text-slate-700">Output Format</span>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
            {outputOptions.map((format) => (
              <label key={format} className="flex items-center gap-3 rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={form.outputFormats.includes(format)}
                  onChange={() => toggleItem("outputFormats", format)}
                  className="h-4 w-4 accent-[#E8690A]"
                />
                {format}
              </label>
            ))}
          </div>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Deadline</span>
            <select
              required
              value={form.deadline}
              onChange={(event) => setForm((previous) => ({ ...previous, deadline: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            >
              <option value="">Select deadline</option>
              <option>Urgent (24-48 hours)</option>
              <option>Standard (3-7 days)</option>
              <option>Flexible (2-4 weeks)</option>
              <option>No deadline</option>
            </select>
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Budget Range</span>
            <select
              value={form.budgetRange}
              onChange={(event) => setForm((previous) => ({ ...previous, budgetRange: event.target.value }))}
              className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
            >
              <option value="">Select budget range</option>
              <option>Under ₹5,000</option>
              <option>₹5,000 - ₹25,000</option>
              <option>₹25,000 - ₹1,00,000</option>
              <option>₹1,00,000+</option>
              <option>Discuss after review</option>
            </select>
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Additional Details</span>
          <textarea
            rows={4}
            placeholder="Any other requirements, sample data links, reference datasets, special instructions..."
            value={form.additionalDetails}
            onChange={(event) => setForm((previous) => ({ ...previous, additionalDetails: event.target.value }))}
            className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
          />
        </label>

        {successMessage && <div className="rounded-2xl border border-green-200 bg-green-50 px-4 py-4 text-green-800">{successMessage}</div>}
        {errorMessage && <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-4 text-red-800">{errorMessage}</div>}

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex w-full items-center justify-center rounded-full bg-[#E8690A] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#d45e07] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? "Sending request..." : "Submit Request"}
        </button>
      </form>
    </div>
  );
}