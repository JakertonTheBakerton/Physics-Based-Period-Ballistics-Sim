import numpy as np
from weapons import parameters

class Projectile:
    def __init__(self, weapon, position, velocity):
        self.mass_kg = weapon.mass_kg
        self.drag_profile = weapon.drag_profile
        self.position = position
        self.velocity = velocity
        self.time_elapsed = 0.0
        self.trajectory_log = [{
            "position": position.copy(),
            "velocity": velocity.copy(),
            "time": 0.0
        }]
    def step(self, dt, wind_model, integrator_fn):
        self.position, self.velocity = integrator_fn(self.position, self.velocity, self.mass_kg, dt, self.drag_profile, wind_model)
        self.time_elapsed += dt
        self.trajectory_log.append({
            "position": self.position.copy(),
            "velocity": self.velocity.copy(),
            "time": self.time_elapsed
        })
    def has_landed(self, ground_level=0.0):
        return self.position[2] <= ground_level
  