# DeepSeek-R1: Prerequisite Reading Guide

## How to Use This Guide

**🔴 Critical (Must Read):** Essential for understanding DeepSeek-R1  
**🟡 Important (Highly Recommended):** Fills major gaps in understanding  
**🟢 Helpful (Nice to Have):** Deepens specific aspects  
**⚪ Background (Optional):** General ML knowledge  

---

## Tier 1: Critical Prerequisites 🔴

### 1. **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models**
- **Authors:** Wei et al., 2022
- **Title:** "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- **Why:** DeepSeek-R1 builds directly on CoT. Understanding why explicit reasoning helps is foundational.
- **Key Concepts:**
  - CoT prompts improve reasoning
  - Models learn to show work
  - Why intermediate steps matter
- **Reading Time:** 20 minutes
- **Importance:** ⭐⭐⭐⭐⭐

### 2. **Proximal Policy Optimization Algorithms**
- **Authors:** Schulman et al., 2017
- **Title:** "Proximal Policy Optimization Algorithms"
- **Why:** PPO is the foundation for understanding GRPO. DeepSeek-R1's GRPO is a variant designed for language models.
- **Key Concepts:**
  - Policy gradient methods
  - Advantage estimation
  - Trust region optimization
  - Stability in RL training
- **Reading Time:** 45 minutes
- **Importance:** ⭐⭐⭐⭐⭐

### 3. **Training Language Models to Follow Instructions with Human Feedback**
- **Authors:** Ouyang et al., 2022 (InstructGPT / ChatGPT paper)
- **Title:** "Training Language Models to Follow Instructions with Human Feedback"
- **Why:** This introduced RLHF, which uses RL on LLMs. DeepSeek-R1 applies similar ideas but for reasoning.
- **Key Concepts:**
  - Reward modeling
  - RLHF algorithm
  - Alignment through RL
  - How RL works at LLM scale
- **Reading Time:** 30 minutes
- **Importance:** ⭐⭐⭐⭐⭐

---

## Tier 2: Important Papers 🟡

### 4. **Attention Is All You Need**
- **Authors:** Vaswani et al., 2017
- **Title:** "Attention Is All You Need"
- **Why:** Foundation of transformers. You need to understand transformer architecture basics.
- **Key Concepts:**
  - Self-attention mechanism
  - Transformer architecture
  - Positional encoding
  - Layer normalization
- **Reading Time:** 60 minutes
- **Importance:** ⭐⭐⭐⭐
- **Note:** Only read Sections 1-3 if short on time

### 5. **Let's Verify Step by Step**
- **Authors:** Lightman et al., 2023
- **Title:** "Let's Verify Step by Step"
- **Why:** Introduces Process Reward Models (PRM) for evaluating reasoning steps. Complements DeepSeek-R1's outcome-based rewards.
- **Key Concepts:**
  - Process rewards vs outcome rewards
  - Reward models for intermediate steps
  - Better guidance for reasoning
- **Reading Time:** 25 minutes
- **Importance:** ⭐⭐⭐⭐

### 6. **Emergent Abilities of Large Language Models**
- **Authors:** Wei et al., 2022
- **Title:** "Emergent Abilities of Large Language Models"
- **Why:** Explains scaling laws and emergent abilities. DeepSeek-R1 shows new scaling laws for reasoning via RL.
- **Key Concepts:**
  - Scaling laws for LLMs
  - Emergent abilities
  - In-context learning
  - Why bigger models are better
- **Reading Time:** 30 minutes
- **Importance:** ⭐⭐⭐⭐

### 7. **Scaling Laws for Neural Language Models**
- **Authors:** Hoffmann et al., 2022 (DeepMind)
- **Title:** "Scaling Laws for Neural Language Models"
- **Why:** DeepSeek-R1 paper discusses new scaling laws. Understanding compute-optimal training is helpful.
- **Key Concepts:**
  - Compute-optimal allocation
  - Scaling laws
  - Model size vs data
  - Training efficiency
- **Reading Time:** 40 minutes
- **Importance:** ⭐⭐⭐⭐

---

## Tier 3: Helpful Papers 🟢

### 8. **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding**
- **Authors:** Devlin et al., 2018
- **Title:** "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
- **Why:** Shows pre-training importance. Understanding why we use pre-trained models helps.
- **Key Concepts:**
  - Pre-training objectives
  - Fine-tuning for downstream tasks
  - Bidirectional context
- **Reading Time:** 40 minutes
- **Importance:** ⭐⭐⭐

### 9. **Language Models are Few-Shot Learners**
- **Authors:** Brown et al., 2020 (GPT-3)
- **Title:** "Language Models are Few-Shot Learners"
- **Why:** Shows why reasoning is hard for LLMs without help. Motivates DeepSeek-R1's approach.
- **Key Concepts:**
  - Few-shot learning
  - In-context learning
  - Scaling to 175B parameters
  - Why models struggle with reasoning
- **Reading Time:** 45 minutes
- **Importance:** ⭐⭐⭐

### 10. **The Curious Case of Neural Text Degeneration**
- **Authors:** Holtzman et al., 2019
- **Title:** "The Curious Case of Neural Text Degeneration"
- **Why:** Explains decoding strategies (top-k, nucleus sampling). Important for generating diverse reasoning chains during RL training.
- **Key Concepts:**
  - Decoding strategies
  - Sampling temperature
  - Why greedy decoding fails
  - Balancing diversity and quality
- **Reading Time:** 25 minutes
- **Importance:** ⭐⭐⭐

---

## Tier 4: Background Knowledge ⚪

### 11. **An Introduction to Policy Gradient Methods**
- **Not a specific paper** - Search for tutorials or lecture notes
- **Why:** General RL background if unfamiliar with policy gradients
- **Key Concepts:**
  - Policy gradients
  - Score function estimator
  - Variance reduction
- **Reading Time:** 60 minutes
- **Importance:** ⭐⭐ (only if RL is new to you)

### 12. **Reinforcement Learning: An Introduction**
- **Authors:** Sutton & Barto, 2018 (Book)
- **Chapters to focus on:** 1, 3, 5, 6, 12-13
- **Why:** Comprehensive RL fundamentals if you need refresher
- **Reading Time:** Several hours
- **Importance:** ⭐⭐ (reference material)

---

## Recommended Reading Order

### Path A: Fastest (Just the essentials - 2-3 hours)
1. Chain-of-Thought Prompting (20 min) 🔴
2. PPO Algorithms (45 min) 🔴
3. InstructGPT/RLHF (30 min) 🔴
4. **Read Phase 0-1 of deep dive**
5. DeepSeek-R1 paper

**Total prep time:** ~2.5 hours

### Path B: Comprehensive (Best understanding - 5-6 hours)
1. Chain-of-Thought Prompting (20 min) 🔴
2. Attention is All You Need (40 min - sections 1-3 only) 🟡
3. PPO Algorithms (45 min) 🔴
4. InstructGPT/RLHF (30 min) 🔴
5. Process Reward Models (25 min) 🟡
6. Emergent Abilities (30 min) 🟡
7. Scaling Laws (40 min) 🟡
8. **Read Phase 0-2 of deep dive**
9. DeepSeek-R1 paper

**Total prep time:** ~5-6 hours

### Path C: Deep Dive (Master level - 8+ hours)
Read all papers in Tiers 1-3 plus materials, in this order:
1. Attention Is All You Need (60 min) 🟡
2. GPT-3 (45 min) 🟢
3. Chain-of-Thought (20 min) 🔴
4. Emergent Abilities (30 min) 🟡
5. Scaling Laws (40 min) 🟡
6. PPO (45 min) 🔴
7. InstructGPT (30 min) 🔴
8. Process Rewards (25 min) 🟡
9. Decoding Strategies (25 min) 🟢
10. **Read all 4 phases of deep dive**
11. DeepSeek-R1 paper

**Total prep time:** ~8-10 hours

---

## Where to Find These Papers

### arXiv (Free)
- Search "arXiv [author name] [year]"
- Example: `arXiv Wei 2022 Chain-of-Thought`
- Link: https://arxiv.org/

### Direct Links (Most are freely available)

**Critical Papers:**
- CoT: https://arxiv.org/abs/2201.11903
- PPO: https://arxiv.org/abs/1707.06347
- InstructGPT: https://arxiv.org/abs/2203.02155

**Important Papers:**
- Transformers: https://arxiv.org/abs/1706.03762
- Process Rewards: https://arxiv.org/abs/2305.20050
- Emergent Abilities: https://arxiv.org/abs/2206.07682
- Scaling Laws: https://arxiv.org/abs/2203.15556

**Helpful Papers:**
- BERT: https://arxiv.org/abs/1810.04805
- GPT-3: https://arxiv.org/abs/2005.14165
- Text Degeneration: https://arxiv.org/abs/1910.14599

### Academic Databases
- Google Scholar: https://scholar.google.com/
- Semantic Scholar: https://www.semanticscholar.org/
- Papers with Code: https://paperswithcode.com/

---

## Reading Strategy Tips

### 1. **Skim First, Deep Read Second**
- First pass: Read abstract, introduction, conclusion (10-15 min)
- Identify key concepts
- Then deep read sections relevant to DeepSeek-R1

### 2. **Focus on These Sections**
For efficiency, prioritize:
- **Abstract:** Overview of contribution
- **Introduction:** Motivation and problem setup
- **Method/Algorithm:** The main technique (most important!)
- **Experiments:** Results and analysis
- **Conclusion:** Key takeaways

Skip detailed proofs unless researching specific aspects.

### 3. **Take Notes**
For each paper, write down:
- Main contribution (1 sentence)
- Key techniques/algorithms
- Key results
- How it relates to DeepSeek-R1

### 4. **Visual Learning**
Many papers have helpful diagrams. Spend time understanding:
- Algorithm flowcharts
- Architecture diagrams
- Performance graphs
- Mathematical notation

### 5. **Watch Video Summaries (Optional)**
YouTube has many paper summaries:
- Search "[paper title] explained" or "[author] [year] paper"
- Watch at 1.5x speed for efficiency
- **Examples:**
  - "Attention is All You Need Explained" (~30 min)
  - "PPO Explained" (~20 min)
  - "Chain of Thought Prompting" (~15 min)

---

## Quick Reference: What Each Paper Teaches

| Paper | Key Takeaway for DeepSeek-R1 |
|-------|------------------------------|
| Chain-of-Thought | Why reasoning steps matter |
| PPO | Foundation of GRPO algorithm |
| InstructGPT | How to use RL on LLMs |
| Transformers | Architecture of the base model |
| Process Rewards | Alternative to outcome rewards |
| Emergent Abilities | Why bigger models work better |
| Scaling Laws | Compute-optimal training |
| BERT | Pre-training importance |
| GPT-3 | Reasoning limitations in LLMs |
| Text Degeneration | Sampling during generation |

---

## FAQ: Do I Really Need All These?

### "I'm short on time"
→ **Minimum:** Read Tier 1 papers (Chain-of-Thought, PPO, InstructGPT) = ~95 minutes

### "I'm new to RL"
→ **Add:** PPO explanation + background on policy gradients = extra 30 minutes

### "I don't know transformers"
→ **Add:** Attention is All You Need (full) = extra 60 minutes

### "I want to implement DeepSeek-R1"
→ **Read all Tier 1 + Tier 2** + our deep dive materials

### "I just want intuition"
→ **Read:** Chain-of-Thought + InstructGPT + Phase 0-1 of deep dive = ~90 minutes total

---

## Integration with This Learning Material

### How This Reading List Aligns with Our Deep Dive

- **Phase 0** covers all the intuition from Tier 1 papers
- **Phase 1** implements concepts from Chain-of-Thought + basic RL
- **Phase 2** implements GRPO (combines PPO + InstructGPT)
- **Phase 3** applies to problems (uses all papers' concepts)

**You don't need to read all papers before starting!** Start with Chain-of-Thought + InstructGPT, then begin our materials.

---

## Next Steps

1. **Pick your path** (A, B, or C above)
2. **Start reading** the Tier 1 papers (prioritize these!)
3. **As you read**, start Phase 0 of the deep dive
4. **Cross-reference** concepts between papers and our materials
5. **Then read** DeepSeek-R1 paper with full understanding

---

## Cheat Sheet: Key Concepts from Prerequisites

### From Chain-of-Thought
```
Problem: Why do models struggle with reasoning?
Answer: They don't decompose problems into steps
Solution: Teach them to show intermediate reasoning
DeepSeek-R1 connection: Uses RL to reward this behavior
```

### From PPO
```
Key Algorithm: Trust Region Optimization
Main Idea: Don't change policy too drastically per update
Implementation: Clipped objective function
DeepSeek-R1 connection: GRPO builds on PPO but optimized for LLMs
```

### From InstructGPT
```
Key Algorithm: RLHF (Reward Model + RL)
Main Idea: Train model with human feedback via RL
Challenge: Stability at scale
DeepSeek-R1 connection: Uses automatic reward (correctness) instead of model
```

### From Scaling Laws
```
Main Finding: Bigger models are better (obvious now!)
But also: Computing scales in specific ways
Training vs inference trade-offs matter
DeepSeek-R1 connection: Shows new scaling laws for reasoning via RL
```

---

## Estimate Your Starting Point

**Rate your familiarity (1-5):**
- Transformers: ___
- Reinforcement Learning: ___
- Language Models: ___
- RLHF / Instruction Tuning: ___

**Total Score:**
- **4-7:** Start with Path A (2-3 hours prep)
- **8-12:** Start with Path B (5-6 hours prep)
- **13-16:** Start with Path C (8+ hours prep)
- **17-20:** Jump straight to Phase 2 of deep dive + paper

---

## Final Advice

> **The perfect is the enemy of the good.** Don't wait to read everything before starting! Read Chain-of-Thought + Phase 0 of our deep dive, then continue learning as you go.

Good luck! 🚀
