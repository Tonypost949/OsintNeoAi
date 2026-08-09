"""
Unit Test Suite for Address and Entity Name Normalizers.
"""
import pytest
from src.core.normalizers import (
    normalize_address,
    normalize_entity_name,
    compute_soundex,
    compute_double_metaphone
)


class TestAddressNormalizer:

    def test_usps_suffix_standardization(self):
        result = normalize_address("123 Main Street", "Las Vegas", "NV", "89101")
        assert result.street == "123 MAIN ST"
        assert result.city == "LAS VEGAS"
        assert result.state == "NV"
        assert result.zip_code == "89101"
        assert "123 MAIN ST, LAS VEGAS, NV 89101" in result.normalized_str

    def test_directional_prefix_and_suffix(self):
        result = normalize_address("456 North Boulevard West", "Reno", "NV", "89501")
        assert result.street == "456 N BLVD W"

    def test_unit_and_suite_stripping(self):
        res1 = normalize_address("789 Broadway Avenue Suite 500", "Carson City", "NV", "89701")
        res2 = normalize_address("789 Broadway Avenue Apt 2B", "Carson City", "NV", "89701")
        assert res1.street == "789 BROADWAY AVE"
        assert res2.street == "789 BROADWAY AVE"
        assert res1.address_hash == res2.address_hash  # Same building hub hash!

    def test_unit_hash_equivalence_across_formats(self):
        """Fix 1 Verification: # 100, STE 100, #100 produce identical SHA256 address hashes."""
        r1 = normalize_address("123 MAIN ST # 100", "LAS VEGAS", "NV", "89101")
        r2 = normalize_address("123 MAIN ST STE 100", "LAS VEGAS", "NV", "89101")
        r3 = normalize_address("123 MAIN ST #100", "LAS VEGAS", "NV", "89101")
        r4 = normalize_address("123 MAIN ST SUITE 100", "LAS VEGAS", "NV", "89101")

        assert r1.street == "123 MAIN ST"
        assert r2.street == "123 MAIN ST"
        assert r3.street == "123 MAIN ST"
        assert r4.street == "123 MAIN ST"
        assert r1.address_hash == r2.address_hash == r3.address_hash == r4.address_hash

    def test_zip_code_padding_and_truncation(self):
        res_short = normalize_address("100 Park Ave", "Boston", "MA", "2108")
        assert res_short.zip_code == "02108"

        res_long = normalize_address("100 Park Ave", "Boston", "MA", "02108-1234")
        assert res_long.zip_code == "02108"

    def test_single_string_address_input(self):
        res = normalize_address("100 S. Virginia Str., Suite 10, Reno, NV 89501")
        assert res.street == "100 S VIRGINIA ST"
        assert res.city == "RENO"
        assert res.state == "NV"
        assert res.zip_code == "89501"
        assert len(res.address_hash) == 64

    def test_single_string_address_without_commas(self):
        """Fix 1 Verification: Single-line addresses without commas parse city, state, zip correctly."""
        res = normalize_address("100 S VIRGINIA ST SUITE 10 RENO NV 89501")
        assert res.street == "100 S VIRGINIA ST"
        assert res.city == "RENO"
        assert res.state == "NV"
        assert res.zip_code == "89501"

    def test_null_address_handling(self):
        """Fix 6 Verification: None inputs do not raise AttributeError."""
        res = normalize_address(None, None, None, None)
        assert res.street == ""
        assert res.city == ""
        assert res.state == ""
        assert res.zip_code == "00000"
        assert len(res.address_hash) == 64


class TestEntityNameNormalizer:

    def test_corporate_suffix_stripping(self):
        names = [
            "ACME ENTERPRISES LLC",
            "Acme Enterprises Inc.",
            "Acme Enterprises Corporation",
            "ACME ENTERPRISES LIMITED LIABILITY COMPANY"
        ]
        for raw in names:
            res = normalize_entity_name(raw, is_business=True)
            assert res.clean_name == "Acme Enterprises"

    def test_dotted_corporate_suffix_stripping(self):
        """Fix 2 Verification: Dotted suffixes like L.L.C., INC., CORP., P.C. are stripped cleanly."""
        dotted_names = [
            "ACME ENTERPRISES L.L.C.",
            "ACME ENTERPRISES INC.",
            "ACME ENTERPRISES CORP.",
            "ACME ENTERPRISES P.C."
        ]
        for raw in dotted_names:
            res = normalize_entity_name(raw, is_business=True)
            assert res.clean_name == "Acme Enterprises"

    def test_corporate_suffix_pattern_ordering(self):
        """Fix 3 Verification: Longest multi-word patterns strip first."""
        res = normalize_entity_name("ACME PROFESSIONAL LIMITED LIABILITY COMPANY", is_business=True)
        assert res.clean_name == "Acme"
        assert res.core_key == "ACME"

    def test_unanchored_corporate_suffix_preservation(self):
        """Fix 4 Verification: Words like COMPANY at start of entity name are preserved."""
        res = normalize_entity_name("COMPANY OF AMERICA INC", is_business=True)
        assert res.clean_name == "Company Of America"
        assert res.core_key == "COMPANY AMERICA"

    def test_person_name_preserves_inc_words(self):
        res = normalize_entity_name("JOHN INCLEMONA", is_business=False)
        assert res.clean_name == "John Inclemona"

    def test_core_key_stop_word_removal(self):
        res = normalize_entity_name("THE ACME AND SONS HOLDINGS LLC", is_business=True)
        assert res.core_key == "ACME SONS HOLDINGS"

    def test_empty_and_stopword_entity_names(self):
        """Fix 5 Verification: Generic/stop-word-only names do not return empty core_key or crash."""
        res1 = normalize_entity_name("LLC", is_business=True)
        assert res1.clean_name == "Llc"
        assert res1.core_key == "LLC"

        res2 = normalize_entity_name(None, is_business=True)
        assert res2.clean_name == "Unknown Entity"
        assert res2.core_key == "UNKNOWN_ENTITY"

    def test_soundex_encoding(self):
        code1 = compute_soundex("Smith")
        code2 = compute_soundex("Smyth")
        assert code1 == code2 == "S530"

    def test_double_metaphone_encoding(self):
        dm1 = compute_double_metaphone("Smith")
        dm2 = compute_double_metaphone("Smidt")
        assert dm1[0] == dm2[0]
