"""
Offline evaluation of the recommender using leave-k-out validation.

For each user with >= 4 interactions, we hide 30% of their positive
interactions (invested / sip_active items), retrain on the rest, and
check whether the hidden items appear in the model's top-N recommendations.

Reports Precision@K, Recall@K, and a risk-suitability violation rate
(how often we'd recommend something clearly outside the user's stated
risk tolerance) for content-only, collaborative-only, and hybrid models.
"""
import json
import os
import random
import numpy as np

from recommenders.content_based import ContentRecommender
from recommenders.collaborative import CollaborativeRecommender
from recommenders.hybrid import HybridRecommender, RISK_BUCKETS

random.seed(7)
np.random.seed(7)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed.json")
with open(DATA_PATH) as f:
    DB = json.load(f)

FUNDS = {f["fund_id"]: f for f in DB["funds"]}
STOCKS = {s["stock_id"]: s for s in DB["stocks"]}
ITEM_LOOKUP = {**FUNDS, **STOCKS}
ITEM_IDS = list(ITEM_LOOKUP.keys())
USERS = {u["user_id"]: u for u in DB["users"]}


def positive_actions(interactions):
    return [it for it in interactions if it["action"] in ("invested", "sip_active")]


def train_test_split(interactions, holdout_frac=0.3):
    by_user = {}
    for it in interactions:
        by_user.setdefault(it["user_id"], []).append(it)

    train, test = [], []
    for uid, items in by_user.items():
        positives = positive_actions(items)
        negatives_or_watch = [it for it in items if it not in positives]
        if len(positives) >= 3:
            random.shuffle(positives)
            n_hold = max(1, int(len(positives) * holdout_frac))
            held = positives[:n_hold]
            kept = positives[n_hold:]
            test.extend(held)
            train.extend(kept + negatives_or_watch)
        else:
            train.extend(items)
    return train, test


def precision_recall_at_k(recommended_ids, relevant_ids, k):
    top_k = recommended_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    precision = hits / k if k else 0
    recall = hits / len(relevant_ids) if relevant_ids else 0
    return precision, recall


def risk_violation(user, item, tolerance_slack=1):
    user_num = RISK_BUCKETS.index(user["risk_bucket"]) + 1
    return item["risk_level"] > user_num + tolerance_slack


def main(K=10):
    train, test = train_test_split(DB["interactions"], holdout_frac=0.3)

    content_model = ContentRecommender(DB["funds"], DB["stocks"])
    collab_model = CollaborativeRecommender(DB["users"], ITEM_IDS, train)
    hybrid_model = HybridRecommender(content_model, collab_model, ITEM_LOOKUP)

    test_by_user = {}
    for it in test:
        test_by_user.setdefault(it["user_id"], []).append(it["item_id"])

    train_hist_by_user = {}
    for it in train:
        train_hist_by_user.setdefault(it["user_id"], []).append(it["item_id"])

    metrics = {
        "content_only": {"p": [], "r": [], "viol": []},
        "collab_only": {"p": [], "r": [], "viol": []},
        "hybrid": {"p": [], "r": [], "viol": []},
    }

    for uid, relevant in test_by_user.items():
        if uid not in USERS:
            continue
        user = USERS[uid]
        hist = train_hist_by_user.get(uid, [])
        exclude = set(hist)

        c_recs = [iid for iid, _ in content_model.recommend(user, hist, top_n=K, exclude_ids=exclude)]
        cf_recs = [iid for iid, _ in collab_model.recommend(uid, top_n=K, exclude_ids=exclude)]
        h_recs_full = hybrid_model.recommend(user, hist, top_n=K)
        h_recs = [r["item_id"] for r in h_recs_full]

        for name, recs in [("content_only", c_recs), ("collab_only", cf_recs), ("hybrid", h_recs)]:
            p, r = precision_recall_at_k(recs, relevant, K)
            metrics[name]["p"].append(p)
            metrics[name]["r"].append(r)
            viol_count = sum(risk_violation(user, ITEM_LOOKUP[iid]) for iid in recs if iid in ITEM_LOOKUP)
            metrics[name]["viol"].append(viol_count / max(len(recs), 1))

    print(f"\nEvaluation over {len(test_by_user)} users, K={K}\n" + "-" * 60)
    print(f"{'Model':<15}{'Precision@K':<15}{'Recall@K':<15}{'RiskViolation%':<15}")
    for name, vals in metrics.items():
        p = np.mean(vals["p"]) if vals["p"] else 0
        r = np.mean(vals["r"]) if vals["r"] else 0
        v = np.mean(vals["viol"]) * 100 if vals["viol"] else 0
        print(f"{name:<15}{p:<15.3f}{r:<15.3f}{v:<15.1f}")
    print("-" * 60)
    print("RiskViolation% = share of recommended items whose risk level is")
    print("more than 1 notch above the user's stated risk tolerance.\n")


if __name__ == "__main__":
    main()
