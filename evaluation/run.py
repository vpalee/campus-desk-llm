"""Offline retrieval evaluation. No LLM, API key, or network required."""
import argparse
import hashlib
import json
from pathlib import Path
from app.retrieval import KnowledgeBase, ROOT


def evaluate(kb, cases, method, threshold):
    answerable = hits = unknown = correctly_empty = 0
    reciprocal = 0.0
    rows = []
    for case in cases:
        ids = [a['id'] for a in kb.search(case['question'], method=method, min_score=threshold)]
        relevant = set(case['relevant_ids'])
        ranks = [i+1 for i, ident in enumerate(ids) if ident in relevant]
        if relevant:
            answerable += 1
            hits += bool(ranks)
            reciprocal += 1/min(ranks) if ranks else 0
        else:
            unknown += 1
            correctly_empty += not ids
        rows.append({**case, 'retrieved_ids': ids, 'reciprocal_rank_at_3': 1/min(ranks) if ranks else 0})
    return {'answerable': answerable, 'out_of_scope': unknown, 'recall_at_3': hits/answerable,
            'mrr_at_3': reciprocal/answerable, 'out_of_scope_abstention_rate': correctly_empty/unknown,
            'decision_accuracy': (hits+correctly_empty)/len(cases), 'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'evaluation/results.json')
    args = parser.parse_args()
    kb = KnowledgeBase()
    load = lambda name: [json.loads(line) for line in (ROOT/f'evaluation/{name}.jsonl').read_text().splitlines()]
    dev = load('dev')
    candidates = []
    for threshold in [.12, .18, .24, .30, .36]:
        m = evaluate(kb, dev, 'hybrid', threshold)
        candidates.append({'min_score':threshold, 'decision_accuracy':m['decision_accuracy'], 'mrr_at_3':m['mrr_at_3']})
    # Prefer the larger threshold on a tie to avoid returning weak matches.
    best = max(candidates, key=lambda m:(m['decision_accuracy'], m['mrr_at_3'], m['min_score']))
    files = ['data/articles.json','data/glossary.json','evaluation/dev.jsonl','evaluation/test.jsonl','app/retrieval.py']
    results = {'schema_version':1, 'kind':'offline retrieval only; not model answer accuracy',
       'k':3, 'threshold_selection':'development cases only; decision accuracy then MRR then larger threshold',
       'dev_candidates':candidates, 'selected_min_score':best['min_score'],
       'sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
       'systems':{name:evaluate(kb,load('test'),method,threshold) for name,method,threshold in [
         ('baseline_bm25','bm25',0),('naive_hybrid','hybrid',0),('selected_hybrid','hybrid',best['min_score'])]}}
    args.output.write_text(json.dumps(results,indent=2)+'\n')
    print('Selected min_score:',best['min_score'])
    for name, metrics in results['systems'].items():
        print(name, {k:round(v,4) if isinstance(v,float) else v for k,v in metrics.items() if k!='cases'})

if __name__ == '__main__':
    main()
