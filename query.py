import sqlite3, re, math, unicodedata as ud
from scipy.stats import poisson, binom
from itertools import chain
from pyevidence import *
import query_tests
from nltk.stem import SnowballStemmer


stem = SnowballStemmer("english").stem
opts = ["GEO", "POI", "CAT", "FOOD", "PROX"]
conn = sqlite3.connect('data/reference.db')
cur  = conn.cursor()


def normalise(q):
    assert isinstance(q, str)
    q = ud.normalize('NFD', q.lower().strip())
    q = re.sub("['`]+", "", q)
    q = re.sub("[^a-z0-9 \\-]+", " ", q)
    q = [x for x in re.split(" +", q) if x]
    return(q)

def lemmatise(q):
    return [stem(x) for x in q]

def ngrams(q, n):
    f = lambda n: [tuple(range(i, i+n)) for i in range(len(q)-n+1)]
    return set(chain(*[f(x) for x in range(1, n+1)]))

def gazetteer(q, subs, lam=[8,3,1], Ps=[0.20, 0.4, 0.4], ngram=3):
    grams = ngrams(q, ngram)
    lemma = lemmatise(q)

    for g in grams:
        sgs  = '"' + " ".join(stem(q[i]) for i in g) + '"'
        sg   = '"' + " ".join(q[i] for i in g) + '"'
        sql = f"""
        select 'POI' as entity,  coalesce(max(n), 0) as n from poi where name match ? 
        union all
        select 'GEO' as entity,  coalesce(max(n), 0) as n from geo where name match ?
        union all
        select 'CAT' as entity,  coalesce(max(exp(n)), 0) as n from categories where name match ?
        union all
        select 'FOOD' as entity, coalesce(max(exp(n)), 0) as n from cuisine where name match ?
        union all
        select 'PROX' as entity, coalesce(max(n), 0) as n from proximity where name match ?
        """
        cnts      = dict(cur.execute(sql, (sgs,sgs,sgs,sgs,sg)).fetchall())
        poi, geo  = cnts["POI"], cnts["GEO"]
        cat, food = cnts["CAT"], cnts["FOOD"]
        prox      = cnts["PROX"]
        n         = poi + geo + cat + food + prox
        if n == 0: continue
        p0        = poisson.cdf(n, lam[len(g)-1]) * Ps[len(g)-1]
        mass      = ( Mass()
                      .add(subs.new(dict(zip(g, [["POI"]]*len(g)))),  (poi/n)  * p0)
                      .add(subs.new(dict(zip(g, [["GEO"]]*len(g)))),  (geo/n)  * p0)
                      .add(subs.new(dict(zip(g, [["CAT"]]*len(g)))),  (cat/n)  * p0)
                      .add(subs.new(dict(zip(g, [["FOOD"]]*len(g)))), (food/n) * p0)
                      .add(subs.new(dict(zip(g, [["PROX"]]*len(g)))), (prox/n) * p0)
                      .add(subs.new(), 1-p0) )
        yield mass

def label_query(q, subs, model, use_coarse=False):
    output, labels= [], []
    f = model.coarse if use_coarse else lambda q0: model.approx(q0, n=4000)
    for i,x in enumerate(q):
        ps = [f(subs.new({i: [o]}))[0] for o in opts]
        labels.append(opts[ps.index(max(ps))])
    labels.reverse(); q.reverse()
    lst = None
    for x,l in zip(q, labels):
        if l != lst:
            output.append(f"[{l}]")
            lst = l
        output.append(x)
    output.reverse()
    return " ".join(output)

def print_summary(evidence):
    print ("--------------------------------------------------------\n")
    print(f"len(evidence) = {len(evidence)}.")
    for i, e in enumerate(evidence):
        print("No.", i)
        for s,p in zip(e.mass, e.probs):
            print("\t", s.schema(), "->", round(p,4))
    print ("--------------------------------------------------------")

def priors(q, subs):
    for i,x in enumerate(q):
        is_num = bool(re.match("[a-z]*[0-9]+", x))
        mass = ( Mass()
                 .add(subs.new({i: ["GEO"] if is_num else ["POI"]}),
                      0.1 if is_num else 0.001)
                 .add(subs.new(), 0.9 if is_num else 0.999) )
        yield mass

def tag_query(q, ngram=3, verbose=True, use_coarse=False):
    q     = normalise(q)
    n     = len(q)
    subs  = Subsets(slots=n, opts=[opts] * n)
    model = Inference(method="dubois-prade")
    mass  = list(chain(priors(q, subs), gazetteer(q, subs)))

    if verbose: print_summary(mass)
    for m in mass: model.add_mass(m)
    return label_query(q, subs,  model, use_coarse=use_coarse)

def test_assert(q):
    q0  = re.sub(" \\[.+?\\]", "", q)
    q1  = tag_query(q0, verbose=False, use_coarse=False)
    q2  = tag_query(q0, verbose=False, use_coarse=True)
    msg = lambda x: f'Expected "{q}", got "{x}"'
    ok1 = q.lower() == q1.lower()
    ok2 = q.lower() == q2.lower()
    if ok1 and ok2:
        print("[OK]", q)
        return
    if not ok1:
        print("\t[ERROR, approx]", msg(q1))
    if not ok2:
        print("\t[ERROR, coarse]", msg(q2))
 
# TESTS
if __name__ == "__main__":
    for q in query_tests.queries:
        test_assert(q)
