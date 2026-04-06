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
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-2xl font-black tracking-tight text-[#E8690A]">Artha AI</p>
            <nav className="flex items-center gap-6 text-sm text-slate-200">
              <a href="#how-it-works" className="hover:text-white">How it works</a>
              <a href="#languages" className="hover:text-white">Languages</a>
              <Link href="/docs" className="hover:text-white">Docs</Link>
            </nav>
            <Button asChild className="bg-[#E8690A] text-white hover:bg-[#d45e07]">
              <Link href="/generate">Generate Dataset</Link>
            </Button>
          </header>

          <div className="relative mt-16 overflow-hidden rounded-3xl border border-slate-700 bg-[linear-gradient(135deg,#0F172A_0%,#111f3c_40%,#0b1220_100%)] px-6 py-16 sm:px-10">
            <div className="absolute -top-20 left-10 h-56 w-56 rounded-full bg-[#E8690A]/20 blur-3xl" />
            <div className="absolute bottom-0 right-0 h-48 w-48 rounded-full bg-white/10 blur-2xl" />
            <div className="relative max-w-3xl">
              <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">Give Meaning to Your Data</h1>
              <p className="mt-6 text-lg text-slate-200">
                Generate high-quality labeled datasets in Hindi, Gujarati, Marathi, Tamil and English in minutes
                not weeks.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild className="bg-[#E8690A] text-white hover:bg-[#d45e07]">
                  <Link href="/generate">
                    Start Generating <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" className="border-slate-500 bg-transparent text-white hover:bg-slate-800">
                  <Link href="/docs">
                    View Documentation <BookOpenText className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold tracking-tight text-[#0F172A]">How It Works</h2>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
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

      <section id="languages" className="border-y border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold tracking-tight text-[#0F172A]">Supported Languages</h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

      <footer className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-8 text-sm text-slate-600 sm:px-6 lg:px-8">
        <p>Built with ❤️ for Indian AI</p>
        <div className="flex gap-4">
          <Link href="/docs" className="hover:text-[#E8690A]">Docs</Link>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-[#E8690A]">GitHub</a>
        </div>
      </footer>
    </main>
  );
}
