import { getDownloadUrl } from "../lib/api";
import { FORMAT_LABELS } from "../lib/types";
import type { ExportFormat } from "../lib/types";

type DownloadCardProps = {
  jobId: string;
  formats: ExportFormat[];
};

export default function DownloadCard({ jobId, formats }: DownloadCardProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {formats.map((format) => (
        <a
          key={format}
          href={getDownloadUrl(jobId, format)}
          target="_blank"
          rel="noopener noreferrer"
          download
        >
          <button
            type="button"
            className="inline-flex w-full items-center justify-start rounded-md bg-[#0F172A] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#111f3c]"
          >
            {FORMAT_LABELS[format]}
          </button>
        </a>
      ))}
    </div>
  );
}
