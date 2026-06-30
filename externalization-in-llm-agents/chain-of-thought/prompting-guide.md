# Chain-of-Thought Prompting Guide: Types & Templates

A complete reference for crafting prompts that leverage CoT effectively. Covers prompt structures, domain-specific examples, and what NOT to do.

---

## 🎯 The Core Principle

```
Standard Prompt:    Q: [question]
                   A:

CoT Prompt:        Q: [question]
                   A: Let me think step by step. [reasoning steps] [answer]
```

**Key Difference:** CoT explicitly shows intermediate reasoning steps before the final answer.

---

## 📋 Prompt Structure: The Anatomy

### Basic Structure
```
[TRIGGER PHRASE]

[FEW-SHOT EXAMPLES]

[USER QUESTION]

[RESPONSE INSTRUCTION]
```

### Detailed Breakdown
```
1. Trigger Phrase (optional but recommended)
   └─ "Let me think step by step"
      or "Let me work through this carefully"
      or "I need to reason through this"

2. Few-Shot Examples (1-8 examples)
   └─ Example 1: Q: ... A: [step-by-step reasoning] [answer]
   └─ Example 2: Q: ... A: [step-by-step reasoning] [answer]
   └─ Example 3: Q: ... A: [step-by-step reasoning] [answer]

3. Your Actual Question
   └─ Q: [Your question]

4. Instruction to Start Reasoning
   └─ A: [optional hint to start reasoning]
```

---

## 📝 Prompt Template Gallery

### Template 1: Basic Math Problems ✅ BEST FOR NUMBERS

**Use When:** Arithmetic, word problems, calculations

```
Let me work through math problems step by step.

Example 1:
Q: If Sarah has 5 apples and gets 3 more, how many total?
A: Sarah starts with 5 apples. She gets 3 more. So 5 + 3 = 8 apples total.

Example 2:
Q: A store has 50 books. They sell 20 books. How many remain?
A: Starting with 50 books. They sell 20. So 50 - 20 = 30 books remain.

Q: A restaurant has 100 chairs. They add 25 more. How many now?
A: Let me think step by step.
```

**Why It Works:**
- Shows concrete number examples first
- Each step is clearly labeled
- Pattern is easy for model to follow

---

### Template 2: Logic & Reasoning ✅ BEST FOR LOGICAL DEDUCTION

**Use When:** Comparisons, ordering, logical conclusions

```
Let me reason through this carefully.

Example 1:
Q: Alice is taller than Bob. Bob is taller than Charlie. Who is tallest?
A: Given: Alice > Bob (in height). Bob > Charlie (in height).
   Therefore: Alice > Bob > Charlie.
   Answer: Alice is tallest.

Example 2:
Q: All dogs are animals. Spot is a dog. Is Spot an animal?
A: Fact: All dogs are animals.
   Fact: Spot is a dog.
   Conclusion: Spot must be an animal.
   Answer: Yes, Spot is an animal.

Q: Every student must attend class. Maria is a student. Does Maria need to attend class?
A: Let me think through the logic.
```

**Why It Works:**
- Uses formal logic (Given → Conclusion)
- Shows deductive reasoning
- Clear cause-and-effect chains

---

### Template 3: Multi-Step Word Problems ✅ BEST FOR COMPLEX PROBLEMS

**Use When:** Multiple operations, several steps needed

```
Let me work through this step by step.

Example 1:
Q: Sarah has 10 apples. She gives 3 to John and buys 5 more. How many does she have?
A:
  Step 1: Sarah starts with 10 apples
  Step 2: She gives 3 away: 10 - 3 = 7 apples
  Step 3: She buys 5 more: 7 + 5 = 12 apples
  Final Answer: Sarah has 12 apples

Example 2:
Q: A class has 30 students. 10 are absent today. Of those present, 5 are sick. How many are fully healthy?
A:
  Step 1: Start with 30 students
  Step 2: 10 are absent: 30 - 10 = 20 present
  Step 3: Of the 20 present, 5 are sick: 20 - 5 = 15 fully healthy
  Final Answer: 15 students are fully healthy

Q: A store has 100 items. They sell 25 items in the morning and 15 in the afternoon. They receive 30 new items. How many now?
A: Let me work through each step.
```

**Why It Works:**
- Numbers each step clearly
- Shows intermediate calculations
- Easy to follow the progression

---

### Template 4: Commonsense Reasoning ✅ BEST FOR GENERAL KNOWLEDGE

**Use When:** "Why" questions, common knowledge, explanations

```
Let me think about this logically.

Example 1:
Q: Why do people wear coats in winter?
A: Winter is cold. Cold weather makes people uncomfortable and can cause harm.
   Coats provide insulation and trap warm air around the body.
   Therefore, people wear coats to stay warm in winter.

Example 2:
Q: Why do plants need sunlight?
A: Plants use sunlight to make food through photosynthesis.
   Sunlight is energy that powers this process.
   Without sunlight, plants cannot make food and will die.
   Therefore, plants need sunlight to survive.

Q: Why do we use passwords for accounts?
A: Let me think through the reasons.
```

**Why It Works:**
- Shows causal reasoning (Because X, therefore Y)
- Connects facts to explanations
- Natural language flow

---

### Template 5: Mathematical Reasoning ✅ BEST FOR FORMULAS & PROOFS

**Use When:** Algebra, geometry, proofs, formulas

```
Let me solve this mathematically.

Example 1:
Q: What is 24 × 5?
A: Using multiplication:
   24 × 5 = (20 + 4) × 5
         = (20 × 5) + (4 × 5)
         = 100 + 20
         = 120

Example 2:
Q: Solve for x: 2x + 5 = 15
A: Starting with: 2x + 5 = 15
   Subtract 5 from both sides: 2x = 10
   Divide both sides by 2: x = 5
   Check: 2(5) + 5 = 10 + 5 = 15 ✓

Q: What is the area of a rectangle with length 8 and width 5?
A: Let me work through this step by step.
```

**Why It Works:**
- Shows algebraic manipulation
- Clear before/after states
- Verification/checking of work

---

## 🚀 Advanced Prompt Techniques

### Technique 1: Few-Shot with Scaffolding

Add explicit hints about intermediate steps:

```
Let me think through this carefully with these steps:
1. Identify what we know
2. Identify what we need to find
3. Show the calculation
4. Verify the answer

Example:
Q: A book costs $12. Tax is 10%. What's the total?
A:
   What we know: Book = $12, Tax = 10%
   What we need: Total price
   Calculation: Tax = $12 × 0.10 = $1.20, Total = $12 + $1.20 = $13.20
   Verification: $12 × 1.10 = $13.20 ✓

Q: A shirt costs $25. Discount is 20%. What's the final price?
A: Let me follow these steps.
```

---

### Technique 2: Error Correction with CoT

Show what NOT to do, then the right way:

```
Let me think carefully about this.

Common Mistake:
Q: Sarah has 10 apples, gives 3 away, buys 5 more. How many?
Wrong answer: Just add them: 10 + 3 + 5 = 18 ✗

Correct Reasoning:
Q: Sarah has 10 apples, gives 3 away, buys 5 more. How many?
A: Start with 10. She gives 3 away (subtract): 10 - 3 = 7.
   Then buys 5 more (add): 7 + 5 = 12.
   Answer: 12 apples ✓

Q: [Your problem]
A: Let me think about this step by step, being careful with each operation.
```

---

### Technique 3: Self-Consistency (Multiple Attempts)

Generate multiple reasoning paths:

```
Let me think about this in different ways.

Approach 1: [reasoning path A]
Approach 2: [reasoning path B]
Approach 3: [reasoning path C]

Most common answer: [voting on answers]
```

---

## 📊 By Domain: What Works Best

### 📐 Mathematics
- **Best Trigger:** "Let me work through this step by step"
- **Format:** Show calculation, show intermediate results, show final answer
- **Temperature:** 0.0 (deterministic)
- **Examples Needed:** 2-4 examples
- **Key:** Show each arithmetic operation explicitly

```python
prompt = """
Q: 10 + 5 × 2 = ?
A: Following order of operations:
   - Multiplication first: 5 × 2 = 10
   - Then addition: 10 + 10 = 20
"""
```

### 🧠 Logic & Reasoning
- **Best Trigger:** "Let me reason through this carefully"
- **Format:** State facts, apply logic, reach conclusion
- **Temperature:** 0.0-0.3 (mostly deterministic)
- **Examples Needed:** 2-3 examples
- **Key:** Explicit logical connections (because, therefore, so)

```python
prompt = """
Q: If all X are Y, and Z is X, then is Z a Y?
A: Given: All X are Y (so any X must be Y)
   Given: Z is X (so Z belongs to the X category)
   Therefore: Z must be Y
"""
```

### 📝 Reading Comprehension
- **Best Trigger:** "Let me identify the relevant information"
- **Format:** Extract info, identify question, cite evidence
- **Temperature:** 0.0 (deterministic)
- **Examples Needed:** 2-3 examples
- **Key:** Quote relevant passages, then answer

```python
prompt = """
Passage: "Cats are animals. Dogs are animals."
Q: Are cats animals?
A: According to the passage: "Cats are animals."
   Answer: Yes, cats are animals.
"""
```

### 💭 Commonsense Reasoning
- **Best Trigger:** "Let me think about what I know about this"
- **Format:** Background knowledge → reasoning → conclusion
- **Temperature:** 0.3-0.7 (some creativity okay)
- **Examples Needed:** 3-4 examples
- **Key:** Common sense connections are enough

```python
prompt = """
Q: Why do we use refrigerators?
A: Refrigerators keep food cold. Cold temperatures slow down bacteria growth.
   Bacteria cause food to spoil. So refrigerators preserve food.
"""
```

---

## ⚠️ Anti-Patterns: What NOT to Do

### ❌ Anti-Pattern 1: Too Vague

```
BAD:   Q: What's the answer to 10 + 5?
       A:

GOOD:  Q: What is 10 + 5? Show your work.
       A: I need to add 10 and 5.
          10 + 5 = 15
```

---

### ❌ Anti-Pattern 2: Examples Don't Match Question

```
BAD:   [Examples are about animals]
       Q: What is 10 + 5?

GOOD:  [Examples are math problems]
       Q: What is 10 + 5?
```

---

### ❌ Anti-Pattern 3: No Step Structure

```
BAD:   Q: Sarah has 10 apples and gives 3 away and buys 5 more.
       A: The answer is 12.

GOOD:  Q: Sarah has 10 apples and gives 3 away and buys 5 more.
       A: Start with 10. Give away 3: 10 - 3 = 7. Buy 5 more: 7 + 5 = 12.
```

---

### ❌ Anti-Pattern 4: Contradictory Examples

```
BAD:   Example 1: 10 + 5 = 15 ✓
       Example 2: 10 + 5 = 20 ✗  [Wrong!]

GOOD:  Example 1: 10 + 5 = 15 ✓
       Example 2: 10 + 5 = 15 ✓  [Consistent]
```

---

### ❌ Anti-Pattern 5: Too Long/Complicated

```
BAD:   Q: [Long complex problem with many details]
       A: [Overwhelming reasoning with 20 steps]

GOOD:  Q: [Clear, specific problem]
       A: [Logical 3-5 step reasoning]
```

---

## 🔍 Checklist: Is Your Prompt Good?

- [ ] **Trigger Phrase:** Starts with "Let me think" or "Let me work through"?
- [ ] **Examples Provided:** 2-4 clear examples for the task?
- [ ] **Examples Match:** Examples are in same domain as question?
- [ ] **Format Clear:** Each step is labeled/numbered?
- [ ] **Calculations Shown:** All math is explicit (not "obviously 15")?
- [ ] **No Contradictions:** All examples give consistent patterns?
- [ ] **Not Too Long:** Reasoning is 3-6 steps, not 20+?
- [ ] **Final Answer Clear:** What exactly is the expected answer format?

---

## 💻 Prompts Used in This Project

### Phase 1: Simple Math

```python
# Standard Prompting
prompt = f'Q: {question}\nA: '

# Chain-of-Thought
prompt = f'''Let me work through math problems step by step.

Example: If I have 5 apples and give away 2, I start with 5. I give away 2.
So 5 - 2 = 3 apples left.

Q: {question}
A: Let me think step by step. '''
```

### Phase 2: Production System

```python
# Few-shot with domain-specific examples
prompt = f"""Let me work through this step by step.

Example 1: If you have 5 oranges and buy 3 more, you start with 5.
You buy 3 more, so 5 + 3 = 8 oranges total.

Example 2: A store has 20 items and sells 5. Starting with 20,
they sell 5, so 20 - 5 = 15 items remain.

Q: {question}
A: Let me think step by step. """
```

### Phase 3: Self-Consistency

```python
# Generate multiple reasoning paths
for i in range(5):  # 5 different attempts
    response = call_model(prompt, temperature=0.7)
    answers.append(extract_answer(response))

# Vote on most common answer
final_answer = most_common(answers)
```

---

## 🎓 Key Parameters

### Temperature Effects

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| 0.0 | Deterministic, same answer always | Math, logic, facts |
| 0.3 | Mostly consistent, slight variation | Reasoning with nuance |
| 0.7 | Creative, different answers each time | Brainstorming, multiple solutions |
| 1.0 | Very random, unpredictable | Not recommended for reasoning |

### Number of Examples

| Complexity | Examples Needed | Details |
|-----------|-----------------|---------|
| Simple math | 2-3 | One operation per example |
| Word problems | 3-4 | Multiple steps per example |
| Logic | 2-3 | Clear reasoning structure |
| Commonsense | 4-5 | Varied scenarios |

---

## 📚 When to Reference This

- **Building your own CoT system?** → Check the Template Gallery
- **Prompt not working?** → Check the Anti-Patterns section
- **Domain-specific prompt?** → Check "By Domain"
- **Not sure about structure?** → Use the Prompt Anatomy checklist

---

## 🚀 Quick Copy-Paste Starters

### For Math
```
Let me work through math problems step by step.

Example:
Q:
A:

Q: [YOUR PROBLEM]
A: Let me think step by step.
```

### For Logic
```
Let me reason through this carefully.

Example:
Q:
A:

Q: [YOUR PROBLEM]
A: Let me work through the logic.
```

### For Multi-Step
```
Let me work through this step by step.

Example:
Q:
A:
  Step 1:
  Step 2:
  Step 3:
  Final Answer:

Q: [YOUR PROBLEM]
A: Let me work through each step.
```

---

## 🏦 Phase 4: Domain-Specific Prompts

### Financial Analysis Domain

**Portfolio Recommendation Prompt:**
```
You are a financial advisor. Analyze this portfolio and provide recommendations.

[Portfolio Details]

Provide:
1. Current allocation assessment
2. Risk analysis
3. Specific recommendations
4. Expected returns estimate

Let me think step by step:
```

**Investment Comparison Prompt:**
```
Solve this financial problem step by step:

[Problem with multiple investment options]

Show all calculations and reasoning:
- Define assumptions
- Calculate each option's value
- Compare results
- Make recommendation
```

### AP Calculus Domain

**Derivative Problem Prompt:**
```
Solve this AP Calculus derivative problem. Show all steps clearly.

[Problem]

Step-by-step solution:
1. Identify the rule needed (power, product, quotient, chain)
2. Apply the rule carefully
3. Simplify the result
4. Show the final answer

Let me work through this carefully:
```

**Optimization Problem Prompt:**
```
Solve this AP Calculus optimization problem. This requires finding max/min values.

[Problem]

Solution process:
1. Define all variables clearly
2. Write the objective function to optimize
3. Identify constraints
4. Take the derivative and find critical points
5. Use second derivative test or check endpoints
6. State the maximum or minimum value
7. Verify the answer is reasonable

Let me work through this optimization problem:
```

**Key Differences by Domain:**
- **Finance:** High stakes → Use Self-Consistency (multiple expert opinions)
- **Calculus:** Complex reasoning → Use Least-to-Most (decompose steps)
- **Both:** Always conclude with confidence scoring (1-10 rating)

---

**Last Updated:** April 5, 2026
**Status:** Updated for Phase 4! ✅
