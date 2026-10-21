"""Rate-dependent generalised Bouc-Wen + tension model for the M6A-219 isolator.

Force (kN) from displacement x (mm):

    F = ka*x + k2*x^2 + k3*x^3 + kt*<x - xt>_+^pt          elastic backbone + tension stiffening
      + kh*z1                                              rate-independent hysteresis (GBW)
      + kr*z2                                              rate-dependent hysteresis (relaxing GBW)
      + c*xdot + m*1e-6*xddot                              viscous + rig/fixture inertia (m in kg)

    dz/dx = 1 - |z/zu|^n * (w + (1-w)*sgn(xdot*z) + r2*sgn(x*xdot))         (z1: zu, z2: zru)
    dz2/dt also has a relaxation term -z2/tau, so z2 creeps away at quasi-static rates
    (the 0.025 Hz tests are clearly softer than >=0.5 Hz) but acts as friction at speed.

Model "base" = rate-independent (kr = c = m = 0), comparable to GBW+T.
Model "rate" = all terms. Both are fitted only on the training set.

Usage: python gbw_rate.py <training_dir> <verification_dir> <out_dir>
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from numba import njit
from scipy.optimize import least_squares

NPTS, NHARM, NCYC = 256, 30, 4
NAMES = ['ka', 'k2', 'k3', 'kt', 'xt', 'pt', 'kh', 'zu', 'n', 'w', 'r2', 'kr', 'zru', 'tau', 'c', 'm']
LO = [0, -0.05, -0.01, 0, -5, 1.2, 0, 0.02, 0.3, 0, -0.9, 0, 0.02, 0.01, 0, -5]
HI = [0.5, 0.05, 0.01, 0.05, 12, 4, 1, 5, 4, 1, 0.9, 1, 5, 100, 0.01, 5]
P0 = [0.05, -0.003, 1e-4, 0.0024, 0.06, 2, 0.3, 0.42, 0.8, 0.5, 0, 0.1, 0.5, 1, 0, 0.5]
RATE_ONLY = ['kr', 'zru', 'tau', 'c', 'm']


def load_cycle(csv, f_approx):
    """Phase-average a test into one smooth periodic cycle (Fourier fit at a refined frequency)."""
    D = pd.read_csv(csv)
    t, x, F = D.time_s.values, D.disp_centred_mm.values, D.force_centred_kN.values
    n = len(t)
    if (t[-1] - t[0]) * f_approx >= 8:  # skip ramp-in / ramp-out of long dynamic records
        s = slice(int(0.15 * n), int(0.85 * n))
        t, x, F = t[s], x[s], F[s]
    t = t - t[0]
    xc = x - x.mean()
    f = f_approx
    for span in (0.06, 0.004):  # coarse then fine search for the fundamental
        fg = f * (1 + np.linspace(-span, span, 121))
        amp = [abs(np.dot(xc, np.exp(-2j * np.pi * fi * t))) for fi in fg]
        f = fg[int(np.argmax(amp))]
    th = (f * t) % 1.0
    nh = int(min(NHARM, 0.45 / (np.median(np.diff(t)) * f)))  # no harmonics above Nyquist (59/89 Hz tests)
    h = np.arange(1, nh + 1)
    A = np.hstack([np.ones((len(th), 1)), np.cos(2 * np.pi * np.outer(th, h)), np.sin(2 * np.pi * np.outer(th, h))])
    reg = 1e-6 * np.eye(A.shape[1])
    cx = np.linalg.solve(A.T @ A + reg, A.T @ x)
    cf = np.linalg.solve(A.T @ A + reg, A.T @ F)
    g = np.arange(NPTS) / NPTS
    w = 2 * np.pi * f
    C, S = np.cos(2 * np.pi * np.outer(g, h)), np.sin(2 * np.pi * np.outer(g, h))
    a, b = cx[1:nh + 1], cx[nh + 1:]
    xg = cx[0] + C @ a + S @ b
    vg = w * (-S @ (a * h) + C @ (b * h))
    ag = -w * w * (C @ (a * h * h) + S @ (b * h * h))
    Fg = cf[0] + C @ cf[1:nh + 1] + S @ cf[nh + 1:]
    xg -= (xg.max() + xg.min()) / 2
    Fg -= (Fg.max() + Fg.min()) / 2
    return dict(f=f, x=xg, v=vg, a=ag, F=Fg, t_raw=t, x_raw=x, F_raw=F)


@njit(cache=True)
def _dz(z, h, xs, zu, n, w, r2):
    sz = 1.0 if h * z > 0 else -1.0
    sx = 1.0 if xs * h > 0 else -1.0
    return h * (1.0 - abs(z / zu) ** n * (w + (1.0 - w) * sz + r2 * sx))


@njit(cache=True)
def simulate(x, v, a, dt, p, ncyc):
    ka, k2, k3, kt, xt, pt, kh, zu, n, w, r2, kr, zru, tau, c, m = p
    N = len(x)
    out = np.empty(N)
    z1 = 0.0
    z2 = 0.0
    zmin = min(zu, zru) if kr > 0 else zu
    for cyc in range(ncyc):
        for i in range(N):
            xa = x[i - 1] if i > 0 else x[N - 1]
            dx = x[i] - xa
            ns = int(abs(dx) / (0.04 * zmin)) + 1
            if kr > 0:
                ns = max(ns, int(dt / (0.2 * tau)) + 1)
            ns = min(ns, 4000)
            hx = dx / ns
            ht = dt / ns
            for s in range(ns):
                xs = xa + hx * (s + 0.5)
                z1 += _dz(z1, hx, xs, zu, n, w, r2)
                if kr > 0:
                    z2 += _dz(z2, hx, xs, zru, n, w, r2) - z2 / tau * ht
            if cyc == ncyc - 1:
                xi = x[i]
                d = xi - xt
                out[i] = (ka * xi + k2 * xi * xi + k3 * xi ** 3 + (kt * d ** pt if d > 0 else 0.0)
                          + kh * z1 + kr * z2 + c * v[i] + m * 1e-6 * a[i])
    return out


def predict(cyc, p):
    Fm = simulate(cyc['x'], cyc['v'], cyc['a'], 1.0 / (cyc['f'] * NPTS), np.asarray(p, float), NCYC)
    return Fm - (Fm.max() + Fm.min()) / 2


def nrmse(cyc, p):
    return np.sqrt(np.mean((predict(cyc, p) - cyc['F']) ** 2)) / np.sqrt(np.mean(cyc['F'] ** 2))


def fit(cycles, free, p0, starts=4, seed=0):
    idx = [NAMES.index(k) for k in free]
    lo, hi = np.array(LO)[idx], np.array(HI)[idx]

    def res(q):
        p = np.array(p0, float)
        p[idx] = q
        return np.concatenate([(predict(c, p) - c['F']) / np.sqrt(np.mean(c['F'] ** 2)) / np.sqrt(NPTS)
                               for c in cycles])

    rng = np.random.default_rng(seed)
    best = None
    q0 = np.clip(np.array(p0, float)[idx], lo, hi)
    for k in range(starts):
        q = q0 if k == 0 else np.clip(q0 * np.exp(0.5 * rng.standard_normal(len(q0))) + 0.02 * (hi - lo) * rng.standard_normal(len(q0)), lo, hi)
        r = least_squares(res, q, bounds=(lo, hi), x_scale=np.maximum(np.abs(q), 1e-3), max_nfev=600)
        print(f'  start {k}: cost {r.cost:.5f}')
        if best is None or r.cost < best.cost:
            best = r
    p = np.array(p0, float)
    p[idx] = best.x
    return p


def main(tr_dir, ve_dir, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(out, exist_ok=True)
    sets = {}
    for name, d in (('training', tr_dir), ('verification', ve_dir)):
        s = pd.read_csv(f'{d}/summary.csv')
        sets[name] = [(r.test, r.f_test_Hz, load_cycle(f'{d}/{r.test}_centred.csv', r.f_approx_Hz)) for _, r in s.iterrows()]
    train = [c for _, _, c in sets['training']]

    base0 = list(P0)
    for k in RATE_ONLY:
        base0[NAMES.index(k)] = 0.0
    print('fitting base (rate-independent) model')
    p_base = fit(train, [k for k in NAMES if k not in RATE_ONLY], base0)
    print('fitting rate model')
    seed_rate = list(p_base)
    for k in RATE_ONLY:
        seed_rate[NAMES.index(k)] = P0[NAMES.index(k)]
    p_rate = fit(train, NAMES, seed_rate)
    json.dump({'base': dict(zip(NAMES, p_base)), 'rate': dict(zip(NAMES, p_rate))}, open(f'{out}/params.json', 'w'), indent=2)

    rows = []
    for name, tests in sets.items():
        for test, fnom, c in tests:
            rows.append(dict(set=name, test=test, f_Hz=fnom, X_mm=np.ptp(c['x']) / 2,
                             nrmse_base=nrmse(c, p_base), nrmse_rate=nrmse(c, p_rate)))
    T = pd.DataFrame(rows)
    T.to_csv(f'{out}/errors.csv', index=False, float_format='%.4f')
    print('fundamental complex stiffness K\' + iK\'\' (kN/mm), verification:')
    for test, fnom, c in sets['verification']:
        e = np.exp(-2j * np.pi * np.arange(NPTS) / NPTS)
        k = lambda F: np.dot(F, e) / np.dot(c['x'], e)
        print(f'  {test} {fnom:5g} Hz  meas {k(c["F"]):.3f}  base {k(predict(c, p_base)):.3f}  rate {k(predict(c, p_rate)):.3f}')
    print(T.round(3).to_string(index=False))
    print(T.groupby('set')[['nrmse_base', 'nrmse_rate']].mean().round(3))

    for name, tests in sets.items():
        ncol = 5
        nrow = int(np.ceil(len(tests) / ncol))
        fig, axs = plt.subplots(nrow, ncol, figsize=(3.8 * ncol, 3.1 * nrow), squeeze=False)
        for ax, (test, fnom, c) in zip(axs.flat, tests):
            ax.plot(c['x_raw'], c['F_raw'], color='#1f3a5f', lw=0.6, alpha=0.5, label='Measured')
            xx = np.r_[c['x'], c['x'][:1]]
            for p, col, ls, lab in ((p_base, '0.55', '--', 'Rate-indep. GBW+T (refit)'), (p_rate, '#c0504d', '-', 'Rate-dependent GBW+T')):
                ff = predict(c, p)
                ax.plot(xx, np.r_[ff, ff[:1]], color=col, ls=ls, lw=1.4, label=lab)
            e0, e1 = nrmse(c, p_base), nrmse(c, p_rate)
            ax.set_title(f'{test[4:]}  {fnom:g} Hz  ±{np.ptp(c["x"]) / 2:.2f} mm\nNRMSE {e0:.1%} → {e1:.1%}', fontsize=9)
            ax.grid(alpha=0.3)
        for ax in axs.flat[len(tests):]:
            ax.axis('off')
        axs[0, 0].legend(fontsize=7)
        fig.suptitle(f'M6A-219 - {name} tests' + (' (held out, not fitted)' if name == 'verification' else ''))
        fig.supxlabel('Displacement (mm)')
        fig.supylabel('Force, offset removed (kN)')
        fig.tight_layout()
        fig.savefig(f'{out}/{name}_loops.png', dpi=110)


if __name__ == '__main__':
    main(*sys.argv[1:4])
