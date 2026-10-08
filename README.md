# Business Strategist LLM (Bangla + English)

A synthetic instruction dataset and QLoRA fine-tuning pipeline for turning a small (3B) open model into a **logical business strategist** that understands **Bangla, English, and mixed Banglish**.

The model is trained to reason step by step (first-principles, unit economics, decision analysis), apply **behavioral economics and business psychology** ethically, and handle **Bangladesh market context** (F-commerce, Cash on Delivery, trust issues, discount culture).

> **Status:** v0.1 dataset (2,848 examples) + working training notebook. The dataset is template-based and meant as a strong base to extend, not a finished product. See [Limitations](#limitations).

---

## Table of contents

- [What is in this repo](#what-is-in-this-repo)
- [Dataset](#dataset)
- [Quick start (Google Colab)](#quick-start-google-colab)
- [Run locally](#run-locally)
- [Training details](#training-details)
- [Reproduce or customize the dataset](#reproduce-or-customize-the-dataset)
- [Evaluating the model](#evaluating-the-model)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [Responsible use](#responsible-use)
- [License](#license)

---

## What is in this repo

```
business-strategist-llm/
├── README.md
├── data/
│   ├── business_strategist_train.jsonl            # 2,706 examples, messages only (use this to train)
│   ├── business_strategist_eval.jsonl             # 142 held-out examples
│   ├── business_strategist_full_with_meta.jsonl   # all 2,848 examples + topic/lang tags
│   └── seed_examples.jsonl                        # 15 hand-written "gold" examples
├── scripts/
│   ├── generate_dataset.py                        # dataset generator (seeded, reproducible)
│   └── finetune_unsloth.py                        # same training code as the notebook, as a script
└── notebooks/
    └── finetune_business_strategist.ipynb         # Colab-ready QLoRA notebook
```

---

## Dataset

### Format

Chat-style JSONL. Each line has a `messages` list with `system`, `user`, and `assistant` turns:

```json
{
  "messages": [
    {"role": "system", "content": "You are a logical business strategist ..."},
    {"role": "user", "content": "My SaaS has ARPU $50/month, 80% gross margin, 5% monthly churn and CAC of $400. Is this healthy?"},
    {"role": "assistant", "content": "## বিশ্লেষণ (Step-by-step)\n1. **Lifetime:** 1 ÷ 5% = 20 months.\n...\n## সুপারিশ\n...\n## ঝুঁকি ও পরবর্তী পদক্ষেপ\n..."}
  ]
}
```

The `full_with_meta` file adds a `meta` object (`{"topic": "ltv_cac", "lang": "en"}`) for filtering and balancing. Remove it before training (the `train`/`eval` files already have it removed).

### Chain-of-thought structure

Every answer follows the same three-part structure so the model learns the reasoning pattern:

1. **বিশ্লেষণ (Step-by-step)**: the reasoning, with explicit calculations or framework steps
2. **সুপারিশ (Recommendation)**: a clear, actionable decision
3. **ঝুঁকি ও পরবর্তী পদক্ষেপ (Risks and next steps)**: assumptions, failure modes, how to validate

### Language mix

| Language | Examples |
|---|---|
| English | 997 |
| Bangla (Bangla script, Bangla numerals, lakh-style taka) | 981 |
| Banglish (romanized Bangla prompts, Bangla-script answers) | 870 |

### Topics

| Pillar | Topic | Examples |
|---|---|---|
| **Logical strategy / unit economics** | LTV, CAC, payback | 220 |
| | Runway and burn rate | 200 |
| | Decision tree / expected value | 220 |
| | Break-even analysis | 160 |
| | Retention and churn math | 28 |
| | Price increase break-even | 90 |
| | Channel comparison (CAC, LTV:CAC) | 200 |
| | RICE prioritization | 160 |
| | Service-business margin and pricing | 200 |
| | MECE revenue-drop diagnosis (5 business types) | 60 |
| **Business psychology** | Anchoring, loss aversion, scarcity, social proof, decoy, reciprocity, commitment (10 industries each) | 210 |
| | Decoy pricing design | 120 |
| | Negotiation with BATNA | 200 |
| **Bangladesh market context** | COD return economics (F-commerce) | 220 |
| | Advance payment resistance, discount culture, page trust, courier failures, Eid demand, Messenger sales | 180 |
| **Ethics** | Polite refusals of deceptive tactics (fake testimonials, fake countdowns, fake scarcity, bought reviews, fake logos, fabricated before/after) with honest alternatives | 180 |
| | **Total** | **2,848** |

### How the numbers are produced

All quantitative examples (LTV, runway, expected value, break-even, margins, and so on) are **computed in Python** from randomized inputs, so the arithmetic in the training data is correct. The model is taught the *method* and the numeric reasoning pattern, not memorized answers.

### Design principle: no manipulation

Psychology examples teach how to use cognitive biases to make a *genuinely good offer* easier to understand, and always include an ethics line. The dataset includes explicit refusals for deceptive requests (fake social proof, fake urgency) and redirects to honest alternatives.

---

## Quick start (Google Colab)

The free **T4 GPU** is enough for a 3B model in 4-bit.

1. Open [Google Colab](https://colab.research.google.com), choose **File → Upload notebook**, and select `notebooks/finetune_business_strategist.ipynb`.
2. **Runtime → Change runtime type → T4 GPU.**
3. Run the cells in order. In the upload cell, select `data/business_strategist_train.jsonl` and `data/business_strategist_eval.jsonl`.
4. Check the token-length output in step 5. If many examples exceed `MAX_SEQ_LEN`, raise it to 3072 or 4096 and set `BATCH = 1`.
5. Train (step 7) and watch the eval loss. Stop if it starts rising (overfitting).
6. Test the model (step 9), save the LoRA adapter (step 8), and optionally export to GGUF or push to the Hugging Face Hub (step 10).

Colab sessions end after a few hours. Save and download the adapter (steps 8 and 11) right after training.

---

## Run locally

Requirements: Linux or WSL2, an NVIDIA GPU with at least 12 GB VRAM (24 GB is comfortable), CUDA drivers, Python 3.10+.

```bash
git clone https://github.com/<your-username>/business-strategist-llm.git
cd business-strategist-llm

python -m venv .venv && source .venv/bin/activate
pip install unsloth
pip install --upgrade trl datasets
```

Edit the paths at the top of `scripts/finetune_unsloth.py` (`TRAIN_FILE`, `EVAL_FILE`, `OUTPUT_DIR`, `LORA_DIR`), remove the Colab-only comment markers if needed, then run it cell by cell or as a script.

> Unsloth and TRL APIs change often. If you see an argument error (for example `tokenizer` vs `processing_class`), check the version-specific docs and adjust.

---

## Training details

| Setting | Default |
|---|---|
| Base model | `unsloth/Qwen2.5-3B-Instruct` (alternative: `unsloth/Llama-3.2-3B-Instruct`) |
| Method | QLoRA (4-bit base, LoRA adapters) |
| LoRA rank / alpha | 16 / 32 on q, k, v, o, gate, up, down projections |
| Max sequence length | 2048 (Bangla needs many tokens; check the length stats) |
| Effective batch size | 16 (2 × 8 gradient accumulation) |
| Learning rate | 2e-4, cosine schedule, 5% warmup |
| Epochs | 2 |
| Optimizer | AdamW 8-bit |
| Loss | **Assistant tokens only** (`train_on_responses_only`) |
| Eval | Every 50 steps on the held-out set |

Switching the base model requires changing the chat template (`get_chat_template`) and the `instruction_part` / `response_part` markers to match that model's format.

Tokenizer note: Qwen's tokenizer is not very efficient for Bangla. If Bangla output quality is weak, try a model with stronger multilingual coverage (for example a Gemma-3 4B variant) and adjust the template and markers.

---

## Reproduce or customize the dataset

The generator is deterministic (fixed random seed) and has no external dependencies.

```bash
cd scripts
python generate_dataset.py
```

It rewrites the three files in `data/` and prints counts by language and topic. To extend it:

- **Add a numeric topic:** write a `g_<name>(lang)` function that samples inputs, computes outputs in Python, and returns `(user_prompt, assistant_answer, topic)`. Register it in `RANDOM_GENS`.
- **Add a qualitative topic:** add an entry to the `BIAS`, `ETH`, `BD`, or `MECE` dictionaries (they hold English and Bangla text side by side).
- **Add industries:** extend the `IND` list.

### Recommended next step: mix in free-form data

Template data teaches structure and math well, but its wording is repetitive. For better natural variety, use a stronger LLM to write additional free-form examples from the hand-written `data/seed_examples.jsonl` and from realistic founder questions, then:

1. Verify any arithmetic with code.
2. Have a native Bangla speaker review a sample (at least 10 to 20 percent).
3. Deduplicate against the existing set.
4. Mix them into the training file, ideally at a ratio that keeps the template data below about 60 percent.

---

## Evaluating the model

Do not trust the training loss alone. After training:

1. **Held-out loss:** the `eval` file is a quick signal for overfitting.
2. **Out-of-distribution prompts:** write 20 new business questions (Bangla, English, Banglish) that are not templated, and read the answers.
3. **Checklist per answer:**
   - Does it show reasoning steps before the recommendation?
   - Is the arithmetic correct? Recompute it yourself.
   - Does it state assumptions and risks?
   - Is the Bangla natural, not machine-translated?
   - Does it refuse deceptive requests (fake reviews, fake urgency) and offer honest alternatives?
4. **Regression check:** ask a few general questions to make sure the base model's general ability did not collapse.

---

## Limitations

- **Template-based data.** Wording repeats across examples. The model may sound formulaic on topics outside the dataset.
- **Assumptions are stated, not measured.** Some scenarios (for example "advance payment reduces returns by 40%") rest on illustrative assumptions, not real-world measurements.
- **Limited depth outside the covered topics.** The dataset does not cover areas such as taxation, detailed legal compliance, or industry-specific regulation.
- **Small base model.** A 3B model can still make arithmetic or logic mistakes, especially with long multi-step problems. Verify important numbers.
- **Bangla quality depends on the base model.** Review outputs with a native speaker before relying on them.
- **Not independently benchmarked.** There is no formal benchmark result yet.

---

## Roadmap

- [ ] Mix in free-form, LLM-written and human-reviewed examples
- [ ] Add multi-turn conversations (follow-up questions, changing constraints)
- [ ] Add more Bangladesh-specific scenarios (B2B supply chains, wholesale, mobile financial services)
- [ ] Build a small human-reviewed Bangla/English evaluation set
- [ ] Compare base models (Qwen, Llama, Gemma) on Bangla quality
- [ ] Publish trained adapters and GGUF files on the Hugging Face Hub

Contributions are welcome. Open an issue to discuss new topics, or submit a pull request with new generators or reviewed examples.

---

## Responsible use

- This project is for education and decision support. **It is not financial, legal, or tax advice.** Verify important decisions with qualified professionals.
- The dataset deliberately teaches the model to **decline deceptive marketing** (fake testimonials, fake scarcity, bought reviews) and to suggest truthful alternatives. Please keep this behavior if you build on the data.
- Do not use the model to generate fabricated social proof, manipulate vulnerable people, or mislead customers.

---

## License

Choose a license before publishing (for example MIT for code and CC BY 4.0 for the data) and add a `LICENSE` file. Also check the license of the base model you fine-tune (Qwen, Llama, and Gemma each have their own terms) since it applies to the resulting weights.
