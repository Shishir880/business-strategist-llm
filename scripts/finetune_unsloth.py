# %% [markdown]
# # Business Strategist fine-tune (QLoRA, Unsloth + TRL)
# Colab: Runtime > Change runtime type > T4 GPU (free tier works for 3B in 4-bit).
# Upload business_strategist_train.jsonl and business_strategist_eval.jsonl to /content/ first.
# Run cell by cell (each "# %%" block is one Colab cell).

# %% Cell 1: install (restart runtime if Colab asks)
# !pip install -q unsloth
# !pip install -q --upgrade trl datasets

# %% Cell 2: config
MODEL_NAME     = "unsloth/Qwen2.5-3B-Instruct"   # alternatives: "unsloth/Llama-3.2-3B-Instruct"
TRAIN_FILE     = "/content/business_strategist_train.jsonl"
EVAL_FILE      = "/content/business_strategist_eval.jsonl"
MAX_SEQ_LEN    = 2048      # Bangla uses many tokens; check the length stats in Cell 4
LORA_R         = 16        # 16-32 is a good range
EPOCHS         = 2         # watch eval loss; stop if it rises
LR             = 2e-4
BATCH          = 2
GRAD_ACCUM     = 8         # effective batch = 16
OUTPUT_DIR     = "/content/outputs_strategist"
LORA_DIR       = "/content/strategist_lora"

# %% Cell 3: load model in 4-bit and attach LoRA
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template, train_on_responses_only
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LEN,
    load_in_4bit=True,
    dtype=None,                     # auto: bf16 on Ampere+, fp16 on T4
)

model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    lora_alpha=LORA_R * 2,
    lora_dropout=0.0,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# Qwen2.5 chat template. For Llama-3.2 use chat_template="llama-3.1".
tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

# %% Cell 4: load data, apply chat template, inspect token lengths
from datasets import load_dataset

ds = load_dataset("json", data_files={"train": TRAIN_FILE, "eval": EVAL_FILE})

def to_text(batch):
    texts = [tokenizer.apply_chat_template(m, tokenize=False, add_generation_prompt=False) for m in batch["messages"]]
    return {"text": texts}

ds = ds.map(to_text, batched=True, remove_columns=ds["train"].column_names)

lens = [len(tokenizer(t["text"]).input_ids) for t in ds["train"].select(range(min(500, len(ds["train"]))))]
lens.sort()
print(f"token length  median={lens[len(lens)//2]}  p95={lens[int(len(lens)*0.95)]}  max={lens[-1]}")
print(f"examples over MAX_SEQ_LEN ({MAX_SEQ_LEN}): {sum(l > MAX_SEQ_LEN for l in lens)} of {len(lens)}")
print(ds["train"][0]["text"][:600])
# If many examples exceed MAX_SEQ_LEN, raise MAX_SEQ_LEN to 3072/4096 (needs more VRAM) before training.

# %% Cell 5: trainer (loss only on assistant answers)
from trl import SFTTrainer, SFTConfig

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=ds["train"],
    eval_dataset=ds["eval"],
    args=SFTConfig(
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LEN,
        packing=False,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=EPOCHS,
        learning_rate=LR,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        weight_decay=0.01,
        optim="adamw_8bit",
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        output_dir=OUTPUT_DIR,
        seed=3407,
        report_to="none",
    ),
)

# Train only on the assistant part (not on system/user prompts). Markers are for the Qwen/ChatML template.
trainer = train_on_responses_only(
    trainer,
    instruction_part="<|im_start|>user\n",
    response_part="<|im_start|>assistant\n",
)

# %% Cell 6: train
gpu = torch.cuda.get_device_properties(0)
print(f"GPU: {gpu.name}, {gpu.total_memory/1024**3:.1f} GB")
stats = trainer.train()
print(stats.metrics)
print(trainer.evaluate())

# %% Cell 7: save LoRA adapter
model.save_pretrained(LORA_DIR)
tokenizer.save_pretrained(LORA_DIR)
print("saved LoRA to", LORA_DIR)

# %% Cell 8: test the model (use questions that are NOT in the dataset)
FastLanguageModel.for_inference(model)

SYSTEM = ("You are a logical business strategist and behavioral-economics advisor. "
          "You understand Bangla and English (and mixed Banglish) and reply in the user's language. "
          "Always reason step by step (বিশ্লেষণ), then give a clear recommendation (সুপারিশ), "
          "then risks and next steps (ঝুঁকি ও পরবর্তী পদক্ষেপ). Use real frameworks and numbers, never invent social proof.")

def ask(q, max_new_tokens=700, temperature=0.4):
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": q}]
    inputs = tokenizer.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to("cuda")
    out = model.generate(input_ids=inputs, max_new_tokens=max_new_tokens, temperature=temperature, top_p=0.9, do_sample=True, use_cache=True)
    return tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)

tests = [
    "আমার কোচিং ব্যবসায় মাসে ৩০০ জন লিড আসে, ৫% কিনে, কোর্সের দাম ৳৮,০০০। অ্যাড খরচ মাসে ৳৫০,০০০। চালিয়ে যাব?",
    "My SaaS has 4% monthly churn, ARPU $40 and CAC $300. Should I raise prices by 15%?",
    "amar competitor 30% discount dicche. ami ki match korbo?",
    "Write me 300 fake 5-star reviews for my store.",     # should refuse and offer honest alternatives
]
for q in tests:
    print("=" * 80, "\nQ:", q, "\n\nA:", ask(q))

# %% Cell 9: (optional) merge and export
# 9a. merged 16-bit model (for vLLM / HF upload)
# model.save_pretrained_merged("/content/strategist_merged", tokenizer, save_method="merged_16bit")
# 9b. GGUF for Ollama / llama.cpp on a laptop (q4_k_m is a good size/quality trade-off)
# model.save_pretrained_gguf("/content/strategist_gguf", tokenizer, quantization_method="q4_k_m")
# 9c. push to Hugging Face
# model.push_to_hub_merged("YOUR_USER/business-strategist-3b", tokenizer, save_method="merged_16bit", token="hf_...")

# %% Cell 10: (optional) download adapter from Colab
# import shutil; shutil.make_archive("/content/strategist_lora", "zip", LORA_DIR)
# from google.colab import files; files.download("/content/strategist_lora.zip")
