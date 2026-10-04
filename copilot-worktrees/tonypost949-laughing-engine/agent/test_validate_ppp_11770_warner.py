#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ppp_data" / "ppp_11770_warner.csv"
SCRIPT = ROOT / "agent" / "validate_ppp_11770_warner.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


class FixedPppValidationTests(unittest.TestCase):
    def test_preserves_fixed_source_and_emits_validation_only_manifest(self) -> None:
        before = sha256(SOURCE)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ppp_validation.json"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                capture_output=True,
                check=True,
                text=True,
            )
            result = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(sha256(SOURCE), before)
        self.assertEqual(result["status"], "validation_only")
        self.assertEqual(result["input"]["path"], "ppp_data/ppp_11770_warner.csv")
        self.assertEqual(result["input"]["sha256"], before)
        self.assertEqual(result["input"]["row_count"], 18)
        self.assertIn('"tool": "validate_ppp_11770_warner"', completed.stdout)
        self.assertIn("does not establish fraud", result["disclaimer"])


if __name__ == "__main__":
    unittest.main()
