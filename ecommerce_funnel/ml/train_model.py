"""
Trains a cart abandonment classifier on mart_cart_abandonment.
Saves model to ml/abandonment_model.joblib
"""
import duckdb, joblib, numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score

DB = "data/ecommerce.duckdb"

def load_data():
    con = duckdb.connect(DB, read_only=True)
    df  = con.execute("SELECT * FROM mart_cart_abandonment").df()
    con.close()
    return df

def preprocess(df):
    cat_cols = ["channel","device","country"]
    encoders = {}
    for c in cat_cols:
        le = LabelEncoder()
        df[c] = le.fit_transform(df[c].astype(str))
        encoders[c] = le
    features = ["channel","device","country","page_views",
                "session_duration","bounce","reached_checkout"]
    X = df[features]
    y = df["abandoned"]
    return X, y, encoders, features

def main():
    print("Loading data …")
    df = load_data()
    X, y, encoders, features = preprocess(df)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = GradientBoostingClassifier(
        n_estimators=200, max_depth=4,
        learning_rate=0.08, random_state=42
    )
    print("Training GradientBoostingClassifier …")
    clf.fit(X_tr, y_tr)

    y_pred = clf.predict(X_te)
    y_prob = clf.predict_proba(X_te)[:,1]
    print(classification_report(y_te, y_pred))
    print(f"ROC-AUC : {roc_auc_score(y_te, y_prob):.4f}")

    Path("ml").mkdir(exist_ok=True)
    joblib.dump({"model": clf, "encoders": encoders, "features": features},
                "ml/abandonment_model.joblib")
    print("Model saved → ml/abandonment_model.joblib")

if __name__ == "__main__":
    main()
