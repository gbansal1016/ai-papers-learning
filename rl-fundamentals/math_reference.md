# RL Mathematics Reference Guide

## All Formulas in One Place

Use this as a reference while learning. Don't memorize—understand!

---

## Core Notation

| Symbol | Meaning |
|--------|---------|
| $s$ | State - current situation |
| $a$ | Action - what agent does |
| $r$ | Immediate reward |
| $\gamma$ | Discount factor (0-1) |
| $\pi$ | Policy - state to action mapping |
| $V(s)$ | Value function - expected return from state |
| $Q(s,a)$ | Q-function - expected return from state-action |
| $A(s,a)$ | Advantage - how good is this action? |
| $G_t$ | Return - total discounted reward from time t |

---

## Fundamental Equations

### 1. Return (Discounted Sum of Rewards)

**Simple version:**
$$G_t = r_t + r_{t+1} + r_{t+2} + ...$$

**With discounting** (what we actually use):
$$G_t = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + ... = \sum_{k=0}^{\infty} \gamma^k r_{t+k}$$

**Explanation:**
- $\gamma$ is discount factor (typically 0.99)
- Immediate rewards matter most
- Future rewards matter less
- Like: \\$100 now > \\$100 next year

**Special case:** Finite horizon (episode ends)
$$G_t = r_t + \gamma r_{t+1} + ... + \gamma^{T-t} r_T$$

---

### 2. Policy

**Deterministic policy:**
$$\pi(s) = a$$
"In state s, always take action a"

**Stochastic policy** (what we use):
$$\pi(a|s) = P(A_t = a | S_t = s)$$
"Probability of action a in state s"

**Example:**
- $\pi(up|position\_left) = 0.8$
- $\pi(right|position\_left) = 0.2$

---

### 3. Value Function

**Definition:**
$$V^\pi(s) = E[G_t | S_t = s]$$

"Expected return starting from state s, following policy $\pi$"

**In terms of immediate reward + future:**
$$V^\pi(s) = E[r_t + \gamma V^\pi(s') | S_t = s]$$

This is the **Bellman equation for value function**!

---

### 4. Q-Function (Action Value)

**Definition:**
$$Q^\pi(s,a) = E[G_t | S_t = s, A_t = a]$$

"Expected return from taking action a in state s, then following policy $\pi$"

**Bellman equation:**
$$Q^\pi(s,a) = E[r_t + \gamma Q^\pi(s',a') | S_t=s, A_t=a]$$

---

### 5. Advantage Function

**Definition:**
$$A^\pi(s,a) = Q^\pi(s,a) - V^\pi(s)$$

"How much better is this action than average?"

**Interpretation:**
- $A > 0$: Action is better than average
- $A < 0$: Action is worse than average
- $A ≈ 0$: Action is about average

**Why use advantage?**
- Reduces variance in learning
- More stable training
- Clearer learning signal

---

## Policy Gradient Theorem

### The Key Equation

$$\nabla J(\theta) = E[\nabla \log \pi_\theta(a|s) Q^\pi(s,a)]$$

**Explanation:**
- $J(\theta)$ = expected return (what we want to maximize)
- $\theta$ = policy parameters (neural network weights)
- $\nabla \log \pi_\theta(a|s)$ = **score function** = gradient of log policy
- $Q^\pi(s,a)$ = advantage/quality of action

**In words:**
> To improve policy: take gradient of log-probability, weighted by how good the action was

**Practical form with baseline:**
$$\nabla J(\theta) ≈ \nabla \log \pi_\theta(a|s) \cdot A(s,a)$$

Where $A(s,a) = Q(s,a) - V(s)$ is advantage

---

## REINFORCE Algorithm

### The Formula

$$\theta_{t+1} = \theta_t + \alpha \nabla \log \pi_\theta(a_t|s_t) G_t$$

**Explanation:**
- $\alpha$ = learning rate (how much to update)
- $\nabla \log \pi_\theta$ = score function (direction to go)
- $G_t$ = total return (weight the update)
- $\theta$ = policy parameters

**In words:** Update policy in direction that increases probability of high-reward actions

---

## Actor-Critic Methods

### Actor Update (Policy Gradient)

$$\theta_{actor} := \theta_{actor} + \alpha \nabla \log \pi(a|s) \cdot A(s,a)$$

Where advantage is: $A(s,a) = r + \gamma V(s') - V(s)$

### Critic Update (Value Estimation)

$$\theta_{critic} := \theta_{critic} + \beta (G_t - V(s))^2$$

Or with TD:
$$\theta_{critic} := \theta_{critic} + \beta (r + \gamma V(s') - V(s))^2$$

---

## Temporal Difference (TD) Learning

### One-Step TD

$$V(s) := V(s) + \alpha (r + \gamma V(s') - V(s))$$

**Parts:**
- $r + \gamma V(s')$ = TD target (estimated value)
- $V(s)$ = current estimate
- Difference = error

### n-Step TD

$$V(s) := V(s) + \alpha (G_{t:t+n} - V(s))$$

Where:
$$G_{t:t+n} = r_t + \gamma r_{t+1} + ... + \gamma^{n-1} r_{t+n-1} + \gamma^n V(s_{t+n})$$

**Interpretation:** Look ahead n steps, then bootstrap with value function

---

## Variance Reduction

### Baseline (Subtraction)

$$\nabla J(\theta) = E[\nabla \log \pi(a|s) (Q(s,a) - b(s))]$$

Where $b(s)$ = baseline = $V(s)$ (typically)

**Effect:**
- Doesn't change expected value of gradient
- Reduces variance
- Better learning

**Formula form:**
$$\nabla J(\theta) = E[\nabla \log \pi(a|s) A(s,a)]$$

### Generalized Advantage Estimation (GAE)

$$A_t^{GAE} = \sum_{l=0}^{\infty} (\gamma \lambda)^l \delta_{t+l}$$

Where $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ (TD error)

And $\lambda \in [0,1]$ controls bias-variance trade-off

**Special cases:**
- $\lambda = 0$: Use only one-step TD error (low variance, high bias)
- $\lambda = 1$: Use full return (high variance, low bias)
- $\lambda = 0.95$: Balance (typical choice)

---

## Key Relationships

### Connection Between V, Q, and A

$$V(s) = E_a[\pi(a|s) Q(s,a)] = E_a[\pi(a|s) (A(s,a) + V(s))]$$

$$Q(s,a) = r + \gamma E_{s'}[V(s')]$$

$$A(s,a) = Q(s,a) - V(s)$$

### Optimal Policy

$$\pi^*(a|s) = 1 \text{ if } a = \arg\max_a Q^*(s,a), 0 \text{ otherwise}$$

(Deterministic optimal policy takes best action)

---

## Common Hyperparameters

| Parameter | Typical Value | Effect |
|-----------|---------------|--------|
| $\alpha$ (learning rate) | 0.001 - 0.01 | How much to update |
| $\gamma$ (discount) | 0.99 - 0.999 | How much to value future |
| $\lambda$ (GAE) | 0.95 - 0.99 | Variance-bias trade-off |
| Batch size | 32 - 256 | How many samples before update |
| Entropy coeff | 0.001 - 0.01 | Encourage exploration |

---

## Probability Review

### Log Probability Trick

**Gradient of log:**
$$\nabla_\theta \log \pi(a|s) = \frac{\nabla_\theta \pi(a|s)}{\pi(a|s)}$$

**Why useful?**
- Avoids numerical issues
- Simplifies computation
- Foundation of policy gradients

### Softmax (for discrete actions)

$$\pi(a|s) = \frac{e^{f_a(s)}}{\sum_b e^{f_b(s)}}$$

Where $f_a(s)$ = neural network output for action a

**Log softmax:**
$$\log \pi(a|s) = f_a(s) - \log \sum_b e^{f_b(s)}$$

### Gaussian (for continuous actions)

$$\pi(a|s) = \mathcal{N}(\mu(s), \sigma^2)$$

Where $\mu(s)$ and $\sigma$ come from neural network

$$\log \pi(a|s) = -\frac{(a-\mu(s))^2}{2\sigma^2} - \log \sigma - \frac{1}{2}\log(2\pi)$$

---

## Exploration-Exploitation Trade-off

### $\epsilon$-Greedy

$$a_t = \begin{cases} \arg\max_a Q(s,a) & \text{with probability } 1-\epsilon \\ \text{random action} & \text{with probability } \epsilon \end{cases}$$

Simple but effective!

### Entropy Regularization

$$J(\theta) = E[\log \pi(a|s) Q(s,a)] + \beta H(\pi(\cdot|s))$$

Where entropy: $H(\pi) = -\sum_a \pi(a|s) \log \pi(a|s)$

Higher entropy = more randomness = more exploration

---

## Convergence Guarantees

### REINFORCE Convergence
If:
- Learning rate decreases: $\sum_t \alpha_t = \infty$, $\sum_t \alpha_t^2 < \infty$
- $|\log \pi(a|s)| < \infty$ (bounded)

Then: Converges to local optimum with probability 1

### Actor-Critic
Under reasonable conditions: Converges to local optimum

**But:** "Local" not "global"—might not find best policy!

---

## Quick Formula Reference Card

```
Return:           G_t = Σ γ^k r_{t+k}
Value:            V(s) = E[G_t | s]
Q-function:       Q(s,a) = E[G_t | s,a]  
Advantage:        A(s,a) = Q(s,a) - V(s)
Policy Gradient:  ∇ log π(a|s) × A(s,a)
REINFORCE:        θ ← θ + α ∇ log π(a|s) G_t
Actor-Critic:     θ_a ← θ_a + α ∇ log π × A
                  θ_c ← θ_c + β (r + γV(s') - V(s))²
TD Error:         δ = r + γV(s') - V(s)
GAE:              A^GAE = Σ (γλ)^l δ_{t+l}
```

---

## When to Use Which

| Problem | Use |
|---------|-----|
| Discrete actions | Softmax policy |
| Continuous actions | Gaussian policy |
| Fast learning | Actor-Critic |
| Sample efficiency | Actor-Critic + GAE |
| Simple exploration | ε-greedy or entropy |
| Stable training | Entropy regularization |
| Reduced variance | Baseline / Advantage |

---

## Common Mistakes

1. **Forgetting discount factor**
   - Will overvalue distant rewards

2. **Not normalizing advantages**
   - Can have huge variance
   - Use: $(A - \text{mean}(A)) / (\text{std}(A) + \epsilon)$

3. **Learning rate too high**
   - Policy oscillates wildly
   - Start with 0.001 or lower

4. **Baseline following reward**
   - Baseline should be roughly $V(s)$
   - If it perfectly tracks return, advantage is always 0!

5. **Ignoring entropy**
   - Policy becomes deterministic too early
   - Misses good exploration regions
   - Add entropy bonus term

---

## Further Reading

For deeper understanding:
- "Reinforcement Learning: An Introduction" (Sutton & Barto) - Chapters 3, 4, 5
- "Deep Reinforcement Learning Hands-On" (Lapan) - Chapters 2, 3, 4
- OpenAI Spinning Up - Policy Gradient section

---

## Remember

> **Formulas are tools, not gods.** Understand the intuition first (why?), then learn the math (how?), then apply (what?).

Most important equation:
$$\nabla \log \pi(a|s) \times \text{(how good was this?)} = \text{policy improvement}$$

Everything else builds on this! 💡
