# AI Papers Learning

A collection of hands-on explorations and implementations of key AI/ML research papers. This repository documents my journey through understanding foundational concepts and modern architectures through code patterns and practical implementations.

## Papers Covered

### 1. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
- **Paper**: https://arxiv.org/abs/1810.04805
- **Description**: BERT revolutionized NLP by showing that a single pre-trained model, fine-tuned on task-specific data, could achieve state-of-the-art results across a wide range of language tasks — it's the paper that kicked off the modern era of large language models.
- **Folder**: `bert/`
- **Notebooks**:
  - `phase1_word2vec.ipynb` - Word embeddings foundations
  - `phase2_bert_embeddings.ipynb` - BERT architecture and contextual embeddings
  - `phase3_sbert.ipynb` - Sentence-level embeddings
  - `phase4_mini_rag.ipynb` - Retrieval-augmented generation system

## Getting Started

### Prerequisites
- Python 3.11+
- Dependencies listed in `requirements.txt`

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Notebooks

```bash
jupyter notebook bert/phase1_word2vec.ipynb
```

## Repository Structure

```
├── README.md
├── requirements.txt
└── bert/
    ├── phase1_word2vec.ipynb
    ├── phase2_bert_embeddings.ipynb
    ├── phase3_sbert.ipynb
    └── phase4_mini_rag.ipynb
```

## Purpose

This repository serves as:
- A learning resource for understanding modern NLP research through code
- A reference for implementing key ML concepts
- A documentation of explorations and discoveries in AI research

## Notes

- Code implementations focus on clarity and understanding over optimization
- Each notebook explores different aspects of the research
- Notebooks can be explored independently or sequentially

---

**Author**: Gaurav Bansal  
**Last Updated**: March 2026
