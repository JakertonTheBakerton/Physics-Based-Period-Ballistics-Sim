import numpy as np
from physics.forces import WindModel


def has_volley_landed(position, ground_level=0.0):
    return position[:, 2] <= ground_level

def run_volley_shot(weapon, launch_angle_deg, dt, integrator_fn, wind_model, n_shooters):
    n = n_shooters
    speeds = weapon.muzzle_vel_ms
    angle_deg = np.array(launch_angle_deg)
    angle_rad = np.radians(angle_deg)
    vx = speeds * np.cos(angle_rad)
    vz = speeds * np.sin(angle_rad)
    vy = np.zeros_like(vx)
    velocities = np.tile(np.array([vx, vy, vz]), (n, 1))

    
    spacing = 1.0
    y_offsets = np.linspace(0, spacing * (n - 1), n)
    positions = np.tile(np.array([0.0, 0.0, 1.65]), (n, 1))
    positions[:, 1] = y_offsets
    
    mass = weapon.mass_kg
    drag_profile = weapon.drag_profile

    landed_mask = has_volley_landed(positions)
    while not np.all(landed_mask):
        new_pos, new_vel = integrator_fn(positions, velocities, mass, dt, drag_profile, wind_model)
        positions = np.where(landed_mask[:, None], positions, new_pos)
        velocities = np.where(landed_mask[:, None], velocities, new_vel)
        landed_mask = has_volley_landed(positions)
    return positions