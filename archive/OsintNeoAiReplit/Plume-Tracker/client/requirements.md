## Packages
leaflet | Core mapping library
react-leaflet | React wrapper for Leaflet maps
@types/leaflet | TypeScript definitions for Leaflet
react-hook-form | Form state management
@hookform/resolvers | Form validation resolvers for Zod

## Notes
Tailwind Config - extend fontFamily:
fontFamily: {
  display: ["var(--font-display)"],
  body: ["var(--font-body)"],
}
Requires leaflet.css which is imported in index.css.
Custom icons are used for Leaflet markers to avoid default webpack asset path issues.
