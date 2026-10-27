"""Small, inspectable sparse TF-IDF vectors + BM25; no model download."""
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = set('a an the to of for is it in on at and or my i me you your do does how what can should with from after have has are be this that as if not'.split())

def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r'[a-z0-9]+', text.lower()) if w not in STOP]

class KnowledgeBase:
    def __init__(self, root: Path = ROOT):
        self.articles = json.loads((root / 'data/articles.json').read_text())
        self.by_id = {a['id']: a for a in self.articles}
        self.glossary = json.loads((root / 'data/glossary.json').read_text())
        self.docs = [tokens(a['title'] + ' ' + a['text']) for a in self.articles]
        self.counts = [Counter(d) for d in self.docs]
        self.n = len(self.docs)
        self.avg_length = sum(map(len, self.docs)) / self.n
        df = Counter(t for d in self.docs for t in set(d))
        self.idf = {t: math.log(1 + (self.n - n + .5) / (n + .5)) for t, n in df.items()}
        # These are sparse bag-of-words embeddings, not neural semantic embeddings.
        self.vectors = [self.vector(d) for d in self.docs]

    def vector(self, words: list[str]) -> dict[str, float]:
        c = Counter(words)
        v = {t: (1 + math.log(n)) * self.idf.get(t, 0) for t, n in c.items()}
        norm = math.sqrt(sum(x*x for x in v.values())) or 1
        return {t: x/norm for t, x in v.items() if x}

    def expand(self, query: str) -> list[str]:
        result = tokens(query)
        normalized = ' '.join(re.findall(r'[a-z0-9]+', query.lower()))
        for phrase, terms in self.glossary.items():
            phrase = ' '.join(re.findall(r'[a-z0-9]+', phrase.lower()))
            if re.search(r'\b' + re.escape(phrase) + r'\b', normalized):
                result.extend(tokens(' '.join(terms)))
        return result

    def search(self, query: str, method: str = 'hybrid', k: int = 3, min_score: float = 0.24) -> list[dict]:
        if method not in {'bm25', 'hybrid'}:
            raise ValueError('Unknown retrieval method')
        words = self.expand(query) if method == 'hybrid' else tokens(query)
        qv = self.vector(words)
        results = []
        for a, d, counts, dv in zip(self.articles, self.docs, self.counts, self.vectors):
            bm25 = 0.0
            for term in set(words):
                f = counts[term]
                bm25 += self.idf.get(term, 0) * f * 2.5 / (f + 1.5 * (.25 + .75 * len(d)/self.avg_length))
            cosine = sum(value * dv.get(t, 0) for t, value in qv.items())
            score = .65*cosine + .35*bm25/(bm25+5) if method == 'hybrid' else bm25
            if score > min_score:
                results.append({**a, 'score': round(score, 6)})
        return sorted(results, key=lambda a: (-a['score'], a['id']))[:k]
