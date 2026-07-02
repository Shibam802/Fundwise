# FundWise — Hybrid Fund & Stock Recommendation Engine

A full-stack recommendation system for mutual funds and stocks, in the spirit of
Groww's discovery surface: a **content-based + collaborative filtering hybrid**
that recommends investments based on a user's risk profile, past behavior, and
portfolio composition.

Built as a placement-portfolio project — the goal was to implement something
that's genuinely evaluable (precision/recall, not just "looks nice"), not just
a UI mockup.

---
<img width="1908" height="977" alt="image" src="https://github.com/user-attachments/assets/74a5d12d-07a3-47b3-b1e4-cfb2b8c4084b" />
<img width="1911" height="978" alt="image" src="https://github.com/user-attachments/assets/44d58b3f-d83e-4283-9a5a-5efb25076d6f" />
<img width="1912" height="977" alt="image" src="https://github.com/user-attachments/assets/04c792c2-d4de-4150-993b-237ecb920a82" />

## Architecture

```
fundwise/
├── backend/
│   ├── app/
│   │   ├── main.py                    FastAPI app + REST endpoints
│   │   ├── generate_data.py           synthetic data generator
│   │   ├── evaluate.py                offline eval: precision/recall @K
│   │   └── recommenders/
│   │       ├── content_based.py       feature-vector + cosine similarity
│   │       ├── collaborative.py       implicit-feedback matrix factorization (SVD)
│   │       └── hybrid.py              weighted blend + risk-suitability guardrail
│   ├── data/seed.json                 generated funds/stocks/users/interactions
│   └── requirements.txt
└── frontend/                          React + Vite dashboard
    └── src/
        ├── pages/                     SelectInvestor, Dashboard, Explore, Portfolio, RiskQuiz
        ├── components/                Layout, RiskGauge, RecCard
        └── api.js                     backend client
```

## How the recommender works

**1. Content-based filtering** (`content_based.py`)
Every fund/stock is turned into a feature vector: one-hot category/sector +
normalized risk level + normalized 1-year return + normalized expense
ratio/PE. Every user gets a preference vector built from their risk score and
the categories they've actually engaged with (cold-start users get a uniform
prior). Recommendations are ranked by cosine similarity between the two.

**2. Collaborative filtering** (`collaborative.py`)
Builds a user × item implicit-feedback matrix, weighting each interaction by
action type (`invested` > `sip_active` > `watchlisted`), amount invested, and
any rating given. Factorizes it with Truncated SVD to learn latent "taste"
dimensions, then recommends the highest-predicted-affinity items the user
hasn't already touched — the "investors like you also bought" surface. Also
powers the *similar investors* panel on the dashboard.

**3. Hybrid blend + risk guardrail** (`hybrid.py`)
```
final_score = alpha * content_score + (1 - alpha) * collab_score
final_score *= risk_fit_multiplier(user_risk_bucket, item_risk_level)
```
- `alpha` is adaptive: users with little history lean on content-based
  (alpha ≈ 0.9); users with 15+ interactions lean collaborative (alpha ≈ 0.35).
- `risk_fit_multiplier` sharply dampens (not hard-blocks) items well above a
  user's stated risk tolerance — mirroring the suitability rules real fund
  platforms apply so a Conservative investor's feed doesn't get dominated by
  Small Cap funds just because the collaborative signal likes them.
- Every recommendation ships with a human-readable explanation and a
  transparent score breakdown (content vs. collaborative vs. risk multiplier),
  visible in the UI under "Show match breakdown."

## Offline evaluation

`backend/app/evaluate.py` does leave-k-out validation: holds out 30% of each
user's positive interactions (invested/SIP), retrains, and checks whether the
held-out items reappear in the top-10 recommendations — comparing content-only,
collaborative-only, and the hybrid.

```
Model          Precision@10   Recall@10   RiskViolation%
content_only   0.012          0.085       50.5
collab_only    0.015          0.110       26.6
hybrid         0.027          0.183       10.5
```

The hybrid roughly **doubles precision and recall** over either individual
approach, and cuts risk-suitability violations by **~5x** versus content-only —
the clearest evidence the blend (plus the guardrail) is doing real work, not
just averaging two mediocre signals. Run it yourself:

```bash
cd backend/app && python3 evaluate.py
```

*(Numbers are naturally modest in absolute terms — this is a small synthetic
catalogue of ~150 items, and precision@10 gets diluted fast with only ~3-4
held-out positives per user. What matters for the portfolio story is the
**relative** lift from the hybrid.)*

## Data

All funds, stocks, users, and interactions are **synthetically generated**
(`generate_data.py`) but with realistic structure: 90 mutual funds across 17
categories (equity/debt/hybrid/gold/sectoral) with plausible return
distributions per category, 60 stocks across 10 sectors, 45 users with
risk-correlated demographics, and ~360 weighted implicit-feedback interactions.
In production this would be swapped for AMFI NAV data, exchange feeds, and a
real transactions table — the recommender code doesn't change.

---

## Running it locally

### Backend
```bash
cd backend
pip install -r requirements.txt
cd app
python3 generate_data.py   # regenerate synthetic data (optional, already included)
uvicorn main:app --reload --port 8000
```
API docs at `http://localhost:8000/docs`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. Pick any demo investor to see live, personalized
recommendations — invest/watchlist actions immediately feed back into the
collaborative model for that session.

### Evaluate the models
```bash
cd backend/app
python3 evaluate.py
```

---

## What to highlight in an interview

- **Not just a wrapper around a library** — content-based and collaborative
  models are both implemented from first principles (feature engineering +
  cosine similarity; implicit-feedback matrix + Truncated SVD), so you can
  speak to the math, not just the API call.
- **Adaptive blending** — the alpha weighting that shifts from content-based
  to collaborative as history accumulates is a real cold-start solution, a
  common recommender-systems interview topic.
- **Domain-aware constraint layer** — the risk-suitability guardrail is the
  kind of business-logic-meets-ML integration that distinguishes a "recommender
  that ships" from a notebook demo.
- **It's measured, not vibes-based** — `evaluate.py` gives you defendable
  precision/recall numbers to cite instead of "the recommendations looked
  good to me."
