"use client";

import { useState } from "react";

const accessKey = "39142af4-75ee-4065-8839-755ad0f2a411";
const subject = "Dataset Quality Report - Artha AI";

const issueTypes = [
  "Wrong label (text labeled incorrectly)",
  "Low quality text (gibberish or irrelevant)",
  "Wrong language detected",
  "Missing data (fewer rows than expected)",
  "Duplicate rows found",
  "Other",
];

const expectedQualityOptions = [
  "95%+ (production grade)",
  "85-95% (research grade)",
  "Any quality is fine",
  "Not sure",
];

export default function ReportPage({ searchParams }: { searchParams: { job_id?: string } }) {
  const [jobId, setJobId] = useState(searchParams.job_id ?? "");
  const [email, setEmail] = useState("");
  const [issueType, setIssueType] = useState("");
  const [affectedRows, setAffectedRows] = useState("");
  const [description, setDescription] = useState("");
  const [expectedQuality, setExpectedQuality] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      const formData = new FormData();
      formData.append("access_key", accessKey);
      formData.append("subject", subject);
      formData.append("job_id", jobId);
      formData.append("email", email);
      formData.append("issue_type", issueType);
      formData.append("affected_rows", affectedRows);
      formData.append("description", description);
      formData.append("expected_quality", expectedQuality);

      const response = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (!response.ok || !result.success) {
        throw new Error(result.message || "Submission failed");
      }

      setSuccessMessage(
        `✅ Report submitted successfully! We will review your dataset and respond to ${email} within 24 hours. Thank you for helping improve Artha AI.`,
      );
      setJobId(searchParams.job_id ?? "");
      setEmail("");
      setIssueType("");
      setAffectedRows("");
      setDescription("");
      setExpectedQuality("");
    } catch {
      setErrorMessage("Failed to submit. Please email us directly: arthaai.dev@gmail.com");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-50 px-4 py-12 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-5xl">Report a Data Issue</h1>
          <p className="mx-auto mt-4 max-w-2xl text-sm text-gray-300 sm:text-base">
            Help us improve dataset quality. We review every report within 24 hours.
          </p>
        </header>

        <section className="mt-10 rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl sm:p-8">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <input type="hidden" name="subject" value={subject} />
            <input type="hidden" name="access_key" value={accessKey} />

            <label className="block">
              <span className="text-sm font-medium text-gray-200">Job ID</span>
              <input
                type="text"
                value={jobId}
                onChange={(event) => setJobId(event.target.value)}
                placeholder="Your job ID"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-200">Your Email</span>
              <input
                type="email"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="your@email.com"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-200">Type of Issue</span>
              <select
                required
                value={issueType}
                onChange={(event) => setIssueType(event.target.value)}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              >
                <option value="">Select issue type</option>
                {issueTypes.map((item) => (
                  <option key={item} value={item} className="text-slate-900">
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-200">Affected Row IDs or Examples</span>
              <input
                type="text"
                value={affectedRows}
                onChange={(event) => setAffectedRows(event.target.value)}
                placeholder="Row numbers or paste example text"
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-200">Describe the Issue</span>
              <textarea
                required
                rows={4}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Please describe what is wrong and what you expected instead..."
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium text-gray-200">What quality did you expect?</span>
              <select
                value={expectedQuality}
                onChange={(event) => setExpectedQuality(event.target.value)}
                className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-[#E8690A] focus:ring-2 focus:ring-[#E8690A]/20"
              >
                <option value="">Select expected quality</option>
                {expectedQualityOptions.map((item) => (
                  <option key={item} value={item} className="text-slate-900">
                    {item}
                  </option>
                ))}
              </select>
            </label>

            {successMessage && (
              <div className="rounded-2xl border border-green-500/30 bg-green-500/10 px-4 py-4 text-green-200">
                {successMessage}
              </div>
            )}
            {errorMessage && (
              <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-4 text-red-200">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex w-full items-center justify-center rounded-full bg-[#E8690A] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[#d45e07] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSubmitting ? "Submitting..." : "Submit Report"}
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}
