# src/initialization.py
#--- START OF FILE initialization.py ---
# src/initialization.py
import numpy as np
import random
from scipy.stats import pareto
from src.particles import Star, BlackHole
from src.galactic_potential import G
from src.ga_utils import to_ga_point # Import to_ga_point


def random_in_spheroid(a, b, c, rng=random):
    """
    Generate a random point uniformly within a spheroid with semi-axes a, b, and c.
    Args:
        a (float): Semi-major axis along x.
        b (float): Semi-major axis along y.
        c (float): Semi-minor axis along z.
        rng (random.Random): Random number generator.
    Returns:
        np.array: Random position within the spheroid.
    """
    while True:
        x = 2 * a * rng.random() - a
        y = 2 * b * rng.random() - b
        z = 2 * c * rng.random() - c
        if (x**2 / a**2) + (y**2 / b**2) + (z**2 / c**2) <= 1.0:
            return np.array([x, y, z])

def random_in_disk(radius, thickness, rng=random):
    """
    Generate a random point within a disk (uniform in radius and z).
    Args:
        radius (float): Radius of the disk.
        thickness (float): Thickness of the disk.
        rng (random.Random): Random number generator.
    Returns:
        np.array: Random position within the disk.
    """
    r = np.sqrt(rng.random()) * radius
    theta = 2 * np.pi * rng.random()
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = rng.uniform(-thickness/2, thickness/2)
    return np.array([x, y, z])

def add_spiral_perturbation(particles, spiral_params):
    """
    Adds a spiral arm perturbation to the positions and velocities of disk stars.
    Args:
        particles (list): List of particle objects.
        spiral_params (SpiralParams): Spiral arm parameters object.
    """
    m = spiral_params.num_arms
    alpha = spiral_params.pitch_angle
    A_pos = spiral_params.amplitude_pos
    A_vel = spiral_params.amplitude_vel
    r0 = spiral_params.scale_length
    for p in particles:
        if isinstance(p, Star):
            r = np.sqrt(p.position[0]**2 + p.position[1]**2)
            if r == 0.0:
                continue
            phi = np.arctan2(p.position[1], p.position[0])
            phase = m * phi - (1/np.tan(alpha)) * np.log(r/r0)

            delta_r = A_pos * np.cos(phase)
            new_r = max(0.0, r + delta_r)

            delta_phi = -(A_pos / (r * np.tan(alpha))) * np.cos(phase)
            new_phi = phi + delta_phi

            p.position = np.array([new_r * np.cos(new_phi), new_r * np.sin(new_phi), p.position[2]])

            delta_vphi = A_vel * np.sin(phase)
            p.velocity = np.array([p.velocity[0] - delta_vphi * np.sin(new_phi), p.velocity[1] + delta_vphi * np.cos(new_phi), p.velocity[2]])

def form_disk(particles, disk_params, spiral_params):
    """
    Forms a disk galaxy by repositioning star particles and setting their initial velocities.
    Args:
        particles (list): List of particle objects.
        disk_params (DiskParams): Disk parameters object.
        spiral_params (SpiralParams): Spiral arm parameters object.
    Returns:
        list: Updated list of particles.
    """
    rng = random.Random(1234)
    disk_radius = disk_params.disk_radius
    disk_thickness = disk_params.disk_thickness
    v_circ_factor = disk_params.v_circ_factor

    for p in particles:
        if isinstance(p, Star):
            new_pos = random_in_disk(disk_radius, disk_thickness, rng)
            p.position = new_pos

            r = np.sqrt(new_pos[0]**2 + new_pos[1]**2)
            v_circ = v_circ_factor * np.sqrt(G * disk_params.M / (np.sqrt(r**2 + disk_params.a**2 + disk_params.b**2)))

            phi = np.arctan2(new_pos[1], new_pos[0])
            p.velocity = np.array([-v_circ * np.sin(phi) + rng.gauss(0, disk_params.velocity_dispersion),
                                   v_circ * np.cos(phi) + rng.gauss(0, disk_params.velocity_dispersion),
                                   rng.gauss(0, disk_params.velocity_dispersion * 0.2)])

    add_spiral_perturbation(particles, spiral_params)
    return particles


def initialize_particles(num_stars, num_bhs, spheroid_a, spheroid_b, spheroid_c, velocity_dispersion,
                         bh_mass_min=50.0, bh_mass_max=200.0, bh_mass_alpha=2.35,
                         bh_a_scale=0.5, bh_b_scale=0.5, bh_c_scale=0.5, rng=random):
    """
    Initializes star and black hole particles with spheroidal distributions and power-law BH masses.
    Args:
        num_stars (int): Number of star particles.
        num_bhs (int): Number of black hole particles.
        spheroid_a (float): Semi-major axis of star spheroid.
        spheroid_b (float): Semi-major axis of star spheroid.
        spheroid_c (float): Semi-minor axis of star spheroid.
        velocity_dispersion (float): Velocity dispersion for stars and BHs.
        bh_mass_min (float): Minimum BH mass.
        bh_mass_max (float): Maximum BH mass.
        bh_mass_alpha (float): Power-law index for BH mass distribution.
        bh_a_scale (float): Scaling factor for BH spheroid a-axis.
        bh_b_scale (float): Scaling factor for BH spheroid b-axis.
        bh_c_scale (float): Scaling factor for BH spheroid c-axis.
        rng (random.Random): Random number generator.
    Returns:
        tuple: (stars, black_holes) - lists of Star and BlackHole objects.
    """
    stars = []
    black_holes = []

    for _ in range(num_stars): # Initialize stars
        star_pos = random_in_spheroid(spheroid_a, spheroid_b, spheroid_c, rng)
        star_vel = np.array([rng.gauss(0, velocity_dispersion), rng.gauss(0, velocity_dispersion), rng.gauss(0, velocity_dispersion)])
        stars.append(Star(star_pos, star_vel, 1.0))

    bh_a = spheroid_a * bh_a_scale # Initialize black holes
    bh_b = spheroid_b * bh_b_scale
    bh_c = spheroid_c * bh_c_scale

    alpha_minus_one = bh_mass_alpha - 1
    power_law_dist = pareto(alpha_minus_one)

    bh_masses_cdf_vals = np.random.uniform(0, 1, num_bhs)
    lower_cdf = power_law_dist.cdf(bh_mass_min)
    upper_cdf = power_law_dist.cdf(bh_mass_max)
    normalized_cdf_values = lower_cdf + bh_masses_cdf_vals * (upper_cdf - lower_cdf)
    bh_masses = power_law_dist.ppf(normalized_cdf_values)

    for _ in range(num_bhs):
        bh_pos = random_in_spheroid(bh_a, bh_b, bh_c, rng)
        bh_vel = np.array([rng.gauss(0, velocity_dispersion * 0.5), rng.gauss(0, velocity_dispersion * 0.5), rng.gauss(0, velocity_dispersion * 0.5)])
        bh_mass = bh_masses[_]
        black_holes.append(BlackHole(bh_pos, bh_vel, bh_mass))

    return stars, black_holes
# --- END OF FILE initialization.py ---