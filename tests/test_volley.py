import numpy as np
from weapons.parameters import Musket
from physics.integrators import rk4_step
from physics.forces import WindModel
from simulation.batch import run_batch_shot
from simulation.single_shot import run_single_shot
from simulation.volley import run_volley_shot

musket = Musket()
launch_angles_deg = [30]
launch_angle_deg = launch_angles_deg[0]
dt = 0.001

def fresh_wind():
    return WindModel(base_wind=np.array([2.0, 0.0, 0.0]), gust_std=0.5, rng=np.random.default_rng(seed=42))

wind = fresh_wind()
volley_positions = run_volley_shot(musket, launch_angle_deg, dt, integrator_fn=rk4_step, wind_model=wind, n_shooters = 20)
volley_ranges = volley_positions[:,0]

wind = fresh_wind()
batch_positions = run_batch_shot(musket, launch_angles_deg, dt, integrator_fn=rk4_step, wind_model=wind)
batch_ranges = batch_positions[:, 0]

wind = fresh_wind()
single_ranges = []
for angle in launch_angles_deg:
    log = run_single_shot(musket, angle, dt, integrator_fn=rk4_step, wind_model=wind)
    single_ranges.append(log[-1]["position"][0])
print('single done')

for angle, batch_r, single_r in zip(launch_angles_deg, batch_ranges, single_ranges):
    diff_b = abs(batch_r - single_r)
    print(f"angle={angle}: batch={batch_r:.4f}, single={single_r:.4f}, diff={diff_b:.6f}")
print('batch done')

print("Volley ranges:", volley_ranges)
print("Volley mean range:", np.mean(volley_ranges))
print("Volley std dev:", np.std(volley_ranges))
print("Single-shot (no wind) reference range:", single_ranges[0])