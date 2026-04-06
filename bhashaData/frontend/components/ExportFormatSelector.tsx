import type { ExportFormat } from "../lib/types";
import { FORMAT_LABELS } from "../lib/types";

type ExportFormatSelectorProps = {
  selected: ExportFormat[];
  onChange: (formats: ExportFormat[]) => void;
};

const descriptions: Record<ExportFormat, string> = {
  csv: "Spreadsheet-friendly tabular format",
  json: "Flexible API and app integration format",
  excel: "Business analysis workbook format",
  parquet: "Columnar format for ML data pipelines",
  huggingface: "Direct dataset folder for HF workflows",
};

export default function ExportFormatSelector({ selected, onChange }: ExportFormatSelectorProps) {
  const toggle = (format: ExportFormat) => {
    const exists = selected.includes(format);
    const next = exists ? selected.filter((item) => item !== format) : [...selected, format];
    onChange(next);
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {(["csv", "json", "excel", "parquet", "huggingface"] as ExportFormat[]).map((format) => {
        const isSelected = selected.includes(format);
        return (
          <button
            key={format}
            type="button"
            onClick={() => toggle(format)}
            className={`rounded-xl border p-4 text-left ${
              isSelected ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
            }`}
          >
            <p className="font-semibold text-slate-900">{FORMAT_LABELS[format]}</p>
            <p className="mt-1 text-sm text-slate-600">{descriptions[format]}</p>
          </button>
        );
      })}
    </div>
  );
}
