"""
Hybrid Recommender
--------------------
Combines Content-Based and Collaborative Filtering scores into a single
ranked list, then applies a risk-profile guardrail so a Conservative
user is never shown a Small Cap / Sectoral fund at the top of their
feed even if the collaborative signal likes it (mirrors suitability
rules real fund platforms must apply).

final_score = alpha * content_score + (1-alpha) * collab_score
            then re-weighted by a risk-fit multiplier

alpha is higher for cold-start / new users (no history -> lean on
content-based) and lower for users with rich interaction history
(lean on collaborative signal).
"""
import numpy as np


RISK_TOLERANCE = {
    # how many risk_levels above the user's own bucket are still "fine"
    "Conservative": 0,
    "Moderate": 1,
    "Balanced": 2,
    "Growth": 3,
    "Aggressive": 4,
}
RISK_BUCKETS = ["Conservative", "Moderate", "Balanced", "Growth", "Aggressive"]


def risk_fit_multiplier(user_risk_bucket, item_risk_level):
    user_num = RISK_BUCKETS.index(user_risk_bucket) + 1  # 1..5
    tolerance = RISK_TOLERANCE[user_risk_bucket]
    diff = item_risk_level - user_num
    if diff <= 0:
        return 1.0          # at or below appetite: always fine
    if diff <= tolerance:
        return 0.85         # a bit above: mildly dampened
    return 0.35 ** diff      # sharply dampen items well beyond risk appetite


class HybridRecommender:
    def __init__(self, content_model, collab_model, item_lookup):
        self.content_model = content_model
        self.collab_model = collab_model
        self.item_lookup = item_lookup  # item_id -> full item dict

    def _alpha_for_user(self, n_interactions):
        # 0 interactions -> alpha=0.9 (mostly content-based)
        # 15+ interactions -> alpha=0.35 (mostly collaborative)
        alpha = 0.9 - min(n_interactions, 15) / 15 * 0.55
        return round(alpha, 2)

    def recommend(self, user, interacted_item_ids, top_n=10):
        exclude = set(interacted_item_ids)
        n_hist = len(interacted_item_ids)
        alpha = self._alpha_for_user(n_hist)

        content_scores = dict(self.content_model.recommend(
            user, interacted_item_ids, top_n=200, exclude_ids=exclude))
        collab_scores = dict(self.collab_model.recommend(
            user["user_id"], top_n=200, exclude_ids=exclude))

        all_candidate_ids = set(content_scores) | set(collab_scores)

        # normalize each score dict to 0-1 so they combine fairly
        def normalize(d):
            if not d:
                return {}
            vals = np.array(list(d.values()))
            lo, hi = vals.min(), vals.max()
            if hi - lo < 1e-9:
                return {k: 0.5 for k in d}
            return {k: (v - lo) / (hi - lo) for k, v in d.items()}

        content_norm = normalize(content_scores)
        collab_norm = normalize(collab_scores)

        results = []
        for item_id in all_candidate_ids:
            c = content_norm.get(item_id, 0.0)
            cf = collab_norm.get(item_id, 0.0)
            base_score = alpha * c + (1 - alpha) * cf

            item = self.item_lookup.get(item_id)
            if item is None:
                continue
            mult = risk_fit_multiplier(user["risk_bucket"], item["risk_level"])
            final_score = base_score * mult

            results.append({
                "item_id": item_id,
                "score": round(float(final_score), 4),
                "content_score": round(float(c), 4),
                "collab_score": round(float(cf), 4),
                "risk_fit_multiplier": round(mult, 3),
                "in_content_topN": item_id in content_scores,
                "in_collab_topN": item_id in collab_scores,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[:top_n]

        for r in top:
            item = self.item_lookup[r["item_id"]]
            r["item"] = item
            r["explanation"] = self._explain(user, item, r, alpha)
            r["alpha_used"] = alpha
        return top

    # ------------------------------------------------------------------
    def _explain(self, user, item, r, alpha):
        reasons = []
        cat = item.get("category") or item.get("sector")
        if r["in_content_topN"] and r["content_score"] > 0.55:
            reasons.append(f"matches your {user['risk_bucket']} risk profile "
                            f"and {cat} preference")
        if r["in_collab_topN"] and r["collab_score"] > 0.55:
            reasons.append("popular among investors with similar behavior to you")
        if item["risk_level"] <= RISK_BUCKETS.index(user["risk_bucket"]) + 1:
            reasons.append("within your risk tolerance")
        if not reasons:
            reasons.append("a solid fit based on your overall profile")
        return "; ".join(reasons).capitalize()
