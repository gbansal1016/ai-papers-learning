# AI Research Paper Reading Schedule

A structured deep-dive into foundational and modern AI research papers, with code implementations and detailed analysis.

---

## 📚 Papers Overview

###  1: BERT - Pre-training of Deep Bidirectional Transformers
**Authors**: Devlin et al. (2018)
**Paper**: [arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805)
**Institution**: Google AI
**Location**: `/bert/`

#### Key Insights
- Bidirectional pre-training is more effective than unidirectional approaches
- Masked Language Modeling (MLM) + Next Sentence Prediction (NSP) objectives
- Transfer learning at scale enables strong performance on downstream tasks
- 340M parameters trained on diverse text corpus

---

### 2: Scaling Laws for Neural Language Models
**Authors**: Kaplan et al. (2020)
**Paper**: [arxiv.org/abs/2001.08361](https://arxiv.org/abs/2001.08361)
**Institution**: OpenAI
**Location**: `/scaling laws/`

#### Key Insights
- Model performance follows predictable power-law relationships
- Three independent scaling factors: Model Size (N), Data Size (D), Compute (C)
- Loss scales as L(N) = a_N × N^(-0.07), suggesting 5% improvement per 2x scale
- Enables resource allocation planning without extensive experimentation
- Foundation for compute-optimal training (improved by Chinchilla, 2022)

#### Key Equations
```
L(N) = 0.34 × N^(-0.07)     # Loss from model size
L(D) = 2.56 × D^(-0.095)    # Loss from data size
D_optimal ≈ 20 × N          # Chinchilla's optimal allocation
```

---

### 3: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

**Authors:** Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc Le, Denny Zhou

**Publication:** NeurIPS 2022
**Location**: `/chain-of-thought/`

#### Key Insights
The paper demonstrates that **prompting language models to show their reasoning (chain-of-thought)** dramatically improves performance on complex reasoning tasks—without any fine-tuning.

**Links:**
- 📄 **ArXiv:** https://arxiv.org/abs/2201.11903
- 📄 **PDF:** https://arxiv.org/pdf/2201.11903
- 🔍 **OpenReview:** https://openreview.net/forum?id=_VjQlMeSB_J

---

### 4: Tree of Thoughts: Deliberate Problem Solving with Large Language Models

**Authors:** Yao, S., Yu, D., Zhao, J., Shang, I., Yuan, Y., Wang, Y., et al.

**Publication:** May 2023
**Location**: `/tree-of-thoughts/`

#### Key Insights
Extends Chain-of-Thought by enabling language models to **explore multiple reasoning paths simultaneously** through a tree structure, rather than following a single linear path. Demonstrates 2-16x improvements over standard prompting on complex reasoning tasks.

**Key Components:**
- **Thought Decomposition**: Break problems into intermediate reasoning steps
- **State Evaluation**: Score intermediate states to guide search
- **Search Strategies**: BFS, DFS, Beam Search for tree exploration
- **Backtracking**: Recover from dead-end reasoning paths

**Links:**
- 📄 **ArXiv:** https://arxiv.org/abs/2305.10601
- 📄 **Applications:** Math puzzles, creative writing, code debugging, planning

**Comparison with CoT:**
- CoT: Single linear reasoning path → can get stuck
- ToT: Multiple exploration paths → can backtrack and explore alternatives
- Result: Better accuracy on complex reasoning tasks with higher token cost

## ⚡ Important: Local Model 
This example  uses **Mistral-7B-Instruct-v0.1** for local inference (free, private, no API keys needed). However, **inference is painfully slow**:

- **CPU:** ~5-10 seconds per inference call
- **GPU (NVIDIA):** ~1-3 seconds per inference call

**If you need speed:** Use cloud APIs (OpenAI, HuggingFace Inference API) instead by modifying `call_model()` function.

**For learning:** The slow inference is acceptable since we're studying CoT concepts, not optimizing production systems.


## 🔗 Connection Between Papers

**BERT (2018)** → **Scaling Laws (2020)**

- BERT showed that **scale matters** for model performance
- Scaling Laws paper quantifies **exactly how much** scale matters
- BERT's success inspired the systematic study of scaling relationships
- Understanding these laws enabled modern models (GPT-3, LLaMA, Claude)

---

## 🛠️ How to Use This Repository

### Getting Started
1. Each folder contains notebooks, guides, and code for the research paper
2. Run the interactive notebook for visualizations


### Key Resources
- **BERT Folder**: `/bert/` - Progressive exploration from Word2Vec to RAG
- **Scaling Laws Folder**: `/scaling laws/` - Complete implementation with code
- **This README**: Overview and connection between papers

---

## 📝 Notes

- Each paper builds on previous understanding
- Scaling Laws is critical for understanding modern LLM design decisions
- Connect findings back to BERT's architecture and training approach

---

**Last Updated**: April 4, 2026 | **Current**: Week 2 of 15 | **Next**: PPO (Week 3)
