# Period Ballistics Simulator

A 3D projectile simulator for 17th/18th century weapons: muskets, flintlock pistols, crossbows and longbows. The project focuses on two questions:

1. **Accuracy vs. cost:** how much does a higher-order integrator (RK4) buy over Euler, and at what step size does each break down?
2. **Performance:** how far can vectorised NumPy simulation push volley fire (many shooters at once) compared with looping over single shots?

## Features

- Full 3D trajectories, including lateral wind drift
- Dynamic air density and wind variation (not constant)
- Shape-dependent drag: sphere (musket/pistol balls), cylinder (crossbow bolts), fletched arrow
- Euler and RK4 integrators sharing one derivative function
- Single-shot, batch (angle sweep) and volley simulation
- Period weapon parameters as dataclasses, with sources documented

## Weapon parameters

| Weapon | Projectile Mass | Muzzle velocity | Diameter | Source |
|---|---|---|---|---|
| Musket | 17.4 g | 450 m/s | 14 mm | Dug-bullet records, colchestertreasurehunting.co.uk |
| Pistol | 14.5 g | 385 m/s | 13.5 mm | Dug-bullet records, colchestertreasurehunting.co.uk |
| Crossbow | 60 g | 75 m/s | 9 mm | **Estimate** (no reliable period bolt data found) |
| Bow | 102 g | 47.23 m/s | 11 mm shaft | Soar, Gibbs, Jury & Stretton (2010) chronographed test of a 144 lbf yew bow; arrow diameter cross-referenced with Mary Rose data |

Estimated values are labelled as such in the docstrings rather than presented as sourced data. The bow's fletching area (0.0108 m²) is also an unsourced estimate.

## Results so far

### Euler vs. RK4

Step sizes `dt` in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5] s were compared against an RK4 reference run at `dt = 0.0001`.

- **Euler** error grows roughly linearly with `dt`, from 0.155 m to 124.7 m.
- **RK4** error stays flat at roughly 0.008-0.017 m until `dt = 0.5`, where it jumps to 2.58 m.

This matches the expected O(dt) vs. O(dt⁴) scaling. See `integrator_comparison.png` (log-log plot).

### Batch vs. single shot

The vectorised batch simulator matches the single-shot simulator to floating-point precision across five test angles (10°, 15°, 25°, 30°, 45°) with zero wind.

### Volley simulation

20 shooters at a 30° launch angle with `gust_std = 0.5`: the volley's mean range matched the windless single-shot reference almost exactly, with a range standard deviation of about 5 cm. This is the physically expected scale of variance from wind and shooter position alone.

## Notes and oddities

- **RK4's flat error is a noise floor.** The 0.008-0.017 m RK4 error is dominated by reference and floating-point noise, not by RK4 truncation error. The curve is flat because the method is already more accurate than the reference can resolve.
- **Volley variance has no random human-error term.** Spread comes only from per-shooter wind gusts and each shooter's position along a line formation (offset along y). Real volleys would scatter more.
- **All shooters share one launch angle** in the volley simulation.
- **Landed projectiles are frozen, not removed.** In batch mode each projectile is masked once it lands, so it stops integrating while the rest of the array continues.
- **`Projectile` is not batch-capable by design.** Batch and volley code operate on raw `(N, 3)` arrays instead, which keeps the vectorised path simple and fast.
- **Type annotations:** `muzzle_vel_ms` is annotated `int` on Musket/Pistol/Crossbow but holds a float for the Bow (47.23). This is left as-is.
- **Crossbow figures are the weakest data** in the project (estimate only).

## Project structure

```
physics/          forces.py, integrators.py, projectile.py
weapons/          parameters.py
simulation/       single_shot.py, batch.py, volley.py
analysis/
visualisation/
test_generic.py
requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/Scripts/activate    # Git Bash on Windows
pip install -r requirements.txt
```

## Status

Phases 1, 2, 3, 4 and 5 are complete (physics foundation, weapon parameters, RK4 accuracy comparison, batch simulation, volley simulation).

Remaining: optimal-angle sweep, visualisation, and final polish.

## License

TBD

###Note:
References are incomplete
