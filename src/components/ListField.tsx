"use client";

interface ListFieldProps {
  label: string;
  placeholder: string;
  items: string[];
  onChange: (items: string[]) => void;
}

export default function ListField({
  label,
  placeholder,
  items,
  onChange,
}: ListFieldProps) {
  const update = (index: number, value: string) => {
    const next = [...items];
    next[index] = value;
    onChange(next);
  };

  const add = () => onChange([...items, ""]);

  const remove = (index: number) => {
    const next = items.filter((_, i) => i !== index);
    onChange(next.length > 0 ? next : [""]);
  };

  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
      </label>
      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <span className="w-5 shrink-0 text-right text-sm text-slate-400">
              {index + 1}.
            </span>
            <input
              type="text"
              value={item}
              placeholder={placeholder}
              onChange={(e) => update(index, e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              type="button"
              onClick={() => remove(index)}
              aria-label={`Remove ${label} item ${index + 1}`}
              className="shrink-0 rounded-md px-2 py-2 text-slate-400 hover:bg-slate-100 hover:text-red-600"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={add}
        className="mt-2 text-sm font-medium text-indigo-600 hover:text-indigo-800"
      >
        + Add {label.toLowerCase()}
      </button>
    </div>
  );
}
