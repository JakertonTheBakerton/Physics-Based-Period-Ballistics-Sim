from dataclasses import dataclass, field
from physics import forces


@dataclass
class Musket:
    "Matchlock LG - https://www.colchestertreasurehunting.co.uk/b/bullets.htm"
    mass_kg: float = 0.0174
    muzzle_vel_ms: int = 450
    diameter_m: float = 0.014
    drag_profile: object = field(init = False)
    def __post_init__(self):
        self.drag_profile = forces.sphere_drag_profile(self.diameter_m)

@dataclass
class Pistol:
    "Flintlock Pistol STp 1128 - https://www.colchestertreasurehunting.co.uk/b/bullets.htm"
    mass_kg: float = 0.0145
    muzzle_vel_ms: int = 385
    diameter_m: float = 0.0135
    drag_profile: object = field(init = False)
    def __post_init__(self):
        self.drag_profile = forces.sphere_drag_profile(self.diameter_m)

@dataclass
class Crossbow:
    """
    Bolt mass/velocity are estimated, not sourced from a specific artifact —
    period military windlass crossbow proof-test records don't survive the
    way musket ordnance records do. Values chosen as representative of a
    mid-to-heavy military crossbow based on the range seen across modern
    reconstruction/experimental-archaeology discussions (roughly 50-90g
    bolt mass, 70-90 m/s), rather than any single documented source.
    """
    mass_kg: float = 0.06
    muzzle_vel_ms: int = 75
    diameter_m: float = 0.009
    drag_profile: object = field(init = False)
    def __post_init__(self):
        self.drag_profile = forces.cylinder_drag_profile(self.diameter_m)

@dataclass
class Bow:
    """
    English longbow (Mary Rose reference).
    Mass/velocity: Soar, Gibbs, Jury & Stretton (2010) chronographed test —
    102g war arrow shot from a 144 lbf yew bow at 47.23 m/s.
    Shaft diameter: 11mm, representative mid-shaft value from the converging
    range (10-13mm) across multiple Mary Rose arrow analyses.
    Fletching area: ESTIMATED, not directly sourced — see fletching_area_m2. - https://en.wikipedia.org/wiki/English_longbow, https://maryrose.org/discover/collections/the-weaponry-of-the-mary-rose/longbows-and-arrows/, https://www.bow-international.com/features/arrows-in-the-middle-ages/, https://leatherworkingreverendsmusings.wordpress.com/research/arrows/mary-rose/, 
    """
    mass_kg: float = 0.102
    muzzle_vel_ms: int = 47
    diameter_m: float = 0.011
    fletching_area_m2: float = 0.0108
    drag_profile: object = field(init = False)
    def __post_init__(self):
        self.drag_profile = forces.fletched_arrow_drag_profile(self.diameter_m, self.fletching_area_m2)