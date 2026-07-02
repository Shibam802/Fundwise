"""
Content-Based Filtering
------------------------
Represents every fund/stock as a numeric feature vector (risk level,
category one-hot, normalized returns, expense ratio, etc.) and every
user as a preference vector derived from their risk profile. Recommends
items whose feature vector is closest (cosine similarity) to the user's
preference vector, optionally re-weighted by the categories the user has
actually interacted with before (their "taste").
"""
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


class ContentRecommender:
    def __init__(self, funds, stocks):
        self.funds = funds
        self.stocks = stocks
        self.items = funds + stocks  # unified catalogue
        self._build_feature_matrix()

    # ------------------------------------------------------------------
    def _build_feature_matrix(self):
        categories = sorted(set(
            [f["category"] for f in self.funds] + [s["sector"] for s in self.stocks]
        ))
        self.category_index = {c: i for i, c in enumerate(categories)}
        n_cat = len(categories)

        rows = []
        for item in self.items:
            is_fund = "fund_id" in item
            cat = item["category"] if is_fund else item["sector"]
            cat_vec = np.zeros(n_cat)
            cat_vec[self.category_index[cat]] = 1.0

            risk = item["risk_level"] / 5.0
            ret_1y = item.get("returns_1y", 0)
            expense_or_pe = item.get("expense_ratio", item.get("pe_ratio", 0))

            row = np.concatenate([cat_vec, [risk, ret_1y, expense_or_pe]])
            rows.append(row)

        raw = np.array(rows)
        # scale the numeric (non one-hot) tail columns to 0-1
        numeric_part = raw[:, n_cat:]
        scaler = MinMaxScaler()
        numeric_scaled = scaler.fit_transform(numeric_part)
        self.feature_matrix = np.hstack([raw[:, :n_cat], numeric_scaled])
        self.n_cat = n_cat
        self.scaler = scaler
        self.item_id_to_row = {
            (item["fund_id"] if "fund_id" in item else item["stock_id"]): i
            for i, item in enumerate(self.items)
        }

    # ------------------------------------------------------------------
    def user_vector(self, user, interacted_item_ids=None):
        """Builds a preference vector for a user: risk-appetite driven,
        nudged toward the categories they've actually engaged with."""
        risk_target = user["risk_score"]  # 0-1 already

        cat_weight = np.zeros(self.n_cat)
        if interacted_item_ids:
            for iid in interacted_item_ids:
                row_idx = self.item_id_to_row.get(iid)
                if row_idx is not None:
                    cat_weight += self.feature_matrix[row_idx, :self.n_cat]
            if cat_weight.sum() > 0:
                cat_weight = cat_weight / cat_weight.sum()

        if cat_weight.sum() == 0:
            # cold-start: uniform light preference across categories
            cat_weight = np.ones(self.n_cat) / self.n_cat

        # numeric tail: prefer risk near user's risk score, don't
        # have a strong opinion on returns/expense (let those be
        # discovered), so we center them at 0.5
        numeric_tail = np.array([risk_target, 0.6, 0.4])
        return np.concatenate([cat_weight, numeric_tail]).reshape(1, -1)

    # ------------------------------------------------------------------
    def recommend(self, user, interacted_item_ids=None, top_n=10, exclude_ids=None):
        uvec = self.user_vector(user, interacted_item_ids)
        sims = cosine_similarity(uvec, self.feature_matrix)[0]

        exclude_ids = exclude_ids or set()
        scored = []
        for i, item in enumerate(self.items):
            item_id = item["fund_id"] if "fund_id" in item else item["stock_id"]
            if item_id in exclude_ids:
                continue
            scored.append((item_id, float(sims[i])))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]
