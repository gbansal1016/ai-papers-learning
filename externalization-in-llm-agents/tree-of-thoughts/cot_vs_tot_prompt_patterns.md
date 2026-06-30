# Chain of Thought vs Tree of Thoughts: Prompt Patterns & Engineering

## Overview

This guide demonstrates the structural differences between CoT and ToT prompts, showing how to engineer effective prompts for each approach. Includes templates, examples, and best practices.

---

## Prompt Structure Comparison

### CoT Prompt Structure

```
[System Message] → [Task Description] → [Process Instructions] → [Output Format]

Components:
1. System prompt (role/context)
2. Problem description
3. Step-by-step instructions
4. Output format specification
```

### ToT Prompt Structure

```
[System Message] → [Task Description] → [Generation Instructions] → 
[Evaluation Instructions] → [Exploration Instructions] → [Synthesis Instructions] → 
[Output Format]

Components:
1. System prompt (role/context)
2. Problem description
3. Generate multiple approaches/hypotheses
4. Evaluate each option
5. Explore promising branches deeper
6. Synthesize findings
7. Output format specification
```

---

## Pattern 1: Mathematics Problems

### CoT Math Prompt

```markdown
# System Prompt (for all CoT math):
You are a mathematical problem solver. Show your reasoning clearly and work 
through problems step by step. Be precise with calculations.

# Example Prompt:
Solve this equation: 2^x + 3x = 20

Show your thinking step by step:
1. Analyze the equation type
2. Try different values or methods
3. Narrow down the solution
4. Verify your answer

Provide the solution and explain your approach.
```

**CoT Response Example:**
```
Step 1: Analyze the equation
This is a transcendental equation (mix of exponential and linear terms).
It doesn't have a closed-form algebraic solution.

Step 2: Try values
Let me estimate bounds first:
- x = 2: 2^2 + 3(2) = 4 + 6 = 10 (too low)
- x = 4: 2^4 + 3(4) = 16 + 12 = 28 (too high)
So solution is between 2 and 4.

Step 3: Narrow down
- x = 3: 2^3 + 3(3) = 8 + 9 = 17 (too low)
- x = 3.5: 2^3.5 + 3(3.5) = 11.31 + 10.5 = 21.81 (too high)
- x = 3.3: 2^3.3 + 3(3.3) = 9.85 + 9.9 = 19.75 (close)
- x = 3.35: 2^3.35 + 3(3.35) = 10.16 + 10.05 ≈ 20.21 (very close)

Step 4: Verify
x ≈ 3.345 gives f(x) ≈ 20.00

Solution: x ≈ 3.345
```

**Tokens Used:**
- Prompt: ~120
- Response: ~200
- Total: ~320

---

### ToT Math Prompt

```markdown
# System Prompt:
You are a mathematical problem solver using tree of thoughts methodology. 
Generate multiple solution strategies, evaluate their efficiency, and explore 
the most promising approaches.

# Example Prompt:
Solve: 2^x + 3x = 20 using tree of thoughts approach.

1. Generate 4-5 different solution strategies
   - Different methods, approaches, techniques
   - For each, outline how it would work

2. For each strategy, evaluate:
   - Time complexity (how fast to converge)
   - Implementation difficulty (1-10)
   - Reliability (how robust is it)
   - Accuracy potential

3. Explore the top 2-3 strategies in detail
   - Show actual calculations
   - Document convergence

4. Synthesize findings:
   - Which strategy is most efficient?
   - Why does it work best for this problem?
   - What did you learn?

Provide all strategies explored, not just the final answer.
```

**ToT Response Example:**
```
Strategy A: Trial & Error with Bisection
├─ Method: Bracket solution, repeatedly halve interval
├─ Efficiency: Medium - logarithmic convergence
├─ Difficulty: 3/10 (straightforward)
├─ Reliability: 9/10 (always converges)
└─ [Exploration shown: 5 iterations to high precision]

Strategy B: Newton-Raphson Method
├─ Method: Iterative using derivative
├─ Efficiency: High - quadratic convergence
├─ Difficulty: 6/10 (requires derivatives)
├─ Reliability: 8/10 (fails if bad initial guess)
├─ Initial guess: x₀ = 3
├─ f(x) = 2^x + 3x - 20
├─ f'(x) = 2^x·ln(2) + 3
├─ x₁ = 3 - f(3)/f'(3) = 3 - (-3)/(8·ln(2)+3) = 3.351
├─ x₂ = 3.345 (converged)
└─ [Detailed iteration shown]

Strategy C: Graphical-Analytical Hybrid
├─ Method: Combine graphical insight with analysis
├─ Efficiency: Low - mostly insights, not direct solution
├─ Difficulty: 4/10
├─ Reliability: 6/10 (depends on graphing accuracy)
└─ [Not developed further - less efficient than A, B]

Strategy D: Analytical Approximation
├─ Method: Use Taylor series near expected solution
├─ Efficiency: Medium-High if guess is good
├─ Difficulty: 7/10 (requires calculus)
├─ Reliability: 7/10 (error bounds needed)
└─ [Development shown with error analysis]

SYNTHESIS:
Ranking by efficiency:
1. Newton-Raphson (fastest: 2 iterations)
2. Bisection (5 iterations)
3. Approximation (comparable, more work)

CONCLUSION: x ≈ 3.345
Best method: Newton-Raphson for this class of problems
Learning: Iterative methods with derivatives are powerful for 
transcendental equations
```

**Tokens Used:**
- Prompt: ~200
- Response: ~700
- Total: ~900

---

## Pattern 2: Creative Writing

### CoT Writing Prompt

```markdown
# System Prompt:
You are a creative writing assistant. Write engaging, vivid prose that draws 
readers in and maintains their interest.

# Example Prompt:
Write an opening paragraph for a mystery novel where the detective discovers 
a crucial clue that changes everything.

Guidelines:
1. Set a compelling scene
2. Introduce tension or mystery
3. Plant the clue naturally
4. Create emotional impact
5. Hook the reader

Write one strong opening paragraph.
```

**CoT Response Example:**
```
The envelope sat on Detective Morrison's desk where nothing had been that 
morning, pristine white against the worn oak like an accusation. She'd been 
a cop for twenty years, long enough to recognize the weight of significance 
before she opened it, long enough to know that some envelopes contained 
truths you couldn't unknow. Her hands trembled slightly as she slid the 
single photograph out—a moment of weakness she'd never allow anyone to 
witness. The image showed Marcus Chen, dead these five years, alive in 
1987, standing next to the woman they'd convicted for his murder. In that 
moment, Morrison understood that the case she'd helped close was built on 
a lie, and that lie had just come back to haunt her.
```

**Tokens Used:**
- Prompt: ~120
- Response: ~180
- Total: ~300

---

### ToT Writing Prompt

```markdown
# System Prompt:
You are a creative writing assistant using tree of thoughts. Generate multiple 
opening approaches, evaluate each, and develop the strongest options.

# Example Prompt:
Write an opening paragraph for a mystery novel where the detective discovers 
a crucial clue. Use tree of thoughts:

1. Generate 5 different opening approaches
   - Different tones (noir, literary, suspenseful, introspective, action-driven)
   - Different POV or narrative techniques
   - Different types of "crucial clues"

2. For each approach, outline:
   - Tone/atmosphere created
   - Type of reader appeal
   - Hook strength (1-10)
   - Uniqueness (1-10)

3. Fully develop the 3 strongest approaches
   - Write complete paragraphs
   - Show how the clue is revealed
   - Create vivid prose for each

4. Compare the three versions:
   - Which is most engaging?
   - Which is most original?
   - Which best serves the mystery?

Provide all versions for side-by-side comparison.
```

**ToT Response Example:**
```
Approach 1: Noir/Hardboiled [Tone: Dark, world-weary]
├─ Technique: First-person internal monologue
├─ Clue type: Physical object with unexpected history
├─ Hook strength: 8/10
├─ Uniqueness: 6/10
└─ Full paragraph:
   "I found the letter in a dead man's pocket—or rather, his widow did, 
   and had the bad luck of showing me. Twenty years on the force teaches 
   you which questions to ask and which to leave alone. This wasn't a 
   question I could leave alone. The letter was dated six months after we 
   buried Tommy Chen. In Tommy's handwriting, it said: 'I was here all 
   along. You just didn't look close enough.' My blood went cold in a way 
   that had nothing to do with the January wind."

Approach 2: Introspective/Literary [Tone: Contemplative, emotionally complex]
├─ Technique: Third-person with internal revelation
├─ Clue type: Something from the past resurfacing
├─ Hook strength: 7/10
├─ Uniqueness: 9/10 ✓
└─ Full paragraph:
   "Detective Morrison had learned long ago to file her doubts in a locked 
   drawer and throw away the key. But keys have a way of appearing on your 
   desk on ordinary Tuesdays, and this key opened a drawer she'd sealed 
   away for five years. Inside: a photograph of Marcus Chen, alive, smiling, 
   standing next to the woman she'd helped convict of his murder. She stared 
   at the image for a long moment, and felt the entire architecture of her 
   career begin to shift like a building settling on an unstable foundation. 
   Some truths, she realized, were too heavy to carry alone."

Approach 3: Action/Suspenseful [Tone: Urgent, dangerous]
├─ Technique: Immediate present-tense action
├─ Clue type: Threatening or dangerous revelation
├─ Hook strength: 9/10 ✓✓
├─ Uniqueness: 7/10
└─ Full paragraph:
   "The call came at 3 AM. A body in the river, weighted down with concrete 
   shoes and twenty-year-old secrets. But it wasn't the body that made 
   Morrison's heart race—it was the victim's tattoo: the same symbol 
   inscribed on the wrist of the woman currently serving life for a murder 
   she'd committed. Which meant only one thing: if this victim was dead, 
   then the killer she'd convicted five years ago had been behind bars when 
   this murder happened. Morrison's mind raced as she stood in the rain, 
   watching the body bag being zipped up. Either she'd convicted the wrong 
   person, or someone else had gone to elaborate lengths to frame her. Both 
   options meant her career was finished."

SYNTHESIS:
Best hook: Approach 3 (9/10)
Most unique: Approach 2 (9/10)
Most balanced: Approach 2
Recommendation: Use Approach 2 or 3 depending on book's target audience
```

**Tokens Used:**
- Prompt: ~200
- Response: ~800
- Total: ~1000

---

## Pattern 3: Code Generation

### CoT Code Prompt

```markdown
# System Prompt:
You are an expert programmer. Write clean, efficient, well-documented code.
Follow best practices and produce production-quality implementations.

# Example Prompt:
Implement a function that finds the longest palindromic substring in a string.

Requirements:
1. Input: string s
2. Output: the longest palindromic substring
3. Time complexity: as efficient as possible
4. Return one result (not all results)

Show your thinking:
1. Explain your approach
2. Discuss time/space complexity
3. Write the code
4. Provide example usage
```

**CoT Response Example:**
```
Approach: Expand Around Centers

I'll use the "expand around center" technique because:
- It's O(n²) time and O(1) space
- More efficient than brute force O(n³)
- Simpler than complex algorithms like Manacher's

Algorithm:
1. For each possible center (including between characters)
2. Expand outward while characters match
3. Track the longest palindrome found

Complexity: O(n²) time, O(1) space

Code:
def longest_palindrome(s: str) -> str:
    if not s or len(s) < 2:
        return s
    
    def expand_around_center(left: int, right: int) -> int:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1  # length of palindrome
    
    start = 0
    max_len = 0
    
    for i in range(len(s)):
        # Odd-length palindromes
        len1 = expand_around_center(i, i)
        # Even-length palindromes
        len2 = expand_around_center(i, i + 1)
        
        max_len_at_i = max(len1, len2)
        if max_len_at_i > max_len:
            max_len = max_len_at_i
            start = i - (max_len - 1) // 2
    
    return s[start:start + max_len]

# Example usage:
assert longest_palindrome("babad") == "bab"  # or "aba"
assert longest_palindrome("cbbd") == "bb"
```

**Tokens Used:**
- Prompt: ~150
- Response: ~400
- Total: ~550

---

### ToT Code Prompt

```markdown
# System Prompt:
You are an expert programmer using tree of thoughts. Generate multiple solution 
approaches, evaluate their trade-offs, and implement the best options.

# Example Prompt:
Find the longest palindromic substring in a string using tree of thoughts.

Requirements:
1. Input: string s (up to 10,000 characters)
2. Output: the longest palindromic substring
3. Consider: time complexity, space complexity, implementation difficulty

Generate and compare solutions:

1. List 4-5 different approaches
   - Different algorithmic techniques
   - Different trade-offs

2. For each approach:
   - Outline the algorithm
   - Time complexity
   - Space complexity
   - Implementation difficulty (1-10)
   - Trade-offs with other approaches

3. Rate each on:
   - Efficiency (1-10)
   - Code clarity (1-10)
   - Practicality (1-10)

4. Implement the 2-3 best approaches
   - Show complete code
   - Include examples
   - Note any edge cases

5. Recommend which approach for what scenario
```

**ToT Response Example:**
```
Approach A: Brute Force
├─ Algorithm: Check all substrings
├─ Time: O(n³) - n² substrings, O(n) to check each
├─ Space: O(1)
├─ Difficulty: 2/10
├─ Efficiency: 2/10 | Clarity: 10/10 | Practicality: 2/10
└─ Score: 14/30 (only for learning)

Approach B: Expand Around Center ✓ SELECTED
├─ Algorithm: For each center, expand while palindrome
├─ Time: O(n²) - n centers, O(n) expansion each
├─ Space: O(1)
├─ Difficulty: 5/10
├─ Efficiency: 7/10 | Clarity: 8/10 | Practicality: 9/10
├─ Score: 24/30
└─ [Full implementation shown]

Approach C: Dynamic Programming
├─ Algorithm: Build table dp[i][j] = is_palindrome(i,j)
├─ Time: O(n²) - n² states, O(1) per state
├─ Space: O(n²) - the DP table
├─ Difficulty: 6/10
├─ Efficiency: 8/10 | Clarity: 6/10 | Practicality: 7/10
├─ Score: 21/30
└─ [Full implementation shown]

Approach D: Manacher's Algorithm ✓ SELECTED
├─ Algorithm: Linear-time algorithm using previous results
├─ Time: O(n) - linear time!
├─ Space: O(n) - auxiliary array
├─ Difficulty: 9/10 (complex to understand)
├─ Efficiency: 10/10 | Clarity: 2/10 | Practicality: 8/10
├─ Score: 20/30 (optimal but hard to implement)
└─ [Full implementation shown with explanation]

Approach E: Reverse String Matching
├─ Algorithm: Find longest common substring(s,s_reversed)
├─ Time: O(n²) using simple algorithm, O(n) with hashing
├─ Space: O(n)
├─ Difficulty: 6/10
├─ Efficiency: 7/10 | Clarity: 5/10 | Practicality: 6/10
├─ Score: 18/30
└─ [Not developed further]

IMPLEMENTATION COMPARISON:

Best for typical use: Approach B (Expand Around Center)
├─ Code: 30 lines
├─ Time: O(n²)
├─ Space: O(1)
├─ Learning curve: Medium
└─ [Code provided]

Best for competitive programming: Approach D (Manacher)
├─ Code: 50 lines
├─ Time: O(n) - actually linear!
├─ Space: O(n)
├─ Learning curve: High (complex algorithm)
└─ [Code provided with detailed comments]

Balanced choice: Approach C (DP)
├─ Code: 25 lines
├─ Time: O(n²)
├─ Space: O(n²)
├─ Learning curve: Medium
└─ [Code provided]

RECOMMENDATION:
├─ Use Approach B for: Interviews, production code (clear + efficient)
├─ Use Approach D for: Competitive programming (optimal)
├─ Use Approach C for: Learning DP concept
└─ Avoid Approach A: Unless teaching/learning basics
```

**Tokens Used:**
- Prompt: ~250
- Response: ~950
- Total: ~1200

---

## Prompt Engineering Best Practices

### For CoT Prompts

**Guidelines:**
```
1. Be explicit about the step-by-step process
   ✓ "Think step by step: 1) Identify assumptions, 2) List factors..."
   ✗ "Analyze this problem"

2. Use numbered steps
   ✓ Makes reasoning easier to follow
   ✗ Use bullet points (less linear)

3. Ask for intermediate reasoning
   ✓ "Show your work at each step"
   ✗ Just ask for final answer

4. Specify output format clearly
   ✓ "Provide: [analysis, recommendation, confidence score]"
   ✗ Leave format open

5. Keep prompts concise
   ✓ CoT works with shorter, focused prompts
   ✗ Don't over-explain the problem
```

**Example CoT Prompt Template:**
```markdown
[Problem]

Think step by step:
1. [First step to take]
2. [Second step]
3. [Third step]
...

Provide:
- [Output 1]: [description]
- [Output 2]: [description]
- [Output 3]: [description]
```

---

### For ToT Prompts

**Guidelines:**
```
1. Be explicit about exploration
   ✓ "Generate 4-5 different approaches"
   ✗ "Consider different angles"

2. Request evaluation for each option
   ✓ "Rate each on: [dimension 1], [dimension 2], [dimension 3]"
   ✗ "Evaluate the approaches"

3. Ask for synthesis/comparison
   ✓ "Compare the options side-by-side"
   ✗ "Which is best?"

4. Request multiple complete solutions
   ✓ "Fully develop the 2-3 highest-scoring approaches"
   ✗ Just show summaries

5. Be more detailed than CoT
   ✓ Longer prompts with explicit structure
   ✓ Specify exploration depth
   ✗ Keep prompts minimal
```

**Example ToT Prompt Template:**
```markdown
[Problem] using tree of thoughts approach.

1. Generate [N] different [solutions/approaches/strategies]
   - Each with [key difference]
   - For each, outline: [factor 1], [factor 2], [factor 3]

2. For each option, evaluate:
   - [Metric 1]: [1-10]
   - [Metric 2]: [1-10]
   - [Metric 3]: [1-10]
   - Score: [Total out of 30]

3. Fully develop the [top N] options
   - Show [specific details]
   - Include [examples/code/analysis]
   - Explain [trade-offs]

4. Compare all versions:
   - Create [comparison table/matrix]
   - Highlight [key differences]

5. Synthesize findings:
   - Which option is best for [use case 1]?
   - Which for [use case 2]?
   - What are the trade-offs?

Provide all approaches explored, showing your full reasoning.
```

---

## System Prompts

### CoT System Prompt

```markdown
You are a helpful assistant that solves problems by thinking step by step.
When given a problem, you:
1. Break it down into manageable parts
2. Work through each part systematically
3. Show your reasoning clearly
4. Provide a clear final answer

You are concise but thorough. You show enough work for readers to verify
your reasoning, but don't over-explain obvious steps.

Your goal is to be both clear and efficient.
```

### ToT System Prompt

```markdown
You are a thoughtful analyst that solves complex problems using tree of thoughts.
When given a problem, you:
1. Generate multiple solution approaches or hypotheses
2. Evaluate each option systematically
3. Identify the most promising paths
4. Explore those paths in depth
5. Synthesize your findings into clear recommendations

You are thorough and structured. You make your thinking transparent by:
- Showing all approaches considered
- Explicitly evaluating trade-offs
- Clearly rating options
- Explaining why some paths are more promising than others

Your goal is to provide comprehensive analysis and robust recommendations.
```

---

## Comparison: Same Problem, Different Prompts

### Problem: Should we adopt AI for customer service?

**CoT Prompt:**
```
Should our company adopt AI for customer service?

Analyze step by step:
1. What are the key benefits?
2. What are the key risks?
3. What's the cost?
4. What's the timeline?
5. What's your recommendation?

Provide: Benefits, Risks, Cost analysis, Timeline, Recommendation
```

**CoT Response (~400 tokens):**
```
Benefits:
- 24/7 availability, faster response times, lower costs per ticket
- Scalability without linear hiring
- Consistent quality, reduced human error

Risks:
- Loss of human touch, difficult edge cases, customer frustration
- Job displacement concerns, implementation challenges

Cost:
- Implementation: $500K-1M, Annual: $200K maintenance

Timeline:
- 3-6 months to full deployment

Recommendation:
PROCEED with AI for Tier 1 support while maintaining human escalation.
This captures benefits while mitigating risks.
```

---

**ToT Prompt:**
```
Should we adopt AI for customer service? Use tree of thoughts.

1. Generate 4 different implementation strategies
   - Each with different scope, cost, timeline
   - For each outline benefits, risks, costs

2. Evaluate each strategy on:
   - Revenue impact (1-10)
   - Risk level (1-10)
   - Implementation difficulty (1-10)

3. Fully develop top 2 strategies
   - Financial projections
   - Implementation timeline
   - Change management needs
   - Success metrics

4. Compare strategically
   - Best case scenario for each
   - Worst case scenario for each
   - Most likely outcome

5. Recommend which strategy for our company
   - Conditional factors
   - Success criteria
```

**ToT Response (~1200 tokens):**
```
Strategy A: Gradual Tier 1 Only
├─ Scope: AI handles simple questions only
├─ Cost: $300K impl, $150K/year
├─ Benefits: Positive customer experience, staff isn't displaced
├─ Risks: Low (humans handle complex cases)
├─ Revenue Impact: 3/10 | Risk: 2/10 | Difficulty: 4/10 | Score: 9/30
└─ [Detailed analysis]

Strategy B: Full Replacement (Aggressive)
├─ Scope: AI handles 80%+ of interactions
├─ Cost: $2M impl, $800K/year
├─ Benefits: Maximum cost savings, fastest response
├─ Risks: High (customer satisfaction, employee issues)
├─ Revenue Impact: 8/10 | Risk: 9/10 | Difficulty: 9/10 | Score: 26/30
└─ [Detailed analysis]

Strategy C: Hybrid Human-AI (Balanced) ✓ SELECTED
├─ Scope: AI for routine, human for complex
├─ Cost: $800K impl, $500K/year
├─ Benefits: Quality + efficiency, preserves jobs
├─ Risks: Medium (requires good routing system)
├─ Revenue Impact: 7/10 | Risk: 4/10 | Difficulty: 6/10 | Score: 17/30
└─ [Detailed analysis]

Strategy D: Outsource AI Platform (Low Risk)
├─ Scope: Use third-party platform, less customization
├─ Cost: $100K impl, $300K/year
├─ Benefits: Fast deployment, no internal expertise needed
├─ Risks: Medium (vendor lock-in, less customization)
├─ Revenue Impact: 5/10 | Risk: 5/10 | Difficulty: 2/10 | Score: 12/30
└─ [Detailed analysis]

COMPARISON TABLE:
[Shows all metrics side-by-side]

RECOMMENDATION:
Strategy C (Hybrid) is optimal IF:
✓ Company prioritizes customer experience AND operational efficiency
✓ Can invest in good AI routing system
✓ Wants to preserve staff roles

Use Strategy A IF:
✓ Risk-averse, prefer incremental change
✓ Limited budget ($300K)
✓ Want fastest deployment

Use Strategy D IF:
✓ Want minimal internal complexity
✓ Willing to pay for convenience
✓ Don't need deep customization

Avoid Strategy B unless:
✓ Cost savings are absolutely critical
✓ Can manage significant change management
✓ Customer satisfaction less important than costs
```

---

## Token Cost Comparison by Prompt Type

| Task Type | CoT Tokens | ToT Tokens | Ratio | Use Case |
|-----------|-----------|-----------|-------|----------|
| Math (simple) | 250 | 650 | 2.6x | CoT |
| Math (complex) | 400 | 950 | 2.4x | ToT |
| Writing (routine) | 300 | 750 | 2.5x | CoT |
| Writing (creative) | 450 | 1100 | 2.4x | ToT |
| Code (standard) | 350 | 900 | 2.6x | CoT |
| Code (optimization) | 500 | 1200 | 2.4x | ToT |
| Decision (simple) | 300 | 800 | 2.7x | CoT |
| Decision (strategic) | 550 | 1300 | 2.4x | ToT |

**Average:** ToT uses ~2.5x more tokens than CoT

---

## Prompting Tips

### For Better CoT Results:
1. **Use explicit numbering** - Structures linear thinking
2. **Ask for verification** - "Verify your answer"
3. **Specify confidence** - "Rate confidence in answer (1-10)"
4. **Request justification** - "Explain why"
5. **Use clear steps** - Break into obvious pieces

### For Better ToT Results:
1. **Explicit evaluation criteria** - Be specific about metrics
2. **Encourage diversity** - "Generate different approaches"
3. **Request synthesis** - "Compare and contrast"
4. **Show the tree** - Ask to display exploration
5. **Rate transparently** - Ask for scores on each dimension

---

## Template Library

### CoT Template: Technical Problem

```markdown
Problem: [Describe the technical issue]

Debug step by step:
1. Identify the symptom
2. Identify likely causes
3. Test each cause
4. Narrow down the root cause
5. Propose solution

Provide: Root cause analysis, Proposed fix, Testing approach
```

### ToT Template: Strategic Decision

```markdown
Decision: [Should we do X?] Use tree of thoughts.

1. Generate 5 different strategic approaches
   - Each with different assumptions
   - Outline for each

2. Evaluate on: Strategic fit (1-10), Risk (1-10), Cost (1-10)

3. Develop top 3 approaches fully
   - Financial impact
   - Timeline
   - Success factors

4. Create comparison matrix

5. Recommend with conditions
```

### ToT Template: Complex Problem-Solving

```markdown
Problem: [Complex challenge] Use tree of thoughts.

1. Generate 4-5 solution approaches
   - Different methodologies
   - Different constraints prioritized

2. For each, outline:
   - How it would work
   - Pros and cons
   - Implementation difficulty

3. Develop 2-3 highest-potential approaches
   - Step-by-step implementation
   - Resource requirements
   - Timeline

4. Synthesize: Which works best for our context?
```

---

## Summary

**CoT Prompts:**
- Shorter (100-150 tokens)
- Linear structure
- Numbered steps
- Emphasis on efficiency
- Better for: Simple, clear problems

**ToT Prompts:**
- Longer (200-350 tokens)
- Branching structure
- Explicit evaluation
- Emphasis on exploration
- Better for: Complex, multi-faceted problems

**Key Rule:** Match prompt structure to problem complexity. Let the problem determine the prompt, not your preference.
