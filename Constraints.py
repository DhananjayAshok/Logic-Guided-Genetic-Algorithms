import numpy as np
import pandas as pd

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Common computation functions declared Below
    
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def pairwise_symmetric_result(func, dls, X, y, col0="X0", col1="X1"):
    temp_clone = X.copy()
    temp_clone[col0] = X[col1]
    temp_clone[col1] = X[col0]
    predsym = dls.get_result(func, temp_clone, y)
    return temp_clone, predsym

def zero_result(func, dls, X, y, cols=["X0"]):
    temp_clone = X.copy()
    for col in cols:
        temp_clone[col] = 0
    return temp_clone, dls.get_result(func, temp_clone, y)

def equality_result(func, dls, X, y, cols=["X0", "X1"]):
    temp_clone = X.copy()
    for col in cols[1:]:
        temp_clone[col] = X[cols[0]]
    predeq = dls.get_result(func, temp_clone, y)
    return temp_clone, predeq

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Common full set functions declared Below
    
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def pairwise_symmetric_equality(func, dls, X, y, col0="X0", col1="X1"):
    X_sym, predsym = pairwise_symmetric_result(func, dls, X, y, col0, col1)
    predr = dls.get_result(func, X, y)
    return X_sym, np.abs(predr - predsym)

def zero_zero(func, dls, X, y, cols=["X0"]):
    X_zero, predzero = zero_result(func, dls, X, y, cols=cols)
    actual = pd.Series(np.zeros(shape=predzero.shape))
    return X_zero, predzero, actual




''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Common output functions declared Below
    
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def get_floored_max(series, floor=0):
    return max(np.append(series, floor))


def get_union_slice(violations):
    """
    Expects violation to be [(boolean frame, X, y)....]
    """
    Xs = pd.concat([violation[1][violation[0]] for violation in violations])
    ys = pd.concat([violation[2][violation[0]] for violation in violations])
    #print(f"Adding {len(ys)} points")
    return Xs, ys
    

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Constraints and LGML functions declared Below
    
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def resistance_computations(func, dls, X, y, threshold):
    predr = dls.get_result(func, X, y)
    Xsym, predsymr = pairwise_symmetric_result(func, dls, X, y)
    X0_zero, predr1zero = zero_result(func, dls, X, y, cols=["X0"])
    X1_zero, predr2zero = zero_result(func, dls, X, y, cols=["X1"])
    X_eq, predeq = equality_result(func, dls, X, y, cols=["X0", "X1"])
    r1 = X['X0']
    r2 = X['X1']
    r = y
    return Xsym, X0_zero, X1_zero, X_eq, predr, predsymr, predr1zero, predr2zero, predeq, r1, r2, r

def resistance_constraints(dls, X, y, weight=1000, threshold=2):
    func = dls.func
    Xsym, X0_zero, X1_zero, X_eq, predr, predsymr, predr1zero, predr2zero, predeq, r1, r2, r = resistance_computations(func,dls, X, y, threshold)
    symmnetry_violation = np.abs(predr - predsymr)
    x1specific = predr - r1
    x2specific = predr - r2
    
    rviolations = max(np.append(symmnetry_violation,0)) + max(np.append(x1specific, 0)) + max(np.append(x2specific, 0))
    return weight * rviolations


def resistance_lgml_func(ind, X=None, y=None, dls=None, threshold=2):
    if X is None or y is None:
        return None, None
    Xsym, X0_zero, X1_zero, X_eq, predr, predsymr, predr1zero, predr2zero, predeq, r1, r2, r = resistance_computations(ind, dls, X, y, threshold)
    symviolation = np.abs(predr - predsymr) > threshold
    x1violation = r1 < predr
    x2violation = r2 < predr
    r1zeroviolation = np.abs(predr1zero) > threshold
    r2zeroviolation = np.abs(predr2zero) > threshold
    equality_violation = np.abs(r1/2 - predeq) > threshold # Equality result function makes all equal to first input column
    zero_col = pd.Series(np.zeros(shape=predr.shape))
    return get_union_slice([(symviolation, Xsym, y), (x1violation, X, y), (x2violation, X, y), (r1zeroviolation, X0_zero, zero_col), (r1zeroviolation, X1_zero, zero_col), (equality_violation, X_eq, r1/2)])
    


def snell_computations(func, dls, X, y, threshold):
    preds = dls.get_result(func, X, y)
    Xsym, predsym = pairwise_symmetric_result(func, dls, X, y)
    X_zero, predzero, actual = zero_zero(func, dls, X, y, cols=["X0"])
    i = X['X0']
    r = X['X1']
    n = y
    return Xsym, X_zero, actual,  predzero, preds, predsym, i, r, n

def snell_constraints(dls, X, y, weight=10, threshold=2):
    func = dls.func
    Xsym, X_zero, actual, predzero, preds, predsym, i, r, n = snell_computations(func, dls, X, y, threshold)
    nonzeros = np.abs(predsym) >= 0.001
    symnetry_violation = np.abs(preds - 1/predsym[nonzeros])
    return weight * (max(np.append(symnetry_violation, 0)) + get_floored_max(predzero))

def snell_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    Xsym, X_zero, actual, predzero, preds, predsym, i, r, n = snell_computations(ind, dls, X, y, threshold)
    nonzeros = np.abs(predsym) >= 0.001
    symnetry_violation = np.abs(preds - 1/predsym[nonzeros]) > threshold
    zero_violation = np.abs(predzero) > threshold
    return get_union_slice([(symnetry_violation, Xsym[nonzeros], 1/y), (zero_violation, X_zero, actual)])

def coloumb_computations(func, dls, X, y, threshold):
    preds = dls.get_result(func, X, y)
    Xsym, symerror = pairwise_symmetric_equality(func, dls, X, y)
    q1 = X['X0']
    q2 = X['X1']
    r = X['X2']
    q = y
    both_positive = (q1 > 0) & (q2 > 0)
    both_negative = (q1 < 0) & (q2 < 0)
    both_same_sign = both_negative | both_positive
    return Xsym, preds, symerror, q1, q2, r, q, both_same_sign

def coloumb_constraints(dls, X, y, weight=10, threshold=2):
    func = dls.func
    Xsym, preds, symerror, q1, q2, r, q, both_same_sign = coloumb_computations(func, dls, X, y, threshold)
    symntery_violation = np.abs(symerror)
    same_sign_violation = -preds[both_same_sign] # If the results are positive then value will be neg if neg then value positive
    diff_sign_violation = preds[~both_same_sign]
    return weight * (get_floored_max(symntery_violation) + get_floored_max(same_sign_violation) + get_floored_max(diff_sign_violation))


def coloumb_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    Xsym, preds, symerror, q1, q2, r, q, both_same_sign = coloumb_computations(ind, dls, X, y, threshold)
    symviolation = symerror > threshold
    same_sign_violation = -preds[both_same_sign] > threshold
    diff_sign_violation = preds[~both_same_sign] > threshold
    return get_union_slice([(symviolation, Xsym, y), (same_sign_violation, X[both_same_sign], y[both_same_sign]), (diff_sign_violation, X[~both_same_sign], y[~both_same_sign]) ])

def reflection_computations(func, dls, X, y, threshold):
    preds = dls.get_result(func, X, y)
    Xsym, symerror = pairwise_symmetric_equality(func, dls, X, y)
    n1 = X['X0']
    n2 = X['X1']
    r = y
    return Xsym, preds, symerror, n1, n2, r

def reflection_constraints(dls, X, y, weight=10, threshold=0.00001):
    func = dls.func
    Xsym, predr, symerror, n1, n2, r = reflection_computations(func, dls, X, y, threshold)
    symnetry_violation = symerror
    range_violation = np.abs(predr - 0.5) - 0.5
    return weight * (get_floored_max(symnetry_violation) + get_floored_max(range_violation))

def reflection_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    Xsym, predr, symerror, n1, n2, r = reflection_computations(ind, dls, X, y, threshold)
    symnetry_violation = symerror > threshold
    range_violation = np.abs(predr - 0.5) > 0.5
    return get_union_slice([(symnetry_violation, Xsym, y), (range_violation, X, y)])


def gas_computations(func, dls, X, y, threshold):
    p = X['X0']
    v = X['X1']
    n = X['X2']
    t = X['X3']
    r = y
    pred = dls.get_result(func, X, y)
    X_sympv, predsympv = pairwise_symmetric_result(func, dls, X, y)
    X_symnt, predsymnt = pairwise_symmetric_result(func, dls, X, y, col0="X2", col1="X3")
    X_zerop, predzerop = zero_result(func, dls, X, y)
    X_zerov, predzerov = zero_result(func, dls, X, y, cols=["X1"])

    return X_sympv, X_symnt,X_zerop, X_zerov , p, v, n, t, r, pred, predsympv, predsymnt, predzerop, predzerov

def gas_constraints(dls, X, y, weight=10, threshold=0.00001):
    func = dls.func
    X_sympv, X_symnt,X_zerop, X_zerov , p, v, n, t, r, pred, predsympv, predsymnt, predzerop, predzerov = gas_computations(func, dls, X, y, threshold)
    symnetry_frames = [predsympv, predsymnt]
    symnetry_violations = [np.abs(pred - predsym) for predsym in symnetry_frames]
    zero_frames = [predzerop, predzerov]
    zero_violations = [zero_frame - 0.001 for zero_frame in zero_frames]
    return weight * (sum([get_floored_max(violation) for violation in symnetry_violations]) + sum([get_floored_max(violation) for violation in zero_violations]))

def gas_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    X_sympv, X_symnt,X_zerop, X_zerov , p, v, n, t, r, pred, predsympv, predsymnt, predzerop, predzerov = gas_computations(ind, dls, X, y, threshold)
    symnetry_frames = [(X_sympv, predsympv), (Xsymnt, predsymnt)]
    zero_frames = [(X_zerop, predzerop), (X_zerov, predzerov)]
    symnetry_violations = [(np.abs(pred - sym[1]) > threshold, sym[0], y) for sym in symnetry_frames]
    zero_violations = [(np.abs(frames[1]) > threshold, frames[0], pd.Series(np.zeros(shape=frames[1].shape))) for frames in zero_frames]
    
    return get_union_slice(symnetry_violations+zero_violations)


def distance_computations(func, dls, X, y, threshold):
    x0 = X['X0']
    x1 = X['X1']
    y0 = X['X2']
    y1 = X['X3']
    d = y
    pred = dls.get_result(func, X, y)
    X_symx, pred_symx = pairwise_symmetric_result(func, dls, X, y)
    X_symy, pred_symy = pairwise_symmetric_result(func, dls, X, y, col0="X2", col1="X3")
    X_zero_x0, pred_zero_x0 = zero_result(func, dls, X, y, cols=["X1", "X2", "X3"])
    X_zero_x1, pred_zero_x1 = zero_result(func, dls, X, y, cols=["X0", "X2", "X3"])
    X_zero_y0, pred_zero_y0 = zero_result(func, dls, X, y, cols=["X0", "X1", "X3"])
    X_zero_y1, pred_zero_y1 = zero_result(func, dls, X, y, cols=["X0", "X1", "X2"])
    X_eq, pred_eq = equality_result(func, dls, X, y, cols=["X0", "X1", "X2", "X3"])
    return X_symx,X_symy, X_zero_x0, X_zero_x1, X_zero_y0, X_zero_y1, X_eq ,x0, x1, y0, y1, d, pred, pred_symx, pred_symy, pred_zero_x0, pred_zero_x1, pred_zero_y0, pred_zero_y1, pred_eq


def distance_constraints(dls, X, y, weight=10, threshold=0.00001):
    func = dls.func
    X_symx,X_symy, X_zero_x0, X_zero_x1, X_zero_y0, X_zero_y1, X_eq ,x0, x1, y0, y1, d, pred, pred_symx, pred_symy, pred_zero_x0, pred_zero_x1, pred_zero_y0, pred_zero_y1, pred_eq = distance_computations(func, dls, X, y, threshold)
    symnetry_frames = [pred_symx, pred_symy]
    symnetry_violations = [np.abs(pred - predsym) for predsym in symnetry_frames]
    x0_violation = np.abs(x0 - pred_zero_x0)
    x1_violation = np.abs(x1 - pred_zero_x1)
    y0_violation = np.abs(y0 - pred_zero_y0)
    y1_violation = np.abs(y1 - pred_zero_y1)
    value_violations = [x0_violation, x1_violation, y0_violation, y1_violation]
    equality_violation = pred_eq - threshold
    return weight * (sum([get_floored_max(violation) for violation in symnetry_violations]) + sum([get_floored_max(violation) for violation in value_violations]) + get_floored_max(equality_violation))

def distance_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    X_symx,X_symy, X_zero_x0, X_zero_x1, X_zero_y0, X_zero_y1, X_eq ,x0, x1, y0, y1, d, pred, pred_symx, pred_symy, pred_zero_x0, pred_zero_x1, pred_zero_y0, pred_zero_y1, pred_eq = distance_computations(ind, dls, X, y, threshold)
    symnetry_frames = [(X_symx, pred_symx), (X_symy, pred_symy)]
    symnetry_violations = [(np.abs(pred - sym[1]) > threshold, sym[0], y) for sym in symnetry_frames]
    x0_violation = (np.abs(x0 - pred_zero_x0) > threshold, X_zero_x0, x0)
    x1_violation = (np.abs(x1 - pred_zero_x1) > threshold, X_zero_x1, x1)
    y0_violation = (np.abs(y0 - pred_zero_y0) > threshold, X_zero_y0, y0)
    y1_violation = (np.abs(y1 - pred_zero_y1) > threshold, X_zero_y1, y1)
    value_violations = [x0_violation, x1_violation, y0_violation, y1_violation]
    equality_violation = (pred_eq > threshold, X_eq, pd.Series(np.zeros(shape=pred_eq.shape)))
    violations = symnetry_violations+value_violations+[equality_violation]
    return get_union_slice(violations)


def normal_computations(func, dls, X, y, threshold):
    x = X['X0']
    n = y
    pred = dls.get_result(func, X, y)
    temp_x = X.copy()
    temp_x['X0'] = -x
    predneg = dls.get_result(func, temp_x, y)
    X_zero, predzero = zero_result(func, dls, X, y, cols=["X0"])
    max_pred = max(pred)
    return temp_x, X_zero, x, n, pred, predneg, predzero, max_pred

def normal_constraints(dls, X, y, weight=10, threshold=0.0001):
    func = dls.func
    negX, X_zero,x, n, pred, predneg, predzero, max_pred = normal_computations(func,dls, X,y, threshold)
    negviolation = np.abs(pred - predzero)
    zero_violation = np.abs(predzero - 0.1591549)
    max_violation = max_pred - predzero
    min_violation = -pred
    return weight * (get_floored_max(negviolation) + get_floored_max(zero_violation) + get_floored_max(max_violation) + get_floored_max(min_violation))


def normal_lgml_func(ind, dls=None, X=None, y=None, threshold=0.001):
    negX, X_zero,x, n, pred, predneg, predzero, max_pred = normal_computations(ind,dls, X,y, threshold)
    negviolation = (np.abs(pred - predzero) > threshold, negX, y)
    zero_violation = (np.abs(predzero - 0.1591549) > threshold, X_zero, (predzero * 0 + 0.1591549))
    max_violation = (max_pred - predzero > threshold, X, y)
    min_violation = (-pred > threshold, X, y)
    return get_union_slice([negviolation, zero_violation, max_violation,  min_violation])


