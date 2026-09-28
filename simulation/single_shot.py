import math
import numpy as np
from physics import projectile

def run_single_shot(weapon, launch_angle_deg, dt, integrator_fn, wind_model):
    speed = weapon.muzzle_vel_ms
    launch_angle_rad = math.radians(launch_angle_deg)
    vx = speed * math.cos(launch_angle_rad)
    vz = speed * math.sin(launch_angle_rad)
    velocity_vec = np.array([vx, 0.0, vz])
    initial_pos = np.array([0.0, 0.0, 1.65])
    shot = projectile.Projectile(weapon, initial_pos, velocity_vec)
    while not np.all(shot.has_landed()):
        shot.step(dt, wind_model, integrator_fn)
    return shot.trajectory_log