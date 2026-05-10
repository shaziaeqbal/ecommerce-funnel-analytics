"""
Generates synthetic Google Merchandise Store-style data
and stores it in DuckDB (ecommerce.duckdb).
"""
import duckdb, numpy as np, pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N   = 50_000   # sessions

CHANNELS   = ["Organic Search","Paid Search","Direct","Email","Social","Referral","Display"]
DEVICES    = ["desktop","mobile","tablet"]
COUNTRIES  = ["United States","India","United Kingdom","Canada","Germany","Australia","France"]
CATEGORIES = ["Apparel","Drinkware","Bags","Office","Lifestyle","Electronics","Sale"]

def gen_sessions(n):
    ch_w = [0.35,0.20,0.15,0.10,0.08,0.07,0.05]
    dv_w = [0.55,0.35,0.10]
    data = {
        "session_id"      : [f"S{i:06d}" for i in range(n)],
        "user_id"         : [f"U{RNG.integers(1,15000):05d}" for _ in range(n)],
        "channel"         : RNG.choice(CHANNELS, n, p=ch_w),
        "device"          : RNG.choice(DEVICES,  n, p=dv_w),
        "country"         : RNG.choice(COUNTRIES, n),
        "session_date"    : pd.to_datetime(
            RNG.integers(
                pd.Timestamp("2023-01-01").value,
                pd.Timestamp("2024-01-01").value, n
            )
        ).normalize(),
        "page_views"      : RNG.integers(1, 20, n),
        "session_duration": RNG.integers(10, 1800, n),
        "bounce"          : RNG.choice([0,1], n, p=[0.55,0.45]),
    }
    return pd.DataFrame(data)

def gen_funnel(sessions):
    n = len(sessions)
    viewed  = RNG.random(n) < 0.65
    carted  = viewed  & (RNG.random(n) < 0.40)
    checked = carted  & (RNG.random(n) < 0.55)
    bought  = checked & (RNG.random(n) < 0.60)
    return sessions.assign(
        viewed_product   = viewed.astype(int),
        added_to_cart    = carted.astype(int),
        reached_checkout = checked.astype(int),
        purchased        = bought.astype(int),
    )

def gen_transactions(sessions_funnel):
    buyers = sessions_funnel[sessions_funnel.purchased == 1].copy()
    rows = []
    for _, row in buyers.iterrows():
        n_items = RNG.integers(1, 5)
        for _ in range(n_items):
            rows.append({
                "transaction_id": f"T{RNG.integers(1e8):.0f}",
                "session_id"    : row.session_id,
                "user_id"       : row.user_id,
                "category"      : RNG.choice(CATEGORIES),
                "revenue"       : round(float(RNG.uniform(5, 120)), 2),
                "quantity"      : int(RNG.integers(1, 4)),
                "transaction_date": row.session_date,
            })
    return pd.DataFrame(rows)

def main():
    Path("data").mkdir(exist_ok=True)
    db = duckdb.connect("data/ecommerce.duckdb")

    print("Generating sessions …")
    s  = gen_sessions(N)
    sf = gen_funnel(s)
    tx = gen_transactions(sf)

    db.execute("DROP TABLE IF EXISTS sessions")
    db.execute("DROP TABLE IF EXISTS transactions")
    db.register("sf_view", sf)
    db.register("tx_view", tx)
    db.execute("CREATE TABLE sessions     AS SELECT * FROM sf_view")
    db.execute("CREATE TABLE transactions AS SELECT * FROM tx_view")

    print(f"  sessions     : {len(sf):,}")
    print(f"  transactions : {len(tx):,}")
    print("Saved to data/ecommerce.duckdb")
    db.close()

if __name__ == "__main__":
    main()
