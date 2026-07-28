# Context Checkpoint

**Date:** 2026-07-28
**Note:** Sample checkpoint created while building the `/checkpoint` command. Topic: connecting Claude to the NiCE WFM DocuHub (MindTouch) and building a connector/skill.

---

## Plans made

- **Goal:** Build a skill that uses the NiCE WFM DocuHub (ACD Integrations docs) as source material, and possibly a **connector (MCP server)** so Claude can read the hub on demand.
- **Connector design (proposed):** A small **MCP server** wrapping the MindTouch / CXone Expert REST API (`/@api/deki/`), exposing tools:
  - `search_docs(query)` — full-text search across the hub
  - `get_page(path or id)` — fetch a page as markdown
  - `list_pages(section)` — browse the tree (e.g. all of `ACD_Integrations`)
- **Build path:** Use the `mcp-builder` skill to scaffold the server. It can be written here, but must **run on the user's laptop** (Claude Desktop / local Claude Code) where the hub is network-reachable.

## Decisions & rationale

- **Cannot browse DocuHub from this session.** Confirmed by test, not assumption: web fetch → 403; headless Chromium → tunnel fail; proxy CONNECT → `403 policy denial` for `wem-dochub.mindtouch.us:443`. The environment network policy hard-blocks the host.
- **Connector must run client-side (user's machine), not in this sandbox** — because of the network block above. This is also how MCP connectors normally run.
- **Fallback if no API access:** export the docs (PDF/HTML/copy-paste) and build the skill from those files. Rejected relying on this session's browser because the network policy makes it impossible.

## Risks & mitigations

- **Risk: Network policy blocks the hub in this cloud session.** → Mitigation: run the connector locally on the NiCE network/VPN; use export-to-file for anything done in this session.
- **Risk: No programmatic auth (SSO-only).** MindTouch needs an API token (key+secret, HMAC) for a clean connector. → Mitigation: get an API token from the DocuHub admin; fallback is a browser session cookie (fragile, expires) or doc export.
- **Risk: Secrets leakage.** → Mitigation: never store tokens in repo files or checkpoints; keep them in local env/config on the user's machine.

## Next steps

1. **User:** confirm whether a **MindTouch API key** is obtainable, or only **SSO login**. (Determines the auth code.)
2. **User:** confirm the connector will run **locally** (recommended).
3. **Claude:** once auth type is known, scaffold the MCP server (search/get/list tools) via `mcp-builder`; if unknown, build it to support both auth modes.
4. **Either path:** if API access isn't available, user exports ACD Integrations docs and Claude builds the skill from the files.

## Working context

- **Live task:** Just built the `/checkpoint` custom command at `.claude/commands/checkpoint.md`; this file is the demo output.
- **Key artifacts:**
  - Target URL: `https://wem-dochub.mindtouch.us/Workforce_Management/Integrations/ACD_Integrations`
  - Platform = MindTouch (a.k.a. NiCE CXone Expert); API base `/@api/deki/`.
  - Branch: `claude/acd-integrations-docs-czt3is`.
  - Environment proxy blocks `mindtouch.us` (403 on CONNECT).
- **Open questions awaiting user:** auth type (API token vs SSO) and runtime location (laptop vs hosted).
