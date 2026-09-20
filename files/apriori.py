from itertools import combinations

transactions = tx['Transaction'].tolist()          # 441 baskets
n_tx = len(transactions)
tx_sets = [set(t) for t in transactions]

def support_count(itemset):                        # baskets containing itemset
    return sum(1 for t in tx_sets if itemset.issubset(t))

def apriori(transactions, min_support, max_k=4):   # (Agrawal & Srikant, 1994)
    items = sorted(set(i for t in transactions for i in t))
    L = {1: [c for c in [(i,) for i in items]
             if support_count(set(c)) / n_tx >= min_support]}
    k = 2
    while L.get(k - 1) and k <= max_k:
        prev = L[k - 1]; cand = set()
        for i in range(len(prev)):                 # JOIN step
            for j in range(i + 1, len(prev)):
                if prev[i][:k-2] == prev[j][:k-2]:
                    cand.add(tuple(sorted(set(prev[i]) | set(prev[j]))))
        freq = []
        for c in cand:                             # PRUNE step (Apriori property)
            if all(tuple(sorted(s)) in set(prev) for s in combinations(c, k-1)):
                if support_count(set(c)) / n_tx >= min_support:
                    freq.append(c)
        L[k] = sorted(freq); k += 1
    return L

freq_itemsets = apriori(transactions, min_support=0.03, max_k=3)
sup_map = {frozenset(its): support_count(set(its)) / n_tx
           for k, v in freq_itemsets.items() for its in v}

rules = []
for k, v in freq_itemsets.items():                 # RULE generation (Han et al., 2011)
    if k < 2: continue
    for its in v:
        ab = frozenset(its); s_ab = sup_map[ab]
        for r in range(1, k):
            for a in combinations(its, r):
                A, B = frozenset(a), ab - frozenset(a)
                conf = s_ab / sup_map[A]
                if conf >= 0.50:
                    rules.append({'antecedent': ', '.join(sorted(A)),
                                  'consequent': ', '.join(sorted(B)),
                                  'support': round(s_ab, 4),
                                  'confidence': round(conf, 4),
                                  'lift': round(conf / sup_map[B], 4)})
rules = pd.DataFrame(rules).drop_duplicates(
    subset=['antecedent', 'consequent']).sort_values(
    ['lift', 'confidence'], ascending=False)       # sorted by chosen metric: LIFT