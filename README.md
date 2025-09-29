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
