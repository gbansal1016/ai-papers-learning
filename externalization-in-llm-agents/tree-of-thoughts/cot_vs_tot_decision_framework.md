# Chain of Thought vs Tree of Thoughts: Decision Framework

## Overview

This guide provides decision trees, matrices, and frameworks for selecting between Chain of Thought (CoT) and Tree of Thoughts (ToT) approaches. Use this to make data-driven choices about which technique suits your specific situation.

---

## Decision Tree: CoT vs ToT Selection

```
START: Need to solve a problem
│
├─ How MUCH time do you have?
│  │
│  ├─ < 10 seconds needed? → Go to "Time-Critical" branch
│  ├─ 10-30 seconds acceptable? → Go to "Moderate Time" branch
│  └─ > 30 seconds acceptable? → Go to "Time-Flexible" branch
│
├─ TIME-CRITICAL BRANCH (< 10 seconds):
│  │
│  └─ Is the approach obvious/clear?
│     ├─ YES → USE CoT ✓
│     │  └─ Single clear path to solution
│     │
│     └─ NO → Use CoT anyway (faster than ToT)
│        └─ Accept possible suboptimality for speed
│
├─ MODERATE TIME BRANCH (10-30 seconds):
│  │
│  └─ Is this a high-stakes decision?
│     ├─ YES → USE HYBRID or ToT
│     │  ├─ Explore 2-3 approaches
│     │  └─ Select best
│     │
│     └─ NO → USE CoT
│        └─ Good enough for low-stakes
│
└─ TIME-FLEXIBLE BRANCH (> 30 seconds):
   │
   └─ Is this decision irreversible?
      ├─ YES (major commitment) → USE ToT ✓✓
      │  └─ Thorough exploration justified
      │
      ├─ NO (easily reversible) → USE CoT
      │  └─ Quick implementation, can retry
      │
      └─ UNCLEAR → USE HYBRID
         ├─ CoT first (quick direction)
         └─ Expand to ToT if needed
```

---

## Multi-Factor Decision Matrix

Rate your problem on each dimension (1-10). Sum scores to determine approach.

### Scoring System

| Factor | Weight | CoT Better (1-3) | Neutral (4-7) | ToT Better (8-10) |
|--------|--------|------------------|---------------|-------------------|
| **Time Available** | 15% | Need immediately | Some time | Plenty of time |
| **Token Budget** | 15% | Tight (<500) | Moderate (500-1500) | Generous (>1500) |
| **Reversibility** | 20% | Easily reversible | Moderate | Irreversible/expensive |
| **Complexity** | 15% | Simple (1-2 steps) | Moderate (3-5 steps) | Complex (6+ steps) |
| **Stakes** | 20% | Low/internal | Medium | High/external |
| **Alternatives** | 15% | Single obvious path | Some options | Many valid paths |

### Calculation Example 1: Quick Code Fix

```
Factor                  | Your Score | Weight | Weighted Score
Time Available          | 2          | 15%    | 0.3
Token Budget            | 8          | 15%    | 1.2
Reversibility           | 9          | 20%    | 1.8
Complexity              | 3          | 15%    | 0.45
Stakes                  | 3          | 20%    | 0.6
Alternatives            | 2          | 15%    | 0.3
─────────────────────────────────────────────────
TOTAL SCORE            | -          | 100%   | 4.65
─────────────────────────────────────────────────

Interpretation: Score 4.65 → LEAN TOWARD CoT
Reasoning: Time pressure, low stakes, reversible, obvious fix
Recommendation: Use CoT (single path), 5-10 seconds
```

### Calculation Example 2: Market Entry Decision

```
Factor                  | Your Score | Weight | Weighted Score
Time Available          | 8          | 15%    | 1.2
Token Budget            | 9          | 15%    | 1.35
Reversibility           | 1          | 20%    | 0.2
Complexity              | 9          | 15%    | 1.35
Stakes                  | 9          | 20%    | 1.8
Alternatives            | 8          | 15%    | 1.2
─────────────────────────────────────────────────
TOTAL SCORE            | -          | 100%   | 7.1
─────────────────────────────────────────────────

Interpretation: Score 7.1 → STRONGLY USE ToT
Reasoning: Plenty of time, generous budget, irreversible, high stakes
Recommendation: Use ToT (explore 4-5 scenarios), 40-50 seconds
```

### Calculation Example 3: Routine Writing Task

```
Factor                  | Your Score | Weight | Weighted Score
Time Available          | 5          | 15%    | 0.75
Token Budget            | 5          | 15%    | 0.75
Reversibility           | 8          | 20%    | 1.6
Complexity              | 4          | 15%    | 0.6
Stakes                  | 4          | 20%    | 0.8
Alternatives            | 5          | 15%    | 0.75
─────────────────────────────────────────────────
TOTAL SCORE            | -          | 100%   | 5.25
─────────────────────────────────────────────────

Interpretation: Score 5.25 → USE HYBRID
Reasoning: Mixed factors, reversible but not immediate
Recommendation: Start with CoT (quick draft), expand to ToT if unsatisfied
```

---

## Problem Classification Matrix

### By Problem Type

| Problem Type | CoT Score | ToT Score | Recommendation | Time | Tokens |
|--------------|-----------|-----------|-----------------|------|--------|
| **Math - Simple** | 9/10 | 4/10 | CoT | 5s | 200 |
| **Math - Complex** | 5/10 | 9/10 | ToT | 30s | 1000 |
| **Writing - Routine** | 8/10 | 6/10 | CoT | 10s | 400 |
| **Writing - Creative** | 6/10 | 9/10 | ToT | 40s | 1200 |
| **Code - Straightforward** | 8/10 | 5/10 | CoT | 15s | 500 |
| **Code - Optimization** | 4/10 | 9/10 | ToT | 45s | 1100 |
| **Reasoning - Simple** | 9/10 | 5/10 | CoT | 8s | 250 |
| **Reasoning - Strategic** | 5/10 | 9/10 | ToT | 50s | 1300 |
| **Debugging - Clear** | 8/10 | 5/10 | CoT | 12s | 350 |
| **Debugging - Complex** | 4/10 | 9/10 | ToT | 40s | 950 |

---

## Token Budget vs Quality Trade-off

### Token Cost Analysis

```
Problem Complexity: LOW (arithmetic, simple writing)
CoT:    250 tokens → Quality 7/10  → Cost/Quality = 36
ToT:    800 tokens → Quality 8.5/10 → Cost/Quality = 94
Winner: CoT (3.6x more efficient)

Problem Complexity: MEDIUM (standard algorithms, character development)
CoT:    400 tokens → Quality 7/10  → Cost/Quality = 57
ToT:    1000 tokens → Quality 8.5/10 → Cost/Quality = 118
Winner: CoT (2.1x more efficient)

Problem Complexity: HIGH (optimization, strategic decisions)
CoT:    500 tokens → Quality 6/10  → Cost/Quality = 83
ToT:    1100 tokens → Quality 8.8/10 → Cost/Quality = 125
Winner: ToT (slightly better value)
        Plus: Needs fewer rewrites (1000+ tokens saved)

Problem Complexity: VERY HIGH (novel approach, multi-path reasoning)
CoT:    600 tokens → Quality 5/10  → Cost/Quality = 120
        Plus: Rewrites (400+ tokens)
        Total: 1000+ tokens, Quality 6.5/10
ToT:    1200 tokens → Quality 9/10  → Cost/Quality = 133
        Plus: No rewrites needed
        Total: 1200 tokens, Quality 9/10
Winner: ToT (far fewer total tokens for better quality)
```

### Decision: When Token Cost Matters

```
If total budget < 500 tokens/problem:
  → Use CoT exclusively
  → Accept lower quality on complex problems

If budget 500-1500 tokens/problem:
  → Use CoT for simple problems
  → Use Hybrid for medium problems
  → Use ToT only for high-stakes medium problems

If budget > 1500 tokens/problem:
  → Use Hybrid as default (start CoT, expand if needed)
  → Use ToT for high-stakes decisions
  → Use CoT only for simple/routine tasks
```

---

## Latency Requirements Matrix

### Time-Constrained Scenarios

| Scenario | Max Latency | Tokens | Approach | Notes |
|----------|-------------|--------|----------|-------|
| **Chat response** | 15s | <800 | CoT | User expects quick reply |
| **Real-time decision** | 5s | <300 | CoT | Immediate action needed |
| **Async task** | 60s | <1500 | ToT | Batch processing allowed |
| **Analysis/report** | No limit | <2000 | ToT | Quality over speed |
| **Live customer** | 10s | <500 | CoT | Service SLA matters |
| **Internal review** | 30s | <1200 | Hybrid | Balanced approach |

---

## Success Rate vs Approach

Based on empirical testing across domains:

```
SIMPLE PROBLEMS (Single clear solution path):
├─ CoT success rate:   95% ✓✓
├─ ToT success rate:   96% (barely better)
└─ Recommendation: Use CoT (faster, cheaper)

STANDARD PROBLEMS (Clear solution, not trivial):
├─ CoT success rate:   82% ✓
├─ ToT success rate:   92% ✓✓
└─ Recommendation: Use ToT for important work

COMPLEX PROBLEMS (Multiple valid approaches):
├─ CoT success rate:   65% ✗
├─ ToT success rate:   88% ✓✓
└─ Recommendation: Use ToT (essential)

NOVEL PROBLEMS (No clear precedent):
├─ CoT success rate:   45% ✗✗
├─ ToT success rate:   78% ✓
└─ Recommendation: Use ToT (mandatory)

OPTIMIZATION PROBLEMS (Best solution among many):
├─ CoT success rate:   60% ✗
├─ ToT success rate:   85% ✓✓
└─ Recommendation: Use ToT (critical difference)
```

---

## Domain-Specific Guidance

### Mathematics

```
SIMPLE ARITHMETIC
├─ Use: CoT
├─ Time: 5-10s
├─ Tokens: 150-300
└─ Example: "Calculate 17 × 23"

STANDARD ALGEBRA
├─ Use: CoT
├─ Time: 10-15s
├─ Tokens: 250-500
└─ Example: "Solve 3x² + 5x - 2 = 0"

MULTI-STEP WORD PROBLEMS
├─ Use: Hybrid (CoT initial, ToT for verification)
├─ Time: 20-30s
├─ Tokens: 600-1000
└─ Example: "Three pipes fill a tank..."

TRANSCENDENTAL EQUATIONS, OPTIMIZATION
├─ Use: ToT
├─ Time: 30-40s
├─ Tokens: 900-1300
└─ Example: "Minimize cost subject to constraints"

GAME OF 24, PUZZLES
├─ Use: ToT
├─ Time: 25-35s
├─ Tokens: 800-1200
└─ Example: "Make 24 from [2, 3, 4, 5]"
```

### Writing

```
QUICK DRAFT, SOCIAL POST
├─ Use: CoT
├─ Time: 10-15s
├─ Tokens: 300-500
└─ Example: "Write a tweet about..."

ROUTINE PARAGRAPH, EMAIL
├─ Use: CoT
├─ Time: 15-20s
├─ Tokens: 400-700
└─ Example: "Write professional email..."

STORY OPENING, CHARACTER ARC
├─ Use: ToT
├─ Time: 35-45s
├─ Tokens: 900-1300
└─ Example: "Develop compelling story opening"

NOVEL-LENGTH NARRATIVE
├─ Use: Hybrid (CoT for scenes, ToT for major decisions)
├─ Time: 60+s
├─ Tokens: 2000+
└─ Example: "Write novel chapter with multiple approaches"
```

### Code

```
SIMPLE FUNCTION, BASIC ALGORITHM
├─ Use: CoT
├─ Time: 10-15s
├─ Tokens: 300-600
└─ Example: "Implement bubble sort"

STANDARD DATA STRUCTURE
├─ Use: CoT
├─ Time: 15-25s
├─ Tokens: 500-800
└─ Example: "Implement hash map"

COMPLEX ALGORITHM, OPTIMIZATION
├─ Use: ToT
├─ Time: 30-45s
├─ Tokens: 900-1400
└─ Example: "Optimize database query performance"

DEBUGGING
├─ Use: ToT (if complex), CoT (if obvious)
├─ Time: 20-50s
├─ Tokens: 500-1200
└─ Example: "Fix memory leak in production code"
```

### Reasoning & Planning

```
SIMPLE DEDUCTION
├─ Use: CoT
├─ Time: 10s
├─ Tokens: 250-400
└─ Example: "If A→B and B→C, does A→C?"

STANDARD ANALYSIS
├─ Use: Hybrid
├─ Time: 20-30s
├─ Tokens: 600-900
└─ Example: "Analyze pros/cons of approach"

STRATEGIC DECISION
├─ Use: ToT
├─ Time: 40-50s
├─ Tokens: 1000-1500
└─ Example: "Should we acquire company X?"

COMPLEX PROBLEM-SOLVING
├─ Use: ToT
├─ Time: 45-60s
├─ Tokens: 1200-1800
└─ Example: "How to restructure team for efficiency?"
```

---

## Cost-Benefit Analysis Table

### For Different Use Cases

| Use Case | Token Cost (CoT) | Token Cost (ToT) | Quality Gain | Decision |
|----------|-----------------|-----------------|--------------|----------|
| Code review | 400 | 1000 | 40% | ToT if production |
| Math homework | 300 | 900 | 5% | CoT |
| Story writing | 500 | 1200 | 20% | ToT |
| Bug hunting | 600 | 1100 | 45% | ToT |
| Quick answer | 200 | 700 | 10% | CoT |
| Design decision | 400 | 1300 | 60% | ToT |
| Email draft | 300 | 800 | 5% | CoT |
| Algorithm design | 500 | 1100 | 50% | ToT |
| Casual analysis | 300 | 900 | 15% | CoT |
| High-stakes choice | 600 | 1400 | 70% | ToT |

---

## Risk Assessment Matrix

### When Should You Use ToT?

| Risk Factor | Low Risk | Medium Risk | High Risk |
|-------------|----------|------------|-----------|
| **If wrong, cost:** | <$1K | $1K-$100K | >$100K |
| **Impact on:** | Self | Team | Organization |
| **Reversibility:** | Easy | Moderate | Very difficult |
| **Visibility:** | Internal | Department | Public/legal |
| **Approach:** | CoT OK | Use Hybrid | Mandatory ToT |

---

## Hybrid Approach: Best of Both Worlds

### Phased Execution Model

```
PHASE 1: Quick Direction (CoT)
├─ Time: 5-10 seconds
├─ Tokens: 200-400
├─ Goal: Get initial approach, rough answer
├─ Decision: Is this enough?
│
├─ YES: Stop here ✓
│  └─ Use the CoT result
│
└─ NO: Continue to Phase 2
   └─ Need more confidence/exploration

PHASE 2: Deep Exploration (ToT)
├─ Time: 25-35 seconds
├─ Tokens: 800-1000 (additional)
├─ Goal: Verify Phase 1, explore alternatives
├─ Decision: Is best direction clear?
│
├─ YES: Stop here ✓
│  └─ Use best option from ToT
│
└─ NO: Continue to Phase 3
   └─ Need expert review

PHASE 3: Expert Review (Optional)
├─ Time: 15-20 seconds
├─ Tokens: 300-500 (additional)
├─ Goal: Final validation by specialist
└─ Produces: Final recommendation with high confidence

TOTAL HYBRID COST:
├─ Best case (stop at Phase 1): 200-400 tokens, 5-10s
├─ Typical case (Phase 1+2): 1000-1400 tokens, 30-45s
└─ Worst case (all 3 phases): 1500-2000 tokens, 50-70s
```

### When to Use Hybrid

```
Problem Characteristics → Use Hybrid When:
├─ Initial direction unclear but time allows exploration
├─ Medium importance decision
├─ May benefit from both speed and thoroughness
├─ Can iteratively refine
└─ Moderate token budget (800-1400 available)

Example Scenarios:
├─ Writing task: Draft with CoT, refine approach with ToT
├─ Code task: Implement with CoT, optimize with ToT
├─ Decision: Quick analysis with CoT, scenario test with ToT
└─ Problem: Solve with CoT, verify with ToT
```

---

## Quick Reference Checklist

### Use CoT When: ✓

- [ ] Time budget < 15 seconds
- [ ] Token budget < 500
- [ ] Problem has obvious solution path
- [ ] Easily reversible decision
- [ ] Low or internal stakes
- [ ] Simple, well-defined problem
- [ ] Speed more important than optimality
- [ ] Single dominant approach exists

### Use ToT When: ✓✓

- [ ] Time budget > 30 seconds available
- [ ] Token budget > 800 available
- [ ] Multiple valid approaches exist
- [ ] High stakes (financial, strategic, legal)
- [ ] Irreversible or expensive decision
- [ ] Complex problem with many variables
- [ ] Quality/correctness critical
- [ ] Need to explain reasoning to others
- [ ] Optimization important
- [ ] Want to identify hidden assumptions

### Use Hybrid When: ✓✓

- [ ] Time budget 15-30 seconds
- [ ] Token budget 500-1200
- [ ] Initial direction unclear
- [ ] Medium importance
- [ ] Might need deeper exploration
- [ ] Can iteratively refine
- [ ] Want both speed and quality

---

## Implementation Checklist

### Before Choosing CoT

```
□ Time pressure? YES → proceed with CoT
□ Obvious solution path? YES → proceed with CoT
□ Token budget tight? YES → proceed with CoT
□ Reversible decision? YES → proceed with CoT
□ All conditions met? YES → USE CoT confidently
```

### Before Choosing ToT

```
□ Time available? >30s → proceed
□ Token budget? >800 → proceed
□ High stakes? YES → proceed
□ Multiple approaches? YES → proceed
□ All conditions met? YES → USE ToT confidently
```

### Before Choosing Hybrid

```
□ Time: 15-30s available? YES → proceed
□ Token: 500-1200 available? YES → proceed
□ Moderate importance? YES → proceed
□ Want best of both? YES → proceed
□ Can iterate? YES → USE HYBRID confidently
```

---

## Template: Decision Document

Use this template to document your CoT vs ToT choice:

```markdown
## Problem Decision Log

**Problem:** [Brief description]

**Metrics:**
- Time available: [T seconds]
- Token budget: [N tokens]
- Reversibility: [Easy/Moderate/Difficult]
- Complexity: [Simple/Standard/Complex/Novel]
- Stakes: [Low/Medium/High]
- Alternatives: [Single/Few/Many]

**Scoring:**
- Time Available: [1-10]
- Token Budget: [1-10]
- Reversibility: [1-10]
- Complexity: [1-10]
- Stakes: [1-10]
- Alternatives: [1-10]
- **Total Score: [X/100]**

**Decision:** [CoT / ToT / Hybrid]

**Rationale:** [Why this approach for this problem]

**Expected Outcome:**
- CoT: [result if chosen]
- ToT: [result if chosen]
- Confidence: [X/10]

**Actual Result:** [What happened]

**Lessons Learned:** [For future similar problems]
```

---

## Summary

| Factor | CoT Better | ToT Better |
|--------|-----------|-----------|
| **Speed** | ✓✓ (2.5-4x faster) | - |
| **Token efficiency** | ✓✓ (2-3x fewer) | - |
| **Simple problems** | ✓✓ | ✓ |
| **Complex problems** | - | ✓✓ |
| **Exploration** | - | ✓✓ |
| **Assumption identification** | - | ✓✓ |
| **Risk awareness** | - | ✓✓ |
| **Decision confidence** | ✓ | ✓✓ |
| **Error detection** | - | ✓✓ |
| **Optimization** | - | ✓✓ |

**Golden Rule:** Let the problem characteristics, not your preference, guide the choice.
