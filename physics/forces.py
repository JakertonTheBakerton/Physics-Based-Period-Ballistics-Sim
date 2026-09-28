"""
forces.py

Force models for the period ballistics simulator.

Covers:
    - Gravity (constant, vector form for 3D integration)
    - Dynamic air density (altitude + temperature dependent)
    - Wind (steady + optional gust/turbulence component)
    - Aerodynamic drag, shape-dependent (sphere / cylinder / fletched-arrow)

All vectors are numpy arrays of shape (3,) in the form [x, y, z],
where z is "up". Velocities in m/s, distances in meters, forces in
Newtons, mass in kg.

Designed to be called per-timestep by an integrator (Euler or RK4 in
integrators.py) and to work unmodified when velocity/position arrays
are batched to shape (N, 3) for vectorized volley simulation -- the
functions below use elementwise numpy ops so they broadcast correctly
in both the single-projectile and batched case.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAVITY_ACCEL = 9.80665          # m/s^2, standard gravity
GRAVITY_VECTOR = np.array([0.0, 0.0, -GRAVITY_ACCEL])

SEA_LEVEL_PRESSURE = 101325.0    # Pa
SEA_LEVEL_DENSITY = 1.225        # kg/m^3
SPECIFIC_GAS_CONSTANT_AIR = 287.05  # J/(kg*K)
LAPSE_RATE = 0.0065              # K/m, standard troposphere lapse rate
SEA_LEVEL_TEMP_K = 288.15        # 15 degrees C


# ---------------------------------------------------------------------------
# Projectile shape / drag profile
# ---------------------------------------------------------------------------

class ProjectileShape(Enum):
    SPHERE = "sphere"          # musket / pistol ball
    CYLINDER = "cylinder"      # crossbow bolt (short, stiff, minimal fletching effect)
    FLETCHED_ARROW = "fletched_arrow"  # longbow / warbow arrow


@dataclass
class DragProfile:
    """
    Shape-dependent aerodynamic properties.

    drag_coefficient: baseline Cd at subsonic period-relevant velocities
    reference_area_fn: given a projectile's characteristic dimension(s),
        returns cross-sectional area in m^2
    """
    shape: ProjectileShape
    drag_coefficient: float
    reference_area_m2: float


def sphere_drag_profile(diameter_m: float, cd: float = 0.47) -> DragProfile:
    """Musket / pistol ball. Cd ~0.47 is the standard smooth-sphere value;
    period roundshot is rougher/undersized (windage) so real Cd trends
    a bit higher -- override cd if you've researched a specific figure."""
    radius = diameter_m / 2.0
    area = np.pi * radius ** 2
    return DragProfile(ProjectileShape.SPHERE, cd, area)


def cylinder_drag_profile(diameter_m: float, cd: float = 1.15) -> DragProfile:
    """Crossbow bolt, modeled as a blunt-nosed cylinder cross-section.
    Cd ~1.0-1.2 for a cylinder presenting frontal area; adjust down
    (~0.6-0.8) if you model a sharpened/tapered bolt head instead."""
    radius = diameter_m / 2.0
    area = np.pi * radius ** 2
    return DragProfile(ProjectileShape.CYLINDER, cd, area)


def fletched_arrow_drag_profile(shaft_diameter_m: float,
                                 fletching_area_m2: float,
                                 cd: float = 0.9) -> DragProfile:
    """Arrow: frontal area is small (shaft tip) but fletching adds
    meaningful drag area and provides the stabilizing effect that keeps
    Cd relatively constant across the flight (unlike an unstable ball).
    Effective reference area = shaft cross-section + fletching contribution."""
    shaft_radius = shaft_diameter_m / 2.0
    shaft_area = np.pi * shaft_radius ** 2
    effective_area = shaft_area + fletching_area_m2
    return DragProfile(ProjectileShape.FLETCHED_ARROW, cd, effective_area)


# ---------------------------------------------------------------------------
# Atmosphere / dynamic air density
# ---------------------------------------------------------------------------

def air_density(altitude_m: float,
                 sea_level_temp_k: float = SEA_LEVEL_TEMP_K,
                 sea_level_pressure_pa: float = SEA_LEVEL_PRESSURE) -> float:
    """
    Dynamic air density via the barometric formula (troposphere model).

    Density drops with altitude and rises/falls with the chosen sea-level
    temperature, so callers can model a hot summer engagement vs. a cold
    winter one, not just a fixed 1.225 kg/m^3 constant.
    """
    temp_k = sea_level_temp_k - LAPSE_RATE * altitude_m
    if temp_k <= 0:
        raise ValueError("Unrealistic altitude produced non-physical temperature")

    exponent = GRAVITY_ACCEL / (LAPSE_RATE * SPECIFIC_GAS_CONSTANT_AIR)
    pressure = sea_level_pressure_pa * (temp_k / sea_level_temp_k) ** exponent
    density = pressure / (SPECIFIC_GAS_CONSTANT_AIR * temp_k)
    return density


# ---------------------------------------------------------------------------
# Wind
# ---------------------------------------------------------------------------

@dataclass
class WindModel:
    """
    Steady wind vector plus optional gust component.

    base_wind: constant wind vector (m/s), e.g. [3.0, 0.0, 0.0] for a
        steady 3 m/s crosswind along x.
    gust_std: standard deviation (m/s) of gaussian turbulence noise
        added per call. Set to 0.0 for deterministic/reproducible runs.
    rng: numpy Generator, so gust sequences are seedable/reproducible.
    """
    base_wind: np.ndarray
    gust_std: float = 0.0
    rng: np.random.Generator = None

    def __post_init__(self):
        if self.rng is None:
            self.rng = np.random.default_rng()

    def sample(self, shape=(3,)) -> np.ndarray:
        """Return a wind vector for this timestep. shape=(3,) for a single
        projectile, or (N, 3) to sample independent gusts per shooter in a
        batched volley."""
        if self.gust_std <= 0.0:
            return np.broadcast_to(self.base_wind, shape).copy()
        gust = self.rng.normal(0.0, self.gust_std, size=shape)
        return np.broadcast_to(self.base_wind, shape) + gust


# ---------------------------------------------------------------------------
# Drag force
# ---------------------------------------------------------------------------

def drag_force(velocity: np.ndarray,
               wind: np.ndarray,
               density: float,
               drag_profile: DragProfile) -> np.ndarray:
    """
    Quadratic drag: F = -0.5 * rho * Cd * A * |v_rel| * v_rel

    velocity: projectile velocity vector(s), shape (3,) or (N, 3)
    wind: wind vector(s) of matching shape, subtracted to get velocity
        relative to the air mass
    density: air density at current altitude (kg/m^3)
    drag_profile: shape-dependent Cd and reference area

    Returns force vector(s) in Newtons, same shape as velocity.
    Fully vectorized: pass (N, 3) arrays for batched volley simulation.
    """
    v_rel = velocity - wind
    speed = np.linalg.norm(v_rel, axis=-1, keepdims=True)

    # Avoid division/zero-vector issues at rest
    speed_safe = np.where(speed == 0, 1e-12, speed)

    coeff = 0.5 * density * drag_profile.drag_coefficient * drag_profile.reference_area_m2
    force = -coeff * speed_safe * v_rel
    return force


# ---------------------------------------------------------------------------
# Gravity force
# ---------------------------------------------------------------------------

def gravity_force(mass_kg, batch_shape=None) -> np.ndarray:
    """
    Returns gravity force vector(s) = mass * g.

    mass_kg: scalar (single projectile) or array of shape (N,) for a
        batched volley with per-projectile mass.
    batch_shape: pass (N, 3) explicitly if you want broadcasting without
        relying on mass_kg's shape (rarely needed -- usually inferred).
    """
    mass_arr = np.asarray(mass_kg)
    if mass_arr.ndim == 0:
        return mass_arr * GRAVITY_VECTOR
    # (N,) mass -> (N, 3) force
    return mass_arr[:, None] * GRAVITY_VECTOR


# ---------------------------------------------------------------------------
# Combined net force (convenience for integrators.py)
# ---------------------------------------------------------------------------

def net_force(velocity: np.ndarray,
              mass_kg,
              altitude_m,
              drag_profile: DragProfile,
              wind_model: WindModel) -> np.ndarray:
    """
    Sums gravity + drag for the current state. This is the function
    integrators.py should call each substep for both Euler and RK4.

    altitude_m: scalar or array (N,) matching velocity's batch dimension,
        so density can vary per-projectile if shooters are at different
        elevations, or be treated as scalar for a single trajectory.
    """
    
    altitude_arr = np.asarray(altitude_m)
    density = air_density(float(altitude_arr)) if altitude_arr.ndim == 0 else \
    np.array([air_density(a) for a in altitude_arr])

    wind = wind_model.sample(shape=velocity.shape)
    f_drag = drag_force(velocity, wind, density if np.isscalar(density)
                         else density[:, None], drag_profile)
    f_gravity = gravity_force(mass_kg)

    return f_gravity + f_drag