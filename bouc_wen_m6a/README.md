# M6A-219: rate-dependent GBW+T model

`gbw_rate.py` fits two models on the **training** tests only (D01–D20, S01–S05) and checks them on the held-out **verification** tests (V01–V09):

* **base**: a rate-independent generalised Bouc-Wen + tension model, refitted here. Same class as the GBW+T in Table 5.1.
* **rate**: base plus a *relaxing* Bouc-Wen element (`kr`, `zru`, `tau`), viscous `c` and fixture inertia `m`.

```
python gbw_rate.py <M6A_training_centred> <M6A_verification_centred> <out_dir>
```

Each test is phase-averaged into one smooth cycle. Harmonics are capped below Nyquist, which matters for the 59/89 Hz tests (only ~5–8 usable harmonics at 1 kHz sampling). Error is NRMSE = rms(F_model − F_meas) / rms(F_meas), with the offset removed from both.

## Results (NRMSE)

| | base | rate |
|---|---|---|
| Training mean (25 tests) | 14.8 % | **8.8 %** |
| Quasi-static S01–S03 | 30–37 % | **8–14 %** |
| V06 22 Hz | 9.0 % | **7.1 %** |
| V07 30 Hz | 15.4 % | **5.1 %** |
| V04 / V05 (1 Hz, ±10/±15 mm) | 14.7 / 15.3 % | **11.3 / 13.0 %** |
| V01 / V02 (1 Hz, ±0.5/±1 mm) | **3.5 / 4.9 %** | 6.7 / 8.8 % |
| V08 59 Hz | 98 % | 131 % |
| V09 89 Hz | 37 % | 59 % |

Per-test values are in `errors.csv`, parameters in `params.json`, and loops in `*_loops.png`.

## What the data say

1. **There is a strong rate effect below 0.5 Hz.** The 0.025 Hz tests are much softer than the tests at 0.5 Hz and above. Above ~1 mm, the extra force is roughly constant (~0.05 kN). That points to rate-dependent friction rather than linear viscoelasticity. A Bouc-Wen element that relaxes with τ ≈ 1 s captures it.
2. **From 0.5 to 30 Hz the isolator is almost rate-independent.** Stiffness depends on amplitude, not frequency. The fitted fixture mass comes out at ~0.04 kg, essentially zero.
3. **The 59 Hz and 89 Hz tests contradict the trend from 0.5 to 30 Hz.** Measured over model at the fundamental (K′ + iK″) is 0.44 at 59 Hz and 0.63 at 89 Hz, with almost no phase change. K′ and K″ fall by the same factor, which inertia cannot do (it only shifts K′), and the drop is non-monotonic in frequency. That looks like the measurement chain, not the isolator material. Candidates are fixture or actuator compliance or resonance, so that the isolator sees less displacement than the transducer records, or a gain or calibration issue at those frequencies. **A model fitted to data at 30 Hz and below cannot predict this, and the rate terms make it slightly worse**, because the data at 30 Hz and below show slight stiffening, not softening.

## Recommended next steps

* Check the rig above 30 Hz: run a rigid dummy specimen through 30–100 Hz, and confirm whether displacement is measured at the actuator or across the isolator.
* If the drop is real, add training tests at 40–100 Hz at several amplitudes. Only then can a frequency-dependent term be identified and validated.
* The rate model is slightly worse than base at small amplitude and 1 Hz (V01/V02). A velocity-dependent slip strength, instead of the linear relaxation `-z2/tau`, is the obvious next refinement.
