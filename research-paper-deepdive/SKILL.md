---
name: research-paper-deepdive
description: |
  Deep dive into research papers with a structured, phased learning approach. 
  
  Use this skill when you want to comprehensively study a research paper. It creates 
  a complete learning structure with progressively complex notebooks, executable code 
  examples, documentation, and practical materials. Perfect for understanding papers 
  in depth rather than just skimming them.
  
  Trigger this when someone says:
  - "Deep dive into [paper name]"
  - "Create a study guide for this research paper"
  - "Generate learning materials for [paper]"
  - "Help me understand [paper] comprehensively"
  - "Create a research exploration for [paper]"
  - "Build a learning path through [paper]"
  - Any variation where someone wants structured, multi-phase exploration of a paper
  
  Input: Paper title, abstract, authors, year, or URL
  Output: Complete folder with 3-4 phase notebooks, code, docs, and guides
---

# Research Paper Deep Dive Skill

## Overview

This skill transforms a research paper into a complete learning journey. Instead of just reading a paper once, you get:

- **Phase 0: Fundamentals** - Pure conceptual understanding (no code)
- **Phase 1: Basic Concepts** - Implement core data structures
- **Phase 2: Algorithms** - Advanced implementations and techniques
- **Phase 3+: Advanced Topics** - Integration, optimization, real-world applications
- **Supporting Materials** - Documentation, comparisons, quickstart guides

Everything is executable Python code in Jupyter notebooks, structured for progressive learning.

---

## How It Works

### 1. You Provide the Paper
Give me:
- Paper title (required)
- Authors and year (helpful)
- Abstract or URL (optional but useful)
- Any research context (what field, why it interests you)

### 2. I Create Your Learning Structure

**Folder Layout:**
```
<paper-name>/
├── readme.md                    (Paper reference & overview)
├── quickstart.md               (Getting started guide)
├── phase0_fundamentals.ipynb   (Concepts only - no code)
├── phase1_basic_concepts.ipynb (Core implementations)
├── phase2_algorithms.ipynb     (Advanced techniques)
├── phase3_applications.ipynb   (Real-world use cases) [if applicable]
├── <paper>_vs_related.md       (Comparison with similar work)
├── requirements.txt            (Python dependencies)
└── .venv/                      (Virtual environment)
```

### 3. Progressive Learning Path

**Phase 0: Fundamentals** (30 minutes)
- Paper abstract and core innovation
- Problem motivation
- Why this matters
- Key concepts explained visually
- Real examples from the paper
- When to use this approach
- All in prose - no code yet

**Phase 1: Basic Concepts** (45 minutes)
- Implement core data structures
- Simple, runnable Python code
- Manual examples you can trace through
- Understanding through building
- Exercises to solidify learning

**Phase 2: Algorithms** (60 minutes)
- Implement key algorithms
- Search strategies / optimization techniques
- Performance metrics and analysis
- Comparison of approaches
- Trade-off discussions
- Practical examples with output

**Phase 3: Applications** (optional, 60+ minutes)
- Real-world use cases
- Integration patterns
- Optimization techniques
- Extension ideas
- How to apply to your own problems

### 4. Supporting Materials

**readme.md**
- Complete paper reference and citation
- Abstract explaining the innovation
- Methodology overview
- Key contributions
- Related work
- Resources for deeper learning

**quickstart.md**
- 2-minute setup
- Which notebook to read first
- Expected learning outcomes
- Troubleshooting guide

**Comparison Document** (if applicable)
- How this paper relates to similar work
- Comparison with prior techniques
- Advantages and disadvantages
- When to use each approach

**requirements.txt**
- All Python dependencies
- Exact versions for reproducibility

### 5. Code Quality

All code includes:
- ✅ Type hints and documentation
- ✅ Clear comments explaining concepts
- ✅ Runnable examples with output
- ✅ Practical use cases
- ✅ Error handling
- ✅ No external LLM dependencies (Phases 0-2)

---

## Customization Options

When requesting, you can specify:

**Depth:**
- Light (2 phases, ~2 hours total)
- Standard (3 phases, ~3 hours total) ← default
- Deep (4+ phases, 4+ hours total)

**Code Focus:**
- Conceptual (understanding) ← default
- Implementation (building systems)
- Both (balanced)

**Comparisons:**
- Compare with related papers
- Compare with related techniques
- No comparisons
- Automatically detected ← default

**Target Audience:**
- Researchers (technical depth)
- Practitioners (practical focus)
- Students (educational) ← default
- Mixed (balanced)

---

## Example Use

```
User: "Create a deep dive study guide for the Transformer paper 
(Vaswani et al., 2017). I want comprehensive learning materials 
with Python code examples."

Skill creates:
- readme.md with full paper reference
- phase0_fundamentals.ipynb explaining self-attention, 
  positional encoding, architecture
- phase1_basic_concepts.ipynb implementing core components
- phase2_algorithms.ipynb implementing training, inference
- phase3_applications.ipynb on transfer learning, fine-tuning
- transformers_vs_related.md comparing with RNNs, CNNs
- requirements.txt with transformers, torch, etc.
```

---

## What You Get

✅ **Complete Learning Journey** - Not just one read-through, but deep understanding
✅ **Executable Code** - Run examples, experiment, learn by doing
✅ **Progressive Difficulty** - Start simple, build to complexity
✅ **Supporting Materials** - Guides, comparisons, references
✅ **Reproducible** - Same environment every time with .venv
✅ **Self-Contained** - Everything you need in one folder
✅ **Reusable Template** - This skill works for any research paper

---

## Before You Start

Have ready:
1. **Paper title** (required)
2. **Authors and year** (helpful)
3. **Paper abstract or URL** (optional)
4. **Your context** (why studying this, your background)
5. **Preferred depth** (standard is good starting point)

---

## Output Format

All deliverables use:
- ✅ **Lowercase filenames** - Consistent and clean
- ✅ **Markdown documentation** - Easy to read
- ✅ **Jupyter Notebooks** - Interactive and executable
- ✅ **Python 3.8+** - Modern, widely compatible
- ✅ **Self-contained** - Works offline with one pip install

---

## Success Criteria

After completing all phases, you should:
- ✅ Understand core concepts deeply
- ✅ Be able to implement key algorithms
- ✅ Know when and how to use these techniques
- ✅ Be able to apply to your own problems
- ✅ Understand trade-offs and limitations
- ✅ Know where to go for deeper learning

---

## Tips for Best Results

1. **Start with readme.md** - Understand the paper context first
2. **Don't skip Phase 0** - Foundation matters
3. **Code along in Phase 1 & 2** - Don't just read, type it out
4. **Experiment** - Modify examples, test your understanding
5. **Take notes** - Write down key insights
6. **Return later** - These materials are reference documents
