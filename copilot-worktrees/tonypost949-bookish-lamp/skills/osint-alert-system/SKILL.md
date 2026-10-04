# OSINT Alert System

This skill helps design and improve OSINT alerting and anomaly detection systems. It is focused on building intelligence notifications, fraud detection rules, and AI-assisted alert triage for suspicious patterns.

## When to use this skill

- You want to extend your alert dispatcher or fraud alert generator.
- You need to detect anomalies across OSINT datasets.
- You want to add AI-driven scoring, prioritization, or alert enrichment.
- You are building event-based notifications from public records and intelligence feeds.

## Key workflow

1. Define alert sources and triggers.
   - Use structured datasets like `scored_data.csv`, `fraud_alerts.csv`, or `cloud_data.csv`.
   - Map triggers to changes, thresholds, or pattern matches.
2. Build detection logic.
   - Use rule-based filters, regex patterns, or statistical anomaly detection.
   - Add heuristics for fraud, corruption, or unusual link activity.
3. Score and prioritize alerts.
   - Apply severity scoring, confidence levels, and risk categories.
   - Use AI or ML models to rank alerts by likely impact.
4. Dispatch notifications.
   - Create email, SMS, or dashboard alerts via existing scripts.
   - Include context, evidence, and next-step actions.
5. Refine with feedback.
   - Tune thresholds based on false positives.
   - Add human review and alert escalation.

## Recommended techniques and tools

- `pandas` for dataset scoring and rule evaluation
- `scikit-learn` or `pyod` for anomaly detection models
- `langchain` or AI prompt-based scoring for alert enrichment
- `SMTP`, `Twilio`, or webhook dispatch for notifications
- `logging` and evidence tracking for auditability

## Practical OSINT examples

- Detect unusual keyword combinations in leaked documents.
- Flag spider graphs showing repeated connections between suspicious actors.
- Alert when a new public record appears for a high-risk entity.
- Generate fraud alerts from cloud asset misconfigurations and exposed data.

## Quality criteria

- Keep alert rules explainable and traceable.
- Include clear evidence and source links in every notification.
- Avoid too many low-value alerts by tuning sensitivity.
- Maintain data provenance for analyst review.

## Prompt examples

- "Help me extend my fraud alert generator with AI-based anomaly scoring."
- "What is the best way to dispatch OSINT alerts by email and SMS?"
- "Show me how to add a priority score column to my alert pipeline."
- "Guide me on building a rule-based detection engine for suspicious public records."
