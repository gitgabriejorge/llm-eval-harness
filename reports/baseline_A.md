# Baseline A — Report
Fonte: `runs/run_A/results.csv`
N amostras: **96**
## Métricas gerais (média + IC95% por bootstrap)
| Métrica | Valor |
|---|---|
| `retrieved_expected@k` | 0.7604  (IC95%: 0.6771 – 0.8438) |
| `top1_is_expected` | 0.3021  (IC95%: 0.2083 – 0.3958) |
| `overclaim` | 0.2396  (IC95%: 0.1562 – 0.3229) |
| `latency_ms` | 1.3619  (IC95%: 1.2476 – 1.5023) |

## Breakdown por tópico (média)
| topic        |   retrieved_expected@k |   top1_is_expected |   overclaim |   latency_ms |
|:-------------|-----------------------:|-------------------:|------------:|-------------:|
| account      |                 1      |             1      |      0      |      1.12302 |
| product_info |                 1      |             0      |      0      |      1.06075 |
| warranty     |                 0.9375 |             0      |      0.0625 |      1.07347 |
| returns      |                 0.5625 |             0      |      0.4375 |      1.95763 |
| shipping     |                 0.5625 |             0.3125 |      0.4375 |      1.48926 |
| payments     |                 0.5    |             0.5    |      0.5    |      1.46713 |

## Observações rápidas
- `retrieved_expected@k` mede se o doc esperado apareceu no top-k (proxy de recall/precision do retrieval).
- `top1_is_expected` mede se o doc correto ficou em primeiro (proxy forte de qualidade do retrieval).
- `overclaim` aqui marca quando o sistema respondeu mesmo sem recuperar o doc esperado (risco de alucinação/overconfidence).
