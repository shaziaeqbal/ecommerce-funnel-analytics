"""
Scores new sessions with the saved abandonment model.
Returns a DataFrame with abandonment_probability column.
"""
import joblib, pandas as pd

def score_sessions(df: pd.DataFrame) -> pd.DataFrame:
    bundle   = joblib.load("ml/abandonment_model.joblib")
    clf      = bundle["model"]
    encoders = bundle["encoders"]
    features = bundle["features"]

    df = df.copy()
    for col, le in encoders.items():
        # handle unseen labels gracefully
        df[col] = df[col].apply(
            lambda x: le.transform([x])[0] if x in le.classes_
                      else len(le.classes_)
        )
    df["abandonment_probability"] = clf.predict_proba(df[features])[:,1]
    return df
