import unittest
from processing.claim_verification import Claim, ClaimStatus, Evidence

class ClaimVerificationTests(unittest.TestCase):
    def test_no_evidence_cannot_be_verified(self):
        claim = Claim("c1", "A statement with no source.")
        self.assertEqual(claim.adjudicate(), ClaimStatus.UNSUPPORTED)
        self.assertFalse(claim.can_be_presented_as_fact())

    def test_support_requires_human_review(self):
        claim = Claim("c2", "The document says X.")
        claim.add_evidence(Evidence("e1", "Primary record", page=4, quote="X"))
        self.assertEqual(claim.adjudicate(), ClaimStatus.SUPPORTED)
        self.assertFalse(claim.can_be_presented_as_fact())
        claim.human_verified = True
        claim.reviewer = "human"
        self.assertTrue(claim.can_be_presented_as_fact())

    def test_conflict_is_unresolved(self):
        claim = Claim("c3", "Conflicting statement")
        claim.add_evidence(Evidence("e1", "Record A", supports=True))
        claim.add_evidence(Evidence("e2", "Record B", supports=False))
        self.assertEqual(claim.adjudicate(), ClaimStatus.UNRESOLVED)

    def test_only_contradiction_is_contradicted(self):
        claim = Claim("c4", "Statement contradicted by record")
        claim.add_evidence(Evidence("e1", "Record", supports=False))
        self.assertEqual(claim.adjudicate(), ClaimStatus.CONTRADICTED)

    def test_sha256_is_deterministic(self):
        digest = Evidence.hash_content(b"evidence")
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, Evidence.hash_content(b"evidence"))

if __name__ == "__main__":
    unittest.main()