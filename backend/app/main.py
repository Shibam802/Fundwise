import json
import os
from collections import defaultdict
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recommenders.content_based import ContentRecommender
from recommenders.collaborative import CollaborativeRecommender
from recommenders.hybrid import HybridRecommender, RISK_BUCKETS

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed.json")

app = FastAPI(title="FundWise Recommendation API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory "database" loaded from the synthetic seed file.
# Swappable later for Postgres/SQLite without changing the API surface.
# ---------------------------------------------------------------------------
with open(DATA_PATH) as f:
    DB = json.load(f)

FUNDS = {f["fund_id"]: f for f in DB["funds"]}
STOCKS = {s["stock_id"]: s for s in DB["stocks"]}
USERS = {u["user_id"]: u for u in DB["users"]}
ITEM_LOOKUP = {**FUNDS, **STOCKS}
ITEM_IDS = list(ITEM_LOOKUP.keys())
INTERACTIONS = DB["interactions"]

USER_INTERACTIONS = defaultdict(list)
for it in INTERACTIONS:
    USER_INTERACTIONS[it["user_id"]].append(it)

# ---------------------------------------------------------------------------
# Build models once at startup
# ---------------------------------------------------------------------------
content_model = ContentRecommender(DB["funds"], DB["stocks"])
collab_model = CollaborativeRecommender(DB["users"], ITEM_IDS, INTERACTIONS)
hybrid_model = HybridRecommender(content_model, collab_model, ITEM_LOOKUP)


def user_item_ids(user_id):
    return [it["item_id"] for it in USER_INTERACTIONS.get(user_id, [])]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class RiskQuizAnswers(BaseModel):
    age: int
    monthly_income: int
    investment_horizon: str      # "< 1 year" | "1-3 years" | "3-5 years" | "5+ years"
    loss_tolerance: int          # 1-5 (1 = can't tolerate any loss, 5 = fully comfortable)
    investment_goal: str         # "capital protection" | "steady growth" | "wealth creation" | "aggressive growth"
    existing_investor: bool


class InteractionIn(BaseModel):
    user_id: str
    item_id: str
    action: str                  # invested | sip_active | watchlisted
    amount: Optional[int] = 0


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "FundWise Recommendation API"}


@app.get("/api/users")
def list_users():
    return list(USERS.values())


@app.get("/api/users/{user_id}")
def get_user(user_id: str):
    if user_id not in USERS:
        raise HTTPException(404, "User not found")
    return USERS[user_id]


@app.get("/api/funds")
def list_funds(category: Optional[str] = None, max_risk: Optional[int] = None):
    items = list(FUNDS.values())
    if category:
        items = [f for f in items if f["category"] == category]
    if max_risk:
        items = [f for f in items if f["risk_level"] <= max_risk]
    return items


@app.get("/api/stocks")
def list_stocks(sector: Optional[str] = None, max_risk: Optional[int] = None):
    items = list(STOCKS.values())
    if sector:
        items = [s for s in items if s["sector"] == sector]
    if max_risk:
        items = [s for s in items if s["risk_level"] <= max_risk]
    return items


@app.get("/api/items/{item_id}")
def get_item(item_id: str):
    if item_id not in ITEM_LOOKUP:
        raise HTTPException(404, "Item not found")
    return ITEM_LOOKUP[item_id]


@app.get("/api/recommendations/{user_id}")
def recommend(user_id: str, top_n: int = 10):
    if user_id not in USERS:
        raise HTTPException(404, "User not found")
    user = USERS[user_id]
    history = user_item_ids(user_id)
    recs = hybrid_model.recommend(user, history, top_n=top_n)
    return {
        "user_id": user_id,
        "risk_bucket": user["risk_bucket"],
        "alpha_used": recs[0]["alpha_used"] if recs else None,
        "n_history_items": len(history),
        "recommendations": recs,
    }


@app.get("/api/similar-investors/{user_id}")
def similar_investors(user_id: str, top_n: int = 5):
    if user_id not in USERS:
        raise HTTPException(404, "User not found")
    sims = collab_model.similar_users(user_id, top_n=top_n)
    return [{"user": USERS[uid], "similarity": round(score, 3)} for uid, score in sims]


@app.get("/api/portfolio/{user_id}")
def portfolio(user_id: str):
    if user_id not in USERS:
        raise HTTPException(404, "User not found")
    holdings = [it for it in USER_INTERACTIONS.get(user_id, [])
                if it["action"] in ("invested", "sip_active")]

    enriched = []
    total_invested = 0
    asset_alloc = defaultdict(int)
    for h in holdings:
        item = ITEM_LOOKUP.get(h["item_id"])
        if not item:
            continue
        amt = h["amount"] or 0
        total_invested += amt
        asset_class = item.get("asset_class") or item.get("sector", "Equity")
        asset_alloc[asset_class] += amt
        enriched.append({**h, "item": item})

    allocation_pct = {
        k: round(v / total_invested * 100, 1) if total_invested else 0
        for k, v in asset_alloc.items()
    }

    return {
        "user_id": user_id,
        "total_invested": total_invested,
        "holdings_count": len(enriched),
        "asset_allocation_pct": allocation_pct,
        "holdings": enriched,
    }


@app.post("/api/risk-profile")
def compute_risk_profile(answers: RiskQuizAnswers):
    """
    Converts quiz answers into a 0-1 risk_score and one of the 5
    risk buckets, using a transparent weighted-points model (the kind
    used by real fund platforms for SEBI-mandated risk profiling).
    """
    score = 0.0
    # Age: younger => higher capacity for risk
    if answers.age < 30:
        score += 0.25
    elif answers.age < 40:
        score += 0.18
    elif answers.age < 50:
        score += 0.10
    else:
        score += 0.03

    # Horizon
    horizon_pts = {"< 1 year": 0.0, "1-3 years": 0.08, "3-5 years": 0.18, "5+ years": 0.27}
    score += horizon_pts.get(answers.investment_horizon, 0.1)

    # Loss tolerance (1-5)
    score += (answers.loss_tolerance - 1) / 4 * 0.30

    # Goal
    goal_pts = {"capital protection": 0.0, "steady growth": 0.08,
                "wealth creation": 0.16, "aggressive growth": 0.22}
    score += goal_pts.get(answers.investment_goal, 0.08)

    # Existing investor: mild bump for experience
    if answers.existing_investor:
        score += 0.03

    score = min(max(score, 0.0), 1.0)
    bucket_idx = int(score * (len(RISK_BUCKETS) - 1))
    bucket = RISK_BUCKETS[bucket_idx]

    return {
        "risk_score": round(score, 3),
        "risk_bucket": bucket,
        "explanation": (
            f"Based on your age, {answers.investment_horizon} horizon, "
            f"loss tolerance of {answers.loss_tolerance}/5, and a goal of "
            f"'{answers.investment_goal}', you're classified as a "
            f"{bucket} investor."
        ),
    }


@app.post("/api/interactions")
def log_interaction(payload: InteractionIn):
    if payload.user_id not in USERS:
        raise HTTPException(404, "User not found")
    if payload.item_id not in ITEM_LOOKUP:
        raise HTTPException(404, "Item not found")

    record = {
        "user_id": payload.user_id,
        "item_id": payload.item_id,
        "item_type": "fund" if payload.item_id in FUNDS else "stock",
        "action": payload.action,
        "amount": payload.amount or 0,
        "user_rating": None,
    }
    INTERACTIONS.append(record)
    USER_INTERACTIONS[payload.user_id].append(record)
    return {"status": "logged", "record": record}


@app.get("/api/categories")
def categories():
    cats = sorted(set(f["category"] for f in FUNDS.values()))
    sectors = sorted(set(s["sector"] for s in STOCKS.values()))
    return {"fund_categories": cats, "stock_sectors": sectors}
