from . import np 
from . import sparse
from . import spsolve
from . import timedelta

def baseline_als(y, lam=10000, p=0.05, n_iter=10):
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
    w = np.ones(L)
    for i in range(n_iter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def remove_baseline_als(ECG):
    time_interval = [time_result for time_result in perdelta(ECG.index.min(), ECG.index.max(), timedelta(seconds=16))]
    ECG_ALS = []
    for time_intv in list(zip(time_interval, time_interval[1:])):
        X = ECG.between_time(time_intv[0].time(), time_intv[1].time())
        X_val = X.values[:,0]
        if len(X_val) > 0 :
            ALS = X_val - baseline_als(X_val)
            ECG_ALS.append(np.array(ALS))
    return ECG_ALS