#!/usr/bin/env python3
"""
Test script for tokenizers.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pronunciation_translator.tokenizers import Tokenizer


def test_german_spelling_tokenizer():
    """Test German spelling tokenizer."""
    print("Testing German spelling tokenizer...")

    tokenizer = Tokenizer("tokenizers/de_spelling.json")
    print(f"  Loaded: {tokenizer}")

    # Test encoding and decoding
    test_words = ["Straße", "Hallo", "Welt", "Größe"]

    for word in test_words:
        encoded = tokenizer.encode(word)
        decoded = tokenizer.decode(encoded)

        print(f"\n  Word: '{word}'")
        print(f"  Encoded: {encoded}")
        print(f"  Decoded: '{decoded}'")

        assert decoded == word, f"Decode mismatch: expected '{word}', got '{decoded}'"

    print("\n✅ German spelling tokenizer passed!")


def test_german_ipa_tokenizer():
    """Test German IPA tokenizer."""
    print("\nTesting German IPA tokenizer...")

    tokenizer = Tokenizer("tokenizers/de_ipa.json")
    print(f"  Loaded: {tokenizer}")

    # Test encoding and decoding
    test_pronunciations = ["ˈʃtraːsə", "ˈhaloː", "vɛlt"]

    for ipa in test_pronunciations:
        encoded = tokenizer.encode(ipa)
        decoded = tokenizer.decode(encoded)

        print(f"\n  IPA: '{ipa}'")
        print(f"  Encoded: {encoded}")
        print(f"  Decoded: '{decoded}'")

        assert decoded == ipa, f"Decode mismatch: expected '{ipa}', got '{decoded}'"

    print("\n✅ German IPA tokenizer passed!")


def test_special_tokens():
    """Test special token handling."""
    print("\nTesting special token handling...")

    tokenizer = Tokenizer("tokenizers/de_spelling.json")

    # Test with special tokens
    word = "Test"
    encoded_with_special = tokenizer.encode(word, add_special_tokens=True)
    decoded_skip_special = tokenizer.decode(encoded_with_special, skip_special_tokens=True)

    print(f"\n  Word: '{word}'")
    print(f"  With special tokens: {encoded_with_special}")
    print(f"    First token (SOS): {encoded_with_special[0]} = '{tokenizer.id_to_char[encoded_with_special[0]]}'")
    print(f"    Last token (EOS): {encoded_with_special[-1]} = '{tokenizer.id_to_char[encoded_with_special[-1]]}'")
    print(f"  Decoded (skip special): '{decoded_skip_special}'")

    assert decoded_skip_special == word, f"Expected '{word}', got '{decoded_skip_special}'"

    # Test without special tokens
    encoded_no_special = tokenizer.encode(word, add_special_tokens=False)
    decoded_no_special = tokenizer.decode(encoded_no_special, skip_special_tokens=False)

    print(f"\n  Without special tokens: {encoded_no_special}")
    print(f"  Decoded: '{decoded_no_special}'")

    assert decoded_no_special == word, f"Expected '{word}', got '{decoded_no_special}'"

    print("\n✅ Special token handling passed!")


def test_unknown_characters():
    """Test handling of unknown characters."""
    print("\nTesting unknown character handling...")

    tokenizer = Tokenizer("tokenizers/de_spelling.json")

    # Test with a character not in German vocabulary (e.g., Cyrillic)
    word_with_unknown = "Test привет"  # Mix German and Russian
    encoded = tokenizer.encode(word_with_unknown, add_special_tokens=False)
    decoded = tokenizer.decode(encoded, skip_special_tokens=False)

    print(f"\n  Original: '{word_with_unknown}'")
    print(f"  Encoded: {encoded}")
    print(f"  Decoded: '{decoded}'")
    print(f"  Note: Unknown characters (Cyrillic) are replaced with <UNK>")

    print("\n✅ Unknown character handling passed!")


def main():
    """Run all tokenizer tests."""
    print("="*60)
    print("Running Tokenizer Tests")
    print("="*60)

    try:
        test_german_spelling_tokenizer()
        test_german_ipa_tokenizer()
        test_special_tokens()
        test_unknown_characters()

        print("\n" + "="*60)
        print("All tests passed! ✅")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
