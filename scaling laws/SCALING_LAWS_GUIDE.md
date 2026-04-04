# Scaling Laws for Neural Language Models - Complete Guide

**Paper**: [Kaplan et al., 2020](https://arxiv.org/abs/2001.08361) | **Week 2 of 15**

## Quick Navigation
- [Core Concepts](#core-concepts)
- [Mathematical Formulations](#mathematical-formulations)
- [Key Findings](#key-findings)
- [Implementation Code](#implementation-code)
- [Practical Applications](#practical-applications)
- [Connection to BERT](#connection-to-bert)

---

## Core Concepts

### What Are Scaling Laws?

The Kaplan et al. paper discovered that **model performance follows predictable power-law relationships** with respect to:
1. **Model Size (N)** - Number of parameters
2. **Dataset Size (D)** - Number of training tokens
3. **Compute Budget (C)** - Total FLOPs for training

### Why This Matters

Before this paper, improving model performance required:
- Clever architectures
- Better training techniques
- Countless experiments

**After** this paper, it was clear:
- **Performance scales predictably with resources**
- You can forecast improvements before training
- Budget allocation becomes a science, not guesswork

---

## Mathematical Formulations

### Power-Law Function
```
L(x) = a × x^(-α)
```
Where:
- `L` = Loss (lower is better)
- `x` = Some measure (N, D, or C)
- `a` = Scaling coefficient (intercept)
- `α` = Scaling exponent (determines steepness)

### The Three Scaling Laws

**1. Model Size Scaling**
```
L(N) = a_N × N^(-α_N)
α_N ≈ 0.07  (empirically observed)
```
Interpretation: Doubling model size reduces loss by ~5%

**2. Dataset Size Scaling**
```
L(D) = a_D × D^(-α_D)
α_D ≈ 0.095  (empirically observed)
```
Interpretation: Doubling dataset reduces loss by ~6.5%

**3. Compute Scaling**
```
L(C) = a_C × C^(-α_C)
α_C ≈ 0.077  (empirically observed)
```
Interpretation: Doubling compute reduces loss by ~5.2%

### Chinchilla's Optimal Allocation

**Discovery**: For fixed compute C, optimal allocation is:
```
D_optimal ≈ 20 × N
N_optimal ≈ √(C / 120)
```

**Implication**: Modern models should have ~20 tokens per parameter!

---

## Key Findings

| Finding | Impact |
|---------|--------|
| Power-law relationships are **universal** | Different architectures follow similar curves |
| Loss is **additive** in N and D | `L(N,D) ≈ L(N) + L(D)` |
| Scaling exponents are **stable** | Same across model families |
| Compute is the **limiting factor** | Better than clever tricks for improvement |
| Early models were **undertrained** | Many had D < 10N (suboptimal) |

### Important Caveats

1. **Scaling laws break down at very small scale** (< 1M params)
2. **Task-specific variations exist** (different tasks may have different exponents)
3. **Transfer learning effects not fully captured** (fine-tuning different from pre-training)
4. **Architectural changes matter** (attention, normalization, etc. affect coefficients)

---

## Implementation Code

### Basic Functions

```python
import numpy as np
from scipy.optimize import curve_fit

# Power-law functions
def loss_from_model_size(N, a_N=0.34, alpha_N=0.07):
    return a_N * (N ** (-alpha_N))

def loss_from_data_size(D, a_D=2.56, alpha_D=0.095):
    return a_D * (D ** (-alpha_D))

def loss_from_compute(C, a_C=0.37, alpha_C=0.077):
    return a_C * (C ** (-alpha_C))

# Fit power law to empirical data
def fit_power_law(x_data, y_data):
    def power_law(x, a, alpha):
        return a * x ** (-alpha)

    popt, pcov = curve_fit(power_law, x_data, y_data,
                           p0=[1, 0.07], maxfev=10000)
    return popt, pcov
```

### Chinchilla Optimization

```python
def compute_optimal_allocation(C):
    """Given compute budget C, find optimal N and D"""
    # C = 6 * N * D
    # D = 20 * N
    # Solving: C = 6 * N * 20 * N = 120 * N^2
    # N = sqrt(C / 120)

    N_optimal = np.sqrt(C / 120)
    D_optimal = 20 * N_optimal

    return N_optimal, D_optimal

def estimate_loss(N, D, a_N=0.34, a_D=2.56, alpha_N=0.07, alpha_D=0.095):
    """Estimate loss from both N and D"""
    return loss_from_model_size(N, a_N, alpha_N) + \
           loss_from_data_size(D, a_D, alpha_D)
```

### Prediction Tool

```python
class ScalingLawPredictor:
    def __init__(self, a_N=0.34, a_D=2.56, a_C=0.37,
                 alpha=0.07, alpha_D=0.095, alpha_C=0.077):
        self.a_N = a_N
        self.a_D = a_D
        self.a_C = a_C
        self.alpha = alpha
        self.alpha_D = alpha_D
        self.alpha_C = alpha_C

    def predict_loss(self, N=None, D=None, C=None):
        """Predict loss given any combination of N, D, C"""
        results = {}

        if N is not None:
            results['from_N'] = self.a_N * (N ** (-self.alpha))

        if D is not None:
            results['from_D'] = self.a_D * (D ** (-self.alpha_D))

        if C is not None:
            results['from_C'] = self.a_C * (C ** (-self.alpha_C))

        return results

    def improvement_when_scaling(self, old_size, new_size, dimension='N'):
        """Estimate improvement % when scaling"""
        if dimension == 'N':
            loss_old = self.a_N * (old_size ** (-self.alpha))
            loss_new = self.a_N * (new_size ** (-self.alpha))
        elif dimension == 'D':
            loss_old = self.a_D * (old_size ** (-self.alpha_D))
            loss_new = self.a_D * (new_size ** (-self.alpha_D))

        improvement_pct = (loss_old - loss_new) / loss_old * 100
        scale_factor = new_size / old_size

        return {
            'improvement_%': improvement_pct,
            'scale_factor': scale_factor,
            'loss_old': loss_old,
            'loss_new': loss_new
        }
```

---

## Practical Applications

### 1. Training Budget Planning

```python
# You have 10^17 FLOPs to spend. What's optimal?
C = 1e17

N_opt, D_opt = compute_optimal_allocation(C)

print(f"Compute budget: {C:.1e} FLOPs")
print(f"Optimal model size: {N_opt/1e9:.1f}B parameters")
print(f"Optimal data size: {D_opt/1e9:.1f}B tokens")
print(f"Ratio D/N: {D_opt/N_opt:.0f}x")
```

### 2. Performance Prediction

```python
# I'm training a 13B model on 260B tokens
# What loss should I expect?

predictor = ScalingLawPredictor()

N = 13e9
D = 260e9

loss_N = predictor.predict_loss(N=N)['from_N']
loss_D = predictor.predict_loss(D=D)['from_D']
combined_loss = loss_N + loss_D

print(f"Loss from N: {loss_N:.4f}")
print(f"Loss from D: {loss_D:.4f}")
print(f"Combined (rough): {combined_loss:.4f}")
```

### 3. Scaling Decisions

```python
# Is it better to scale from 7B to 13B, or scale data from 100B to 200B tokens?

improvement_model = predictor.improvement_when_scaling(7e9, 13e9, 'N')
improvement_data = predictor.improvement_when_scaling(100e9, 200e9, 'D')

print("Scale model 7B→13B:")
print(f"  Improvement: {improvement_model['improvement_%']:.2f}%")
print(f"  Scale factor: {improvement_model['scale_factor']:.2f}x")

print("\nDouble data 100B→200B tokens:")
print(f"  Improvement: {improvement_data['improvement_%']:.2f}%")
print(f"  Scale factor: {improvement_data['scale_factor']:.2f}x")
```

---

## Practical Applications

### Comparison: Kaplan vs. Chinchilla vs. Real Models

| Model | Year | Params | Tokens | D/N Ratio | Approach |
|-------|------|--------|--------|-----------|----------|
| BERT | 2018 | 340M | 3.4B | 10x | Pre-Kaplan |
| GPT-3 | 2020 | 175B | 300B | 1.7x | Kaplan (undertrained) |
| Chinchilla | 2022 | 70B | 1.4T | 20x | Optimal allocation |
| LLaMA 7B | 2023 | 7B | 1T | 143x | Over-trained (by choice) |
| LLaMA 65B | 2023 | 65B | 1.4T | 22x | Near-optimal |

**Insight**: Modern models train on **20-150x** more tokens than params!

---

## Connection to BERT

### How Scaling Laws Built On BERT's Foundation

**BERT (2018)** showed:
- Bidirectional pre-training works
- Large models are better
- Scale to hundreds of millions

**Scaling Laws (2020)** answered:
- *How much* better with scale?
- What's the mathematical relationship?
- How to optimally allocate resources?

### Applying Scaling Laws to BERT

```python
# What if we trained BERT with Chinchilla principles?

bert_original = {
    'params': 340e6,
    'tokens': 3.4e9,
    'ratio': 3.4e9 / 340e6  # ~10x (suboptimal)
}

bert_chinchilla = {
    'params': 340e6,
    'tokens': 340e6 * 20,   # 6.8B tokens
    'ratio': 20
}

# Predict improvement
predictor = ScalingLawPredictor()

loss_original_N = predictor.predict_loss(N=bert_original['params'])['from_N']
loss_original_D = predictor.predict_loss(D=bert_original['tokens'])['from_D']

loss_improved_N = predictor.predict_loss(N=bert_chinchilla['params'])['from_N']
loss_improved_D = predictor.predict_loss(D=bert_chinchilla['tokens'])['from_D']

print("BERT with original data (3.4B tokens):")
print(f"  Loss: {loss_original_N + loss_original_D:.4f}")

print("\nBERT with Chinchilla-optimal data (6.8B tokens):")
print(f"  Loss: {loss_improved_N + loss_improved_D:.4f}")

improvement = ((loss_original_N + loss_original_D) -
               (loss_improved_N + loss_improved_D)) / (loss_original_N + loss_original_D) * 100
print(f"\nImprovement: {improvement:.2f}%")
```

---

## Further Resources

### Key Papers
1. **Scaling Laws for Neural Language Models** (This one!) - Kaplan et al., 2020
2. **Training Compute-Optimal Large Language Models** - Hoffmann et al., 2022
3. **LLaMA: Open and Efficient Foundation Language Models** - Touvron et al., 2023
4. **Emergent Abilities of Large Language Models** - Wei et al., 2022

### Tools & Resources
- **Scaling laws calculator**: [OpenAI research](https://openai.com/research)
- **Model card comparisons**: [Hugging Face Model Hub](https://huggingface.co)
- **Compute tracking**: [Papers with Code](https://paperswithcode.com)

---

## Practice Exercises

### Exercise 1: Calculate Optimal Allocation
Given a compute budget of $100 (approximately 10^16 FLOPs for current GPU prices):
- What's the optimal model size?
- What's the optimal training data size?
- How much data per parameter?

```python
# Your code here
C = 1e16  # 10^16 FLOPs
N_opt, D_opt = compute_optimal_allocation(C)
print(f"Model: {N_opt/1e9:.1f}B params, Data: {D_opt/1e12:.1f}T tokens")
```

### Exercise 2: Scaling Comparison
Compare three strategies with 10^18 FLOPs:
1. **Wide & Shallow**: 100B params, 100B tokens
2. **Deep & Narrow**: 10B params, 1T tokens
3. **Balanced**: Use Chinchilla formula

Predict loss for each and explain the results.

### Exercise 3: Connect to BERT
Take your BERT notebooks and:
1. Estimate what BERT's scaling laws would predict
2. Compare with actual BERT performance
3. Propose how BERT could be improved with Chinchilla scaling

---

## Summary

**Scaling Laws** showed that improving language models isn't random—it follows predictable mathematical relationships. This enabled:

✅ Predictable improvement planning
✅ Optimal resource allocation
✅ The modern era of large language models
✅ Understanding BERT→GPT-3→Claude evolution

**Next week**: PPO (Proximal Policy Optimization) — how to make models follow instructions!
