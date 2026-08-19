import type { Metadata } from "next";

import CustomDatasetRequestForm from "./request-form";

export const metadata: Metadata = {
  title: "Custom Dataset - Artha AI",
  description: "Request custom AI training datasets in any language, domain or format. Delivered in 48-72 hours.",
};

const stats = [
  { value: "48-72 hrs", label: "Average delivery time" },
  { value: "98%+", label: "Quality score guaranteed" },
  { value: "Any Format", label: "CSV, JSON, COCO, YOLO, HuggingFace" },
];

const steps = [
  {
    icon: "📝",
    title: "You Describe",
    description: "Tell us your dataset requirements — domain, size, labels, format, language",
  },
  {
    icon: "🔍",
    title: "We Source",
    description: "We collect data from web scraping, public sources, synthetic generation, or human annotation",
  },
  {
    icon: "✅",
    title: "We Label",
    description: "Expert AI + human review ensures 95%+ accuracy on every label",
  },
  {
    icon: "📦",
    title: "We Deliver",
    description: "Download your dataset in your preferred format with full quality report",
  },
];

export default function CustomDatasetPage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#FFF9F4_0%,#FFFFFF_30%,#FFFDFB_100%)] text-slate-900">
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border border-orange-100 bg-white px-6 py-10 shadow-[0_20px_80px_rgba(15,23,42,0.08)] sm:px-10 lg:px-12">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#E8690A]">Custom Dataset Solutions</p>
            <h1 className="mt-4 text-3xl sm:text-5xl font-black tracking-tight text-[#0F172A]">
              Describe what you need. We build it.
            </h1>
            <p className="mt-4 text-lg text-slate-600">Delivered in days, not months.</p>
          </div>

          <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {stats.map((item) => (
              <div key={item.label} className="rounded-2xl border border-orange-100 bg-[#FFF8F1] p-5">
                <p className="text-2xl font-black text-[#E8690A]">{item.value}</p>
                <p className="mt-2 text-sm text-slate-600">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {steps.map((step) => (
            <article key={step.title} className="h-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-3xl">{step.icon}</p>
              <h2 className="mt-4 text-xl font-semibold text-slate-900">{step.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{step.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="space-y-8">
          <div className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#E8690A]">Tell Us What You Need</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-[#0F172A]">Request a custom dataset</h2>
            <p className="mt-4 text-slate-600">
              Fill this form and we will get back within 24 hours at arthaai.dev@gmail.com.
            </p>

            <div className="mt-8 space-y-4 rounded-2xl bg-[#FFF8F1] p-5 text-sm text-slate-700">
              <p><span className="font-semibold text-slate-900">Fast response:</span> We reply within one business day.</p>
              <p><span className="font-semibold text-slate-900">Flexible scope:</span> Text, image, audio, documents, and more.</p>
              <p><span className="font-semibold text-slate-900">Quality first:</span> Built with validation and review checkpoints.</p>
            </div>
          </div>

          <div className="max-w-2xl mx-auto w-full px-4 sm:px-0">
            <CustomDatasetRequestForm />
          </div>
        </div>
      </section>
    </main>
  );
}