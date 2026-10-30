"""
Offline analysis of the pilot, from the dashboard's "derived.csv" export.
Usage:  python3 analyze.py derived.csv
Needs: pandas, numpy, scipy. Reports estimates and 95% intervals, not significance claims.
These are the robustness checks that the dashboard does not run.
"""
import sys, numpy as np, pandas as pd
from scipy import stats

def z(s): return (s - s.mean()) / s.std(ddof=0)

def ols_cluster(df, y, xs, cl="pid"):
    X = np.column_stack([np.ones(len(df))] + [z(df[x]).values for x in xs])
    Y = df[y].values.astype(float)
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ Y
    e = Y - X @ b
    g = df[cl].values
    ug = np.unique(g); G = len(ug); n, k = X.shape
    meat = sum(np.outer(X[g == u].T @ e[g == u], X[g == u].T @ e[g == u]) for u in ug)
    c = G / (G - 1) * (n - 1) / (n - k)
    V = c * XtXi @ meat @ XtXi
    se = np.sqrt(np.diag(V)); t = stats.t.ppf(0.975, G - 1)
    return pd.DataFrame({"coef": b, "se": se, "lo": b - t * se, "hi": b + t * se}, index=["const"] + xs), e

def loo_rmse(df, y, xs):
    errs = []
    for p in df.pid.unique():
        tr, te = df[df.pid != p], df[df.pid == p]
        mu = tr[xs].mean(); sd = tr[xs].std(ddof=0).replace(0, 1)
        Xtr = np.column_stack([np.ones(len(tr))] + [((tr[x] - mu[x]) / sd[x]).values for x in xs])
        Xte = np.column_stack([np.ones(len(te))] + [((te[x] - mu[x]) / sd[x]).values for x in xs])
        b = np.linalg.pinv(Xtr) @ tr[y].values
        errs += list(te[y].values - Xte @ b)
    return float(np.sqrt(np.mean(np.square(errs))))

def boot_ci(df, fn, B=1000, seed=1):
    rng = np.random.default_rng(seed); ids = df.pid.unique(); out = []
    for _ in range(B):
        s = rng.choice(ids, len(ids)); d = pd.concat([df[df.pid == i] for i in s])
        try: out.append(fn(d))
        except Exception: pass
    return np.percentile(out, [2.5, 97.5])

def main(path):
    d = pd.read_csv(path)
    d = d[d.ok.astype(str).str.lower().isin(["true", "1"])].dropna(subset=["Uw", "confB", "revC", "gC", "revB"]).copy()
    d["cred"] = np.where(d.credLabel == "high", 0.5, -0.5)
    print(f"Rows {len(d)}, participants {d.pid.nunique()}  ({d.groupby('domain').pid.nunique().to_dict()})\n")

    print("A. Descriptives (mean, SD)")
    print(d[["gB", "revB", "gC", "revC", "w", "wT", "confB", "behav"]].agg(["mean", "std"]).round(2).T, "\n")

    print("B. Weight by credibility, per-participant paired difference")
    pm = d.groupby(["pid", "credLabel"]).w.mean().unstack().dropna()
    if len(pm) > 2:
        diff = (pm["high"] - pm["low"]) * 100
        print(f"  high-low = {diff.mean():.1f} pts, dz = {diff.mean()/diff.std(ddof=1):.2f}, n = {len(pm)}\n")

    print("C. Models for revision at the test report (z-scored predictors, clustered SEs)")
    specs = {"M0": ["gC", "revB"], "M1": ["gC", "revB", "cred", "confB"], "M2": ["gC", "revB", "cred", "confB", "Uw"]}
    for k, xs in specs.items():
        r, _ = ols_cluster(d, "revC", xs)
        print(f"  {k}  LOPO RMSE = {loo_rmse(d, 'revC', xs):.3f}")
        if k == "M2": print(r.round(3).to_string())
    print()

    print("D. Robustness of the Uw coefficient")
    base = specs["M2"]
    checks = {
        "by task: trust": d[d.domain == "trust"], "by task: health": d[d.domain == "health"],
        "gap at least 20": d[d.gB >= 20], "challenge weight only (w in 0.1-0.9)": d[(d.w > .1) & (d.w < .9)],
    }
    for name, sub in checks.items():
        if sub.pid.nunique() >= 8:
            r, _ = ols_cluster(sub, "revC", base)
            print(f"  {name:38s} Uw = {r.loc['Uw','coef']:.2f} [{r.loc['Uw','lo']:.2f}, {r.loc['Uw','hi']:.2f}]  n={sub.pid.nunique()}")
    d["revC_s"] = d.revC; xs = base + ["pos"]
    r, _ = ols_cluster(d, "revC", xs)
    print(f"  {'adding target position':38s} Uw = {r.loc['Uw','coef']:.2f} [{r.loc['Uw','lo']:.2f}, {r.loc['Uw','hi']:.2f}]")
    dm = d.copy()
    for c in ["revC"] + base: dm[c] = dm[c] - dm.groupby("pid")[c].transform("mean")
    dm = dm.loc[:, ~dm.columns.duplicated()]
    r, _ = ols_cluster(dm, "revC", [c for c in base if dm[c].std() > 0])
    print(f"  {'within-participant (demeaned)':38s} Uw = {r.loc['Uw','coef']:.2f} [{r.loc['Uw','lo']:.2f}, {r.loc['Uw','hi']:.2f}]\n")

    print("E. Does the seek-more choice or behavioural readout track the same state?")
    if d.seek.notna().any():
        print("  seek-more rate by credibility:", d.groupby("credLabel").seek.mean().round(2).to_dict())
    print("  corr(behav, Uw) =", round(d[["behav", "Uw"]].dropna().corr().iloc[0, 1], 2),
          "| corr(behav, revC) =", round(d[["behav", "revC"]].dropna().corr().iloc[0, 1], 2))

if __name__ == "__main__":
    main(sys.argv[1])
