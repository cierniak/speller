"""
Tokenizer Builder

Extracts character vocabularies from data and generates tokenizer JSON files.
"""

import json
from pathlib import Path
from typing import Set, List
import polars as pl


class TokenizerBuilder:
    """
    Builds tokenizer vocabulary from training data.

    Extracts unique characters from a dataset and generates
    tokenizer JSON files for use in training and inference.
    """

    def __init__(self, language: str, modality: str):
        """
        Initialize tokenizer builder.

        Args:
            language: Language code (e.g., 'de', 'fr', 'es')
            modality: Either 'spelling' or 'ipa'
        """
        self.language = language
        self.modality = modality

        if modality not in ['spelling', 'ipa']:
            raise ValueError(f"Modality must be 'spelling' or 'ipa', got '{modality}'")

        self.vocab: List[str] = []
        self.special_tokens = {
            "pad": "<PAD>",
            "sos": "<SOS>",
            "eos": "<EOS>",
            "unk": "<UNK>"
        }

    def build_from_data(self, data: pl.DataFrame, column_name: str) -> 'TokenizerBuilder':
        """
        Extract vocabulary from a Polars DataFrame.

        Args:
            data: Polars DataFrame containing text data
            column_name: Name of column to extract characters from

        Returns:
            Self for method chaining
        """
        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in data. Available columns: {data.columns}")

        # Extract all unique characters
        char_set: Set[str] = set()

        for text in data[column_name].to_list():
            if text:  # Skip None/empty values
                char_set.update(text)

        # Sort characters for consistency
        self.vocab = sorted(list(char_set))

        return self

    def build_from_text_list(self, texts: List[str]) -> 'TokenizerBuilder':
        """
        Extract vocabulary from a list of text strings.

        Args:
            texts: List of text strings

        Returns:
            Self for method chaining
        """
        char_set: Set[str] = set()

        for text in texts:
            if text:  # Skip None/empty values
                char_set.update(text)

        # Sort characters for consistency
        self.vocab = sorted(list(char_set))

        return self

    def save(self, output_path: Path | str) -> None:
        """
        Save tokenizer to JSON file.

        Args:
            output_path: Path where to save the tokenizer JSON
        """
        output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "language": self.language,
            "modality": self.modality,
            "vocab": self.vocab,
            "special_tokens": self.special_tokens
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Tokenizer saved to {output_path}")
        print(f"  Language: {self.language}")
        print(f"  Modality: {self.modality}")
        print(f"  Vocabulary size: {len(self.vocab)} characters")
        print(f"  Total tokens (with special): {len(self.vocab) + len(self.special_tokens)}")

    def get_vocab_size(self) -> int:
        """
        Get total vocabulary size including special tokens.

        Returns:
            Total vocabulary size
        """
        return len(self.vocab) + len(self.special_tokens)

    def __repr__(self) -> str:
        return f"TokenizerBuilder(language={self.language}, modality={self.modality}, vocab_size={len(self.vocab)})"
