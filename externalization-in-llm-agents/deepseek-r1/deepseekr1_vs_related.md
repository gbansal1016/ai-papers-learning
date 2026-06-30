# DeepSeek-R1 vs Related Work

## Comparison with Similar Research

This document compares DeepSeek-R1 with related approaches to reasoning in language models.

---

## 1. DeepSeek-R1 vs Chain-of-Thought Prompting

### Chain-of-Thought (Wei et al., 2022)

**Approach:**
- Demonstrate step-by-step reasoning in prompts
- Model learns to imitate this pattern
- Purely supervised learning

**Strengths:**
- Simple and intuitive
- Works with any model
- No training required
- Easy to implement

**Weaknesses:**
- Limited by quality of examples
- Requires hand-crafted demonstrations
- Doesn't improve with scale
- Reasoning pattern is fixed

### DeepSeek-R1

**Approach:**
- Use RL to reward correct answers
- Model discovers its own reasoning strategies
- Learns from reward signal, not examples

**Strengths:**
- More scalable (works with larger models)
- Adaptive reasoning (varies by problem)
- Emerges naturally from reward signal
- Continues improving with more data
- No need for human demonstrations

**Weaknesses:**
- Requires reward function design
- More complex training procedure
- Computational cost of RL training
- Less interpretable reasoning chains

### Direct Comparison

```
Aspect              | CoT           | DeepSeek-R1
--------------------|---------------|------------------
Supervision         | Demonstration | Reward signal
Scalability         | Limited       | Good
Adaptation          | Fixed         | Adaptive
Training Cost       | Minimal       | Moderate
Inference Cost      | Variable      | Variable
Generalization      | Poor          | Good
Human Effort        | High (labels) | Moderate (reward)
Emerging Behavior   | No            | Yes
```

---

## 2. DeepSeek-R1 vs Process Reward Models

### Process Reward Models (Lightman et al., 2023)

**Approach:**
- Train model to score each intermediate step
- Use process scores for RL training
- Rewards for correct reasoning process

**Strengths:**
- More fine-grained feedback
- Rewards intermediate steps
- Can learn from partial attempts
- Better interpretability

**Weaknesses:**
- Requires labeled intermediate steps
- More expensive to train
- Complex reward function
- More hyperparameters

### DeepSeek-R1

**Approach:**
- Simple final-answer reward (often)
- Uses GRPO for efficient optimization
- Can incorporate process rewards optionally

**Strengths:**
- Simpler reward design
- Fewer hyperparameters
- More sample-efficient
- Clearer learning signal
- Works with just 1-bit feedback

**Weaknesses:**
- Less guided by intermediate steps
- Might learn inefficient reasoning
- Harder to debug

### Hybrid Approach

DeepSeek-R1 can be enhanced with process rewards:
- Final answer reward: 1.0 if correct, 0.0 otherwise
- Process reward bonus: +0.1 for each step if on right track

---

## 3. DeepSeek-R1 vs RLHF

### Reinforcement Learning from Human Feedback (RLHF)

**Approach (InstructGPT, ChatGPT):**
- Train reward model on human preferences
- Use RL (PPO) to optimize for reward model
- Focus: instruction following and alignment

**Strengths:**
- Aligns model with human values
- Improves instruction following
- Proven effective in practice
- Reasonable computational cost

**Weaknesses:**
- Not designed for reasoning
- Requires human annotation
- Reward model can be unreliable
- Less stable training

### DeepSeek-R1

**Approach:**
- Task-specific automatic reward (correctness)
- Use RL (GRPO) to optimize
- Focus: reasoning accuracy

**Strengths:**
- Automatic, objective rewards
- Stable training (GRPO designed for this)
- Better for reasoning tasks
- More sample-efficient

**Weaknesses:**
- Doesn't capture human preferences
- Only works for tasks with clear rewards
- Different reward function per task

### When to Use Each

- **RLHF:** General instruction following, alignment, safety
- **DeepSeek-R1:** Math, logic, code, any task with clear correctness

---

## 4. DeepSeek-R1 vs Supervised Fine-Tuning (SFT)

### Supervised Fine-Tuning (Standard)

**Approach:**
- Collect dataset of (problem, reasoning, answer)
- Train model to imitate dataset
- Single pass, no RL

**Strengths:**
- Simple training procedure
- Predictable behavior
- Easy to implement
- Works with standard tools

**Weaknesses:**
- Limited by dataset quality
- Reasoning pattern is fixed
- Doesn't improve with scale
- Sample inefficient
- Reasoning length is wasted on easy problems

### DeepSeek-R1

**Approach:**
- Define reward for correctness
- Use RL to optimize
- Adaptive reasoning

**Strengths:**
- Learns beyond dataset
- Adaptive reasoning depth
- Improves with scale
- More sample-efficient
- Optimal reasoning per problem

**Weaknesses:**
- More complex training
- Requires reward engineering
- Longer training time
- Less predictable initially

### Scaling Laws Comparison

```
Training Stage  | SFT Accuracy | R1 Accuracy
-----------------|-------------|-------------
After phase 1   | 70%         | 60%
After phase 2   | 78%         | 75%
After phase 3   | 82%         | 88%
After phase 4   | 83%         | 92%
```

DeepSeek-R1 accelerates over time!

---

## 5. DeepSeek-R1 vs Search-Based Methods

### Tree/Graph Search (AlphaZero-style)

**Approach:**
- Use search algorithm to explore solution space
- Evaluate each path with value function
- No gradient-based training

**Strengths:**
- Can explore many solutions
- Provably optimal for some tasks
- Interpretable search process
- Works without training

**Weaknesses:**
- Very slow at inference time
- Requires domain-specific search
- Doesn't learn from examples
- Computational cost is prohibitive

### DeepSeek-R1

**Approach:**
- Learning-based generation of reasoning
- No explicit search, just neural sampling
- Training with RL

**Strengths:**
- Fast inference
- Learns patterns efficiently
- Generalizes across problems
- No domain-specific search needed

**Weaknesses:**
- Might miss optimal solutions
- Can get stuck in local modes
- Less rigorous than search

### Hybrid Possibility

Could combine:
- DeepSeek-R1 for fast initial generation
- Limited search for hard problems
- Best of both worlds

---

## 6. DeepSeek-R1 vs Test-Time Scaling

### Test-Time Scaling (Recent Work)

**Approach:**
- Train standard model (SFT)
- At test time, generate many attempts and vote
- Compute expensive but effective

**Strengths:**
- Simple to implement
- Works with existing models
- Improves performance at test time
- No retraining needed

**Weaknesses:**
- Very expensive at inference
- Random sampling (not optimized)
- Doesn't adapt reasoning strategy
- No learning of better strategies

### DeepSeek-R1

**Approach:**
- Train with RL to optimize reasoning
- Model learns best reasoning strategy
- More efficient inference

**Strengths:**
- More efficient reasoning
- Learns strategies, not just attempts
- Can adapt reasoning per problem
- Better sample efficiency

**Weaknesses:**
- Requires RL training
- Can't be applied to existing models

---

## 7. Related Techniques Comparison Table

| Technique | Reasoning | Adaptive | Scalable | Training Cost | Inference Cost | Comments |
|-----------|-----------|----------|----------|---------------|----------------|----------|
| CoT Prompt | ✓ | ✗ | ✗ | None | Fast | Baseline |
| Process Reward | ✓ | ✓ | ✓ | High | Medium | Fine-grained rewards |
| RLHF | ✓ | ✓ | ✓ | Medium | Medium | General alignment |
| SFT | ✓ | ✗ | ✗ | Low | Fast | Limited |
| Search | ✓✓ | ✓✓ | ✗ | None | Very High | Rigorous but slow |
| Test-Time Voting | ✓ | ✗ | ✗ | None | Very High | Simple but expensive |
| **DeepSeek-R1** | **✓✓** | **✓✓** | **✓✓** | **Medium** | **Medium** | **Best balance** |

---

## 8. Key Innovations of DeepSeek-R1

### 1. **GRPO Algorithm**
- Group Relative Policy Optimization
- More stable than standard PPO
- Designed specifically for language models
- Better sample efficiency

### 2. **Minimal Supervision**
- Only needs 1-bit reward (correct/incorrect)
- No intermediate step labels
- Scales to new domains easily

### 3. **Emergent Reasoning**
- Reasoning strategies emerge naturally
- Not forced into human-designed patterns
- Can discover novel approaches

### 4. **Scaling Properties**
- Performance improves with model size
- Continues improving beyond SFT plateau
- Reasoning depth scales automatically

### 5. **Generalization**
- Works across reasoning domains
- Transfers to unseen problem types
- Doesn't require task-specific tuning

---

## 9. Future Directions

### Combinations & Extensions

**Process + Outcome Rewards**
- Combine with process reward models
- Better guidance for complex reasoning
- Hybrid approach benefits

**Self-Play**
- Models generate both attempts and evaluations
- Competitive improvement
- Reduces annotation burden

**Curriculum Learning**
- Start with easy problems
- Gradually increase difficulty
- Better sample efficiency

**Multi-Task Learning**
- Train on diverse reasoning tasks
- Shared reasoning capabilities
- Better generalization

**Meta-Learning**
- Learn how to learn rewards
- Automatic reward function design
- Adapt to new domains quickly

---

## 10. When to Choose DeepSeek-R1

### Use DeepSeek-R1 if:
- ✅ Task has clear correctness evaluation
- ✅ Want adaptive reasoning depth
- ✅ Need to scale with model size
- ✅ Want to improve beyond SFT
- ✅ Have access to compute for RL training
- ✅ Want emerging behaviors

### Use Alternative if:
- ❌ Task has subjective evaluation (use RLHF)
- ❌ Need fast training (use SFT)
- ❌ Need interpretable search (use search methods)
- ❌ Need to work with existing models (use CoT)
- ❌ Task requires rigorous solutions (use search)

---

## Summary

DeepSeek-R1 combines:
1. **GRPO** algorithm - stable, efficient RL
2. **Minimal supervision** - just rewards, not examples
3. **Scaling benefits** - improves with model size
4. **Adaptive reasoning** - different depth per problem
5. **Emergence** - discovers strategies naturally

Making it the **best approach for reasoning tasks** when:
- You can evaluate correctness automatically
- You have compute for RL training
- You want models that improve with scale
- You want adaptive, efficient reasoning

---

**Conclusion:** DeepSeek-R1 is not a minor improvement on CoT or RLHF—it's a fundamentally different approach that achieves better results through better incentives.
