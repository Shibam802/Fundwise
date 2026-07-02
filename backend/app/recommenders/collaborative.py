"""
Collaborative Filtering
-------------------------
Builds a user x item implicit-feedback matrix (weighted by action type:
invested > sip_active > watchlisted, scaled further by amount), then
factorizes it with Truncated SVD to learn latent taste dimensions.
Recommends items with the highest predicted affinity that the user
hasn't already interacted with.

This is the "people like you also invested in..." engine.
"""
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD

ACTION_WEIGHTS = {"invested": 3.0, "sip_active": 2.0, "watchlisted": 1.0}


class CollaborativeRecommender:
    def __init__(self, users, items, interactions, n_factors=12):
        self.user_ids = [u["user_id"] for u in users]
        self.item_ids = [it for it in items]  # list of item ids (funds+stocks)

        self.user_index = {uid: i for i, uid in enumerate(self.user_ids)}
        self.item_index = {iid: i for i, iid in enumerate(self.item_ids)}

        self._build_matrix(interactions)
        self.n_factors = min(n_factors, min(self.matrix.shape) - 1)
        self._fit()

    # ------------------------------------------------------------------
    def _build_matrix(self, interactions):
        n_users = len(self.user_ids)
        n_items = len(self.item_ids)
        mat = np.zeros((n_users, n_items), dtype=np.float32)

        for it in interactions:
            u = self.user_index.get(it["user_id"])
            i = self.item_index.get(it["item_id"])
            if u is None or i is None:
                continue
            base = ACTION_WEIGHTS.get(it["action"], 1.0)
            amt_boost = np.log1p(it.get("amount") or 0) / 10.0
            rating_boost = (it.get("user_rating") or 3) / 3.0
            mat[u, i] += base * (1 + amt_boost) * rating_boost

        self.matrix = mat
        self.sparse_matrix = csr_matrix(mat)

    # ------------------------------------------------------------------
    def _fit(self):
        self.svd = TruncatedSVD(n_components=self.n_factors, random_state=42)
        self.user_factors = self.svd.fit_transform(self.sparse_matrix)
        self.item_factors = self.svd.components_.T
        # reconstructed affinity scores
        self.predicted = self.user_factors @ self.item_factors.T

    # ------------------------------------------------------------------
    def recommend(self, user_id, top_n=10, exclude_ids=None):
        if user_id not in self.user_index:
            return []  # true cold start, caller should fall back to content-based
        u = self.user_index[user_id]
        scores = self.predicted[u]

        exclude_ids = exclude_ids or set()
        already = set(np.nonzero(self.matrix[u])[0])

        results = []
        for i, score in enumerate(scores):
            item_id = self.item_ids[i]
            if i in already or item_id in exclude_ids:
                continue
            results.append((item_id, float(score)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_n]

    # ------------------------------------------------------------------
    def similar_users(self, user_id, top_n=5):
        """Used for the 'investors like you' explanation surface."""
        if user_id not in self.user_index:
            return []
        u = self.user_index[user_id]
        uvec = self.user_factors[u].reshape(1, -1)
        norms = np.linalg.norm(self.user_factors, axis=1) * np.linalg.norm(uvec)
        norms[norms == 0] = 1e-9
        sims = (self.user_factors @ uvec.T).flatten() / norms
        order = np.argsort(-sims)
        out = []
        for idx in order:
            if idx == u:
                continue
            out.append((self.user_ids[idx], float(sims[idx])))
            if len(out) >= top_n:
                break
        return out
