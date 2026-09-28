import csv
import numpy as np
from weapons import parameters as param
from physics.integrators import rk4_step
from physics.forces import WindModel
from simulation.batch import run_batch_shot
import matplotlib.pyplot as plt

wind = WindModel(base_wind=np.array([0.0, 0.0, 0.0]))
weapon = param.Bow()
dt = 0.001
coarse_angles = np.arange(0, 91, 5)  # 0, 5, 10, ..., 90 — 19 angles
coarse_positions = run_batch_shot(weapon, coarse_angles.tolist(), dt, integrator_fn=rk4_step, wind_model=wind)
coarse_ranges = coarse_positions[:, 0]
best_index = np.argmax(coarse_ranges)
best_coarse_angle = coarse_angles[best_index]
print(f'best coarse angle: {best_coarse_angle}°')
fine_angles = np.arange(best_coarse_angle - 5, best_coarse_angle + 5 + 0.1, 0.1)
fine_positions = run_batch_shot(weapon, fine_angles.tolist(), dt, integrator_fn=rk4_step, wind_model=wind)
fine_ranges = fine_positions[:, 0]

best_fine_index = np.argmax(fine_ranges)
optimal_angle = fine_angles[best_fine_index]
optimal_range = fine_ranges[best_fine_index]
print(f'optimal angle is: {round(optimal_angle, 2)}°')
with open('analysis/findings.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Optimal Angle of Fire', 'Bow', round(optimal_angle, 2)])