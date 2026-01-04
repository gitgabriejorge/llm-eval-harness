import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Doc:
    #Representa um documento da KB
    doc_id: str
    title: str
    category: str
    text: str


class TfidfRetriever:
    """
    Retriever simples:
    - lê a KB (jsonl)
    - cria matriz TF-IDF dos textos
    - dado uma pergunta, retorna top-k docs por similaridade coseno
    """

    def __init__(self, kb_path: str) -> None:
        self.docs: List[Doc] = self._load_kb(kb_path)

        # Vetorizador TF-IDF. Usamos unigramas e bigramas pra melhorar matching.
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=1,
            strip_accents="unicode",
        )

        # Matriz [n_docs x n_features]
        self.doc_matrix = self.vectorizer.fit_transform([d.text for d in self.docs])

    def _load_kb(self, kb_path: str) -> List[Doc]:
        docs: List[Doc] = []
        path = Path(kb_path)
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                docs.append(Doc(**row))
        return docs

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Vetoriza a pergunta no mesmo espaço TF-IDF
        q_vec = self.vectorizer.transform([query])

        # Similaridade coseno entre query e todos os docs
        sims = cosine_similarity(q_vec, self.doc_matrix)[0]

        # Índices dos top-k docs por score
        top_idx = sims.argsort()[::-1][:k]

        results: List[Dict[str, Any]] = []
        for idx in top_idx:
            d = self.docs[int(idx)]
            results.append(
                {
                    "doc_id": d.doc_id,
                    "title": d.title,
                    "category": d.category,
                    "score": float(sims[int(idx)]),
                    "text": d.text,
                }
            )
        return results
