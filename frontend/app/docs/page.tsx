import { Card } from "../../components/ui/card";

const languageRows = [
  ["English", "en", "Latin", "Reddit, YouTube, Play Store, News"],
  ["Hindi", "hi", "Devanagari", "Reddit, YouTube, Play Store, News"],
  ["Gujarati", "gu", "Gujarati", "Reddit, YouTube, Play Store, News"],
  ["Marathi", "mr", "Devanagari", "Reddit, YouTube, Play Store, News"],
  ["Tamil", "ta", "Tamil", "Reddit, YouTube, Play Store, News"],
];

const labelRows = [
  ["sentiment", "Classifies polarity", "positive / negative / neutral"],
  ["topic", "Classifies theme", "politics / sports / entertainment"],
  ["ner", "Classifies entity type", "PERSON / LOCATION / ORGANIZATION"],
  ["all", "Runs all labelers", "sentiment + topic + ner"],
];

const exportRows = [
  ["CSV", "Analytics and spreadsheet workflows", "UTF-8 SIG for Excel compatibility"],
  ["JSON", "APIs and data interchange", "Indented and Unicode-safe"],
  ["Excel", "Business reporting", "Includes Dataset and Quality_Info sheets"],
  ["Parquet", "ML pipelines and lakehouses", "Strict numeric/boolean dtypes"],
  ["HuggingFace", "Model training teams", "Saved as Dataset folder with Arrow data"],
];

const schemaRows = [
  ["id", "int64", "Sequential row id"],
  ["text_original", "string", "Raw source text"],
  ["text_clean", "string", "Normalized text for labeling"],
  ["language", "string", "Language code"],
  ["language_name", "string", "Human language name"],
  ["script", "string", "Writing script"],
  ["domain", "string", "Selected domain"],
  ["source", "string", "Source provider"],
  ["source_url", "string | null", "Direct content URL"],
  ["source_subreddit", "string | null", "Subreddit name if applicable"],
  ["label_sentiment", "string | null", "Sentiment label"],
  ["label_topic", "string | null", "Topic label"],
  ["label_ner", "string | null", "NER label"],
  ["confidence", "float64", "Label confidence"],
  ["confidence_reason", "string", "Model reasoning summary"],
  ["llm_used", "string", "Label provider"],
  ["needs_review", "boolean", "Manual review flag"],
  ["app_id", "string | null", "Play Store app id"],
  ["star_rating", "int | null", "App rating value"],
  ["rating_hint", "string | null", "Rating context"],
  ["created_at", "ISO datetime", "Export creation timestamp"],
  ["job_id", "string", "Dataset job id"],
];

const apiRows = [
  ["POST", "/api/generate-dataset", "Submit dataset request and get job id", '{"job_id":"...","estimated_minutes":4,"message":"Dataset generation queued successfully"}'],
  ["GET", "/api/job-status/{job_id}", "Fetch live progress for a job", '{"status":"labeling","progress_percent":62,...}'],
  ["GET", "/api/quality-report/{job_id}", "Get final quality report", '{"overall_quality_score":90.1,...}'],
  ["GET", "/api/download/{job_id}/{format}", "Download generated export file", 'Binary file response'],
  ["GET", "/api/health", "Service health and dependency checks", '{"status":"ok","version":"1.0.0",...}'],
];

function Table({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200">
      <table className="w-full min-w-[680px] text-left text-sm">
        <thead className="bg-slate-50 text-slate-700">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-3 py-3 font-semibold">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${row[0]}-${index}`} className="border-t border-slate-100">
              {row.map((cell) => (
                <td key={cell} className="px-3 py-3 align-top text-slate-700">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function DocsPage() {
  return (
    <main className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
      <h1 className="text-2xl sm:text-3xl font-bold text-[#0F172A]">Artha AI Documentation</h1>
      <p className="mt-2 text-slate-600">Everything you need to run multilingual dataset generation end to end.</p>

      <div className="mt-8 space-y-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold">1. What is Artha AI</h2>
          <p className="mt-3 text-slate-700">
            Artha AI is a multilingual dataset generation platform that collects, cleans, labels, quality-checks, and exports
            training-ready data across Indian and English languages for modern ML teams.
          </p>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">2. How It Works</h2>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-slate-700">
            <li><code>scrape</code>: source collection across configured connectors.</li>
            <li><code>clean</code>: language filtering, normalization, deduplication.</li>
            <li><code>label</code>: LLM-backed annotation by selected label type.</li>
            <li><code>quality_check</code>: confidence scoring and distribution checks.</li>
            <li><code>merge</code>: per-language outputs combined into unified dataset.</li>
            <li><code>export</code>: parallel export to requested formats + metadata.</li>
          </ol>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">3. Supported Languages</h2>
          <Table headers={["Language", "Code", "Script", "Sources"]} rows={languageRows} />
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">4. Label Types</h2>
          <Table headers={["Type", "Description", "Example Labels"]} rows={labelRows} />
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">5. Export Formats</h2>
          <Table headers={["Format", "Best For", "Notes"]} rows={exportRows} />
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">6. Data Schema</h2>
          <Table headers={["Column", "Type", "Description"]} rows={schemaRows} />
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">7. Quality Scoring</h2>
          <p className="mt-3 text-slate-700">Quality is derived from labeling confidence:</p>
          <div className="mt-2 overflow-x-auto rounded-md bg-slate-100 p-3">
            <p className="font-mono text-xs sm:text-sm text-slate-800">quality_score = average(confidence) * 100</p>
          </div>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-slate-700">
            <li>&gt;= 90: Excellent</li>
            <li>80-89: Good</li>
            <li>70-79: Acceptable</li>
            <li>&lt; 70: Review recommended</li>
          </ul>
          <p className="mt-3 text-slate-700">
            English acts as a benchmark language when included, helping compare relative quality between language outputs.
          </p>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold">8. API Reference</h2>
          <Table headers={["Method", "Path", "Description", "Example Response"]} rows={apiRows} />
        </Card>
      </div>
    </main>
  );
}
