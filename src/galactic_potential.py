# src/galactic_potential.py
# src/galactic_potential.py
import numpy as np
import math

# Gravitational constant (consistent units: kpc, km/s, 10^9 Msun)
G = 4.499e-6  # kpc^3 / (10^9 Msun Myr^2)  ->  kpc (km/s)^2 / (10^9 Msun)

# Parameter structs (using Python classes for simplicity)
class PlummerParams:
    """Parameters for Plummer potential."""
    def __init__(self, M, b):
        """
        Initializes PlummerParams.
        Args:
            M (float): Total mass.
            b (float): Plummer scale length.
        """
        self.M = float(M)
        self.b = float(b)

class SpheroidalParams:
    """Parameters for spheroidal potential."""
    def __init__(self, a, b, c, M):
        """
        Initializes SpheroidalParams.
        Args:
            a (float): Semi-major axis along x.
            b (float): Semi-major axis along y.
            c (float): Semi-minor axis along z.
            M (float): Total mass.
        """
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.M = float(M)

class DiskParams:
    """Parameters for disk potential."""
    def __init__(self, M, a, b, disk_radius, disk_thickness, v_circ_factor, velocity_dispersion):
        """
        Initializes DiskParams.
        Args:
            M (float): Total mass of the disk.
            a (float): Radial scale length.
            b (float): Vertical scale length.
            disk_radius (float): Radius of the disk.
            disk_thickness (float): Thickness of the disk.
            v_circ_factor (float): Factor for circular velocity scaling.
            velocity_dispersion (float): Velocity dispersion in the disk.
        """
        self.M = float(M)
        self.a = float(a)
        self.b = float(b)
        self.disk_radius = float(disk_radius)
        self.disk_thickness = float(disk_thickness)
        self.v_circ_factor = float(v_circ_factor)
        self.velocity_dispersion = float(velocity_dispersion)

class SpiralParams:
    """Parameters for spiral arm potential."""
    def __init__(self, num_arms, pitch_angle, pattern_speed, amplitude_pos, amplitude_vel, scale_length):
        """
        Initializes SpiralParams.
        Args:
            num_arms (int): Number of spiral arms.
            pitch_angle (float): Pitch angle (radians).
            pattern_speed (float): Pattern speed (radians/Myr).
            amplitude_pos (float): Amplitude of position perturbation (kpc).
            amplitude_vel (float): Amplitude of velocity perturbation (km/s).
            scale_length (float): Radial scale length of spiral arms (kpc).
        """
        self.num_arms = int(num_arms)
        self.pitch_angle = float(pitch_angle)
        self.pattern_speed = float(pattern_speed)
        self.amplitude_pos = float(amplitude_pos)
        self.amplitude_vel = float(amplitude_vel)
        self.scale_length = float(scale_length)

# --- Potential functions (Placeholders - not directly used in GA version for force calculation) ---
# You can keep these for reference or remove them if not needed.
def plummer_potential(position, params):
    """Calculate the Plummer potential (placeholder)."""
    return 0.0 # Placeholder

def spheroidal_potential(position, spheroidal_params):
    """Calculate spheroidal potential (placeholder)."""
    return 0.0 # Placeholder

def miyamoto_nagai_potential(position, params):
    """Calculates the Miyamoto-Nagai potential (placeholder)."""
    return 0.0 # Placeholder

def spiral_arm_potential(position, time, spiral_params):
    """Calculates the spiral arm potential (placeholder)."""
    return 0.0 # Placeholder

def total_potential(position, time, disk_params, spiral_params, spheroidal_params):
    """Calculate the total potential (placeholder)."""
    return 0.0 # Placeholder
# --- END OF FILE galactic_potential.py ---