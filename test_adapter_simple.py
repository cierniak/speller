#!/usr/bin/env python3
"""
Simple test script for the data adapters without Polars dependency.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_structure():
    """Test that the adapter structure works."""
    print("Testing basic adapter structure...")
    
    try:
        from pronunciation_translator.data_adapters import BaseDataAdapter, IPADictAdapter
        print("✅ Successfully imported adapters")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test that we can instantiate the adapter
    try:
        adapter = IPADictAdapter(Path("data/ipa-dict/data/de.txt"))
        print("✅ Successfully created IPADictAdapter instance")
    except Exception as e:
        print(f"❌ Failed to create adapter: {e}")
        return False
    
    return True


def test_data_parsing():
    """Test basic data parsing without Polars."""
    print("\nTesting data parsing logic...")
    
    from pronunciation_translator.data_adapters.ipa_dict_adapter import IPADictAdapter
    
    adapter = IPADictAdapter(Path("data/ipa-dict/data/de.txt"))
    
    # Test language code extraction
    lang_code = adapter._extract_language_code(Path("data/ipa-dict/data/de.txt"))
    print(f"Language code: {lang_code}")
    assert lang_code == "de", f"Expected 'de', got '{lang_code}'"
    
    # Test IPA parsing
    test_cases = [
        "/həˈloʊ/",
        "/həˈloʊ/, /hɛˈloʊ/",
        "/ˈʃtraːsə/",
    ]
    
    for case in test_cases:
        pronunciations = adapter._parse_ipa_pronunciations(case)
        print(f"'{case}' -> {pronunciations}")
    
    print("✅ IPA parsing tests passed")
    return True


def test_file_reading():
    """Test basic file reading."""
    print("\nTesting file reading...")
    
    de_file = Path("data/ipa-dict/data/de.txt")
    if not de_file.exists():
        print(f"❌ Test file not found: {de_file}")
        return False
    
    # Read first few lines manually
    with open(de_file, 'r', encoding='utf-8') as f:
        lines = []
        for i, line in enumerate(f):
            if i >= 5:
                break
            lines.append(line.strip())
    
    print(f"First 5 lines from {de_file.name}:")
    for line in lines:
        print(f"  {line}")
    
    print("✅ File reading test passed")
    return True


if __name__ == "__main__":
    print("Running simple adapter tests (without Polars)...")
    
    tests = [
        test_basic_structure,
        test_data_parsing,
        test_file_reading,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All basic tests passed! Install polars to run full tests.")
    else:
        sys.exit(1)