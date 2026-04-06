import { getDownloadUrl } from "../lib/api";
import { FORMAT_LABELS } from "../lib/types";
import type { ExportFormat } from "../lib/types";
import { Button } from "./ui/button";

type DownloadCardProps = {
  jobId: string;
  formats: ExportFormat[];
};

export default function DownloadCard({ jobId, formats }: DownloadCardProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {formats.map((format) => (
        <Button
          key={format}
          asChild
          className="justify-start bg-[#0F172A] text-white hover:bg-[#111f3c]"
        >
          <a href={getDownloadUrl(jobId, format)} target="_blank" rel="noreferrer">
            {FORMAT_LABELS[format]}
          </a>
        </Button>
      ))}
    </div>
  );
}
