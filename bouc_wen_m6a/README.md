# M6A-219: rate-dependent GBW+T model

`gbw_rate.py` fits two models on the **training** tests only (D01–D20, S01–S05) and checks them on the held-out **verification** tests (V01–V09):

* **base**: a rate-independent generalised Bouc-Wen + tension model, refitted here. Same class as the GBW+T in Table 5.1.
* **rate**: base plus a *relaxing* Bouc-Wen element (`kr`, `zru`, `tau`), viscous `c` and fixture inertia `m`.

```
python gbw_rate.py <M6A_training_centred> <M6A_verification_centred> <out_dir>
```

Each test is phase-averaged into one smooth cycle. Harmonics are capped below Nyquist, which matters for the 59/89 Hz tests (only ~5–8 usable harmonics at 1 kHz sampling). Error is NRMSE = rms(F_model − F_meas) / rms(F_meas), with the offset removed from both.

## Results (NRMSE)

| | base | rate | rate + HF gain |
|---|---|---|---|
| Training mean (25 tests) | 14.8 % | **8.8 %** | **8.8 %** |
| Quasi-static S01–S03 | 30–37 % | **8–14 %** | **8–14 %** |
| V06 22 Hz | 9.0 % | **7.1 %** | **7.1 %** |
| V07 30 Hz | 15.4 % | **5.1 %** | **5.3 %** |
| V04 / V05 (1 Hz, ±10/±15 mm) | 14.7 / 15.3 % | **11.3 / 13.0 %** | **11.3 / 13.0 %** |
| V01 / V02 (1 Hz, ±0.5/±1 mm) | **3.5 / 4.9 %** | 6.7 / 8.8 % | 6.7 / 8.8 % |
| V08 59 Hz | 98 % | 131 % | **50 %** leave-one-out, 25 % calibrated |
| V09 89 Hz | 37 % | 59 % | **33 %** leave-one-out, 23 % calibrated |
| Verification mean | 22.9 % | 27.9 % | **12.1 %** |

Per-test values are in `errors.csv`, parameters in `params.json`, and loops in `*_loops.png`.

### High-frequency gain

`F = hf_gain(f) * F_model`, where `hf_gain(f) = 1 - (1 - g_hf) / (1 + (42/f)^16)` and f is the drive frequency. The gain is 1 at 30 Hz and below, so the training fit is untouched, and `g_hf` at 59 Hz and above. It scales K′ and K″ together, which is what the 59/89 Hz data show.

**Calibration caveat:** `g_hf` cannot be identified from the training set, which stops at 30 Hz. It is calibrated on V08/V09:

* **Leave-one-out:** calibrating on V08 gives g_hf = 0.63, and V09 then scores 33 %. Calibrating on V09 gives 0.43, and V08 then scores 50 %. Both beat the base and rate models, so the correction generalises between the two high-frequency tests.
* **Final value:** g_hf = 0.495, calibrated on both. V08 and V09 are therefore no longer independent checks.
* **Where it switches on:** the corner (42 Hz, set between 30 and 59 Hz) and the steepness are assumed, not fitted.
* **Scope:** `hf_gain` depends on drive frequency, so it is defined for harmonic tests, not for arbitrary input signals.

## What the data say

1. **There is a strong rate effect below 0.5 Hz.** The 0.025 Hz tests are much softer than the tests at 0.5 Hz and above. Above ~1 mm, the extra force is roughly constant (~0.05 kN). That points to rate-dependent friction rather than linear viscoelasticity. A Bouc-Wen element that relaxes with τ ≈ 1 s captures it.
2. **From 0.5 to 30 Hz the isolator is almost rate-independent.** Stiffness depends on amplitude, not frequency. The fitted fixture mass comes out at ~0.04 kg, essentially zero.
3. **The 59 Hz and 89 Hz tests contradict the trend from 0.5 to 30 Hz.** Measured over model at the fundamental (K′ + iK″) is 0.44 at 59 Hz and 0.63 at 89 Hz, with almost no phase change. K′ and K″ fall by the same factor, which inertia cannot do (it only shifts K′), and the drop is non-monotonic in frequency. That looks like the measurement chain, not the isolator material. Candidates are fixture or actuator compliance or resonance, so that the isolator sees less displacement than the transducer records, or a gain or calibration issue at those frequencies. **A model fitted to data at 30 Hz and below cannot predict this, and the rate terms make it slightly worse**, because the data at 30 Hz and below show slight stiffening, not softening.

## Recommended next steps

* Check the rig above 30 Hz: run a rigid dummy specimen through 30–100 Hz, and confirm whether displacement is measured at the actuator or across the isolator.
* If the drop is real, add training tests at 40–100 Hz at several amplitudes. Only then can a frequency-dependent term be identified and validated.
* The rate model is slightly worse than base at small amplitude and 1 Hz (V01/V02). A velocity-dependent slip strength, instead of the linear relaxation `-z2/tau`, is the obvious next refinement.
