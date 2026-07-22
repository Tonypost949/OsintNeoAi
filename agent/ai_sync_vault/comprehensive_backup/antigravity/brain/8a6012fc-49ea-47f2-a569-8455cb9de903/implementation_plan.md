# Design & Visual Overhaul for OSINT Analyzer

To address the feedback on the user interface, we will perform a comprehensive design and styling upgrade. This plan moves the application to a premium, dark-themed dashboard featuring modern layouts, glowing elements, micro-animations, and glassmorphic designs.

## User Review Required

> [!IMPORTANT]
> The theme of the app will be set to **Dark Mode by default**, utilizing deep slate (`oklch(0.141 0.005 285.823)`) and midnight-blue backdrops, neon accents (indigo/violet/cyan), and clean sans-serif typography.

## Proposed Changes

We will modify the core layout files, the theme settings, and update the UI styling across key client pages.

---

### UI & Styling Updates

#### [MODIFY] [App.tsx](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/web/client/src/App.tsx)
- Set the default theme in `<ThemeProvider>` to `dark` to launch in dark mode immediately.

#### [MODIFY] [Home.tsx](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/web/client/src/pages/Home.tsx)
- Upgrade the layout of the homepage/dashboard:
  - Add deep slate gradient background (`bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950/20`).
  - Introduce glowing, frosted-glass card containers (`bg-slate-900/50 backdrop-blur-md border border-slate-800/80 shadow-2xl`).
  - Style dashboard headers, title text, and tabs with vibrant, interactive highlights (neon cyan and royal purple).
  - Add subtle pulse animations and transition states on upload areas and list elements.

#### [MODIFY] [Analysis.tsx](file:///c:/Users/HP/OneDrive/Documents/OsintNeoAi/web/client/src/pages/Analysis.tsx)
- Redesign the analysis detail and network graph dashboard layout:
  - Use high-contrast layout grids for displaying metadata.
  - Upgrade the visual cards containing network graphs and intelligence summaries with premium headers and glowing badges.

## Verification Plan

### Manual Verification
- Launch the server on `http://localhost:3000/`.
- Access and verify the visual rendering, ensuring the theme loads dark, text contrast is excellent, borders are glowing/sharp, and hover transitions are smooth.
