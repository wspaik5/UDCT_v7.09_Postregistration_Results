# UDCT v7.09 - Post-registration results and reproducibility

**Positive global virial work with local Jeans obstructions**  
Won Shik Paik, independent researcher, Auckland, New Zealand  
Post-registration numerical report, 4 October 2026

This repository reproduces the calculations reported in *Positive global virial work with local Jeans obstructions: Results of the UDCT v7.09 registered GQUMOND example-A test in three ultra-faint dwarfs*. It preserves the original v7.09 implementation and v7.06 dependency byte-for-byte. A new runner executes their frozen routines, checks the registered decision, localizes the Hydrus I central pressure problems, and records numerical/environment information.

## Scientific status

The test concerns the specified GQUMOND example structure, **not a new UDCT constitutive law**. Density and Galactic field are prescribed; no coupled matter-field evolution, bidirectional projection, or dynamical back-reaction is simulated.

- Three objects × two stellar profiles × six screening lengths = **36 GQUMOND cases**.
- Six QUMOND controls, one per object/profile pair.
- Registered default and smoke grids: **Outcome B**. All 42 global virial values are positive, and their signs agree.
- Hydrus I / tapered cusp: negative conditional isotropic Jeans pressure at screening lengths **1, 3 and 10 pc**.
- At **10 pc**, this profile also has outward mean force and negative effective enclosed mass in the registered diagnostic interval, **0.1-10 rh**.
- The 1 and 3 pc outward-force regions lie below 0.1 rh. Their central pressure failure is detected by the Jeans calculation even though the registered in-range force flag is false.
- Positive global virial work is not proof of physical local equilibrium or agreement with observed velocity dispersions.

This result does not cancel the older v7.06 candidate's recorded static-equilibrium problems. It does not establish a unique cause of those problems, make the operation `Q = integral(nu dz)` inherently defective, validate MOND generally, or reject/confirm bidirectional projection. It shows that negative global work is **not inevitable merely because an action-derived Hessian term is present**, within the tested protocol. The historical O8d 0/22 gate is not rerun or reopened.

## Files

| File | Purpose |
|---|---|
| `UDCT_v7_09_Postregistration_reproduce.py` | New report-reproduction runner. |
| `UDCT_v7_09_Preregistration_GQUMOND_Example_A_Virial_Test_run.py` | Unchanged original v7.09 implementation. |
| `UDCT_v7_06_Hessian_Term_Sign_Audit_reproduce.py` | Unchanged frozen v7.06 dependency. |
| `requirements.txt` | NumPy/SciPy versions used for package validation. |
| `reference/registered.json` | Previously computed registered default + smoke outputs. |
| `reference/refined.json` | Previously computed supplementary refined-grid outputs. |
| `reference/local_check.json` | Previously computed default + refined central-band diagnostics. |
| `README.md` | Scope, instructions, results and interpretation. |
| `LICENSE.txt` | MIT license for code and README. |
| `.gitattributes` | Prevent line-ending conversion of hash-identified Python sources. |
| `.gitignore` | Ignore environment, cache and generated results. |

**Extract the ZIP and upload its contents to GitHub, preserving the `reference/` folder.** The new runner requires both original scripts next to it. Do not upload only the runner. If using the existing v7.09 repository, preserve the preregistration PDF and original scripts; this README can document the new post-registration status.

## Installation

Python 3.11 or newer is required by the pinned dependencies; package validation used Python 3.12.14. NumPy and SciPy are required. No downloaded astronomical dataset, credential or internet connection is needed during calculation.

```bash
python -m venv .venv
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install:

```bash
python -m pip install -r requirements.txt
```

## Reproduce the registered result

From the extracted repository directory:

```bash
python UDCT_v7_09_Postregistration_reproduce.py
```

The runner first verifies both source hashes and runs the original analytic/geometry self-tests. It then computes all 42 cases on **both registered grids**, checks the sign-convergence gate, compares global virial values and diagnostic sign flags to supplied reference outputs, and evaluates the default-grid Hydrus I central diagnostics.

Expected completion message: `Outcome B reproduced; results: ...`

## Reproduce the supplementary refined-grid results

```bash
python UDCT_v7_09_Postregistration_reproduce.py --refined --output-dir results_full
```

This also computes all 42 cases on the refined grid and localizes Hydrus I's negative-pressure bands on that grid. This is a **post-registration check**, not a replacement of the registered grids or a new decision criterion. The full paper's default + refined local-band table requires this command.

The code refuses a nonempty output directory by default. Use a fresh `--output-dir`, or explicitly use `--overwrite` to replace result files. The bundled `reference/` directory is protected. Running time depends on hardware and BLAS threading; refined runs need more memory and work than the registered grids.

Optionally limit BLAS threading on Linux/macOS, as used in validation:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python UDCT_v7_09_Postregistration_reproduce.py --refined --output-dir results_full
```

## Generated outputs

| Output | Meaning |
|---|---|
| `selftest.txt` | Original analytic and geometry self-test log. |
| `registered.json` | Full registered-grid numerical outputs and decision. |
| `refined.json` | Supplementary high-resolution output; only with `--refined`. |
| `local_check.json` | Sampled negative force/pressure intervals and minima. |
| `environment.json` | Python, platform, NumPy/SciPy versions, source hashes, reference comparison. |
| `summary.md` | Readable result summary and six-row virial table. |

The original implementation labels a custom refined run `runs.default`; inspect its actual `grid` values to distinguish it from the registered default. The runner preserves this original JSON schema. Reference comparison tolerates relative global virial differences up to `1e-5`, with exact agreement required for the reported sign flags. This is a software regression tolerance, **not an uncertainty estimate for the physical model**. A missing reference folder is reported in the environment output; calculations still run, but comparison is unavailable.

## Main numerical values

Default-grid normalized work `V/VN`; GQUMOND range spans screening lengths 0.03, 0.1, 0.3, 1, 3 and 10 pc.

| Object | Profile | QUMOND | GQUMOND min | GQUMOND max |
|---|---|---:|---:|---:|
| Leo IV | Plummer | 14.014605 | 13.864456 | 14.014603 |
| Leo IV | Tapered cusp | 13.896448 | 13.480055 | 13.896442 |
| Pegasus III | Plummer | 19.373652 | 19.057039 | 19.373649 |
| Pegasus III | Tapered cusp | 19.217916 | 18.461326 | 19.217905 |
| Hydrus I | Plummer | 3.994097 | 3.900006 | 3.994096 |
| Hydrus I | Tapered cusp | 3.556883 | 3.153367 | 3.556879 |

| Grid | Radial | Polar × azimuth | Galactic disk R × azimuth × height |
|---|---:|---:|---:|
| Smoke | 180 | 16 × 24 | 40 × 24 × 8 |
| Default | 360 | 24 × 36 | 120 × 64 × 12 |
| Refined (supplementary) | 720 | 48 × 72 | 240 × 128 × 24 |

Maximum relative global virial differences in the report: default-smoke `9.42e-7`; default-refined `5.57e-8`. The refined direct-force versus integration-by-parts cross-check differs by at most `2.90e-6` relatively. These are numerical consistency checks, not physical-model error bars.

Hydrus I / tapered cusp, supplementary refined grid:

| Screening length (pc) | Minimum sigma_r^2 (km^2/s^2) | Sampled negative-pressure r/rh | Sampled outward-force r/rh |
|---:|---:|---:|---:|
| 1 | -0.113062 | 0.002-0.00470 | 0.002-0.01199 |
| 3 | -0.435382 | 0.002-0.01837 | 0.002-0.03709 |
| 10 | -1.571442 | 0.002-0.08475 | 0.002-0.13351 |

These are sampled bounds, not fitted roots. The lower mesh limit is `0.002 rh`; the 1 pc minimum occurs at that limit and no smaller-radius extrapolation is asserted. At 10 pc the minimum effective mass in the registered interval is approximately -721 solar masses (default), -700 (smoke), and -705 (refined). Its sign is stable; its sampled magnitude has about 3% registered-grid variation.

A negative local variance is not a physical dispersion. Positive formal aperture RMS values from a negative-pressure solution must not be treated as valid observed-velocity predictions. Negative effective mass is a static diagnostic here, not a stellar-ejection trajectory.

## Frozen assumptions and decision

The scalar function is `P = f(u) Q(Z/f)`, `f(u) = u/(1+u)`, with `Q'(w) = sqrt(1+w^(-1/2))` and `Q(0)=0`. This fixes one campaign function choice within Milgrom's example structure. Both leading and action-derived Hessian sources are retained. The control uses `f=1`.

The acceleration scale is `1.082401e-10 m/s^2`; stellar M/L is 2. Plummer and tapered cusp profiles use frozen object inputs. The visible Galactic disks and bulge supply a local second-order Taylor field. No dark halo, LMC potential or time evolution is included. Jeans calculations are conditional spherical isotropic integrals with zero outer radial pressure. No fitting or post-outcome retuning is performed.

- A: at least one negative GQUMOND global virial case with positive controls.
- B: all 36 GQUMOND global virial cases positive.
- C: a negative QUMOND control triggers a protocol-validity concern.

Sign claims require agreement on the registered default and smoke grids. No reported case triggers the more-than-tenfold outward-force warning within `0.1-10 rh`, so the registered conditional `5 rh` truncation follow-up is not activated.

## Original-script commands and hashes

The runner is a convenience layer. The registered calculation can also be executed directly:

```bash
python UDCT_v7_09_Preregistration_GQUMOND_Example_A_Virial_Test_run.py --selftest
python UDCT_v7_09_Preregistration_GQUMOND_Example_A_Virial_Test_run.py --mode all --convergence > registered.json
```

Frozen full SHA-256 hashes:

```text
v7.09: 7dc3b908c20bdda90ec91da9f4a687b3e96e4eee2c817920ced2cc3315762dbf
v7.06: a64440e1350ae8bf10eb3188ec34829b6d586abf275de5cdc841a50ad3478284
```

Preserve exact bytes. The original source's “not yet run” statement describes its preregistration/deposit-time status; it is deliberately not edited. This README and the new runner document the subsequent execution. Both scripts are required despite their different version labels. Source changes, including line-ending conversion, invalidate the exact-hash reproduction path.

## References and licensing

- v7.09 preregistration: https://doi.org/10.5281/zenodo.23120660
- v7.06 verification note: https://doi.org/10.5281/zenodo.23039754
- Milgrom, *Generalizations of Quasilinear MOND (QUMOND)*, Physical Review D 108, 084005 (2023): https://doi.org/10.1103/PhysRevD.108.084005 ; https://arxiv.org/abs/2305.01589
- Existing v7.09 repository: https://github.com/wspaik5/UDCT_v7.09_Preregistration_GQUMOND_Example_A_Virial_Test

Code and README: MIT License, copyright (c) 2026 Won Shik Paik. The original preregistration PDF is separately licensed CC BY 4.0; it is not included in this code bundle. Numerical execution, packaging and documentation were assisted by OpenAI Codex. This is a reproducible independent research record, not peer review.
