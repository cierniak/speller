#!/usr/bin/env python3
"""
Test script for the data adapters.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pronunciation_translator.data_adapters import IPADictAdapter


def test_ipa_dict_adapter():
    """Test the IPA Dict adapter with sample data."""
    print("Testing IPADictAdapter...")
    
    # Test with German data
    adapter = IPADictAdapter(Path("data/ipa-dict/data/de.txt"))
    
    print("Loading German data...")
    data = adapter.get_data()
    
    print(f"Loaded {len(data)} entries")
    print(f"Columns: {data.columns}")
    print(f"Languages: {data['language'].unique().to_list()}")
    
    # Show sample data
    print("\nFirst 5 entries:")
    print(data.head())
    
    # Test validation
    print("\nValidation results:")
    validation = adapter.validate_data(data)
    print(f"Valid: {validation['is_valid']}")
    print(f"Stats: {validation['stats']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    
    # Test word pairs extraction
    print(f"\nFirst 5 German word-IPA pairs:")
    pairs = adapter.get_word_pairs('de')[:5]
    for word, ipa in pairs:
        print(f"  {word} -> {ipa}")
    
    # Test data splits
    print("\nTesting data splits...")
    train, val, test = adapter.create_splits()
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    
    return True


def test_multiple_languages():
    """Test adapter with multiple language files."""
    print("\n" + "="*50)
    print("Testing multiple language files...")
    
    adapter = IPADictAdapter(Path("data/ipa-dict/data/"))
    
    available_languages = adapter.get_available_languages()
    print(f"Available languages: {available_languages}")
    
    # Load data from multiple files (limit to first few for testing)
    test_languages = ['de', 'es_ES', 'en_US']
    for lang in test_languages:
        if lang in available_languages:
            lang_adapter = IPADictAdapter(Path(f"data/ipa-dict/data/{lang}.txt"))
            data = lang_adapter.get_data()
            stats = lang_adapter.validate_data(data)['stats']
            print(f"{lang}: {stats['total_entries']} entries, {stats['unique_words']} unique words")


if __name__ == "__main__":
    try:
        test_ipa_dict_adapter()
        test_multiple_languages()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)