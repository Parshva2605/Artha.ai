import Link from "next/link";
import { ArrowRight, BookOpenText, Download, Languages, Search, Tags } from "lucide-react";

import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";

const howItWorks = [
  {
    icon: Search,
    title: "Describe",
    description: "Tell us what dataset you need",
  },
  {
    icon: Languages,
    title: "Scrape",
    description: "We collect data from real sources",
  },
  {
    icon: Tags,
    title: "Label",
    description: "AI labels with quality checks",
  },
  {
    icon: Download,
    title: "Download",
    description: "Export in your preferred format",
  },
];

const languages = [
  {
    flag: "🇬🇧",
    name: "English",
    script: "Latin",
    sample: "This is really good",
  },
  {
    flag: "🇮🇳",
    name: "Hindi",
    script: "Devanagari",
    sample: "यह बहुत अच्छा है",
  },
  {
    flag: "🇮🇳",
    name: "Gujarati",
    script: "Gujarati",
    sample: "આ ખૂબ સારું છે",
  },
  {
    flag: "🇮🇳",
    name: "Marathi",
    script: "Devanagari",
    sample: "हे खूप चांगले आहे",
  },
  {
    flag: "🇮🇳",
    name: "Tamil",
    script: "Tamil",
    sample: "இது மிகவும் நல்லது",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      <section className="bg-[#0F172A] text-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-2xl font-black tracking-tight text-[#E8690A]">Artha AI</p>
            <nav className="hidden sm:flex items-center gap-6 text-sm text-slate-200">
              <a href="#how-it-works" className="hover:text-white">How it works</a>
              <a href="#languages" className="hover:text-white">Languages</a>
              <Link href="/docs" className="hover:text-white">Docs</Link>
            </nav>
            <Button asChild className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]">
              <Link href="/generate">Generate Dataset</Link>
            </Button>
          </header>

          <div className="relative mt-10 overflow-hidden rounded-3xl border border-slate-700 bg-[linear-gradient(135deg,#0F172A_0%,#111f3c_40%,#0b1220_100%)] px-6 py-12 sm:mt-16 sm:py-16 sm:px-10">
            <div className="absolute -top-20 left-10 h-56 w-56 rounded-full bg-[#E8690A]/20 blur-3xl" />
            <div className="absolute bottom-0 right-0 h-48 w-48 rounded-full bg-white/10 blur-2xl" />
            <div className="relative max-w-3xl mx-auto">
              <h1 className="text-3xl sm:text-4xl lg:text-6xl font-bold text-white text-center tracking-tight">Give Meaning to Your Data</h1>
              <p className="mt-6 text-base sm:text-xl text-gray-300 text-center max-w-2xl mx-auto">
                Generate high-quality labeled datasets in Hindi, Gujarati, Marathi, Tamil and English in minutes
                not weeks.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center items-center">
                <Button asChild className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]">
                  <Link href="/generate">
                    Start Generating <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" className="w-full sm:w-auto border-slate-500 bg-transparent text-white hover:bg-slate-800">
                  <Link href="/docs">
                    View Documentation <BookOpenText className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-[#0F172A]">How It Works</h2>
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {howItWorks.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title} className="h-full border-slate-200 p-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E8690A]/15 text-[#E8690A]">
                  <Icon className="h-5 w-5" />
                </div>
                <p className="mt-4 text-lg font-semibold text-slate-900">{item.title}</p>
                <p className="mt-2 text-sm text-slate-600">{item.description}</p>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="py-16 px-4 bg-[#0F172A]">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-4 text-center text-2xl font-bold text-white sm:text-3xl">Double-Verified Quality You Can Trust</h2>
          <p className="mx-auto mb-12 max-w-2xl text-center text-gray-400">
            Every dataset goes through our 5-layer quality pipeline before you download it.
          </p>

          <div className="space-y-4">
            {[
              {
                icon: "🕷️",
                title: "Real Data Collection",
                text: "We scrape real content from Google Play, YouTube and news sites — never synthetic or fake data.",
              },
              {
                icon: "🧹",
                title: "Language Verification",
                text: "Every row is verified to be in the correct language using detection algorithms. Wrong language rows are automatically removed.",
              },
              {
                icon: "🔍",
                title: "Deduplication",
                text: "MD5 hashing removes duplicate rows before labeling. You never pay for the same data twice.",
              },
              {
                icon: "🤖",
                title: "AI Labeling with Confidence Score",
                text: "Each row is labeled by Groq AI and assigned a confidence score from 0 to 1. Only rows scoring 0.80 or above are included.",
              },
              {
                icon: "⚖️",
                title: "Balance Enforcement",
                text: "No single label can exceed 50% of your dataset. Our balancer ensures positive, negative and neutral are fairly represented.",
              },
            ].map((step, index) => (
              <div key={step.title} className="flex gap-4 rounded-2xl border border-gray-700 bg-[#1E293B] p-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#E8690A]/15 text-xl">
                  {index + 1}
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">
                    {step.icon} {step.title}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-gray-300">{step.text}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-xl bg-[#1E293B] p-6 text-center">
            <p className="text-4xl font-bold text-[#E8690A]">98.8%</p>
            <p className="mt-1 text-gray-400">Average confidence score across all generated datasets</p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold tracking-tight text-[#0F172A] sm:text-3xl">Getting Started in 4 Steps</h2>
        <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-4">
          {[
            ["1", "Create Account", "Sign up free at artha-ai.dev. No credit card required for demo."],
            ["2", "Describe Your Dataset", "Choose language, domain, label type and how many rows you need."],
            ["3", "Download Your Data", "Get CSV, JSON or HuggingFace format with full quality report."],
            ["4", "Report Any Issues", "Not satisfied? Use our report tool and we fix it within 24 hours."],
          ].map(([number, title, text]) => (
            <Card key={title} className="border-slate-200 p-5">
              <p className="text-sm font-semibold text-[#E8690A]">Step {number}</p>
              <p className="mt-3 text-lg font-semibold text-slate-900">{title}</p>
              <p className="mt-2 text-sm text-slate-600">{text}</p>
            </Card>
          ))}
        </div>
        <div className="mt-8 flex justify-center">
          <Button asChild className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]">
            <Link href="/generate">Start Generating Free →</Link>
          </Button>
        </div>
      </section>

      <section className="border-y border-orange-100 bg-[linear-gradient(180deg,#FFF8F1_0%,#FFFFFF_100%)]">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[#E8690A]">Beyond Text — We Build Any Dataset</p>
          <div className="mt-3 max-w-3xl">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-[#0F172A]">Need a Custom Dataset? We Build It For You</h2>
            <p className="mt-4 text-lg text-slate-600">Not just text. Any data. Any domain. Any format.</p>
          </div>

          <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              {
                icon: "🖼️",
                title: "Computer Vision",
                description: "Object detection, image classification, segmentation labels for any domain",
                examples: "doors, windows, vehicles, medical imaging",
              },
              {
                icon: "🎙️",
                title: "Audio & Speech",
                description: "Transcription, speaker identification, emotion detection in Indian languages",
                examples: "call center data, voice commands",
              },
              {
                icon: "📄",
                title: "Document Intelligence",
                description: "Invoice parsing, legal document classification, form field extraction",
                examples: "GST invoices, court documents, forms",
              },
              {
                icon: "🏥",
                title: "Medical & Healthcare",
                description: "Medical image labeling, clinical note classification, drug interaction datasets",
                examples: "X-ray labels, prescription data",
              },
              {
                icon: "🌾",
                title: "Agriculture",
                description: "Crop disease detection, yield prediction, soil classification datasets",
                examples: "plant disease images, satellite data",
              },
              {
                icon: "💬",
                title: "Indian Languages",
                description: "Sentiment, topic, NER in Hindi, Gujarati, Marathi, Tamil, English — automated",
                examples: "app reviews, social media, news",
              },
            ].map((item) => (
              <Card key={item.title} className="h-full border-orange-100 bg-white p-5 shadow-sm">
                <p className="text-3xl">{item.icon}</p>
                <p className="mt-4 text-lg font-semibold text-slate-900">{item.title}</p>
                <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
                <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-[#E8690A]">Examples</p>
                <p className="mt-1 text-sm text-slate-700">{item.examples}</p>
              </Card>
            ))}
          </div>

          <div className="mt-10 flex flex-col items-start gap-4">
            <Button asChild className="w-full sm:w-auto bg-[#E8690A] text-white hover:bg-[#d45e07]">
              <Link href="/custom-dataset">Request Custom Dataset →</Link>
            </Button>
            <p className="text-sm text-slate-600">Trusted by researchers and AI teams across India</p>
          </div>
        </div>
      </section>

      <section id="languages" className="border-y border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-[#0F172A]">Supported Languages</h2>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {languages.map((language) => (
              <Card key={language.name} className="border-slate-200 p-5">
                <p className="text-2xl">{language.flag}</p>
                <p className="mt-3 text-xl font-semibold text-slate-900">{language.name}</p>
                <p className="text-sm text-slate-600">Script: {language.script}</p>
                <p className="mt-4 rounded-lg bg-white p-3 text-sm text-slate-700">{language.sample}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-8 text-sm text-slate-600 sm:px-6 lg:px-8">
        <p>Built with ❤️ for Indian AI</p>
        <div className="flex gap-4">
          <Link href="/docs" className="hover:text-[#E8690A]">Docs</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-[#E8690A]">GitHub</a>
        </div>
      </footer>
    </main>
  );
}
