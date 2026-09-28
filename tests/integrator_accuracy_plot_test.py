import numpy as np
from weapons.parameters import Musket
from physics.integrators import euler_step, rk4_step
from physics.forces import WindModel
from simulation.single_shot import run_single_shot
import matplotlib.pyplot as plt

wind = WindModel(base_wind=np.array([0.0, 0.0, 0.0]))
musket = Musket()
launch_angles_deg = [45]
launch_angle_deg = launch_angles_deg[0]

reference_log = run_single_shot(musket, launch_angle_deg, dt=0.0001,
                                 integrator_fn=rk4_step, wind_model=wind)
reference_range = reference_log[-1]["position"][0]

dt_values = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
results = []
for dt in dt_values:
    rk4_log = run_single_shot(musket, launch_angle_deg, dt, integrator_fn=rk4_step, wind_model=wind)
    euler_log = run_single_shot(musket, launch_angle_deg, dt, integrator_fn=euler_step, wind_model=wind)

    rk4_range = rk4_log[-1]["position"][0]
    euler_range = euler_log[-1]["position"][0]

    results.append({
        "dt": dt,
        "rk4_error": abs(rk4_range - reference_range),
        "euler_error": abs(euler_range - reference_range)
    })
rk4_errors = [r["rk4_error"] for r in results]
euler_errors = [r["euler_error"] for r in results]

plt.figure()
plt.loglog(dt_values, rk4_errors, marker='o', label='RK4')
plt.loglog(dt_values, euler_errors, marker='o', label='Euler')
plt.xlabel('dt (s)')
plt.ylabel('Range error (m)')
plt.title('Integrator error vs. timestep size')
plt.legend()
plt.grid(True, which='both', ls='--', alpha=0.5)
plt.savefig('integrator_comparison.png')
plt.show()