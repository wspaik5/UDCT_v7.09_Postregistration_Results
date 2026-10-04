#!/usr/bin/env python3
"""Reproduce the v7.09 post-registration report without changing frozen laws.
Copyright (c) 2026 Won Shik Paik. MIT License; see LICENSE.txt.
"""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FROZEN = {
    'UDCT_v7_09_Preregistration_GQUMOND_Example_A_Virial_Test_run.py':
    '7dc3b908c20bdda90ec91da9f4a687b3e96e4eee2c817920ced2cc3315762dbf',
    'UDCT_v7_06_Hessian_Term_Sign_Audit_reproduce.py':
    'a64440e1350ae8bf10eb3188ec34829b6d586abf275de5cdc841a50ad3478284',
}
REFINED = dict(radial=720, polar=48, azimuth=72,
               disk_radial=240, disk_azimuth=128, disk_height=24)

def load_model():
    for name, expected in FROZEN.items():
        path = ROOT / name
        if not path.is_file():
            raise RuntimeError(f'Missing dependency: {name}. Extract the complete ZIP.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Frozen file hash mismatch: {name}; restore original bytes.')
    spec = importlib.util.spec_from_file_location('udct_v709_registered', ROOT / next(iter(FROZEN)))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # The frozen dependency supports an environment override; require the same bytes here.
    if module.V706_SHA256 != FROZEN['UDCT_v7_06_Hessian_Term_Sign_Audit_reproduce.py']:
        raise RuntimeError('Environment override loaded a different dependency.')
    return module

def arguments(convergence, overrides=None):
    values = dict(mode='all', object='all', ell0=None, smoke=False, convergence=convergence)
    values.update({k: None for k in REFINED})
    values.update(overrides or {})
    return argparse.Namespace(**values)

def cases(run):
    for r in run['outputs']:
        yield (r['object'], r['profile'], 'control'), r['control_qumond']
        for ell, x in r['gqumond'].items():
            yield (r['object'], r['profile'], ell), x

def compare_reference(actual, filename):
    path = ROOT / 'reference' / filename
    if not path.is_file():
        return {'available': False, 'matched': None}
    expected = json.loads(path.read_text())
    errors = []
    for label, run in actual['runs'].items():
        ref = dict(cases(expected['runs'][label]))
        for key, x in cases(run):
            y = ref[key]
            error = abs(x['virial'] - y['virial']) / abs(y['virial'])
            errors.append(error)
            if error > 1e-5:
                raise RuntimeError(f'Reference virial mismatch: {label}, {key}, rel={error:g}')
            for flag in ('meff_negative', 'force_negative_in_range'):
                if x[flag] != y[flag]:
                    raise RuntimeError(f'Reference sign mismatch: {label}, {key}, {flag}')
            if x['jeans']['has_negative_pressure'] != y['jeans']['has_negative_pressure']:
                raise RuntimeError(f'Reference pressure flag mismatch: {label}, {key}')
    return {'available': True, 'matched': True, 'max_relative_virial_error': max(errors),
            'relative_tolerance': 1e-5, 'note': 'Regression tolerance, not physical uncertainty.'}

def local_check(m, label, grid):
    import numpy as np
    obj = m.DWARFS['Hydrus I']
    e, h, _ = m.V706.galactic_field(obj, grid)
    out = []
    for ell in (1., 3., 10.):
        st = m.model_state(obj, 'Tapered cusp', m.mesh('Tapered cusp', grid), e, h, grid, ell)
        work, force = m.V706.work_from_state(st)
        _, sigma2 = m.V706.aperture_jeans(st, force, obj.re_pc)
        x = st['r'] / st['rh']
        def bounds(mask):
            return [float(x[mask].min()), float(x[mask].max())] if mask.any() else None
        out.append(dict(grid=label, ell_pc=ell, negative_force_r_rh=bounds(force < 0),
                        negative_sigma2_r_rh=bounds(sigma2 < 0),
                        min_sigma2_kms2=float(sigma2.min() / 1e6),
                        min_sigma2_r_rh=float(x[sigma2.argmin()]),
                        virial=work['virial'], direct_virial=work['direct']))
    return out

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refined', action='store_true', help='Also run supplementary high-resolution grid.')
    parser.add_argument('--output-dir', type=Path, default=Path('results'))
    parser.add_argument('--overwrite', action='store_true', help='Replace outputs in an existing output directory.')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out == (ROOT / 'reference').resolve():
        parser.error('Reference output directory is protected.')
    if out.exists() and any(out.iterdir()) and not args.overwrite:
        parser.error('Output directory is not empty. Choose a new directory or use --overwrite.')
    out.mkdir(parents=True, exist_ok=True)
    m = load_model()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        status = m.selftest()
    (out / 'selftest.txt').write_text(log.getvalue(), encoding='utf-8')
    if status != 0:
        raise RuntimeError('Analytic/geometry self-test failed. See selftest.txt.')
    print('Self-tests passed. Running all 42 cases on default and smoke grids...', flush=True)
    registered = m.run(arguments(True))
    write_json(out / 'registered.json', registered)
    if not registered['convergence']['claim_allowed']:
        raise RuntimeError('Registered sign-convergence gate was not satisfied.')
    for label, run in registered['runs'].items():
        if run['outcome']['outcome'] != 'B':
            raise RuntimeError(f'Unexpected registered outcome on {label}; inspect raw results.')
    comparisons = {'registered': compare_reference(registered, 'registered.json')}
    local = local_check(m, 'default', m.make_grid(False, {}))
    if args.refined:
        print('Running supplementary refined grid (not a new registered gate)...', flush=True)
        refined = m.run(arguments(False, REFINED))
        write_json(out / 'refined.json', refined)
        if refined['runs']['default']['outcome']['outcome'] != 'B':
            raise RuntimeError('Refined-grid outcome differs; inspect raw results.')
        comparisons['refined'] = compare_reference(refined, 'refined.json')
        local += local_check(m, 'highres', m.make_grid(False, REFINED))
    write_json(out / 'local_check.json', local)
    import numpy, scipy
    write_json(out / 'environment.json', dict(python=sys.version, platform=platform.platform(),
               numpy=numpy.__version__, scipy=scipy.__version__, frozen_sha256=FROZEN,
               runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               supplementary_refined=args.refined, reference_comparison=comparisons))
    rows = ['# Reproduced v7.09 result', '', 'Primary outcome: **B**, with registered-grid sign agreement.',
            '', '36 GQUMOND cases and six controls have positive global virial work.',
            'Hydrus I tapered-cusp cases at 1, 3 and 10 pc have negative conditional Jeans pressure.',
            'At 10 pc, negative effective mass occurs within the registered 0.1-10 rh interval.',
            '', '| Object | Profile | QUMOND V/VN | GQUMOND min | GQUMOND max |',
            '|---|---|---:|---:|---:|']
    for r in registered['runs']['default']['outputs']:
        vals = [x['virial'] for x in r['gqumond'].values()]
        rows.append(f"| {r['object']} | {r['profile']} | {r['control_qumond']['virial']:.6f} | {min(vals):.6f} | {max(vals):.6f} |")
    rows += ['', 'This is a static diagnostic, not coupled dynamical evolution, observed-data validation,',
             'or an adjudication of bidirectional projection. Earlier v7.06 problems are not cancelled.']
    (out / 'summary.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'Outcome B reproduced; results: {out}', flush=True)
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError) as exc:
        print(f'Reproduction failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
