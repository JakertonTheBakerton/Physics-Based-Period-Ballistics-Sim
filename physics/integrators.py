import numpy as np
from physics import forces

def euler_step(position, velocity, mass, dt, drag_profile, wind_model):
    vel, accel = state_derivative(position, velocity, mass, drag_profile, wind_model)
    new_position = position + dt * vel
    new_velocity = velocity + dt * accel
    return new_position, new_velocity

def rk4_step(position, velocity, mass, dt, drag_profile, wind_model):
    k1_pos, k1_vel = state_derivative(position, velocity, mass, drag_profile, wind_model)

    guess_pos2 = position + 0.5 * dt * k1_pos
    guess_vel2 = velocity + 0.5 * dt * k1_vel
    k2_pos, k2_vel = state_derivative(guess_pos2, guess_vel2, mass, drag_profile, wind_model)

    guess_pos3 = position + 0.5 * dt * k2_pos
    guess_vel3 = velocity + 0.5 * dt * k2_vel
    k3_pos, k3_vel = state_derivative(guess_pos3, guess_vel3, mass, drag_profile, wind_model)

    guess_pos4 = position + dt * k3_pos
    guess_vel4 = velocity + dt * k3_vel
    k4_pos, k4_vel = state_derivative(guess_pos4, guess_vel4, mass, drag_profile, wind_model)

    weighted_pos = (k1_pos + 2 * (k2_pos) + 2 * (k3_pos) + k4_pos) / 6
    weighted_vel = (k1_vel + 2 * (k2_vel) + 2 * (k3_vel) + k4_vel) / 6
    new_pos = position + dt * weighted_pos
    new_vel = velocity + dt * weighted_vel
    return new_pos, new_vel

def state_derivative(position, velocity, mass, drag_profile, wind_model):
    altitude = position[..., 2]
    net_force = forces.net_force(velocity, mass, altitude, drag_profile, wind_model)
    
    mass_arr = np.asarray(mass)
    if mass_arr.ndim == 0:
        accel = net_force / mass_arr
    else:
        accel = net_force / mass_arr[:, None]
    
    return velocity, accel