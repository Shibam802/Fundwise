"""
Generates a realistic synthetic dataset of mutual funds, stocks, users,
risk profiles, and interaction history (invests / watchlists / SIPs).

This stands in for what would, in production, be pulled from AMFI NAV
data, exchange feeds, and a users/transactions database.
"""
import json
import random
import numpy as np

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. FUND UNIVERSE
# ---------------------------------------------------------------------------

CATEGORIES = {
    "Large Cap Equity":      {"risk": 3, "ret_mean": 13, "ret_std": 3},
    "Mid Cap Equity":        {"risk": 4, "ret_mean": 16, "ret_std": 5},
    "Small Cap Equity":      {"risk": 5, "ret_mean": 19, "ret_std": 8},
    "Flexi Cap Equity":      {"risk": 4, "ret_mean": 14, "ret_std": 4},
    "ELSS (Tax Saver)":      {"risk": 4, "ret_mean": 14, "ret_std": 4},
    "Index Fund":            {"risk": 3, "ret_mean": 12, "ret_std": 2},
    "Sectoral - Technology": {"risk": 5, "ret_mean": 17, "ret_std": 9},
    "Sectoral - Banking":    {"risk": 5, "ret_mean": 15, "ret_std": 7},
    "Sectoral - Pharma":     {"risk": 5, "ret_mean": 14, "ret_std": 7},
    "International Equity":  {"risk": 4, "ret_mean": 13, "ret_std": 6},
    "Debt - Liquid":         {"risk": 1, "ret_mean": 6.5, "ret_std": 0.5},
    "Debt - Short Duration": {"risk": 1, "ret_mean": 7,   "ret_std": 1},
    "Debt - Corporate Bond": {"risk": 2, "ret_mean": 7.5, "ret_std": 1.2},
    "Debt - Gilt":           {"risk": 2, "ret_mean": 7,   "ret_std": 1.5},
    "Hybrid - Aggressive":   {"risk": 3, "ret_mean": 11,  "ret_std": 3},
    "Hybrid - Conservative": {"risk": 2, "ret_mean": 8.5, "ret_std": 1.5},
    "Gold Fund":             {"risk": 3, "ret_mean": 10,  "ret_std": 4},
}

AMCS = ["Parivar", "NorthStar", "Bharosa", "Suraksha", "Vridhi", "Ananta",
        "Trishul", "Kalpataru", "Nivesh", "Samriddhi", "Gatiman", "Udaan"]

FUND_NAME_WORDS = {
    "Large Cap Equity": ["Bluechip", "Top 100", "Large Cap", "Leaders"],
    "Mid Cap Equity": ["Midcap", "Emerging Growth", "Mid Cap Opportunities"],
    "Small Cap Equity": ["Smallcap", "Micro Growth", "Small Cap Discovery"],
    "Flexi Cap Equity": ["Flexicap", "Multi Cap", "Diversified Equity"],
    "ELSS (Tax Saver)": ["Tax Saver", "ELSS Advantage", "Tax Shield"],
    "Index Fund": ["Nifty 50 Index", "Sensex Index", "Nifty Next 50 Index"],
    "Sectoral - Technology": ["Digital India", "Tech Opportunities", "Infotech Fund"],
    "Sectoral - Banking": ["Banking & Financial Services", "BFSI Fund"],
    "Sectoral - Pharma": ["Pharma & Healthcare", "Healthcare Opportunities"],
    "International Equity": ["US Equity FoF", "Global Innovation", "China-India FoF"],
    "Debt - Liquid": ["Liquid Fund", "Cash Management Fund"],
    "Debt - Short Duration": ["Short Term Debt", "Low Duration Fund"],
    "Debt - Corporate Bond": ["Corporate Bond Fund", "Credit Opportunities"],
    "Debt - Gilt": ["Gilt Fund", "Government Securities Fund"],
    "Hybrid - Aggressive": ["Equity Hybrid", "Balanced Advantage"],
    "Hybrid - Conservative": ["Conservative Hybrid", "Regular Savings Fund"],
    "Gold Fund": ["Gold Fund", "Gold ETF FoF"],
}


def gen_funds(n=90):
    funds = []
    fid = 1
    cats = list(CATEGORIES.keys())
    while len(funds) < n:
        cat = random.choice(cats)
        stats = CATEGORIES[cat]
        amc = random.choice(AMCS)
        base_name = random.choice(FUND_NAME_WORDS[cat])
        plan = random.choice(["Direct Growth", "Direct Growth", "Regular Growth"])
        name = f"{amc} {base_name} Fund - {plan}"
        # avoid exact dup names
        if any(f["name"] == name for f in funds):
            continue

        ret_3y = round(np.random.normal(stats["ret_mean"], stats["ret_std"]), 2)
        ret_1y = round(ret_3y + np.random.normal(0, 3), 2)
        ret_5y = round(ret_3y + np.random.normal(0, 2), 2)
        expense_ratio = round(np.random.uniform(0.1, 0.3) if "Direct" in plan
                               else np.random.uniform(0.8, 2.2), 2)
        aum = round(np.random.lognormal(mean=8.5, sigma=1.2), 1)  # in Cr
        rating = int(np.clip(np.random.normal(3.4, 1.1), 1, 5))

        funds.append({
            "fund_id": f"F{fid:03d}",
            "name": name,
            "amc": amc,
            "category": cat,
            "risk_level": stats["risk"],  # 1 (low) - 5 (high)
            "returns_1y": ret_1y,
            "returns_3y": ret_3y,
            "returns_5y": ret_5y,
            "expense_ratio": expense_ratio,
            "aum_cr": aum,
            "rating": rating,
            "min_sip": random.choice([100, 250, 500, 1000]),
            "asset_class": "Equity" if "Equity" in cat or "Sectoral" in cat or "ELSS" in cat
                            else ("Debt" if "Debt" in cat else
                                  ("Hybrid" if "Hybrid" in cat else
                                   ("Gold" if "Gold" in cat else "International"))),
        })
        fid += 1
    return funds


# ---------------------------------------------------------------------------
# 2. DIRECT STOCK UNIVERSE (large/mid/small cap NSE-style names, fictionalized)
# ---------------------------------------------------------------------------

STOCK_SECTORS = ["IT", "Banking", "FMCG", "Auto", "Pharma", "Energy",
                  "Infrastructure", "Telecom", "Metals", "Realty"]

STOCK_PREFIXES = ["Tata", "Reliant", "Bajaj", "Adani", "Mahindra", "Hind",
                   "ICICI", "HDFC", "Larsen", "Wipro", "Infosys", "Kotak",
                   "SBI", "Sun", "Cipla", "Vedanta", "JSW", "UltraTech",
                   "Asian", "Bharti"]

STOCK_SUFFIXES = ["Industries", "Corp", "Ltd", "Enterprises", "Motors",
                   "Technologies", "Bank", "Power", "Steel", "Pharma"]


def gen_stocks(n=60):
    stocks = []
    sid = 1
    seen = set()
    while len(stocks) < n:
        name = f"{random.choice(STOCK_PREFIXES)} {random.choice(STOCK_SUFFIXES)}"
        if name in seen:
            continue
        seen.add(name)
        sector = random.choice(STOCK_SECTORS)
        cap = random.choices(["Large", "Mid", "Small"], weights=[0.35, 0.35, 0.3])[0]
        risk = {"Large": 3, "Mid": 4, "Small": 5}[cap]
        pe = round(np.random.uniform(10, 60), 1)
        ret_1y = round(np.random.normal({"Large": 12, "Mid": 18, "Small": 22}[cap],
                                         {"Large": 10, "Mid": 18, "Small": 28}[cap]), 2)
        mcap_cr = round(np.random.lognormal({"Large": 12, "Mid": 9.5, "Small": 7.5}[cap], 0.8), 1)
        stocks.append({
            "stock_id": f"S{sid:03d}",
            "name": name,
            "ticker": (name.replace(" ", "")[:8]).upper(),
            "sector": sector,
            "market_cap_category": cap,
            "risk_level": risk,
            "pe_ratio": pe,
            "returns_1y": ret_1y,
            "market_cap_cr": mcap_cr,
        })
        sid += 1
    return stocks


# ---------------------------------------------------------------------------
# 3. USERS + RISK PROFILES
# ---------------------------------------------------------------------------

RISK_BUCKETS = ["Conservative", "Moderate", "Balanced", "Growth", "Aggressive"]

FIRST_NAMES = ["Aarav", "Vivaan", "Aditi", "Ananya", "Ishaan", "Priya", "Rohan",
               "Sneha", "Karan", "Meera", "Arjun", "Diya", "Kabir", "Neha",
               "Rahul", "Pooja", "Siddharth", "Anjali", "Yash", "Riya",
               "Dev", "Tanvi", "Aryan", "Kavya", "Nikhil", "Sanya", "Varun",
               "Ira", "Aditya", "Simran"]

LAST_NAMES = ["Sharma", "Verma", "Iyer", "Nair", "Gupta", "Reddy", "Das",
              "Bose", "Menon", "Chatterjee", "Rao", "Malhotra", "Kapoor",
              "Joshi", "Pillai"]

OCCUPATIONS = ["Salaried - IT", "Salaried - Finance", "Salaried - Other",
               "Business Owner", "Student", "Freelancer", "Retired"]


def gen_users(n=45):
    users = []
    for i in range(1, n + 1):
        age = int(np.clip(np.random.normal(32, 9), 21, 65))
        # younger + salaried IT/finance skew toward higher risk appetite
        occ = random.choice(OCCUPATIONS)
        base_risk = np.random.uniform(0, 1)
        if age < 28:
            base_risk += 0.15
        if age > 50:
            base_risk -= 0.25
        if occ in ("Business Owner", "Salaried - Finance"):
            base_risk += 0.1
        if occ == "Retired":
            base_risk -= 0.3
        base_risk = np.clip(base_risk, 0, 1)
        bucket_idx = int(base_risk * (len(RISK_BUCKETS) - 1))
        risk_bucket = RISK_BUCKETS[bucket_idx]

        monthly_income = int(np.clip(np.random.lognormal(10.9, 0.5), 20000, 800000))
        investment_horizon = random.choice(["< 1 year", "1-3 years", "3-5 years", "5+ years"])
        existing_investor = random.random() < 0.75

        users.append({
            "user_id": f"U{i:03d}",
            "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "age": age,
            "occupation": occ,
            "monthly_income": monthly_income,
            "risk_score": round(base_risk, 3),        # 0-1 continuous
            "risk_bucket": risk_bucket,                # 5 buckets
            "investment_horizon": investment_horizon,
            "existing_investor": existing_investor,
        })
    return users


# ---------------------------------------------------------------------------
# 4. INTERACTIONS (implicit feedback: invested / watchlisted / sip_active)
# ---------------------------------------------------------------------------

def risk_bucket_to_num(bucket):
    return RISK_BUCKETS.index(bucket) + 1  # 1..5


def gen_interactions(users, funds, stocks):
    """
    Each user interacts with a handful of instruments. Probability of
    interacting with a fund/stock is weighted by how close the
    instrument's risk_level is to the user's risk appetite, so the
    synthetic data actually encodes a learnable signal for both the
    content-based and collaborative-filtering models.
    """
    interactions = []
    all_items = (
        [{"item_id": f["fund_id"], "item_type": "fund", "risk_level": f["risk_level"]} for f in funds]
        + [{"item_id": s["stock_id"], "item_type": "stock", "risk_level": s["risk_level"]} for s in stocks]
    )

    for u in users:
        user_risk = risk_bucket_to_num(u["risk_bucket"])
        weights = []
        for item in all_items:
            dist = abs(item["risk_level"] - user_risk)
            w = np.exp(-0.9 * dist)  # closer risk level => much more likely
            weights.append(w)
        weights = np.array(weights)
        weights /= weights.sum()

        n_interactions = np.random.randint(4, 14)
        chosen_idx = np.random.choice(len(all_items), size=n_interactions,
                                       replace=False, p=weights)
        for idx in chosen_idx:
            item = all_items[idx]
            action = np.random.choice(
                ["invested", "sip_active", "watchlisted"],
                p=[0.45, 0.25, 0.30]
            )
            amount = 0
            if action in ("invested", "sip_active"):
                amount = int(np.random.choice([500, 1000, 2000, 5000, 10000, 25000]))
            rating = None
            if action == "invested" and random.random() < 0.5:
                rating = int(np.clip(np.random.normal(4, 1), 1, 5))

            interactions.append({
                "user_id": u["user_id"],
                "item_id": item["item_id"],
                "item_type": item["item_type"],
                "action": action,
                "amount": amount,
                "user_rating": rating,
            })
    return interactions


# ---------------------------------------------------------------------------
def main():
    funds = gen_funds(90)
    stocks = gen_stocks(60)
    users = gen_users(45)
    interactions = gen_interactions(users, funds, stocks)

    out = {
        "funds": funds,
        "stocks": stocks,
        "users": users,
        "interactions": interactions,
    }
    with open("/home/claude/fundwise/backend/data/seed.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"Generated {len(funds)} funds, {len(stocks)} stocks, "
          f"{len(users)} users, {len(interactions)} interactions")


if __name__ == "__main__":
    main()
