import matplotlib.pyplot as plt

dt_values = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
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