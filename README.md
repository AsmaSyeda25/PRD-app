# PRD Builder

A minimal MVP web app that helps product managers draft a clean Product
Requirements Document. Built with **Next.js (App Router)**, **TypeScript**, and
**Tailwind CSS**.

## Features

- Capture the essentials of a PRD:
  - Product name
  - Problem statement
  - Target users
  - Goals and non-goals
  - Functional requirements
  - Success metrics
- Live, formatted **PRD preview** as you type
- **Edit** and **Save** your document — saved locally in the browser
  (`localStorage`), so it persists across reloads
- **Copy Markdown** to export the document anywhere

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

```bash
npm run build
npm start
```

## Project structure

```
src/
  app/
    layout.tsx      # Root layout + global styles
    page.tsx        # Main screen: form + preview, save/edit logic
    globals.css     # Tailwind entry point
  components/
    PrdForm.tsx     # The input form
    PrdPreview.tsx  # The rendered PRD preview
    ListField.tsx   # Reusable repeatable list input
  lib/
    types.ts        # Prd type + storage key
    prd.ts          # Markdown export + helpers
```

## Notes

This is an MVP. PRDs are stored in the browser only — there is no backend or
account system. Use **Copy Markdown** to move a document out of the app.
