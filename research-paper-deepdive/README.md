# Research Paper Deep Dive Skill

A reusable Claude skill for creating comprehensive, phased learning materials for any research paper.

## What This Skill Does

Transforms a research paper into a complete, structured learning journey with:

✅ **Phase 0: Fundamentals** - Conceptual understanding (no code)
✅ **Phase 1: Basic Concepts** - Core data structures and implementations
✅ **Phase 2: Algorithms** - Advanced techniques and algorithms
✅ **Phase 3+: Applications** - Real-world use cases (optional)
✅ **Supporting Materials** - Documentation, guides, comparisons

## How to Use

### Quick Example

```
User: "Deep dive into the Attention is All You Need paper 
(Vaswani et al., 2017). Create comprehensive learning materials."

Skill generates:
├── readme.md (paper reference)
├── quickstart.md (setup guide)
├── phase0_fundamentals.ipynb (concepts)
├── phase1_basic_concepts.ipynb (implementation)
├── phase2_algorithms.ipynb (advanced)
├── requirements.txt
└── .venv/ (virtual environment)
```

### Key Input Parameters

When requesting this skill, provide:
- **Paper title** (required)
- **Authors & year** (helpful)
- **Abstract** (optional)
- **Depth preference** (light/standard/deep)
- **Code focus** (conceptual/implementation/both)

## File Structure

```
research-paper-deepdive/
├── SKILL.md                    (Skill definition)
├── README.md                   (This file)
├── scripts/
│   ├── generate_deepdive.py   (Main generator script)
│   └── __init__.py            (Module init)
└── references/ (future)
    ├── phase0_template.md
    ├── phase1_template.py
    └── phase2_template.py
```

## Installation

### In Cowork/Claude Code

1. Copy this skill folder to your `.claude/skills/` directory:
```bash
cp -r research-paper-deepdive ~/.claude/skills/
```

2. Restart Claude Code to load the skill

3. Now you can invoke it:
```
"Deep dive into [paper name] with comprehensive study materials"
```

### Standalone Usage

Use the generator script directly:

```bash
cd scripts
python generate_deepdive.py \
    --paper-title "Attention is All You Need" \
    --authors "Vaswani et al." \
    --year 2017 \
    --abstract "The paper introduces the Transformer architecture..." \
    --output-dir ../my-research \
    --phases 3
```

## Generated Output

The skill generates a complete, self-contained study package:

### readme.md
- Full paper reference with citation
- Learning structure overview
- Quick reference guide

### quickstart.md
- 2-minute setup guide
- Learning objectives
- Troubleshooting

### Jupyter Notebooks

**phase0_fundamentals.ipynb** (~30 min)
- Paper abstract and core innovation
- Problem motivation
- Key concepts overview
- When to use this approach

**phase1_basic_concepts.ipynb** (~45 min)
- Core data structures
- Simple, runnable Python code
- Learning through building
- Exercises

**phase2_algorithms.ipynb** (~60 min)
- Algorithm implementations
- Performance analysis
- Trade-off discussions
- Practical examples

**phase3_applications.ipynb** (optional, ~60+ min)
- Real-world use cases
- Integration patterns
- Extension ideas

### requirements.txt
- All Python dependencies
- Exact versions for reproducibility

## Customization Options

When using the skill, you can specify:

### Depth
- **Light** (2 phases, ~2 hours)
- **Standard** (3 phases, ~3 hours) - default
- **Deep** (4+ phases, 4+ hours)

### Code Focus
- **Conceptual** - Understanding focused
- **Implementation** - Systems building
- **Both** - Balanced approach

### Audience
- **Researchers** - Technical depth
- **Practitioners** - Practical focus
- **Students** - Educational
- **Mixed** - Balanced

### Comparisons
- Compare with related papers
- Compare with related techniques
- No comparisons
- Auto-detect (default)

## Example Workflow

1. **Request the skill:**
   ```
   "Create a deep dive study guide for the Tree of Thoughts paper 
   (Yao et al., 2023). Focus on implementation with practical examples."
   ```

2. **Skill generates all materials** in organized folder

3. **You study progressively:**
   - Read readme.md (understand context)
   - Work through phase0 (grasp concepts)
   - Code phase1 (build foundations)
   - Implement phase2 (advanced techniques)
   - Explore phase3 (real applications)

4. **You have permanent reference materials**
   - Can return anytime for review
   - Runnable code to experiment with
   - Progressive learning path

## Features

✅ **Comprehensive** - 3-4 phases covering breadth and depth
✅ **Executable** - All code runs immediately
✅ **Progressive** - Concepts → Basic → Advanced
✅ **Self-Contained** - Everything in one folder
✅ **Reproducible** - Virtual environment included
✅ **Reusable** - Works for any research paper
✅ **Documented** - Extensive comments and guides
✅ **Professional** - Publication-quality structure

## Success Metrics

After using this skill, you should:

✅ Understand paper concepts deeply
✅ Be able to implement key ideas
✅ Know when and how to apply the techniques
✅ Understand trade-offs and limitations
✅ Have permanent reference materials
✅ Be ready to extend the work further

## Tips

1. **Start with readme.md** - Get paper context
2. **Don't skip Phase 0** - Foundation matters
3. **Code along** - Don't just read
4. **Experiment** - Modify examples, test understanding
5. **Take notes** - Document insights
6. **Return later** - Use as reference document

## Integration with Other Tools

Works great with:
- Your existing research folders (bert, chain-of-thought, etc.)
- Jupyter notebooks and JupyterLab
- Standard Python development tools
- Version control (git)
- Research management systems

## Limitations

- Generates templates/scaffolding (you can customize)
- Phase 0-2 don't require external APIs
- Phase 3+ may benefit from LLM integration
- Requires Python 3.8+
- Jupyter installation needed

## Future Enhancements

Potential improvements:
- Automatic paper download and summarization
- Template customization per domain
- Phase 3+ auto-generation with LLM integration
- Comparison generation with related work
- Bibliography extraction
- Citation management

## Credits

Created as a reusable skill based on the Tree of Thoughts deep dive project.
Designed for comprehensive research paper understanding and study.

---

**Ready to use?** Try requesting:
```
"Create a deep dive study guide for [paper name]"
```

The skill will generate everything you need for comprehensive learning! 🚀
