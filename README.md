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



### 5: Mixtral of Experts - Sparse Mixture of Experts Language Model

**Authors:** Albert Q. Jiang, Alexandre Sablayrolles, Antoine Roux, Arthur Mensch, Blanche Savary, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Emma Bou Hanna, Florian Bressand, and 16 others from Mistral AI

**Publication:** January 2024
**Location**: `/mixtral-deepdive/`

#### Key Insights
Mixtral 8x7B demonstrates that **sparse mixture-of-experts (MoE) architecture achieves state-of-the-art performance with high efficiency**. Only 2 of 8 experts are activated per token, enabling 3.6x faster inference than 70B dense models while maintaining superior quality.

**Key Metrics:**
- **Total Parameters:** 47B
- **Active Parameters per Token:** 13B (only ~28% active)
- **Performance:** Outperforms Llama 2 70B and GPT-3.5 on multiple benchmarks
- **Inference Speed:** 3.6x faster than 70B dense models
- **Specialization:** Experts automatically specialize on different domains (code, math, language, reasoning)

**Architecture Highlights:**
- **Sparse Routing:** Top-2 expert selection per token (vs Top-1 in Switch Transformers)
- **Load Balancing:** Auxiliary loss prevents expert collapse
- **Expert Pool:** 8 independent feedforward experts (d_model=4096, d_hidden=14336)
- **Attention:** Dense (not sparse) multi-head attention layer
- **Temperature Scaling:** Controls routing sharpness during training vs inference
- **Capacity Management:** Hard limits prevent expert overload

**Training Innovations:**
- Load balancing with auxiliary loss (prevents all tokens going to same expert)
- Softmax temperature annealing (soft routing early, sharp routing late)
- Importance-weighted load balancing (experts specialize naturally)
- Capacity management (bounded expert load)

**Real-World Impact:**
- More accessible than 70B models (runs on consumer GPUs with quantization)
- Better code generation than GPT-3.5
- Strong mathematical reasoning
- Excellent multilingual performance

**Links:**
- 📄 **ArXiv:** https://arxiv.org/abs/2401.04088
- 📄 **PDF:** https://arxiv.org/pdf/2401.04088
- 🤗 **HuggingFace:** https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
- 🔍 **Semantic Scholar:** https://www.semanticscholar.org/paper/Mixtral-of-Experts-Jiang-Sablayrolles/411114f989a3d1083d90afd265103132fee94ebe

---

### 6: DeepSeek-R1 - Reasoning Optimization via GRPO and Process Rewards

**Authors:** DeepSeek Team

**Publication:** January 2025
**Location**: `/deepseek-r1/`

#### Key Insights
DeepSeek-R1 revolutionizes reasoning in language models through **Group Relative Policy Optimization (GRPO)** and **Process Reward Models**. Rather than optimizing for final answer correctness alone, it rewards the entire reasoning chain—achieving human-level performance on complex reasoning tasks while scaling efficiently.

**Core Innovation: GRPO (Group Relative Policy Optimization)**
- Unlike standard policy gradients that use fixed baselines, GRPO uses **group-relative rewards**
- Compare each reasoning attempt against the group mean rather than a fixed baseline
- Reduces variance without explicit value function training
- More stable and sample-efficient than PPO for reasoning tasks

**Architecture Highlights:**
- **Process Reward Model:** Evaluates intermediate reasoning steps, not just final answers
- **Group Sampling:** Multiple attempts per problem enable relative comparison
- **Compute-Optimal Scaling:** Demonstrates reasoning time can substitute for model size
- **Emergent Capabilities:** Long-chain reasoning emerges from training signal

**Training Pipeline:**
1. Supervised Fine-Tuning (SFT) on reasoning trajectories
2. Process Reward Model training from human preference annotations
3. GRPO optimization using group-relative advantages
4. Iterative refinement with harder problems and longer reasoning chains

**Key Differences from RLHF:**
- **RLHF:** Trains reward model on final answer preferences, uses PPO
- **GRPO:** Trains reward model on step-level feedback, uses group-relative comparisons
- **Result:** GRPO is more sample-efficient for reasoning-heavy tasks

**Real-World Impact:**
- Demonstrates that reasoning capability is teachable through RL
- Shows compute-performance trade-off: more reasoning time → better accuracy
- Enables open-source reasoning models competitive with proprietary systems
- Applicable to any task where intermediate steps matter (code, math, planning)

**Links:**
- 📄 **ArXiv:** https://arxiv.org/abs/2501.xxxxx (check official DeepSeek repo)
- 📖 **Blog Post:** https://deepseek.com/blog/deepseek-r1
- 🔧 **Official Repository:** https://github.com/deepseek-ai/DeepSeek-R1
- 📚 **Learning Materials:** `/deepseek-r1/` - Complete deep dive with implementations

---

## 🔗 Connection Between Papers

**BERT (2018)** → **Scaling Laws (2020)** → **Chain-of-Thought (2022)** → **DeepSeek-R1 (2025)**

- **BERT (2018)** showed that **scale matters** for model performance
- **Scaling Laws (2020)** quantified **exactly how much** scale matters
- **Chain-of-Thought (2022)** showed that **reasoning as text** improves complex task performance
- **DeepSeek-R1 (2025)** combines all insights: scale + reasoning + RL optimization to achieve state-of-the-art reasoning
- **Key Progression:** Pre-training → Understanding scale → Prompting for reasoning → Optimizing reasoning with RL

**Relationship to Other Papers:**
- **vs Mixtral:** Mixtral optimizes model efficiency through sparsity; DeepSeek-R1 optimizes reasoning through RL
- **vs ToT:** Tree of Thoughts searches multiple paths at inference; DeepSeek-R1 learns better reasoning during training
- **vs Scaling Laws:** Validates that reasoning time (compute) can improve performance as much as model size

---

## 🛠️ How to Use This Repository

### Getting Started
1. Each folder contains notebooks, guides, and code for the research paper
2. Run the interactive notebook for visualizations
3. **For DeepSeek-R1:** Start with `/rl-fundamentals/` for prerequisites, then `/deepseek-r1/` for the deep dive


### Recommended Learning Path
1. **BERT** (`/bert/`) - Understand transformer foundations
2. **Scaling Laws** (`/scaling laws/`) - Learn how scale affects performance
3. **Chain-of-Thought** (`/chain-of-thought/`) - Understand reasoning prompting
4. **RL Fundamentals** (`/rl-fundamentals/`) - Master policy gradients and actor-critic methods
5. **DeepSeek-R1** (`/deepseek-r1/`) - Apply RL to reasoning optimization

### Key Resources
- **BERT Folder**: `/bert/` - Progressive exploration from Word2Vec to RAG
- **Scaling Laws Folder**: `/scaling laws/` - Complete implementation with code
- **RL Fundamentals**: `/rl-fundamentals/` - 5 phases covering RL theory and practice (5.5 hours)
- **DeepSeek-R1 Deep Dive**: `/deepseek-r1/` - Prerequisites guide, comprehensive materials, and implementations
- **This README**: Overview and connection between papers

### Time Estimates
- **BERT**: 2-3 hours
- **Scaling Laws**: 1-2 hours
- **Chain-of-Thought**: 1-2 hours
- **RL Fundamentals**: 5.5 hours (can skip Phase 3-4 if pressed for time)
- **DeepSeek-R1**: 4-6 hours (including paper reading and code exploration)
- **Total**: ~15-20 hours for complete understanding

---

## 📝 Notes

- Each paper builds on previous understanding
- Scaling Laws is critical for understanding modern LLM design decisions
- RL Fundamentals (especially Phase 2: Policy Gradients) is essential before DeepSeek-R1
- DeepSeek-R1 represents the cutting edge of reasoning optimization in language models
- Materials include both educational implementations and production-ready concepts

---