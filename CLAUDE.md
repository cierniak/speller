# Pronunciation Translation Project Plan

## Important: Progress Tracking

**When implementing any part of this plan, always update `PROGRESS.md` to reflect:**
- Completed tasks (update checkboxes)
- Implementation details and files created
- Technical decisions made and their rationale
- Any deviations from the original plan
- Known issues or blockers encountered

This keeps the project organized and maintains a clear record of what has been accomplished.

---

## Project Overview
Build a cross-linguistic pronunciation translation system that converts words from one language to phonetic spellings that approximate the pronunciation using another language's orthographic rules. The system uses IPA (International Phonetic Alphabet) as an intermediate representation and machine learning models for grapheme-to-phoneme and phoneme-to-grapheme conversion.

**Example:** German "Straße" → IPA "ˈʃtraːsə" → Spanish-compatible IPA → Spanish spelling approximation

## Architecture Overview
```
Source Language Word → [Dictionary lookup OR Lang→IPA model] → Source IPA → 
[IPA Sound Mapping] → Target IPA → [IPA→Target Lang model] → Target Language Spelling
```

## Technology Stack
- **ML Framework:** PyTorch (custom seq2seq architecture)
- **Model Storage:** HuggingFace Hub (for custom model weights)
- **Data Processing:** Polars (instead of pandas)
- **Package Structure:** Installable Python library + separate Flask app
- **Web Framework:** Flask (imports the core library)
- **Deployment:** GKE Autopilot (for Kubernetes learning)
- **Containerization:** Docker
- **Workflow Orchestration:** Prefect (optional, for learning)

## Key Design Decisions
- **Custom seq2seq:** Lightweight character-level models (1-5M parameters each)
- **Language scalability:** Support 50+ languages without model size explosion
- **Library structure:** Installable package separate from Flask web app
- **HuggingFace storage:** Custom model weights hosted professionally
- **Character-level tokenization:** Simple, handles morphological variations, no OOV issues
- **Separate tokenizers per language:** Avoids vocabulary drift when adding new languages
- **Data adapter pattern:** Support multiple dataset formats

## Project Phases

### Phase 1: Core Infrastructure & Data

#### 1.1 Repository Setup
```
pronunciation-translator/
├── pyproject.toml                    # Package definition
├── data/                            # Raw datasets, IPA mappings
├── src/
│   └── pronunciation_translator/    # Main library package
│       ├── __init__.py             # Main API exports
│       ├── models/                 # Custom seq2seq architectures
│       ├── tokenizers/             # Character-level tokenizers
│       ├── inference/              # Model loading and prediction
│       ├── training/               # Training pipelines
│       └── data_adapters/          # Dataset format adapters
├── models/                         # Local model cache (gitignored)
├── web/                            # Flask application (imports library)
├── cli/                            # Command-line interface
├── examples/                       # Usage examples
├── k8s/                            # Kubernetes manifests
├── docker/                         # Containerization
├── flows/                          # Prefect flows (optional)
└── CLAUDE.md                       # This file
```

#### 1.2 Data Source and Adapters
- **Primary dataset:** ipa-dict (https://github.com/open-dict-data/ipa-dict)
- **Rationale:** Clean word→IPA pairs, multiple languages, proven quality
- **Data adapter interface:** Abstract base class for different dataset formats
- **Use Polars** for CSV/TSV reading instead of pandas

#### 1.3 Tokenizer Infrastructure
- **Character-level tokenizers:** Per language and modality (spelling/IPA)
- **Structure:** `{lang}_spelling.json`, `{lang}_ipa.json`
- **Special tokens:** `<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`
- **Auto-generation:** Build vocabularies from training data
- **Library integration:** Clean tokenizer API for easy use

#### 1.4 Dataset Infrastructure
- Training data format and PyTorch DataLoaders
- Dictionary lookup system (hash tables for known words)
- Data validation and statistics
- Train/validation/test splits

### Phase 2: Model Development

#### 2.1 Model Architecture
- **Custom seq2seq:** Encoder-decoder with attention mechanism
- **Lightweight design:** 1-5M parameters per language pair
- **Character-level:** Input/output sequences of characters
- **Scalability:** 50 models × 5MB each = ~250MB total vs. 10GB+ for transformers
- **Language agnostic:** No English bias, works equally well for any language

#### 2.2 Training Pipeline
- **From scratch training:** No pretrained weights, train on IPA datasets
- **Custom architecture:** Seq2seq with attention, designed for character translation
- **Evaluation metrics:** Character accuracy, phoneme accuracy, BLEU scores
- **MLX training:** Leverage MLX for faster training on Apple Silicon
- **Library integration:** Training utilities as part of installable package

```python
from pronunciation_translator.models import Seq2SeqModel
from pronunciation_translator.training import Trainer

model = Seq2SeqModel(input_vocab_size=45, output_vocab_size=89)
trainer = Trainer(model, train_dataset, val_dataset)
trainer.train(epochs=20)
# Upload to HuggingFace Hub
trainer.save_to_hub("your-username/pronunciation-models", "de_to_ipa")
```

#### 2.3 Model Storage Strategy
- **HuggingFace Hub:** Host custom PyTorch model weights professionally
- **Repository structure:** Single repo `{username}/pronunciation-models` with organized files
- **Naming convention:** `{lang}_{direction}_{architecture}_{config_hash}_{epochs}ep_{val_loss}.pth`
- **Example:** `de_TO_IPA_seq2seq_a1b2c3_15ep_0.023loss.pth`
- **Model configs:** JSON files with architecture details stored alongside weights
- **Library integration:** Clean download/upload API in library

**Implementation:**
```python
from huggingface_hub import upload_file, hf_hub_download
from pronunciation_translator import Seq2SeqModel

# Upload after training
upload_file(
    path_or_fileobj="de_to_ipa_model.pth",
    path_in_repo="models/de_TO_IPA_seq2seq_a1b2c3_15ep_0.023loss.pth",
    repo_id="your-username/pronunciation-models"
)

# Load for inference (via library)
from pronunciation_translator import load_model
model = load_model("german", "to_ipa")  # Handles HF download automatically
```

#### 2.4 IPA → Language Model Training
- Train reverse direction for each language
- Same architecture and evaluation approach

### Phase 2.5: Development Tools & Testing

#### 2.5.1 Training CLI Tools
- **Model training:** `python -m pronunciation_translator.training.train --lang german --direction to_ipa`
- **Training monitoring:** Real-time loss tracking and early stopping
- **Hyperparameter testing:** Easy config modification and comparison
- **Data validation:** Check dataset quality before training

```python
# Training CLI usage
python -m pronunciation_translator.training.train \
    --config configs/de_to_ipa.json \
    --data data/ipa-dict/data/de.txt \
    --epochs 20 \
    --save-to-hub your-username/pronunciation-models
```

#### 2.5.2 Model Testing & Evaluation
- **Single model testing:** `python -m pronunciation_translator.test --model de_to_ipa --word "Straße"`
- **Batch evaluation:** Test on validation sets with metrics
- **Round-trip testing:** German → IPA → German accuracy
- **Model comparison:** Compare different checkpoints/architectures

```python
# Testing CLI usage
python -m pronunciation_translator.test \
    --model de_to_ipa \
    --test-file data/test_words_de.txt \
    --metrics accuracy,bleu \
    --output results/de_to_ipa_eval.json
```

#### 2.5.3 Development Utilities
- **Tokenizer testing:** Verify vocabulary and encoding/decoding
- **Model debugging:** Attention visualization, error analysis
- **Data exploration:** Statistics and sample inspection
- **Config validation:** Check model architecture compatibility

### Phase 3: Cross-Language Pipeline

#### 3.1 Same-Language Sanity Testing
- Round-trip testing: German → IPA → German
- Compute reconstruction accuracy
- Identify model weaknesses

#### 3.2 Second Language Implementation
- Start with Spanish (existing IPA mappings available)
- Train Spanish ↔ IPA models
- Use existing IPA equivalence table as starting point:
```
ɑ,a | ɲ,nj | ə,e | x,h | θ,s | ʃ,s | etc.
```

#### 3.3 Cross-Language Pipeline
- Implement German → IPA → Spanish-IPA → Spanish
- Test with known word pairs
- Evaluate output quality

#### 3.4 Model Discovery System
- **HF Hub integration:** Query single pronunciation-models repo for available weights
- **File parsing:** Extract language pairs from model filenames
- **Model selection:** Prefer higher epochs/lower loss from filename metadata
- **Library API:** Simple discovery through installable package

```python
from huggingface_hub import list_repo_files
from pronunciation_translator import discover_models, load_model

def discover_available_models():
    files = list_repo_files("your-username/pronunciation-models")
    model_files = [f for f in files if f.startswith("models/") and f.endswith(".pth")]
    return parse_model_metadata(model_files)  # Extract lang, direction, metrics

# Library usage
available = discover_models()  # Returns list of (lang, direction) pairs
model = load_model("german", "to_ipa")  # Automatic download + loading
```

### Phase 4: Library Development

#### 4.1 Python Package Structure
- **Installable library:** `pip install pronunciation-translator`
- **Clean API:** Simple functions for translation
- **Model management:** Automatic download and caching
- **Documentation:** Usage examples and API reference

```python
# Simple library usage
from pronunciation_translator import translate_pronunciation

result = translate_pronunciation("Straße", from_lang="german", to_lang="spanish")
print(result)  # Spanish spelling approximation
```

### Phase 5: Web Application

#### 5.1 End-User CLI Development
- **Polished CLI:** `pronunciation-translate "Straße" --from german --to spanish`
- **End-to-end pipeline:** Full cross-language translation using library
- **User-friendly options:** Language selection, output formatting
- **Batch processing:** Handle files and multiple translations
- **Model management:** Auto-download, list available language pairs

```bash
# End-user CLI examples
pronunciation-translate "Straße" --from german --to spanish
pronunciation-translate --list-languages
pronunciation-translate --batch input_words.txt --from german --to spanish --output results.json
```

#### 5.2 Flask Web Server
- **Library import:** `from pronunciation_translator import translate_pronunciation`
- **Simple interface:** Clean web UI for pronunciation translation
- **API endpoints:** REST API for programmatic access
- **Model loading:** Lazy loading of needed models only
- **Error handling:** Graceful fallbacks when models unavailable

#### 5.3 Frontend Polish
- **Bootstrap styling:** Professional appearance
- **Language selection:** Dynamic list based on available models
- **Progress indicators:** Show model loading status
- **Examples:** Pre-populated examples for each language pair

### Phase 6: Deployment & Kubernetes Learning

#### 6.1 Containerization
- **Multi-stage Dockerfile:** Build library + Flask app
- **Model preloading:** Download common models during build
- **Lightweight base:** Only PyTorch + library dependencies
- **Flexible loading:** Support runtime model downloads

```dockerfile
# Install library
RUN pip install ./pronunciation-translator

# Pre-download popular models (optional)
RUN python -c "from pronunciation_translator import load_model; \
    load_model('german', 'to_ipa'); load_model('spanish', 'to_ipa')"

# Flask app imports the library
CMD ["python", "web/app.py"]
```

#### 6.2 Local Kubernetes Testing
- Use minikube or kind for development
- Basic deployment and service manifests
- Test model loading and inference

#### 6.3 GKE Autopilot Deployment
- Create GKE Autopilot cluster
- Deploy containerized application
- Configure services and ingress
- **Learning goal:** Understand Kubernetes concepts

#### 6.4 CI/CD and Updates
- GitHub Actions → Google Container Registry → GKE
- Rolling deployment strategy for model updates
- Blue/green deployments for major changes

#### 6.5 Domain and SSL
- Custom domain configuration via Ingress
- Google-managed SSL certificates
- DNS configuration

## Technical Considerations

### Model Configuration Versioning
Store configurations as JSON with computed hashes:
```json
{
  "architecture": "seq2seq_attention",
  "hidden_size": 256,
  "num_layers": 2,
  "dropout": 0.1,
  "vocab_sizes": {"input": 45, "output": 89}
}
```

### IPA Sound Mapping Evolution
- **Phase 1:** Use existing manual mappings
- **Phase 2:** Add confidence scores and multiple alternatives
- **Phase 3:** Phonetic feature-based automatic mapping

### Data Quality and Evaluation
- Need human evaluation dataset for cross-language quality
- Consider phonetic similarity metrics beyond exact matches
- Handle regional pronunciation variants

### Production Concerns
- **Model loading optimization:** Memory caching + lazy loading from HF Hub
- **HF Hub reliability:** Fallback strategies for Hub unavailability
- **Model versioning:** Pin specific model versions in production
- **Rate limiting:** Both API and HF Hub download limits
- **Error handling:** Graceful degradation when models unavailable
- **Monitoring:** Track model download times and cache hit rates
- **Security:** Validate model integrity after downloads

## Learning Objectives
- **Kubernetes:** GKE Autopilot deployment and management
- **MLX:** Apple Silicon-optimized training
- **Polars:** Modern DataFrame library
- **Prefect:** Workflow orchestration (optional)
- **Cross-linguistic phonetics:** IPA mapping and sound correspondences

## Success Criteria
- **Functional translation:** German ↔ Spanish pronunciation translation working
- **Library package:** Installable `pip install pronunciation-translator`
- **Web interface:** Flask app with custom domain using the library
- **Kubernetes deployment:** GKE deployment of containerized application
- **Scalable architecture:** Support for 50+ languages with lightweight models
- **Model accuracy:** Round-trip accuracy >70% for same-language testing
- **Professional hosting:** Models hosted on HuggingFace Hub with proper versioning