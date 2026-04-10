# Chain-of-Thought Prompting: Quick Reference Guide

## 🚀 Quick Start

### What is Chain-of-Thought (CoT)?
Prompting language models to generate intermediate reasoning steps before providing a final answer. Simple, but effective.

### Why Use It?
- **Improves accuracy** on reasoning tasks (17% improvement on math benchmarks)
- **No fine-tuning needed** - works purely through prompting
- **Scales with model size** - better results with larger models
- **Works across domains** - math, logic, commonsense reasoning

### Quick Example
```
Standard Prompt:
"If Sarah has 10 apples and gives 3 to John, how many does she have?"
Answer: 7 apples

CoT Prompt:
"Let me think step by step.
Sarah has 10 apples.
She gives 3 to John, so: 10 - 3 = 7
Sarah has 7 apples."
```

**Result:** CoT shows reasoning, harder to make mistakes, clearer intermediate steps

---

## 📊 Key Numbers

| Metric | Value |
|--------|-------|
| Model params for CoT to work | 100B+ |
| Average improvement on benchmarks | 9-17% |
| Benchmark datasets tested | 3-4 |
| Few-shot examples recommended | 8 |
| Temperature suggested | 0.0-0.3 |

---

## 🎯 When to Use CoT

### ✅ Use CoT When:
- Problem requires multiple reasoning steps
- Task involves math or logic
- Accuracy is more important than speed
- Model is 100B+ parameters
- You have time for longer outputs

### ❌ Don't Use CoT When:
- Task is simple fact retrieval ("What's the capital of France?")
- Real-time, low-latency requirements
- Model is small (< 70B parameters)
- Text generation quality matters more than reasoning
- You need short, concise answers

---

## 💻 Implementation Quick Checklist

### Using OpenAI API
```python
import openai

prompt = """Let me think step by step.

Q: A group has 4 cars. 2 new cars are given. How many cars now?
A: They started with 4 cars. 2 new cars are given, so they have 4 + 2 = 6 cars.

Q: [YOUR QUESTION]
A:"""

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,  # Lower = more deterministic
)
```

### Using Hugging Face
```python
from transformers import pipeline

generator = pipeline("text-generation", model="meta-llama/Llama-2-70b")
prompt = "Let me think step by step.\n[Your reasoning task]"
output = generator(prompt, max_length=500)
```

---

## 📈 Benchmark Results (Paper)

### GSM8K (Grade School Math)
- **Standard:** 40.7%
- **CoT:** 58.1%
- **Improvement:** +17.4%

### DROP (Discrete Reasoning)
- **Standard:** 54.9%
- **CoT:** 64.1%
- **Improvement:** +9.2%

### CommonsenseQA
- **Standard:** 71.2%
- **CoT:** 78.7%
- **Improvement:** +7.5%

---

## 🔑 Core Concepts

### In-Context Learning
Models learn from examples in the prompt. No training needed.

### Emergent Ability
CoT benefits only appear in very large models (100B+ params).

### Few-Shot Prompting
Provide 5-8 examples, then ask your question.

### Temperature
- `temperature = 0`: Deterministic, same answer every time
- `temperature = 1`: Creative, diverse outputs

---

## 🛠️ Prompting Tips

### 1. Trigger Phrase
Start with: "Let me think step by step" or "I need to work through this"

### 2. Few-Shot Examples (Best Practice)
```
[2-4 examples with their reasoning chains]
[Your question]
```

### 3. Specific Format
```
Q: [Question]
A: [Step 1]
   [Step 2]
   [Step 3]
   Therefore, [Final Answer]
```

### 4. Domain-Specific Examples
Use examples from the same domain as your question (math examples for math problems)

### 5. Temperature Settings
- Math problems: `temperature = 0.0` (deterministic)
- Creative tasks: `temperature = 0.7` (diverse)

---

## 🚨 Common Pitfalls

| Problem | Solution |
|---------|----------|
| Wrong answer but good reasoning | Use self-consistency (multiple attempts) |
| Model hallucinates numbers | Add constraint: "Only use numbers from the problem" |
| Reasoning is too long | Limit output length or use more examples |
| Works sometimes, not always | Lower temperature, use more examples |
| Small model doesn't work | Upgrade to 100B+ parameter model |

---

## 📚 Advanced Techniques

### Self-Consistency Sampling
1. Generate multiple reasoning chains (e.g., 5-10)
2. Vote on the final answer
3. Take the most common answer

**Code:**
```python
def self_consistency(question, n_samples=10):
    answers = []
    for _ in range(n_samples):
        response = get_cot_response(question, temperature=0.7)
        answer = extract_final_answer(response)
        answers.append(answer)
    return most_common(answers)
```

### Least-to-Most Prompting
1. Ask model to break down problem
2. Solve step by step
3. Build up to complex solution

### Tree-of-Thoughts
- Generate multiple reasoning branches
- Explore promising branches deeper
- Backtrack on wrong paths

---

## 🔍 Analyzing Results

### Track These Metrics
1. **Accuracy:** % of correct answers
2. **Speed:** Tokens generated (more = slower)
3. **Reasoning Quality:** Does intermediate reasoning make sense?
4. **Error Analysis:** What types of problems fail?

### Sample Evaluation Script
```python
def evaluate_cot(questions, true_answers, model_fn):
    correct = 0
    for q, true_ans in zip(questions, true_answers):
        response = model_fn(q)
        pred_ans = extract_answer(response)
        if pred_ans == true_ans:
            correct += 1

    accuracy = correct / len(questions)
    print(f"Accuracy: {accuracy:.1%}")
```

---

## 📖 Paper Sections Quick Summary

| Section | Main Idea | Key Result |
|---------|-----------|-----------|
| 1. Intro | CoT improves reasoning | Simple, effective technique |
| 2. Method | How to use CoT | Few-shot prompting format |
| 3. Experiments | Testing on benchmarks | 9-17% improvement |
| 4. Analysis | Why does it work? | Works only on large models |
| 5. Related Work | Context in literature | Builds on GPT-3 prompting |

---

## 🎓 Key Takeaways

1. **Simple but Powerful:** Just ask the model to think step by step
2. **Scale Matters:** Doesn't work well with small models
3. **No Training:** Pure prompting, no fine-tuning
4. **Broadly Applicable:** Math, logic, commonsense reasoning
5. **Trade-off:** Better accuracy, longer outputs, slower speed

---

## 🔌 Phase 4: Intelligent Technique Router

**The Problem:** Different problems need different techniques

**The Solution:** Build a router that analyzes problems and picks the best method

### Decision Logic
```
Problem Type                  → Best Technique
Simple, low stakes            → Basic CoT (Phase 1)
Complex, multi-step          → Least-to-Most (Phase 3)
High stakes, critical        → Self-Consistency (Phase 3)
Any problem                  → Always add Confidence Scoring
```

### Domain-Specific Applications
**Financial Analysis:**
- Portfolio recommendations (high stakes → Self-Consistency)
- Investment comparisons (complex → Least-to-Most)
- Uses confidence scoring to filter low-confidence decisions

**AP Calculus Tutoring:**
- Derivatives (medium complexity → Basic CoT + Confidence)
- Optimization (complex multi-step → Least-to-Most)
- Shows complete step-by-step reasoning

---

## 🔗 External Links

- **Paper:** https://arxiv.org/abs/2201.11903
- **OpenAI API:** https://platform.openai.com/
- **Hugging Face Models:** https://huggingface.co/models
- **Self-Consistency Paper:** https://arxiv.org/abs/2203.11171
- **Tree-of-Thoughts:** https://arxiv.org/abs/2305.10601

---

## 📝 Cheat Sheet: Copy-Paste Templates

### Template 1: Basic Math Problem
```
Let me work through this step by step.

Example:
Q: If you have 5 oranges and buy 3 more, how many do you have?
A: I start with 5 oranges. I buy 3 more, so 5 + 3 = 8 oranges total.

Now solve:
Q: [YOUR PROBLEM]
A:
```

### Template 2: Logic Problem
```
Let me reason through this carefully.

Example:
Q: Alice is taller than Bob. Bob is taller than Charlie. Who is tallest?
A: Alice > Bob (given). Bob > Charlie (given). So Alice > Bob > Charlie. Alice is tallest.

Your turn:
Q: [YOUR LOGIC PROBLEM]
A:
```

### Template 3: Commonsense Question
```
Let me think about what I know:

Example:
Q: Why do people use umbrellas?
A: Umbrellas block rain from falling on you. They keep you dry. That's why people use them in rain.

Your question:
Q: [YOUR QUESTION]
A:
```

---

**Last Updated:** April 4, 2026 | **Status:** Ready to Dive In! 🚀
