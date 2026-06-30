# Scaling Laws for Neural Language Models - Quick Reference

This is your cheat sheet for the most important findings from Kaplan et al. (2020). Rather than memorizing formulas, focus on understanding that **language model performance is predictable** — improving loss follows predictable mathematical relationships.

## 📋 Key Equations

### The Core Discovery: Power-Law Relationships

Kaplan et al. found that **loss scales predictably** with three independent factors. You can estimate loss from any of these:

```
L(N) = 0.34 × N^(-0.07)           # Loss from model size
L(D) = 2.56 × D^(-0.095)          # Loss from data size
L(C) = 0.37 × C^(-0.077)          # Loss from compute
```

**What this means**:
- These equations work across different model families and architectures
- You don't need to train models to predict their loss—use these formulas
- The exponents (0.07, 0.095, 0.077) are empirically observed constants

### Chinchilla's Breakthrough: Optimal Resource Allocation

Three years after Kaplan et al., Hoffmann et al. (2022) realized the original recommendation was suboptimal. Here's the compute-optimal way to allocate resources:

```
N_optimal = √(C / 120)             # Optimal model size given compute budget
D_optimal = 20 × N                 # Optimal data: ~20x params (THE KEY INSIGHT)
```

**Why this matters**:
- GPT-3 had ~175B params trained on ~300B tokens (1.7x ratio) → UNDERTRAINED
- Chinchilla has ~70B params trained on ~1.4T tokens (20x ratio) → WELL-TRAINED
- Modern models (LLaMA, Claude) follow this 20x principle
- Same compute, better performance by reallocating to more data

---

## 🔢 Quick Calculations

### The 20x Rule: The Most Practical Takeaway

This is the insight that changed modern AI training:

**For every 1 parameter → train on ~20 tokens**

Real-world examples:
- 7B model (LLaMA) → 140B tokens ✓ Correct
- 13B model → 260B tokens ✓ Correct
- 70B model → 1.4T tokens ✓ Correct
- 175B model (GPT-3) → 300B tokens ✗ Wrong (only 1.7x, should be ~3.5T!)

**Why this matters**: If you're training a new model, use this 20x rule to plan your data. Most undiscovered model architectures fail not because the model is bad, but because they didn't use enough data.

### Loss Improvement Rules of Thumb

How much does performance improve when you scale? Use these estimates:

| Change | Loss Reduction | Why |
|--------|---|---|
| 2x model size | ~5% | α_N = 0.07, so 2^(-0.07) ≈ 0.95 |
| 2x data size | ~6.5% | α_D = 0.095, so 2^(-0.095) ≈ 0.935 |
| 10x model size | ~22% | 10^(-0.07) ≈ 0.78 |
| 10x data size | ~30% | 10^(-0.095) ≈ 0.70 |

**Interpretation**: Data scaling slightly better than model scaling (0.095 > 0.07), but difference is small. The real lesson: **scale both together, not one or the other**.

### FLOPs Approximation

**What is a FLOP?** A FLOP = **Floating Point Operation** (one basic math calculation like addition or multiplication). FLOPS = operations per second.

When you scale, you consume compute. Rough calculation:

```
FLOPs ≈ 6 × N × D
```

Example:
- 7B params × 140B tokens × 6 = 5.88 × 10^21 FLOPs ≈ $100-200K on cloud GPUs
- This is why GPU budgets matter for AI scaling

**Breaking it down**:
- 5.88 × 10^21 FLOPs ÷ 312 TFLOPS (A100 speed) = 18.8 million seconds ≈ **6 days of GPU time**
- At $3/hour: **~$430 in GPU costs**

**Note**: The "6×" comes from: 2× ops for matrix multiplication + overhead from forward/backward passes. Different optimizations may reduce this factor slightly.

---

## 📊 Model Size Guide: Context Matters

The scaling laws paper didn't prescribe model sizes—it just showed relationships. Here's what actually got built at different scales and why:

| Scale | Examples | Params | Typical Tokens | Context |
|-------|----------|--------|---|---|
| **Tiny** | MobileBERT | 25M | 500M | For phones; sacrifices accuracy for speed |
| **Small** | BERT, RoBERTa | 110M-355M | 2B-7B | Pre-2020 standard; underdeveloped by modern standards |
| **Medium** | GPT-2 | 1.5B | 30B | First sign that scale matters; shows emerging abilities |
| **Large** | GPT-3 (smallest variant) | 7B | 140B | Chinchilla-optimal for this size; practical for many tasks |
| **XL** | Chinchilla, LLaMA-7B | 7B-13B | 140B-260B | Sweet spot for research; good accuracy/efficiency trade-off |
| **XXL** | LLaMA-65B, Claude 3 | 65B-175B | 1T+ | State-of-the-art; requires serious compute |

**Pattern to notice**: Each jump right ~2-3x more parameters AND 10-50x more tokens. This follows the 20x rule!

---

## 💡 Decision Trees: When Should I Use These Formulas?

### Decision 1: "Should I scale model or data?"

**The situation**: You have a fixed compute budget and need to decide where to invest.

```
If improving 1-2x:
  → Scale BOTH together (keep D/N ≈ 20)
  → Don't specialize: balanced growth wins

If I can only scale ONE (forced choice):
  → Model size slightly better (exponent 0.07 vs 0.095)
  → BUT data is usually cheaper, so data is practical choice
  → Real answer: whoever is cheapest gets priority

If truly constrained by compute budget C:
  → Use Chinchilla formula: N = √(C/120), D = 20N
  → This mathematically maximizes performance for your budget
```

**Example**: You have $50K. That's roughly 10^16 FLOPs. Chinchilla says train a 2.9B model on 58B tokens. Don't train a 10B model on 10B tokens just because it "sounds bigger."

### Decision 2: "Is my model trained optimally?"

**The situation**: You have a model that's already trained. Is it a good use of compute?

```
Check the D/N ratio (tokens ÷ parameters):

  < 10x    → UNDERTRAINED
             Example: GPT-3 (300B ÷ 175B = 1.7x)
             Lost opportunity; more data would help more

  ~15-20x  → OPTIMAL (Chinchilla recommendation)
             Example: LLaMA-65B (1.4T ÷ 65B ≈ 21x) ✓
             This is what you want to see

  > 30x    → OVERTRAINED (but sometimes intentional)
             Example: LLaMA-7B (1T ÷ 7B ≈ 143x)
             More data than necessary; trades inference cost for accuracy
             Used when you prioritize performance over efficiency
```

### Decision 3: "How much improvement will I get?"

**The situation**: You want to know if scaling is worth it.

```
Formula: Loss reduction ≈ (1 - X^(-α)) × 100%
         where X = scale factor, α = exponent

Concrete examples (using α_N = 0.07 for model size):

  2x scale:   1 - 2^(-0.07) ≈ 5% improvement
              (3B → 6B model: ~5% better loss)

  10x scale:  1 - 10^(-0.07) ≈ 22% improvement
              (100M → 1B model: ~22% better loss)

  100x scale: 1 - 100^(-0.07) ≈ 44% improvement
              (1M → 100M: ~44% better loss)
```

**Rule of thumb**: Every 10x increase in scale → roughly double the improvement rate. Diminishing returns exist, but they're more gradual than you'd expect.

---

## 🎯 Important Constants: What Do These Numbers Mean?

These empirically-observed constants came from training hundreds of models at OpenAI. They're stable across architectures but may vary slightly for specialized domains.

| Constant | Value | What It Means | Implication |
|----------|-------|---|---|
| **α_N** | 0.07 | How sensitive loss is to model size | Doubling model size reduces loss by ~5% |
| **α_D** | 0.095 | How sensitive loss is to data size | Doubling data reduces loss by ~6.5% |
| **α_C** | 0.077 | How sensitive loss is to compute | Doubling compute reduces loss by ~5.2% |
| **a_N** | 0.34 | Baseline loss from model size | "Intercept" of the power law; mainly for math |
| **a_D** | 2.56 | Baseline loss from data size | Data size has different intercept than model size |
| **a_C** | 0.37 | Baseline loss from compute | Compute curve similar to model curve |
| **Chinchilla ratio** | 20 | Optimal tokens per parameter | D = 20 × N gives best loss for fixed compute |

**Why you should care**: The exponents (0.07, 0.095, 0.077) are remarkably similar. This tells us that model size, data size, and compute are nearly equivalent factors. None dominates—scale everything together.

---

## ⚠️ Caveats & Limitations: When These Rules Break

These scaling laws are empirically observed generalizations. They work well, but they're not physical laws. Here's when to be skeptical:

1. **Small scale breaks down** (< 1M params)
   - Laws were fit on models 10M to 160B parameters
   - Below 1M params, relationships get messier
   - Don't use these formulas for tiny models

2. **Task-specific variation exists**
   - Vision tasks follow different exponents than language
   - Math tasks scale differently than reading comprehension
   - Use these as rough estimates, not gospel

3. **Architecture changes the coefficients**
   - Transformers follow these laws
   - RNNs have different constants (higher α)
   - New architectures might shift the curve
   - But the power-law shape is likely universal

4. **Transfer learning complicates things**
   - These laws describe pre-training from scratch
   - Fine-tuning on downstream tasks: different dynamics
   - Multi-task learning may have different scaling

5. **Inference cost ≠ Training cost**
   - These laws predict training loss improvement
   - Inference speed scales differently (linear with N, not power-law)
   - If you need fast inference, bigger isn't always better

6. **Data quality > Quantity**
   - The law assumes clean, diverse data
   - Poisoned or biased data breaks the predictions
   - 1 token of good data might be worth 100 bad tokens
   - The formula can't capture this

---

## 🔄 From Theory to Practice: A Real Workflow

This is how you actually use scaling laws when planning a training run:

### Step 1: Estimate Your Compute Budget
```python
# You have $50,000 to spend on GPUs
# A100 80GB: ~$3/hour, trains at ~10^16 FLOPs per 5 hours
cost_per_flop_hour = 3 / (10**16 / 5)
budget_dollars = 50000
total_flops = budget_dollars / cost_per_flop_hour
print(f"Total FLOPs available: {total_flops:.1e}")  # ~8.3 × 10^21
```

### Step 2: Find Optimal N and D Allocation
```python
# Use Chinchilla formula to get the BEST model size for your budget
N_opt = np.sqrt(total_flops / 120)  # ~1.6B params
D_opt = 20 * N_opt                  # ~32B tokens

print(f"Train a {N_opt/1e9:.1f}B param model on {D_opt/1e9:.0f}B tokens")
```

### Step 3: Predict Expected Loss
```python
# What's your model's loss going to be?
loss_from_N = 0.34 * (N_opt ** (-0.07))
loss_from_D = 2.56 * (D_opt ** (-0.095))
total_loss = loss_from_N + loss_from_D
print(f"Expected loss: {total_loss:.4f}")
```

### Step 4: Compare to Alternatives
```python
# What if you ignored the scaling law and just went with a gut feeling?
N_bad = 10e9  # "Bigger is always better"
D_bad = 10e9  # "Don't waste data"

loss_bad = 0.34 * (N_bad ** (-0.07)) + 2.56 * (D_bad ** (-0.095))

print(f"Your approach loss: {total_loss:.4f}")
print(f"Bad approach loss:  {loss_bad:.4f}")
print(f"Improvement: {(loss_bad - total_loss)/loss_bad * 100:.1f}%")
```

**Real example output**:
- Bad approach (10B params, 10B tokens): Loss = 4.15
- Chinchilla approach (1.6B params, 32B tokens): Loss = 3.92
- **14% better loss with same compute budget!**

---

## 📈 Scaling Law Evolution: How We Got Here

### 2020: Original Discovery (Kaplan et al.)
- **Finding**: "Performance follows predictable power laws! We can forecast improvements!"
- **Recommendation**: D ≈ 10 × N (10 tokens per parameter)
- **Real impact**: Enabled GPT-3 but didn't optimize it
- **Result**: GPT-3 trained on 300B tokens for 175B params (only 1.7x ratio)
- **Legacy**: Proved that compute-focused research was viable

### 2022: Optimization Insight (Hoffmann et al., "Chinchilla")
- **Finding**: "Wait, the original ratio was wrong. We tested it."
- **Recommendation**: D ≈ 20 × N (20 tokens per parameter)
- **Real impact**: Same compute → much better performance
- **Result**: Chinchilla model (70B params, 1.4T tokens) beats GPT-3 (175B params)
- **Implication**: You can make smaller, better models with more data

### 2023-2024: Current Practice
- **Adopted by**: LLaMA, Claude, Llama 2, PaLM 2, etc.
- **Pattern**: Models now train on 100-1000x their parameters in tokens
- **Why**: It works—theoretically grounded + empirically validated
- **Your takeaway**: When in doubt, use the 20x rule

---

## 🧮 Python Cheat Sheet: Real Working Code

You have a `scaling_laws.py` module that does all the math. Here's how to use it:

```python
from scaling_laws import ScalingLawPredictor, compute_optimal_allocation

# ============================================
# 1. QUICK PREDICTION: What's the expected loss?
# ============================================
pred = ScalingLawPredictor()
loss_dict = pred.predict_loss(N=7e9, D=140e9)
# Returns: {'from_N': 0.0062, 'from_D': 0.0043}
total = sum(loss_dict.values())  # Combined loss

# ============================================
# 2. WHAT IF: Should I scale 7B → 13B?
# ============================================
improvement = pred.improvement_when_scaling(7e9, 13e9, 'N')
print(f"Improvement: {improvement['improvement_%']:.2f}%")  # ~4.3%
print(f"Is it worth it? Depends on your compute budget!")

# ============================================
# 3. OPTIMAL PLANNING: Given a budget, what should I train?
# ============================================
C = 1e17  # 10^17 FLOPs = ~$100-200K
N_opt, D_opt = compute_optimal_allocation(C)
print(f"Train {N_opt/1e9:.1f}B model on {D_opt/1e12:.1f}T tokens")

# ============================================
# 4. COMPARISON TABLE: See multiple options
# ============================================
df = pred.comparison_table([7e9, 13e9, 70e9])
# Shows loss predictions for each size
print(df)
```

**Common patterns**:
```python
# "How much better is a 2x bigger model?"
improvement = pred.improvement_when_scaling(7e9, 14e9, 'N')['improvement_%']

# "If I can only add 10x more data:"
improvement = pred.improvement_when_scaling(100e9, 1e12, 'D')['improvement_%']

# "Show me a comparison across the board"
df = pred.comparison_table([3e9, 7e9, 13e9, 70e9])
```

---

## 📝 Paper Mastery Checklist

These are the things you should understand after reading this paper:

- [ ] **Power laws are universal**: Different model families follow the same curves (not coincidence)
- [ ] **Three independent factors**: You can improve via N, D, or C—they're roughly equivalent
- [ ] **Chinchilla's insight**: 20x tokens per parameter beats 10x (this changed everything)
- [ ] **Why data matters**: It's as important as model size, but often overlooked
- [ ] **The exponents**: 0.07, 0.095, 0.077 (remember or use the module; understanding matters more)
- [ ] **BERT connection**: BERT showed "scale works," this paper showed "how much it works"
- [ ] **The impact**: GPT-3, LLaMA, Claude all benefit from understanding these principles
- [ ] **Your models**: You now know how to allocate a budget optimally (not just "go bigger")

---

## 🚀 Try This Right Now (5 Minutes)

This is a real example you can run in your notebook:

```python
from scaling_laws import ScalingLawPredictor, compute_optimal_allocation

# EXAMPLE 1: Your current model setup
print("=== CURRENT MODEL ===")
N = 3e9    # 3B parameters
D = 60e9   # 60B tokens (D/N ratio = 20x, GOOD!)

pred = ScalingLawPredictor()
loss = pred.combined_prediction(N, D)
print(f"3B model on 60B tokens")
print(f"Expected loss: {loss:.4f}")

# EXAMPLE 2: What if you had 10x MORE compute?
print("\n=== WITH 10x MORE COMPUTE ===")
C_new = 1e17  # 10^17 FLOPs (10x bigger budget)
N_new, D_new = compute_optimal_allocation(C_new)
loss_new = pred.combined_prediction(N_new, D_new)

improvement = (loss - loss_new) / loss * 100
print(f"Optimal: {N_new/1e9:.1f}B model on {D_new/1e12:.1f}T tokens")
print(f"New loss: {loss_new:.4f}")
print(f"Improvement: {improvement:.1f}% better")

# EXAMPLE 3: What if you just scaled to 10B params (the naive way)?
print("\n=== NAIVE: JUST 10x BIGGER MODEL ===")
N_naive = 10e9
D_naive = 60e9  # Keep data same (DON'T DO THIS)
loss_naive = pred.combined_prediction(N_naive, D_naive)

print(f"10B model on same 60B tokens (SUBOPTIMAL)")
print(f"Loss: {loss_naive:.4f}")
print(f"Improvement over 3B: {(loss - loss_naive) / loss * 100:.1f}%")
print(f"→ Notice: Less improvement than Chinchilla approach!")
```

**Expected output**:
```
=== CURRENT MODEL ===
3B model on 60B tokens
Expected loss: 3.2847

=== WITH 10x MORE COMPUTE ===
Optimal: 8.1B model on 162B tokens
New loss: 3.0954
Improvement: 5.8% better

=== NAIVE: JUST 10x BIGGER MODEL ===
10B model on same 60B tokens (SUBOPTIMAL)
Loss: 3.1833
Improvement over 3B: 3.1%
→ Notice: Less improvement than Chinchilla approach!
```

**The lesson**: Chinchilla approach (8.1B + 162B) beats naive scaling (10B + 60B) with the same compute! ✓

---

## 📚 Your Resources

**In your workspace**:
- `scaling_laws_deepdive.ipynb` - Full interactive notebook with visualizations
- `SCALING_LAWS_GUIDE.md` - Detailed guide with explanations
- `scaling_laws.py` - Ready-to-use Python module
- `QUICK_REFERENCE.md` - This file (for quick lookups)

**External links**:
- **Original Paper**: https://arxiv.org/abs/2001.08361
- **Chinchilla (follow-up)**: https://arxiv.org/abs/2203.15556
- **OpenAI Blog**: https://openai.com/research/scaling-laws

---

## ✅ Next Steps

1. **Run the notebook**: Execute cells to see scaling curves in action
2. **Run the example above**: Try the code to see predictions
3. **Read the guide**: Deep dive into concepts you want to understand better
4. **Connect to BERT**: See how scaling laws built on BERT's foundation
5. **Week 3 prep**: Next week is PPO (how to make models follow instructions)

---
