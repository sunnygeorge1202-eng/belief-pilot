"""
Design simulation for the belief-updating pilot.

Question answered: given the paradigm (4 targets/person, 2 high and 2 low credibility challenges),
how likely is the main test to detect a real "discounted vs under-learned" effect, and how often does
it fire when there is none, as a function of sample size and measurement noise in the weight rating?

Main test (mirrors admin.html model M2): revC ~ gC + revB + cred + confB + Uw, z-scored predictors,
participant-clustered SEs. 'Detect' = 95% CI for Uw excludes 0.

Usage: python3 simulate.py            (about 1 minute)
"""
import numpy as np
rng = np.random.default_rng(11)

def clip(x, lo, hi): return np.minimum(hi, np.maximum(lo, x))

def simulate(n, gamma, w_noise, noise=4.0):
    P = np.repeat(np.arange(n), 4)
    cred = np.tile([0.5, 0.5, -0.5, -0.5], n)
    prior = rng.normal(78, 6, n*4)
    gB = prior - 20
    alpha = clip(rng.normal(0.6, 0.15, n), 0.15, 1.0)[P]
    w_person = rng.normal(0, 0.10, n)[P]
    w_true = clip(np.where(cred > 0, 0.78, 0.38) + w_person + rng.normal(0, 0.12, n*4), 0.02, 1)
    revB = alpha * w_true * gB + rng.normal(0, noise, n*4)
    bB = prior - revB
    gC = bB - 20
    Ul_true = w_true * gB - revB
    revC = 0.35 * gC + gamma * Ul_true + rng.normal(0, noise, n*4)   # gamma = true carry-forward effect of under-learned part
    w_rep = clip(w_true + rng.normal(0, w_noise, n*4), 0, 1)           # self-reported weight, with measurement noise
    Uw = (1 - w_rep) * gB
    confB = rng.normal(60, 15, n*4)
    ok = (gB >= 10) & (gC >= 10)
    return P[ok], revC[ok], np.column_stack([gC, revB, cred, confB, Uw])[ok]

def cluster_ols(P, y, Xraw):
    X = (Xraw - Xraw.mean(0)) / Xraw.std(0)
    X = np.column_stack([np.ones(len(y)), X])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    u = y - X @ b
    k = X.shape[1]; n = len(y)
    ids = np.unique(P); G = len(ids)
    meat = np.zeros((k, k))
    for g in ids:
        m = P == g
        s = X[m].T @ u[m]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (G/(G-1)) * ((n-1)/(n-k))
    se = np.sqrt(np.diag(V))
    return b, se, G

def tcrit(df):
    z = 1.96
    return z*(1+(z*z+1)/(4*df)+(5*z**4+16*z*z+3)/(96*df*df))

def power(n, gamma, w_noise, reps=400):
    hit = 0; est = []
    for _ in range(reps):
        P, y, X = simulate(n, gamma, w_noise)
        b, se, G = cluster_ols(P, y, X)
        j = X.shape[1]            # Uw is the last predictor (index = k-1 incl. intercept)
        t = tcrit(G-1)
        lo, hi = b[j] - t*se[j], b[j] + t*se[j]
        hit += (lo > 0) or (hi < 0)
        est.append(b[j])
    return hit/reps, np.mean(est)

if __name__ == "__main__":
    print("Detection rate for the Uw (discounted share) coefficient; gamma=0 row = false-positive rate")
    print("Ns are total participants (both tasks pooled). 'noise' is SD of weight-rating measurement error.\n")
    for w_noise in (0.0, 0.10, 0.20):
        print(f"--- weight-rating noise SD = {w_noise} ---")
        print("gamma   " + "  ".join(f"N={n:<4d}" for n in (40, 60, 80, 120)))
        for gamma in (0.0, 0.10, 0.20, 0.30):
            row = []
            for n in (40, 60, 80, 120):
                pw, _ = power(n, gamma, w_noise)
                row.append(f"{pw:5.2f} ")
            print(f"{gamma:<7.2f} " + "  ".join(row))
        print()
