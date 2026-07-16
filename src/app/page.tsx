"use client";

import { useEffect, useState } from "react";
import { Prd, emptyPrd, STORAGE_KEY } from "@/lib/types";
import { prdToMarkdown } from "@/lib/prd";
import PrdForm from "@/components/PrdForm";
import PrdPreview from "@/components/PrdPreview";

type SaveState = "idle" | "saved";

export default function Home() {
  const [prd, setPrd] = useState<Prd>(emptyPrd);
  const [isEditing, setIsEditing] = useState(true);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [loaded, setLoaded] = useState(false);

  // Load any previously saved PRD from localStorage on mount.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<Prd>;
        setPrd({ ...emptyPrd, ...parsed });
        setIsEditing(false);
      }
    } catch {
      // Ignore malformed storage and start fresh.
    }
    setLoaded(true);
  }, []);

  const handleChange = (next: Prd) => {
    setPrd(next);
    setSaveState("idle");
  };

  const handleSave = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prd));
    setSaveState("saved");
    setIsEditing(false);
  };

  const handleCopyMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(prdToMarkdown(prd));
    } catch {
      // Clipboard may be unavailable; silently ignore.
    }
  };

  const handleReset = () => {
    if (!confirm("Clear this PRD and start over? This cannot be undone.")) {
      return;
    }
    localStorage.removeItem(STORAGE_KEY);
    setPrd(emptyPrd);
    setIsEditing(true);
    setSaveState("idle");
  };

  if (!loaded) {
    return null;
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">PRD Builder</h1>
          <p className="text-sm text-slate-500">
            Draft a clean product requirements document in minutes.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {saveState === "saved" && (
            <span className="text-sm font-medium text-green-600">
              Saved ✓
            </span>
          )}
          <button
            type="button"
            onClick={() => setIsEditing((v) => !v)}
            className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            {isEditing ? "Hide editor" : "Edit"}
          </button>
          <button
            type="button"
            onClick={handleCopyMarkdown}
            className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Copy Markdown
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
          >
            Save
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {isEditing && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Details</h2>
              <button
                type="button"
                onClick={handleReset}
                className="text-sm font-medium text-slate-400 hover:text-red-600"
              >
                Reset
              </button>
            </div>
            <PrdForm prd={prd} onChange={handleChange} />
          </div>
        )}

        <div
          className={`rounded-xl border border-slate-200 bg-white p-6 shadow-sm ${
            isEditing ? "" : "lg:col-span-2"
          }`}
        >
          <PrdPreview prd={prd} />
        </div>
      </div>
    </main>
  );
}
