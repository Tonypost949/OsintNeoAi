# Claim Verification Gate

OSINTNeoAI must distinguish collected evidence from AI-generated interpretation.

## Non-negotiable rule

No evidence = no verified fact.

AI output is an analysis artifact, not primary evidence.

## Workflow

1. Ingest the original source.
2. Preserve provenance and a SHA-256 hash when bytes are available.
3. Extract a candidate claim.
4. Attach exact evidence supporting or contradicting the claim.
5. Adjudicate the claim.
6. Keep conflicting evidence as UNRESOLVED.
7. Present as verified fact only when SUPPORTED and explicitly human-reviewed.
8. Keep ALLEGATION and HYPOTHESIS separate from factual findings.
9. Never infer causation from correlation.
10. Never manufacture a quotation, page, source, date, case number, or document.

## Important distinction

A document can establish that a contaminant was detected. That does not by itself establish exposure, injury, disease, or causation. Those are separate claims requiring their own evidence.