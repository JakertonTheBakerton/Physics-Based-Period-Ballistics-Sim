import numpy as np


def has_batch_landed(position, ground_level=0.0):
    return position[:, 2] <= ground_level

def run_batch_shot(weapon, launch_angles_deg, dt, integrator_fn, wind_model):
    speeds = weapon.muzzle_vel_ms
    angles_deg = np.array(launch_angles_deg)
    angles_rad = np.radians(angles_deg)
    vx = speeds * np.cos(angles_rad)
    vz = speeds * np.sin(angles_rad)
    vy = np.zeros_like(vx)
    velocities = np.column_stack([vx, vy, vz])

    n = len(launch_angles_deg)
    positions = np.tile(np.array([0.0, 0.0, 1.65]), (n, 1))
    
    mass = weapon.mass_kg
    drag_profile = weapon.drag_profile

    landed_mask = has_batch_landed(positions)
    while not np.all(landed_mask):
        new_pos, new_vel = integrator_fn(positions, velocities, mass, dt, drag_profile, wind_model)
        positions = np.where(landed_mask[:, None], positions, new_pos)
        velocities = np.where(landed_mask[:, None], velocities, new_vel)
        landed_mask = has_batch_landed(positions)
    return positions