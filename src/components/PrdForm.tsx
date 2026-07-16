"use client";

import { Prd } from "@/lib/types";
import ListField from "./ListField";

interface PrdFormProps {
  prd: Prd;
  onChange: (prd: Prd) => void;
}

export default function PrdForm({ prd, onChange }: PrdFormProps) {
  const set = <K extends keyof Prd>(key: K, value: Prd[K]) =>
    onChange({ ...prd, [key]: value });

  return (
    <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
      <div>
        <label className="mb-1.5 block text-sm font-medium text-slate-700">
          Product name
        </label>
        <input
          type="text"
          value={prd.productName}
          placeholder="e.g. Acme Analytics"
          onChange={(e) => set("productName", e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-medium text-slate-700">
          Problem statement
        </label>
        <textarea
          value={prd.problemStatement}
          placeholder="What problem are we solving and why does it matter?"
          rows={3}
          onChange={(e) => set("problemStatement", e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="mb-1.5 block text-sm font-medium text-slate-700">
          Target users
        </label>
        <textarea
          value={prd.targetUsers}
          placeholder="Who is this for? Describe the primary personas."
          rows={2}
          onChange={(e) => set("targetUsers", e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <ListField
        label="Goals"
        placeholder="A measurable outcome we want to achieve"
        items={prd.goals}
        onChange={(goals) => set("goals", goals)}
      />

      <ListField
        label="Non-Goals"
        placeholder="Something explicitly out of scope"
        items={prd.nonGoals}
        onChange={(nonGoals) => set("nonGoals", nonGoals)}
      />

      <ListField
        label="Functional requirements"
        placeholder="A capability the product must provide"
        items={prd.requirements}
        onChange={(requirements) => set("requirements", requirements)}
      />

      <ListField
        label="Success metrics"
        placeholder="How we'll measure success"
        items={prd.successMetrics}
        onChange={(successMetrics) => set("successMetrics", successMetrics)}
      />
    </form>
  );
}
