"use client";

import { Prd } from "@/lib/types";
import { cleanList } from "@/lib/prd";

interface PrdPreviewProps {
  prd: Prd;
}

function TextBlock({ heading, body }: { heading: string; body: string }) {
  return (
    <section className="mb-6">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-indigo-600">
        {heading}
      </h2>
      {body.trim() ? (
        <p className="whitespace-pre-line text-sm leading-relaxed text-slate-700">
          {body}
        </p>
      ) : (
        <p className="text-sm italic text-slate-400">Not provided yet.</p>
      )}
    </section>
  );
}

function ListBlock({ heading, items }: { heading: string; items: string[] }) {
  const cleaned = cleanList(items);
  return (
    <section className="mb-6">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-indigo-600">
        {heading}
      </h2>
      {cleaned.length > 0 ? (
        <ul className="list-disc space-y-1 pl-5 text-sm leading-relaxed text-slate-700">
          {cleaned.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="text-sm italic text-slate-400">Not provided yet.</p>
      )}
    </section>
  );
}

export default function PrdPreview({ prd }: PrdPreviewProps) {
  const title = prd.productName.trim() || "Untitled Product";

  return (
    <article>
      <header className="mb-6 border-b border-slate-200 pb-4">
        <p className="text-xs font-medium uppercase tracking-widest text-slate-400">
          Product Requirements Document
        </p>
        <h1 className="mt-1 text-2xl font-bold text-slate-900">{title}</h1>
      </header>

      <TextBlock heading="Problem Statement" body={prd.problemStatement} />
      <TextBlock heading="Target Users" body={prd.targetUsers} />
      <ListBlock heading="Goals" items={prd.goals} />
      <ListBlock heading="Non-Goals" items={prd.nonGoals} />
      <ListBlock heading="Functional Requirements" items={prd.requirements} />
      <ListBlock heading="Success Metrics" items={prd.successMetrics} />
    </article>
  );
}
