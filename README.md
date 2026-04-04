# AI Research Paper Reading Schedule

A structured deep-dive into foundational and modern AI research papers, with code implementations and detailed analysis.

---

## 📚 Papers Overview

### Week 1: BERT - Pre-training of Deep Bidirectional Transformers
**Authors**: Devlin et al. (2018)
**Paper**: [arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805)
**Institution**: Google AI

#### Key Insights
- Bidirectional pre-training is more effective than unidirectional approaches
- Masked Language Modeling (MLM) + Next Sentence Prediction (NSP) objectives
- Transfer learning at scale enables strong performance on downstream tasks
- 340M parameters trained on diverse text corpus

#### Folder
- Location: `/scaling laws/bert/`
- Resources: Phase 1-4 notebooks (Word2Vec → BERT → Sentence BERT → Mini RAG)
- Focus: Understanding contextual embeddings and transfer learning

---

### Week 2: Scaling Laws for Neural Language Models
**Authors**: Kaplan et al. (2020)
**Paper**: [arxiv.org/abs/2001.08361](https://arxiv.org/abs/2001.08361)
**Institution**: OpenAI

#### Key Insights
- Model performance follows predictable power-law relationships
- Three independent scaling factors: Model Size (N), Data Size (D), Compute (C)
- Loss scales as L(N) = a_N × N^(-0.07), suggesting 5% improvement per 2x scale
- Enables resource allocation planning without extensive experimentation
- Foundation for compute-optimal training (improved by Chinchilla, 2022)

#### Folder
- Location: `/scaling laws/`
- Resources:
  - `scaling_laws_deepdive.ipynb` - Interactive notebook with visualizations
  - `SCALING_LAWS_GUIDE.md` - Comprehensive guide with explanations
  - `scaling_laws.py` - Ready-to-use Python module with prediction tools
  - `QUICK_REFERENCE.md` - Quick lookup reference with practical examples
  - `requirements.txt` - Python dependencies
- Focus: Understanding and implementing scaling laws for model planning

#### Key Equations
```
L(N) = 0.34 × N^(-0.07)     # Loss from model size
L(D) = 2.56 × D^(-0.095)    # Loss from data size
D_optimal ≈ 20 × N          # Chinchilla's optimal allocation
```

---

## 🔗 Connection Between Papers

**BERT (2018)** → **Scaling Laws (2020)**

- BERT showed that **scale matters** for model performance
- Scaling Laws paper quantifies **exactly how much** scale matters
- BERT's success inspired the systematic study of scaling relationships
- Understanding these laws enabled modern models (GPT-3, LLaMA, Claude)

---

## 🛠️ How to Use This Repository

### Getting Started
1. Each folder contains notebooks, guides, and code for that week's paper
2. Start with the comprehensive guide (`*_GUIDE.md`)
3. Run the interactive notebook for visualizations
4. Use the Python module for hands-on experimentation

### Scaling Laws Paper Specifically
```bash
# Install dependencies
pip install -r scaling\ laws/requirements.txt

# Run the interactive notebook
jupyter notebook scaling\ laws/scaling_laws_deepdive.ipynb

# Use the Python module
python3
>>> from scaling_laws import ScalingLawPredictor, compute_optimal_allocation
>>> pred = ScalingLawPredictor()
>>> loss = pred.predict_loss(N=7e9, D=140e9)
```

### Key Resources
- **BERT Folder**: `/bert/` - Progressive exploration from Word2Vec to RAG
- **Scaling Laws Folder**: `/scaling laws/` - Complete implementation with code
- **This README**: Overview and connection between papers

---

## 📝 Notes

- Each paper builds on previous understanding
- Scaling Laws is critical for understanding modern LLM design decisions
- Recommended: Compare real models (GPT-3, LLaMA, Claude) against scaling law predictions
- Connect findings back to BERT's architecture and training approach

---

**Last Updated**: April 4, 2026 | **Current**: Week 2 of 15 | **Next**: PPO (Week 3)
