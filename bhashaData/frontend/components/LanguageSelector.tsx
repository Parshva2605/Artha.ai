import type { Language } from "../lib/types";
import { LANGUAGE_FLAGS, LANGUAGE_LABELS } from "../lib/types";

type LanguageSelectorProps = {
  selected: Language[];
  onChange: (languages: Language[]) => void;
};

const scripts: Record<Language, string> = {
  en: "Latin",
  hi: "Devanagari",
  gu: "Gujarati",
  mr: "Devanagari",
  ta: "Tamil",
};

export default function LanguageSelector({ selected, onChange }: LanguageSelectorProps) {
  const toggle = (language: Language) => {
    const exists = selected.includes(language);
    const next = exists ? selected.filter((item) => item !== language) : [...selected, language];
    onChange(next);
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {(["en", "hi", "gu", "mr", "ta"] as Language[]).map((language) => {
        const isSelected = selected.includes(language);
        const checkboxId = `lang-selector-${language}`;
        return (
          <label
            key={language}
            htmlFor={checkboxId}
            className={`block cursor-pointer rounded-xl border p-4 text-left ${
              isSelected ? "border-[#E8690A] ring-2 ring-[#E8690A]/20" : "border-slate-200"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-base font-semibold">{LANGUAGE_FLAGS[language]} {LANGUAGE_LABELS[language]}</p>
                <p className="text-sm text-slate-600">Script: {scripts[language]}</p>
              </div>
              <input
                id={checkboxId}
                type="checkbox"
                checked={isSelected}
                onChange={() => toggle(language)}
                className="h-4 w-4 accent-[#E8690A]"
              />
            </div>
          </label>
        );
      })}
    </div>
  );
}
