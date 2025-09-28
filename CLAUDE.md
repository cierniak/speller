# Pronunciation Translation Project Plan

## Project Overview
Build a cross-linguistic pronunciation translation system that converts words from one language to phonetic spellings that approximate the pronunciation using another language's orthographic rules. The system uses IPA (International Phonetic Alphabet) as an intermediate representation and machine learning models for grapheme-to-phoneme and phoneme-to-grapheme conversion.

**Example:** German "Straße" → IPA "ˈʃtraːsə" → Spanish-compatible IPA → Spanish spelling approximation

## Architecture Overview
```
Source Language Word → [Dictionary lookup OR Lang→IPA model] → Source IPA → 
[IPA Sound Mapping] → Target IPA → [IPA→Target Lang model] → Target Language Spelling
```

## Technology Stack
- **ML Framework:** PyTorch (with MLX for training on Mac)
- **Data Processing:** Polars (instead of pandas)
- **Web Framework:** Flask
- **Deployment:** GKE Autopilot (for Kubernetes learning)
- **Containerization:** Docker
- **Workflow Orchestration:** Prefect (optional, for learning)

## Key Design Decisions
- **Character-level tokenization:** Simple, handles morphological variations, no OOV issues
- **Separate tokenizers per language:** Avoids vocabulary drift when adding new languages
- **Model versioning with config hashing:** Enables multiple architectures to coexist
- **Data adapter pattern:** Support multiple dataset formats

## Project Phases

### Phase 1: Core Infrastructure & Data

#### 1.1 Repository Setup
```
pronunciation-translator/
├── data/               # Raw datasets, IPA mappings
├── src/
│   ├── data_adapters/  # Dataset format adapters
│   ├── tokenizers/     # Character-level tokenizers
│   ├── models/         # Model architectures
│   └── training/       # Training pipelines
├── models/             # Trained model artifacts
├── web/                # Flask application
├── k8s/                # Kubernetes manifests
├── docker/             # Containerization
├── flows/              # Prefect flows (optional)
└── CLAUDE.md           # This file
```

#### 1.2 Data Source and Adapters
- **Primary dataset:** ipa-dict (https://github.com/open-dict-data/ipa-dict)
- **Rationale:** Clean word→IPA pairs, multiple languages, proven quality
- **Data adapter interface:** Abstract base class for different dataset formats
- **Use Polars** for CSV/TSV reading instead of pandas

#### 1.3 Tokenizer Infrastructure
- Character-level tokenizers per language and modality
- Structure: `{lang}_spelling.json`, `{lang}_ipa.json`
- Special tokens: `<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`
- Auto-generate vocabularies from training data

#### 1.4 Dataset Infrastructure
- Training data format and PyTorch DataLoaders
- Dictionary lookup system (hash tables for known words)
- Data validation and statistics
- Train/validation/test splits

### Phase 2: Model Development

#### 2.1 Model Architecture Selection
- **Primary:** Seq2Seq with attention (proven, interpretable)
- **Alternative:** Transformer encoder-decoder (if seq2seq insufficient)
- Model configuration with hashing for versioning

#### 2.2 Training Pipeline
- Language → IPA model training
- Evaluation metrics: character accuracy, phoneme accuracy, BLEU scores
- MLX training on Mac for performance
- **Optional:** Prefect flows for training orchestration

#### 2.3 Model Persistence Strategy
- Naming convention: `{lang}_{direction}_{architecture}_{config_hash}_{epochs}ep_{val_loss}.pth`
- Example: `de_TO_IPA_transformer_a1b2c3_15ep_0.023loss.pth`
- Store model configs alongside weights
- Auto-discovery system for available models

#### 2.4 IPA → Language Model Training
- Train reverse direction for each language
- Same architecture and evaluation approach

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
- Auto-detect available language pairs from model files
- Model selection logic (prefer higher epochs/lower loss)
- Configuration validation and compatibility checks

### Phase 4: Web Application

#### 4.1 Python CLI Development
- Command-line interface for quick testing
- Support for single words and batch processing
- Model selection options

#### 4.2 Flask Web Server
- Simple translation interface
- Input validation and error handling
- API endpoints for programmatic access
- Progress indicators and error messages

#### 4.3 Frontend Polish
- Bootstrap/CSS styling for usability
- Responsive design
- Clear language pair selection
- Example inputs and help text

### Phase 5: Deployment & Kubernetes Learning

#### 5.1 Containerization
- Multi-stage Dockerfile (build/runtime separation)
- Include trained models and dependencies
- Optimize image size and loading times

#### 5.2 Local Kubernetes Testing
- Use minikube or kind for development
- Basic deployment and service manifests
- Test model loading and inference

#### 5.3 GKE Autopilot Deployment
- Create GKE Autopilot cluster
- Deploy containerized application
- Configure services and ingress
- **Learning goal:** Understand Kubernetes concepts

#### 5.4 CI/CD and Updates
- GitHub Actions → Google Container Registry → GKE
- Rolling deployment strategy for model updates
- Blue/green deployments for major changes

#### 5.5 Domain and SSL
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
- Model loading optimization (memory caching)
- Rate limiting and input validation
- Error handling and graceful degradation
- Monitoring and logging

## Learning Objectives
- **Kubernetes:** GKE Autopilot deployment and management
- **MLX:** Apple Silicon-optimized training
- **Polars:** Modern DataFrame library
- **Prefect:** Workflow orchestration (optional)
- **Cross-linguistic phonetics:** IPA mapping and sound correspondences

## Success Criteria
- Functional German ↔ Spanish pronunciation translation
- Web interface with custom domain
- Kubernetes deployment on GKE
- Extensible architecture for adding new languages
- Round-trip accuracy >70% for same-language testing