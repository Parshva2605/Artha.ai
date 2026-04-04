type JobPageProps = { params: { id: string } };

export default function JobPage({ params }: JobPageProps) {
  return <main className="mx-auto max-w-4xl px-6 py-12">Job progress for {params.id} (Phase 9).</main>;
}
