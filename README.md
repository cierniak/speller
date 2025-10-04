# Pronunciation Translation System

**🚧 Work in Progress 🚧**

This project builds a cross-linguistic pronunciation translation system that converts words from one language to phonetic spellings that approximate the pronunciation using another language's orthographic rules. The system uses the International Phonetic Alphabet (IPA) as an intermediate representation, employing machine learning models for grapheme-to-phoneme and phoneme-to-grapheme conversion. For example, it can translate German "Straße" through IPA "ˈʃtraːsə" to a Spanish spelling approximation that helps Spanish speakers pronounce the German word correctly. The system is built using PyTorch/MLX for model training, Polars for data processing, Flask for the web interface, and is designed for deployment on Google Kubernetes Engine.

For detailed implementation plans and architecture overview, see [CLAUDE.md](CLAUDE.md).

## Setup for Collaborators

This project uses Git submodules for dataset dependencies. After cloning the repository, run:

```bash
git submodule update --init --recursive
```

This will download the required datasets including the ipa-dict data in `data/ipa-dict/`.

## Development Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Note: On Apple Silicon Macs running Python under Rosetta, use `polars-lts-cpu` instead:
   ```bash
   pip install polars-lts-cpu torch numpy
   ```

2. **Test Data Adapters:**
   ```bash
   python3 test_adapter.py
   ```

   This will test the data loading and processing capabilities with:
   - German dataset (840K+ word-IPA pairs)
   - Spanish dataset (596K+ pairs)
   - English dataset (135K+ pairs)
   - Data validation and statistics
   - Train/validation/test splits

   Example output:
   ```
   Testing IPADictAdapter...
   Loading German data...
   Loaded 840277 entries
   Languages: ['de']

   Validation results:
   Valid: True
   Stats: {'total_entries': 840277, 'unique_words': 787104, ...}

   ✅ All tests passed!
   ```

3. **Build and Test Tokenizers:**

   Tokenizers are character-level vocabularies stored as JSON files. Each language has two tokenizers: one for orthographic spelling and one for IPA pronunciations.

   **Generate tokenizer files:**
   ```bash
   python3 build_tokenizers.py
   ```

   This extracts character vocabularies from the dataset and creates JSON files in `tokenizers/`:
   - `de_spelling.json` - German orthography (125 chars)
   - `de_ipa.json` - German IPA symbols (104 chars)

   **Test tokenizers:**
   ```bash
   python3 test_tokenizer.py
   ```

   This verifies:
   - Encoding text to token IDs
   - Decoding token IDs back to text
   - Special token handling (`<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`)
   - Unknown character handling

   Example output:
   ```
   Testing German spelling tokenizer...
     Loaded: Tokenizer(language=de, modality=spelling, vocab_size=129)

     Word: 'Straße'
     Encoded: [1, 44, 71, 69, 52, 84, 56, 2]
     Decoded: 'Straße'

   ✅ All tests passed!
   ```

   **Tokenizer structure:**
   ```
   tokenizers/              # Generated JSON files (gitignored)
   ├── de_spelling.json     # German orthography vocabulary
   ├── de_ipa.json          # German IPA vocabulary
   └── ...                  # Other languages as needed
   ```

   Each tokenizer JSON contains:
   - Language code and modality (spelling/ipa)
   - Sorted character vocabulary
   - Special token definitions

   Tokenizers are loaded at training and inference time to ensure consistent vocabulary.
