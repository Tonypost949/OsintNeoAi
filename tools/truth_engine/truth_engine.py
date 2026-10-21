"""
The Trinity: Foundational Engine for Truth & Accuracy
=====================================================
Implements The Trinity's Three-Gate Fact-Check Pipeline from the AI Laws.

Source: User theory, session https://share.gemini.google/KAI8NsC4Pk8j (Oct 20-21, 2026)
Integrated: 2026-10-21

Gate 1 — Physics/Reality Check (Hard Constraints)
Gate 2 — Probabilistic Weighting (Stochastic Likelihood)
Gate 3 — Baseline & Frequency Analysis (Reversion to Mean)

Usage:
    from truth_engine import TruthEngine, DataPoint
    engine = TruthEngine()
    result = engine.validate(data_point)
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional


class GateResult(Enum):
    PASS = "PASS"
    FAIL_REJECT = "FAIL_REJECT"           # Gate 1: violates physics → quarantine
    FAIL_FLAG = "FAIL_FLAG"               # Gate 2: low confidence → flag for corroboration
    FAIL_ESCALATE = "FAIL_ESCALATE"       # Gate 3: outlier → high-scrutiny review
    PENDING = "PENDING"


class Verdict(Enum):
    VALIDATED = "VALIDATED"
    QUARANTINED = "QUARANTINED"
    FLAGGED_FOR_CORROBORATION = "FLAGGED_FOR_CORROBORATION"
    ESCALATED_HIGH_SCRUTINY = "ESCALATED_HIGH_SCRUTINY"


@dataclass
class DataPoint:
    """A piece of data/intelligence/evidence to be validated through the Truth Engine."""
    content: str
    source: str
    source_type: str = "unknown"          # official, witness, digital, sensor, etc.
    timestamp: Optional[str] = None
    geolocation: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    # Gate 1 inputs
    physical_constraints_met: Optional[bool] = None        # Does it obey physics/reality?
    spatial_plausibility: Optional[float] = None           # 0.0–1.0
    temporal_plausibility: Optional[float] = None          # 0.0–1.0

    # Gate 2 inputs
    source_reliability_score: Optional[float] = None       # 0.0–1.0
    cross_corroboration_count: int = 0
    confidence_interval: Optional[float] = None            # 0.0–1.0

    # Gate 3 inputs
    historical_baseline_deviation: Optional[float] = None  # std devs from mean
    frequency_alignment: Optional[float] = None            # 0.0–1.0 (1.0 = matches cycle)
    is_known_outlier: bool = False


@dataclass
class ValidationResult:
    """Result of running a DataPoint through the Three-Gate Fact-Check Pipeline."""
    data_point_content: str
    source: str
    gate_1_result: GateResult = GateResult.PENDING
    gate_1_reason: str = ""
    gate_2_result: GateResult = GateResult.PENDING
    gate_2_reason: str = ""
    gate_3_result: GateResult = GateResult.PENDING
    gate_3_reason: str = ""
    final_verdict: Verdict = Verdict.QUARANTINED
    confidence_score: float = 0.0
    transparency_log: list = field(default_factory=list)
    validated_at: str = field(default_factory=lambda: datetime.now(tz=__import__('datetime').timezone.utc).isoformat())

    def to_dict(self):
        d = asdict(self)
        d["gate_1_result"] = self.gate_1_result.value
        d["gate_2_result"] = self.gate_2_result.value
        d["gate_3_result"] = self.gate_3_result.value
        d["final_verdict"] = self.final_verdict.value
        return d


class TruthEngine:
    """
    The Trinity — Three-Gate Fact-Check Pipeline.

    Separates Truth & Accuracy (what is real) from Transparency (how decided).
    """

    # Configurable thresholds
    GATE2_CONFIDENCE_THRESHOLD = 0.5      # Below this → flag for corroboration
    GATE3_DEVIATION_THRESHOLD = 2.5       # Std devs from mean to trigger outlier escalation

    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(
            "C:\\Amd949609_Antigravity_v1", "tools", "truth_engine", "logs"
        )
        os.makedirs(self.log_dir, exist_ok=True)

    def validate(self, dp: DataPoint) -> ValidationResult:
        """Run a DataPoint through all three gates sequentially."""
        result = ValidationResult(
            data_point_content=dp.content,
            source=dp.source,
        )

        # ── Gate 1: Physics / Reality Check ──
        result = self._gate_1_physics(dp, result)
        if result.gate_1_result == GateResult.FAIL_REJECT:
            result.final_verdict = Verdict.QUARANTINED
            result.transparency_log.append(
                f"[GATE 1 FAIL] Data quarantined — violates physical/reality constraints. Reason: {result.gate_1_reason}"
            )
            self._log_result(result)
            return result

        # ── Gate 2: Probabilistic Weighting ──
        result = self._gate_2_probability(dp, result)
        if result.gate_2_result == GateResult.FAIL_FLAG:
            result.final_verdict = Verdict.FLAGGED_FOR_CORROBORATION
            result.transparency_log.append(
                f"[GATE 2 FLAG] Insufficient confidence — flagged for secondary corroboration. Reason: {result.gate_2_reason}"
            )
            self._log_result(result)
            return result

        # ── Gate 3: Baseline & Frequency Analysis ──
        result = self._gate_3_baseline(dp, result)
        if result.gate_3_result == GateResult.FAIL_ESCALATE:
            result.final_verdict = Verdict.ESCALATED_HIGH_SCRUTINY
            result.transparency_log.append(
                f"[GATE 3 ESCALATE] Outlier detected — escalated to high-scrutiny review. Reason: {result.gate_3_reason}"
            )
            self._log_result(result)
            return result

        # All gates passed
        result.final_verdict = Verdict.VALIDATED
        result.transparency_log.append("[ALL GATES PASSED] Data point validated through The Trinity.")
        self._log_result(result)
        return result

    def _gate_1_physics(self, dp: DataPoint, result: ValidationResult) -> ValidationResult:
        """Gate 1: Physical / Physics — Hard Constraints."""
        reasons = []

        if dp.physical_constraints_met is False:
            result.gate_1_result = GateResult.FAIL_REJECT
            result.gate_1_reason = "Explicit physical constraint violation flagged."
            result.transparency_log.append("[GATE 1] Physical constraint violation detected.")
            return result

        if dp.spatial_plausibility is not None and dp.spatial_plausibility < 0.2:
            reasons.append(f"Spatial plausibility critically low: {dp.spatial_plausibility:.2f}")

        if dp.temporal_plausibility is not None and dp.temporal_plausibility < 0.2:
            reasons.append(f"Temporal plausibility critically low: {dp.temporal_plausibility:.2f}")

        if reasons:
            result.gate_1_result = GateResult.FAIL_REJECT
            result.gate_1_reason = "; ".join(reasons)
        else:
            result.gate_1_result = GateResult.PASS
            spatial = dp.spatial_plausibility if dp.spatial_plausibility is not None else 1.0
            temporal = dp.temporal_plausibility if dp.temporal_plausibility is not None else 1.0
            result.transparency_log.append(
                f"[GATE 1 PASS] Physics check OK. Spatial: {spatial:.2f}, Temporal: {temporal:.2f}"
            )

        return result

    def _gate_2_probability(self, dp: DataPoint, result: ValidationResult) -> ValidationResult:
        """Gate 2: Probability & Odds — Stochastic Likelihood."""
        # Compute composite confidence
        scores = []
        if dp.source_reliability_score is not None:
            scores.append(dp.source_reliability_score)
        if dp.confidence_interval is not None:
            scores.append(dp.confidence_interval)

        # Cross-corroboration bonus
        corroboration_bonus = min(dp.cross_corroboration_count * 0.1, 0.3)

        if scores:
            base_confidence = sum(scores) / len(scores)
            composite = min(base_confidence + corroboration_bonus, 1.0)
        else:
            # No probabilistic data provided — default pass with note
            composite = 0.5 + corroboration_bonus
            result.transparency_log.append(
                "[GATE 2] No explicit confidence scores provided; using baseline + corroboration."
            )

        result.confidence_score = composite

        if composite < self.GATE2_CONFIDENCE_THRESHOLD:
            result.gate_2_result = GateResult.FAIL_FLAG
            result.gate_2_reason = (
                f"Composite confidence {composite:.2f} below threshold {self.GATE2_CONFIDENCE_THRESHOLD}. "
                f"Source reliability: {dp.source_reliability_score}, "
                f"Cross-corroboration: {dp.cross_corroboration_count}"
            )
        else:
            result.gate_2_result = GateResult.PASS
            result.transparency_log.append(
                f"[GATE 2 PASS] Confidence: {composite:.2f} (threshold: {self.GATE2_CONFIDENCE_THRESHOLD}). "
                f"Corroborations: {dp.cross_corroboration_count}"
            )

        return result

    def _gate_3_baseline(self, dp: DataPoint, result: ValidationResult) -> ValidationResult:
        """Gate 3: Reversion to Mean, Frequency, Ebb & Flow — Cyclical Dynamics."""
        reasons = []

        if dp.is_known_outlier:
            reasons.append("Explicitly marked as known outlier.")

        if dp.historical_baseline_deviation is not None:
            if abs(dp.historical_baseline_deviation) > self.GATE3_DEVIATION_THRESHOLD:
                reasons.append(
                    f"Historical deviation {dp.historical_baseline_deviation:.2f} std devs "
                    f"exceeds threshold {self.GATE3_DEVIATION_THRESHOLD}"
                )

        if dp.frequency_alignment is not None and dp.frequency_alignment < 0.2:
            reasons.append(f"Frequency alignment critically low: {dp.frequency_alignment:.2f}")

        if reasons:
            result.gate_3_result = GateResult.FAIL_ESCALATE
            result.gate_3_reason = "; ".join(reasons)
        else:
            result.gate_3_result = GateResult.PASS
            deviation = dp.historical_baseline_deviation if dp.historical_baseline_deviation is not None else 0.0
            freq = dp.frequency_alignment if dp.frequency_alignment is not None else 1.0
            result.transparency_log.append(
                f"[GATE 3 PASS] Baseline check OK. Deviation: {deviation:.2f} std devs, "
                f"Frequency alignment: {freq:.2f}"
            )

        return result

    def _log_result(self, result: ValidationResult):
        """Write immutable transparency log (Accuracy ≠ Transparency — separate axis)."""
        ts = datetime.now(tz=__import__('datetime').timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        log_file = os.path.join(self.log_dir, f"validation_{ts}.json")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Non-blocking — transparency logging should never halt the engine


# ── Quick self-test ──
if __name__ == "__main__":
    engine = TruthEngine()

    # Example: Valid official record
    valid = DataPoint(
        content="Property deed recorded at OC Recorder Office, instrument #2021-000456789",
        source="Orange County Recorder",
        source_type="official",
        physical_constraints_met=True,
        spatial_plausibility=0.95,
        temporal_plausibility=0.99,
        source_reliability_score=0.95,
        cross_corroboration_count=3,
        confidence_interval=0.92,
        historical_baseline_deviation=0.3,
        frequency_alignment=0.88,
    )
    r = engine.validate(valid)
    print(f"[{r.final_verdict.value}] {r.data_point_content[:80]}")
    for log in r.transparency_log:
        print(f"  {log}")

    print()

    # Example: Physics violation
    impossible = DataPoint(
        content="Suspect was at location A and location B (50 miles apart) within 2 minutes",
        source="Digital metadata",
        source_type="digital",
        physical_constraints_met=False,
        spatial_plausibility=0.01,
        temporal_plausibility=0.01,
    )
    r = engine.validate(impossible)
    print(f"[{r.final_verdict.value}] {r.data_point_content[:80]}")
    for log in r.transparency_log:
        print(f"  {log}")

    print()

    # Example: Low confidence outlier
    sketchy = DataPoint(
        content="Anonymous tip: hidden offshore account in Cayman Islands",
        source="Anonymous",
        source_type="tip",
        physical_constraints_met=True,
        spatial_plausibility=0.7,
        temporal_plausibility=0.7,
        source_reliability_score=0.15,
        cross_corroboration_count=0,
        confidence_interval=0.1,
    )
    r = engine.validate(sketchy)
    print(f"[{r.final_verdict.value}] {r.data_point_content[:80]}")
    for log in r.transparency_log:
        print(f"  {log}")
