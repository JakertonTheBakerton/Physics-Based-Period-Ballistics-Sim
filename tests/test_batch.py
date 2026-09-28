import numpy as np
from weapons.parameters import Musket
from physics.integrators import rk4_step
from physics.forces import WindModel
from simulation.batch import run_batch_shot
from simulation.single_shot import run_single_shot

wind = WindModel(base_wind=np.array([0.0, 0.0, 0.0]))
musket = Musket()
launch_angles_deg = [10, 15, 25, 30, 45]
dt = 0.001

batch_positions = run_batch_shot(musket, launch_angles_deg, dt,
                                  integrator_fn=rk4_step, wind_model=wind)
batch_ranges = batch_positions[:, 0]

single_ranges = []
for angle in launch_angles_deg:
    log = run_single_shot(musket, angle, dt, integrator_fn=rk4_step, wind_model=wind)
    single_ranges.append(log[-1]["position"][0])

for angle, batch_r, single_r in zip(launch_angles_deg, batch_ranges, single_ranges):
    diff = abs(batch_r - single_r)
    print(f"angle={angle}: batch={batch_r:.4f}, single={single_r:.4f}, diff={diff:.6f}")