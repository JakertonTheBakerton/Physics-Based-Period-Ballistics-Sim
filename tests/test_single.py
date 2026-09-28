import numpy as np
from weapons.parameters import Musket
from physics.integrators import euler_step, rk4_step
from physics.forces import WindModel
from simulation.single_shot import run_single_shot

wind = WindModel(base_wind=np.array([0.0, 0.0, 0.0]))
musket = Musket()
launch_angle_deg = 45

# reference: fine RK4 run, established once, before the sweep
reference_log = run_single_shot(musket, launch_angle_deg, dt=0.0001,
                                 integrator_fn=rk4_step, wind_model=wind)
reference_range = reference_log[-1]["position"][0]
print("reference range:", reference_range)

rk4_results = []
euler_results = []
dt = 0.001
for i in range(6):
    log_rk4 = run_single_shot(musket, launch_angle_deg, dt,
                            integrator_fn=rk4_step, wind_model=wind)
    rk4_range = log_rk4[-1]["position"][0]
    rk4_results.append({"dt": dt, "range": rk4_range, "error": abs(rk4_range - reference_range)})

    log_euler = run_single_shot(musket, launch_angle_deg, dt,
                              integrator_fn=euler_step, wind_model=wind)
    euler_range = log_euler[-1]["position"][0]
    euler_results.append({"dt": dt, "range": euler_range, "error": abs(euler_range - reference_range)})

    if i % 2 == 0:
        dt = dt * 5
    else:
        dt = dt * 2

for r in rk4_results:
    print("RK4:", r)
for r in euler_results:
    print("Euler:", r)