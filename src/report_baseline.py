from pathlib import Path

import pandas as pd

from src.bootstrap import bootstrap_ci_mean


METRICS = [
    "retrieved_expected@k",
    "top1_is_expected",
    "overclaim",
    "latency_ms",
]


def fmt(mean: float, lo: float, hi: float) -> str:
    return f"{mean:.4f}  (IC95%: {lo:.4f} – {hi:.4f})"


def main() -> None:
    results_path = Path("runs/run_A/results.csv")
    out_path = Path("reports/baseline_A.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(results_path)

    lines = []
    lines.append("# Baseline A — Report\n")
    lines.append(f"Fonte: `{results_path.as_posix()}`\n")
    lines.append(f"N amostras: **{len(df)}**\n")

    # Tabela geral
    lines.append("## Métricas gerais (média + IC95% por bootstrap)\n")
    lines.append("| Métrica | Valor |\n|---|---|\n")

    for m in METRICS:
        mean, lo, hi = bootstrap_ci_mean(df[m])
        lines.append(f"| `{m}` | {fmt(mean, lo, hi)} |\n")

    # Breakdown por tópico
    lines.append("\n## Breakdown por tópico (média)\n")
    grp = df.groupby("topic")[METRICS].mean(numeric_only=True).sort_values("retrieved_expected@k", ascending=False)
    lines.append(grp.to_markdown())

    # Algumas observações automáticas simples
    lines.append("\n\n## Observações rápidas\n")
    lines.append(
        "- `retrieved_expected@k` mede se o doc esperado apareceu no top-k (proxy de recall/precision do retrieval).\n"
    )
    lines.append(
        "- `top1_is_expected` mede se o doc correto ficou em primeiro (proxy forte de qualidade do retrieval).\n"
    )
    lines.append(
        "- `overclaim` aqui marca quando o sistema respondeu mesmo sem recuperar o doc esperado (risco de alucinação/overconfidence).\n"
    )

    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"OK: wrote {out_path}")


if __name__ == "__main__":
    main()
