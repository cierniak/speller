#!/usr/bin/env python3
"""
Build tokenizer JSON files from IPA-dict data.

This script extracts character vocabularies from the dataset
and generates tokenizer JSON files for each language and modality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pronunciation_translator.data_adapters import IPADictAdapter
from pronunciation_translator.tokenizers import TokenizerBuilder


def build_tokenizers_for_language(language_code: str, data_file: Path, output_dir: Path):
    """
    Build spelling and IPA tokenizers for a language.

    Args:
        language_code: Language code (e.g., 'de', 'fr', 'es')
        data_file: Path to the language data file
        output_dir: Directory where tokenizer JSON files will be saved
    """
    print(f"\n{'='*60}")
    print(f"Building tokenizers for {language_code}")
    print(f"{'='*60}")

    # Load data
    print(f"Loading data from {data_file}...")
    adapter = IPADictAdapter(data_file, language_code=language_code)
    data = adapter.load_data()

    print(f"Loaded {len(data)} entries")

    # Build spelling tokenizer
    print("\nBuilding spelling tokenizer...")
    spelling_builder = TokenizerBuilder(language_code, "spelling")
    spelling_builder.build_from_data(data, "word")
    spelling_path = output_dir / f"{language_code}_spelling.json"
    spelling_builder.save(spelling_path)

    # Build IPA tokenizer
    print("\nBuilding IPA tokenizer...")
    ipa_builder = TokenizerBuilder(language_code, "ipa")
    ipa_builder.build_from_data(data, "ipa")
    ipa_path = output_dir / f"{language_code}_ipa.json"
    ipa_builder.save(ipa_path)

    print(f"\n✅ Tokenizers for {language_code} created successfully!")


def main():
    """Build tokenizers for available languages."""
    # Set up paths
    data_dir = Path("data/ipa-dict/data")
    output_dir = Path("tokenizers")

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please ensure ipa-dict data is available.")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Start with German
    languages = [
        ("de", "German"),
    ]

    for lang_code, lang_name in languages:
        data_file = data_dir / f"{lang_code}.txt"
        if data_file.exists():
            build_tokenizers_for_language(lang_code, data_file, output_dir)
        else:
            print(f"⚠️  Skipping {lang_name} - data file not found: {data_file}")

    print(f"\n{'='*60}")
    print("All tokenizers built successfully!")
    print(f"{'='*60}")
    print(f"\nTokenizer files saved to: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
