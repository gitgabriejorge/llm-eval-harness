import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from tqdm import tqdm

from src.rag import TfidfRetriever


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Lê JSONL (um JSON por linha) e retorna lista de dicts."""
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def make_baseline_answer(retrieved: List[Dict[str, Any]]) -> str:
    """
    Baseline A (sem LLM ainda):
    - "responde" devolvendo o texto do doc top-1.
    Medir métricas e fechar o pipeline hoje.
    """
    top = retrieved[0]
    return top["text"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb", default="data/kb.jsonl")
    parser.add_argument("--questions", default="data/questions.jsonl")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--out", default="runs/run_A")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    retriever = TfidfRetriever(args.kb)
    questions = load_jsonl(Path(args.questions))

    logs_path = out_dir / "logs.jsonl"
    results_path = out_dir / "results.csv"

    results: List[Dict[str, Any]] = []

    with logs_path.open("w", encoding="utf-8") as log_f:
        for q in tqdm(questions, desc="Evaluating"):
            t0 = time.perf_counter()

            retrieved = retriever.retrieve(q["question"], k=args.k)
            answer = make_baseline_answer(retrieved)

            latency_ms = (time.perf_counter() - t0) * 1000.0

            retrieved_ids = [r["doc_id"] for r in retrieved]
            expected = q["expected_doc_id"]

            # Métricas mínimas:
            retrieved_expected = int(expected in retrieved_ids)       # "precision@k" binária aqui
            top1_is_expected = int(retrieved_ids[0] == expected)      # acerto no top-1

            # Overclaim (heurística simples):
            # baseline sempre responde; então se NÃO recuperou o doc esperado, marcamos overclaim
            overclaim = int(retrieved_expected == 0)

            row = {
                "qid": q["qid"],
                "topic": q["topic"],
                "question": q["question"],
                "expected_doc_id": expected,
                "retrieved_expected@k": retrieved_expected,
                "top1_is_expected": top1_is_expected,
                "answer_length_chars": len(answer),
                "latency_ms": latency_ms,
                "overclaim": overclaim,
            }
            results.append(row)

            log_event = {
                "qid": q["qid"],
                "topic": q["topic"],
                "question": q["question"],
                "expected_doc_id": expected,
                "retrieved": retrieved,
                "answer": answer,
                "latency_ms": latency_ms,
                "metrics": {
                    "retrieved_expected@k": retrieved_expected,
                    "top1_is_expected": top1_is_expected,
                    "overclaim": overclaim,
                },
            }
            log_f.write(json.dumps(log_event, ensure_ascii=False) + "\n")

    df = pd.DataFrame(results)
    df.to_csv(results_path, index=False, encoding="utf-8")

    # Um resumo rápido pra você ver se está bom
    print(f"OK: wrote {results_path}")
    print(df[["retrieved_expected@k", "top1_is_expected", "overclaim", "latency_ms"]].mean(numeric_only=True))


if __name__ == "__main__":
    main()
