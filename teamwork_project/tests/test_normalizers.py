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

    def test_person_name_preserves_inc_words(self):
        res = normalize_entity_name("JOHN INCLEMONA", is_business=False)
        assert res.clean_name == "John Inclemona"

    def test_core_key_stop_word_removal(self):
        res = normalize_entity_name("THE ACME AND SONS HOLDINGS LLC", is_business=True)
        assert res.core_key == "ACME SONS HOLDINGS"

    def test_soundex_encoding(self):
        code1 = compute_soundex("Smith")
        code2 = compute_soundex("Smyth")
        assert code1 == code2 == "S530"

    def test_double_metaphone_encoding(self):
        dm1 = compute_double_metaphone("Smith")
        dm2 = compute_double_metaphone("Smidt")
        assert dm1[0] == dm2[0]
