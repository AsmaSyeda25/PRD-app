import { Prd } from "./types";

/** Trim list entries and drop empty ones for display / export. */
export function cleanList(items: string[]): string[] {
  return items.map((i) => i.trim()).filter((i) => i.length > 0);
}

/** Render the PRD as Markdown, suitable for copy/paste or download. */
export function prdToMarkdown(prd: Prd): string {
  const title = prd.productName.trim() || "Untitled Product";
  const lines: string[] = [`# ${title} — Product Requirements Document`, ""];

  const section = (heading: string, body: string) => {
    lines.push(`## ${heading}`, "");
    lines.push(body.trim() ? body.trim() : "_Not provided yet._", "");
  };

  const listSection = (heading: string, items: string[]) => {
    const cleaned = cleanList(items);
    lines.push(`## ${heading}`, "");
    if (cleaned.length === 0) {
      lines.push("_Not provided yet._", "");
    } else {
      cleaned.forEach((item) => lines.push(`- ${item}`));
      lines.push("");
    }
  };

  section("Problem Statement", prd.problemStatement);
  section("Target Users", prd.targetUsers);
  listSection("Goals", prd.goals);
  listSection("Non-Goals", prd.nonGoals);
  listSection("Functional Requirements", prd.requirements);
  listSection("Success Metrics", prd.successMetrics);

  return lines.join("\n");
}
