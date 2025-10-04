"""
Tokenizer

Character-level tokenizer for pronunciation translation.
Loads vocabulary from JSON files and provides encode/decode functionality.
"""

import json
from pathlib import Path
from typing import Dict, List


class Tokenizer:
    """
    Character-level tokenizer that loads vocabulary from JSON.

    JSON format:
    {
        "language": "de",
        "modality": "spelling",
        "vocab": ["a", "b", "c", ...],
        "special_tokens": {
            "pad": "<PAD>",
            "sos": "<SOS>",
            "eos": "<EOS>",
            "unk": "<UNK>"
        }
    }
    """

    def __init__(self, json_path: Path | str):
        """
        Initialize tokenizer from JSON file.

        Args:
            json_path: Path to tokenizer JSON file
        """
        self.json_path = Path(json_path)

        if not self.json_path.exists():
            raise FileNotFoundError(f"Tokenizer file not found: {self.json_path}")

        # Load configuration
        with open(self.json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.language = config.get("language", "unknown")
        self.modality = config.get("modality", "unknown")
        self.special_tokens = config.get("special_tokens", {
            "pad": "<PAD>",
            "sos": "<SOS>",
            "eos": "<EOS>",
            "unk": "<UNK>"
        })

        # Build vocabulary with special tokens first
        self.vocab = []
        self.vocab.append(self.special_tokens["pad"])
        self.vocab.append(self.special_tokens["sos"])
        self.vocab.append(self.special_tokens["eos"])
        self.vocab.append(self.special_tokens["unk"])

        # Add regular vocabulary
        self.vocab.extend(config["vocab"])

        # Create bidirectional mappings
        self.char_to_id: Dict[str, int] = {char: idx for idx, char in enumerate(self.vocab)}
        self.id_to_char: Dict[int, str] = {idx: char for idx, char in enumerate(self.vocab)}

        # Store special token IDs for easy access
        self.pad_id = self.char_to_id[self.special_tokens["pad"]]
        self.sos_id = self.char_to_id[self.special_tokens["sos"]]
        self.eos_id = self.char_to_id[self.special_tokens["eos"]]
        self.unk_id = self.char_to_id[self.special_tokens["unk"]]

    @property
    def vocab_size(self) -> int:
        """Return the vocabulary size."""
        return len(self.vocab)

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Encode text into token IDs.

        Args:
            text: Input text to encode
            add_special_tokens: If True, add <SOS> and <EOS> tokens

        Returns:
            List of token IDs
        """
        ids = []

        if add_special_tokens:
            ids.append(self.sos_id)

        for char in text:
            ids.append(self.char_to_id.get(char, self.unk_id))

        if add_special_tokens:
            ids.append(self.eos_id)

        return ids

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        """
        Decode token IDs back into text.

        Args:
            ids: List of token IDs
            skip_special_tokens: If True, skip special tokens in output

        Returns:
            Decoded text string
        """
        chars = []

        special_token_ids = {self.pad_id, self.sos_id, self.eos_id}

        for token_id in ids:
            if skip_special_tokens and token_id in special_token_ids:
                continue

            char = self.id_to_char.get(token_id, self.special_tokens["unk"])
            chars.append(char)

        return ''.join(chars)

    def __repr__(self) -> str:
        return f"Tokenizer(language={self.language}, modality={self.modality}, vocab_size={self.vocab_size})"

    def __len__(self) -> int:
        return self.vocab_size
