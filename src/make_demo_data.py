import json
import random
from pathlib import Path

#arquivos em /data:
#kb.jsonl: documentos (politicas/FAQ)
#questions.jsonl: perguntas com doc esperado (ground truth)
OUT_DIR = Path("data")
KB_PATH = OUT_DIR / "kb.jsonl"
Q_PATH = OUT_DIR / "questions.jsonl"

random.seed(42)

def write_jsonl(path: Path, rows: list[dict]) -> None:
    #lista de dicts em JSONL (um JSON/lin)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    #base pequena de politicas/FAQ tipicas de e-commerce
    base_docs = [
        {
            "doc_id": "RETURNS_001",
            "title": "Troca e devolução - prazo",
            "category": "returns",
            "text": "Você pode solicitar devolução em até 7 dias após o recebimento. Trocas podem ser solicitadas em até 30 dias, desde que o produto esteja sem uso e com embalagem original."
        },
        {
            "doc_id": "RETURNS_002",
            "title": "Troca e devolução - produto aberto",
            "category": "returns",
            "text": "Produtos abertos só podem ser devolvidos se apresentarem defeito. Em caso de arrependimento, o produto deve estar sem uso e com lacres intactos."
        },
        {
            "doc_id": "SHIPPING_001",
            "title": "Frete - prazos",
            "category": "shipping",
            "text": "O prazo de entrega varia por CEP e modalidade. Após o envio, você recebe um código de rastreio. O prazo começa a contar após a confirmação do pagamento."
        },
        {
            "doc_id": "SHIPPING_002",
            "title": "Frete - atraso",
            "category": "shipping",
            "text": "Se o pedido atrasar, verifique o rastreio. Caso o status fique parado por mais de 3 dias úteis, entre em contato para abrir uma solicitação com a transportadora."
        },
        {
            "doc_id": "PAYMENTS_001",
            "title": "Pagamentos - cartão",
            "category": "payments",
            "text": "Aceitamos cartão de crédito em até 12x. A aprovação pode levar até 24 horas. Se a compra for negada, verifique limite, dados do cartão e tente novamente."
        },
        {
            "doc_id": "PAYMENTS_002",
            "title": "Pagamentos - boleto e PIX",
            "category": "payments",
            "text": "Boletos podem levar até 2 dias úteis para compensar. Pagamentos via PIX são confirmados em minutos. O pedido só é enviado após a confirmação."
        },
        {
            "doc_id": "WARRANTY_001",
            "title": "Garantia - prazo",
            "category": "warranty",
            "text": "A garantia padrão é de 12 meses para defeitos de fabricação. Danos por mau uso não são cobertos. Para acionar, envie número do pedido e descrição do problema."
        },
        {
            "doc_id": "ACCOUNT_001",
            "title": "Conta - alteração de endereço",
            "category": "account",
            "text": "Após a confirmação do pagamento, o endereço não pode ser alterado pelo cliente. Se precisar corrigir, entre em contato rapidamente para tentarmos intervir antes do envio."
        },
        {
            "doc_id": "PRODUCT_001",
            "title": "Produto - especificações",
            "category": "product_info",
            "text": "As especificações técnicas estão na página do produto. Caso tenha dúvida, informe o SKU e a característica desejada (dimensão, voltagem, compatibilidade) para confirmar."
        },
    ]

    #expandido para ~36 docs para o retrieval ter mais “distrações” e ficar mais real.
    expanded_docs = []
    for base in base_docs:
        for j in range(4):  # 9 * 4 = 36 docs
            expanded_docs.append(
                {
                    "doc_id": f"{base['doc_id']}_V{j+1}",
                    "title": base["title"],
                    "category": base["category"],
                    "text": base["text"],
                }
            )

    write_jsonl(KB_PATH, expanded_docs)

    #cada pergunta aponta para um doc esperado (o V1 daquela categoria)
    templates = {
        "returns": [
            "Qual é o prazo para devolução?",
            "Posso trocar um produto depois de quantos dias?",
            "Posso devolver um produto aberto?",
            "Como funciona arrependimento de compra?"
        ],
        "shipping": [
            "Qual o prazo de entrega?",
            "Como rastrear meu pedido?",
            "O que faço se o pedido atrasar?",
            "Quando começa a contar o prazo de entrega?"
        ],
        "payments": [
            "Em quantas vezes posso parcelar no cartão?",
            "Quanto tempo demora para aprovar o cartão?",
            "Boleto demora quanto para compensar?",
            "PIX confirma em quanto tempo?"
        ],
        "warranty": [
            "Qual é o prazo de garantia?",
            "Garantia cobre mau uso?",
            "Como acionar a garantia?",
            "O que preciso enviar para suporte?"
        ],
        "account": [
            "Posso mudar o endereço depois de pagar?",
            "Como corrigir o endereço do pedido?",
            "Consigo alterar dados após compra?",
            "O que faço se errei o endereço?"
        ],
        "product_info": [
            "Onde vejo as especificações do produto?",
            "Como confirmar compatibilidade?",
            "Preciso da dimensão exata do produto, onde encontro?",
            "Como tirar dúvida de voltagem?"
        ],
    }

    #mapeia categoria -> doc esperado (primeiro V1 daquela categoria)
    expected_by_category = {}
    for d in expanded_docs:
        if d["doc_id"].endswith("_V1") and d["category"] not in expected_by_category:
            expected_by_category[d["category"]] = d["doc_id"]

    questions = []
    qid = 0
    for category, qs in templates.items():
        expected = expected_by_category[category]
        for _ in range(16):  #16 por categoria -> ~96 perguntas
            qid += 1
            base_q = random.choice(qs)
            variant = random.choice(["", " Por favor.", " Pode me ajudar?", " Preciso disso hoje."])
            questions.append(
                {
                    "qid": f"Q{qid:04d}",
                    "question": base_q + variant,
                    "expected_doc_id": expected,
                    "topic": category,
                }
            )

    write_jsonl(Q_PATH, questions)

    print(f"OK: {len(expanded_docs)} docs -> {KB_PATH}")
    print(f"OK: {len(questions)} perguntas -> {Q_PATH}")

if __name__ == "__main__":
    main()
