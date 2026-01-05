# LLM Conversational Eval Harness + Drift Lite (RAG)

A minimal evaluation suite for a conversational RAG agent using a synthetic knowledge base, with metrics + bootstrap confidence intervals and structured logs (foundation for drift/quality monitoring).

## What it does
- Loads a small knowledge base (`data/kb.jsonl`) and a question set with expected sources (`data/questions.jsonl`)
- Retrieves top-k documents (TF-IDF with character n-grams)
- Runs an evaluation pipeline that produces:
  - `runs/run_A/results.csv`
  - `runs/run_A/logs.jsonl`
- Generates a baseline report with bootstrap 95% confidence intervals:
  - `reports/baseline_A.md`

## Key metrics
- `retrieved_expected@k`: whether the expected doc appears in the top-k results (retrieval success proxy)
- `top1_is_expected`: whether the expected doc is ranked #1 (stronger retrieval quality proxy)
- `overclaim`: answered without retrieving the expected doc (risk proxy)
- `latency_ms`: retrieval/evaluation latency

## Reproduce locally

### 1) Create and activate a virtual environment
**Windows (PowerShell):**
python -m venv .venv
.\.venv\Scripts\Activate.ps1
**macOS/Linux:**
python3 -m venv .venv
source .venv/bin/activate
### 2) Install dependencies
pip install -r requirements.txt
### 3) Generate demo data and run the baseline
python -m src.make_demo_data
python -m src.run_eval --k 5 --out runs/run_A
python -m src.report_baseline

## Outputs
Baseline results: runs/run_A/results.csv
Detailed logs: runs/run_A/logs.jsonl
Report: reports/baseline_A.md
