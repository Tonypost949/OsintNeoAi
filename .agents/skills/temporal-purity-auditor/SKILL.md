---
name: temporal-purity-auditor
description: Automatically segregates modern survey records, filters post-1949 structures, and corrects State Plane Zone VI mathematical projection offsets for all historical archival dossiers.
---

# Temporal & Title Purity Auditor

This repeating tool executes automatically during any pre-1960 historical archival compilation to ensure data purity without requiring user input.

## Automated Execution Directives:
1. **Modern Survey Segregation:** Automatically detect and separate any modern (post-1960) survey records, placing them in an isolated "Modern Addendum" section.
2. **Post-1949 Structure Filtering:** Strip or flag any structures built after 1949 to ensure pure historical baselines.
3. **State Plane Zone VI Correction:** Automatically apply mathematical projection offset corrections for all California State Plane Zone VI cadastral data extracted from Orange County plats.
4. **Zero Human Prompting:** Execute these checks silently and automatically on all dossier data prior to final output.

## Trigger Command
Type `/temporal-purity-auditor` to force an immediate audit pass on any active dossier, even outside a pre-1960 compilation. Under `always_on` mode the audit runs automatically with no command required.

## Output Schema (JSON)
Every audit emits `purity_audit.json` alongside the dossier using this schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TemporalPurityAudit",
  "type": "object",
  "required": ["audit_timestamp", "dossier_id", "modern_addendum", "post_1949_flags", "zone_vi_corrections", "verdict"],
  "properties": {
    "audit_timestamp": { "type": "string", "format": "date-time" },
    "dossier_id": { "type": "string" },
    "modern_addendum": {
      "type": "object",
      "description": "Segment 1: post-1960 survey records segregated from main body",
      "required": ["count", "records"],
      "properties": {
        "count": { "type": "integer", "minimum": 0 },
        "records": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["record_id", "survey_date", "source", "reason"],
            "properties": {
              "record_id": { "type": "string" },
              "survey_date": { "type": "string", "format": "date" },
              "source": { "type": "string" },
              "reason": { "const": "post_1960_survey" }
            }
          }
        }
      }
    },
    "post_1949_flags": {
      "type": "object",
      "description": "Segment 2: structures built/recorded after 1949",
      "required": ["count", "structures"],
      "properties": {
        "count": { "type": "integer", "minimum": 0 },
        "structures": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["parcel_id", "built_year", "action", "reason"],
            "properties": {
              "parcel_id": { "type": "string" },
              "built_year": { "type": "integer", "minimum": 1950 },
              "action": { "enum": ["stripped", "flagged"] },
              "reason": { "const": "post_1949_structure" }
            }
          }
        }
      }
    },
    "zone_vi_corrections": {
      "type": "object",
      "description": "Segment 3: CA State Plane Zone VI (EPSG:2227) projection offset corrections for Orange County plats",
      "required": ["count", "corrections"],
      "properties": {
        "count": { "type": "integer", "minimum": 0 },
        "corrections": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["plat_id", "original_easting", "original_northing", "corrected_easting", "corrected_northing", "offset_x_ft", "offset_y_ft"],
            "properties": {
              "plat_id": { "type": "string" },
              "original_easting": { "type": "number" },
              "original_northing": { "type": "number" },
              "corrected_easting": { "type": "number" },
              "corrected_northing": { "type": "number" },
              "offset_x_ft": { "type": "number" },
              "offset_y_ft": { "type": "number" },
              "grid_system": { "const": "CA_State_Plane_Zone_VI_ft_US" },
              "datum": { "const": "NAD83" }
            }
          }
        }
      }
    },
    "verdict": {
      "type": "string",
      "enum": ["PURE", "PURE_WITH_ADDENDUM", "CONTAMINATED"]
    }
  }
}
```

### Field Rules
- `verdict = PURE` — no modern surveys, no post-1949 structures, no uncorrected Zone VI coordinates.
- `verdict = PURE_WITH_ADDENDUM` — all contaminants successfully segregated/flagged/corrected; main body is clean.
- `verdict = CONTAMINATED` — any contaminant remains unhandled in the main body, **or** the audit strips every record (empty historical baseline = failed compilation); script exits with code 1 and final output must be blocked pending a re-run.
- Script `Invoke-TemporalPurityAudit.ps1` implements this schema; offsets load from `zone_vi_offsets.json` (US ft, EPSG:2227).
- All coordinates in feet (US survey feet), EPSG:2227, NAD83. Correction = target_zone_origin offset applied mathematically, never by hand-editing plat values.
