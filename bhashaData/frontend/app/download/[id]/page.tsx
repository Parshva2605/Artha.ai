type DownloadPageProps = { params: { id: string } };

export default function DownloadPage({ params }: DownloadPageProps) {
  return <main className="mx-auto max-w-4xl px-6 py-12">Downloads for {params.id} (Phase 9).</main>;
}
