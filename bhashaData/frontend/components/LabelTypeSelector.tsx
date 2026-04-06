import type { LabelType } from "../lib/types";

type LabelTypeSelectorProps = {
  selected: LabelType;
  onChange: (value: LabelType) => void;
};

const options: Array<{ value: LabelType; title: string; example: string }> = [
  { value: "sentiment", title: "Sentiment", example: "positive / negative / neutral" },
  { value: "topic", title: "Topic Classification", example: "politics / sports / entertainment..." },
  { value: "ner", title: "NER", example: "PERSON / LOCATION / ORGANIZATION..." },
  { value: "all", title: "All Types", example: "all of the above" },
];

export default function LabelTypeSelector({ selected, onChange }: LabelTypeSelectorProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={`rounded-xl border p-4 text-left ${
            selected === option.value ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
          }`}
        >
          <p className="font-semibold text-slate-900">{option.title}</p>
          <p className="mt-1 text-sm text-slate-600">{option.example}</p>
        </button>
      ))}
    </div>
  );
}
