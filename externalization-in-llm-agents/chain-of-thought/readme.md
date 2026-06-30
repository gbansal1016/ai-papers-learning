# Chain-of-Thought (CoT) Prompting - Deep Dive Study

A comprehensive, executable deep dive into the **Chain-of-Thought Prompting** research paper with 4 progressive phases from basics to real-world applications.

**Paper:** [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)

---

## ⚡ Important: Local Model Performance

This study uses **Mistral-7B-Instruct-v0.1** for local inference (free, private, no API keys needed). However, **inference is painfully slow**:

- **CPU:** ~5-10 seconds per inference call
- **GPU (NVIDIA):** ~1-3 seconds per inference call

**If you need speed:** Use cloud APIs (OpenAI, HuggingFace Inference API) instead by modifying `call_model()` function.

**For learning:** The slow inference is acceptable since we're studying CoT concepts, not optimizing production systems.

---

## 📚 Quick Start

### Option 1: Run Locally (Recommended for Learning)
```bash
# Install dependencies
pip install -r requirements.txt

# Start with Phase 1
jupyter notebook phase1_prompting_basics.ipynb
```

### Option 2: Check System Before Running
```bash
python3 << 'EOF'
import torch
print("GPU Available:", torch.cuda.is_available())
print("GPU Type:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")
EOF
```

---

## 🎯 The Four Phases

### **Phase 1: Prompting Basics** (15-20 min)
- Understand standard vs CoT prompting
- Test on simple math problems
- Measure accuracy improvements
- **File:** `phase1_prompting_basics.ipynb`

### **Phase 2: CoT Implementation** (20-30 min)
- Build a production-ready CoT evaluator class
- Test on real benchmark datasets
- Hyperparameter tuning (temperature effects)
- **File:** `phase2_cot_implementation.ipynb`

### **Phase 3: Advanced Techniques** (25-35 min)
- Self-Consistency Sampling (multiple reasoning paths)
- Least-to-Most Prompting (problem decomposition)
- Confidence scoring
- **File:** `phase3_advanced_techniques.ipynb`

### **Phase 4: Integrated Applications** (30-40 min)
- Intelligent technique router (chooses best method automatically)
- Domain-specific solvers:
  - **Financial Analysis:** Portfolio recommendations, investment comparisons
  - **AP Calculus:** Derivatives, optimization, step-by-step reasoning
- Combines all Phases 1-3 techniques in production system
- **File:** `phase4_applications.ipynb`

---

## 📖 Documentation

- **cot-guide.md** - Complete paper breakdown with key concepts
- **quick-reference.md** - Quick lookup for syntax and patterns
- **prompting-guide.md** - ⭐ Complete guide to prompt types, templates, and best practices

---

## 🛠️ Technical Stack

| Component | Details |
|-----------|---------|
| **Model** | Mistral-7B-Instruct-v0.1 (7B parameters) |
| **Framework** | HuggingFace Transformers |
| **Inference** | Local (on CPU or GPU) |
| **Notebooks** | Jupyter with progressive sections |
| **Output** | JSON results, CSV analysis, PNG visualizations |

---

## ⏱️ Performance Expectations

### First Run (Model Download + Load)
- Download: 1-5 minutes (~4GB)
- Load: ~30 seconds
- First inference: 7-8 minutes (CPU) / 1-2 minutes (GPU)

### Subsequent Runs
- Model cached locally
- Load time: ~5 seconds
- Per inference: 5-10 seconds (CPU) / 1-3 seconds (GPU)

### Total Study Time
- All 4 phases: 1.5-2 hours (plus ~3 minutes for initial model download)

---

## 🔧 Troubleshooting

### Issue: Model loads but inference fails
**Solution:** Run Section 5.5 (DEBUG) in Phase 1 to diagnose the exact error

### Issue: Out of memory (OOM)
**Solutions:**
- Close other applications
- Reduce `max_tokens` parameter (default: 150)
- Use smaller model (GPT-2 fallback available)

### Issue: Very slow inference
**Causes:**
- Running on CPU (expected: 5-10 seconds/call)
- Not enough RAM (causes swapping)

**Solutions:**
- Use GPU (CUDA) if available
- Reduce `max_tokens`
- Switch to cloud API

### Issue: Can't find Python dependencies
**Solution:**
```bash
pip install -r requirements.txt --break-system-packages
```

---

## 📊 What You'll Learn

By completing all phases, you'll understand:

✅ **Concept:** How Chain-of-Thought prompting improves reasoning
✅ **Theory:** Why it works and when it applies
✅ **Implementation:** How to build CoT systems from scratch
✅ **Evaluation:** Measuring accuracy and performance
✅ **Advanced Techniques:** Self-consistency, tree-of-thoughts
✅ **Production Patterns:** Real-world deployment considerations

---

## 📁 File Structure

```
chain-of-thought/
├── readme.md                          ← You are here
├── cot-guide.md                       # Detailed paper breakdown
├── quick-reference.md                 # Quick lookup guide
├── prompting-guide.md                 # Prompt types & templates
├── requirements.txt                   # Python dependencies
│
├── phase1_prompting_basics.ipynb      # Phase 1: Basics
├── phase2_cot_implementation.ipynb    # Phase 2: Implementation
├── phase3_advanced_techniques.ipynb   # Phase 3: Advanced
├── phase4_applications.ipynb          # Phase 4: Applications
│
├── phase1_results.json                # Phase 1 results
├── phase1_results.csv                 # Phase 1 analysis
├── phase1_results.png                 # Phase 1 visualization
├── phase2_results.json                # Phase 2 results
├── phase2_results.csv                 # Phase 2 analysis
└── temperature_tuning.png             # Hyperparameter tuning
```

---

## 🚀 Getting Started Now

1. **Check hardware:**
   ```bash
   python3 -c "import torch; print('GPU:', torch.cuda.is_available())"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Phase 1:**
   ```bash
   jupyter notebook phase1_prompting_basics.ipynb
   ```

4. **Run Section 1-3 first** to verify everything works

5. **If Section 6-7 fails:** Run Section 5.5 (DEBUG) for detailed error info

---

## 💡 Key Takeaways

| Topic | Takeaway |
|-------|----------|
| **CoT Concept** | Showing reasoning improves accuracy on complex tasks |
| **Scale Dependency** | Only works well with models 100B+ parameters |
| **Performance** | Slow inference (7-10 seconds/call on CPU) but better accuracy |
| **Best For** | Complex reasoning, math, multi-step logic |
| **Not For** | Simple factual Q&A, real-time systems, latency-critical apps |

---

## 📚 Related Resources

- **Original Paper:** https://arxiv.org/abs/2201.11903
- **Self-Consistency:** https://arxiv.org/abs/2203.11171
- **Tree of Thoughts:** https://arxiv.org/abs/2305.10601
- **Least-to-Most:** https://arxiv.org/abs/2205.10625

---

## ✍️ Notes for Learners

- Each phase builds on previous knowledge - **don't skip around**
- Results vary based on model randomness - **don't expect identical outputs**
- Speed depends heavily on hardware - **GPU makes a massive difference**
- Errors in Section 6-7? Use **Section 5.5 DEBUG** to diagnose
- Model is 7B parameters - **it's not as smart as GPT-4, that's intentional**

---

**Status:** ✅ All phases updated to use local Mistral-7B (April 2026)

**Estimated Time:** 1.5-2 hours (all phases)

**Difficulty:** Intermediate (assumes basic Python + LLM knowledge)

---

Happy learning! 🎓✨
