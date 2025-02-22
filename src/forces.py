# src/forces.py
#--- START OF FILE forces.py ---
# src/forces.py
import numpy as np
from src.ga_utils import to_ga_point, to_ga_vector, from_ga_vector, ga_vector_subtract, ga_dot_product, ga_vector_add, ga_vector_norm_sq, ga_vector_normalize, ga_scalar_mul  # Import GA utilities
from src.shell_potential import spheroidal_shell_force_approximation  # Corrected import name
from src.galactic_potential import G  # Gravitational Constant
import kingdon as kg  # Import kingdon
from scipy.spatial import cKDTree  # Efficient k-d tree implementation


alg = kg.Algebra(p=3, q=0, r=0)  # Create Algebra instance here


def compute_average_interstellar_distance(particles):
    """Estimate the average interstellar distance based on star density."""
    num_particles = len(particles)
    if num_particles < 2:
        return np.inf  # If only one particle, avoid division by zero

    positions = np.array([p.position for p in particles])
    if positions.size == 0: # Handle case of no particles
        return np.inf

    volume = np.ptp(positions, axis=0).prod()  # Approximate volume of the system
    if volume == 0: # Handle case of zero volume (e.g., all particles at same position in one dimension)
        return np.inf

    density = num_particles / volume
    avg_distance = (density ** (-1 / 3)) if density > 0 else np.inf  # Approximate mean separation distance, handle zero density
    return avg_distance


def localized_gravity_force(particle, particles, shells, interaction_radius_kpc):
    """
    Calculates the total gravitational force on a particle using localized N-body and Shell Theorem approximation.
    Args:
        particle (AbstractParticle): The particle to calculate the force on.
        particles (list): List of all particles in the simulation.
        shells (list): List of SpheroidalShell objects for potential approximation.
        interaction_radius_kpc (float): Radius within which to calculate direct N-body forces (kpc).
    Returns:
        kingdon.MultiVector: Total gravitational force on the particle as a GA vector.
    """
    if not particles:  # Handle empty particles list
        return kg.MultiVector(algebra=alg, values=None)

    positions = np.array([p.position for p in particles])
    if positions.size == 0: # Handle case of no positions
        return kg.MultiVector(algebra=alg, values=None)


    tree = cKDTree(positions)  # Build k-d tree for quick neighbor search
    neighbors_indices = tree.query_ball_point(particle.position, interaction_radius_kpc)  # Find nearby particles

    total_force_ga = kg.MultiVector(algebra=alg, values=None)  # Initialize force to zero using kingdon, adjust if needed - keyword values
    shell_force_ga = spheroidal_shell_force_approximation(particle.position_ga, shells)  # Force from spheroidal background
    total_force_ga = ga_vector_add(total_force_ga, shell_force_ga)  # Add shell force

    # Local N-body force from nearby particles
    for idx in neighbors_indices:
        other_particle = particles[idx]
        if other_particle is particle:
            continue

        r_vec_ga = ga_vector_subtract(other_particle.position_ga, particle.position_ga)  # Vector from particle to other
        r_vec_cart = from_ga_vector(r_vec_ga)
        r_mag = np.linalg.norm(r_vec_cart)

        if 0.0 < r_mag < interaction_radius_kpc:  # Nearby particle
            r_mag_sq_ga = ga_vector_norm_sq(r_vec_ga)  # Use kingdon GA norm_sq
            r_mag_sq_val = r_mag_sq_ga.e
            if float(r_mag_sq_val) == 0:  # Compare float value, adjust if needed
                continue
            force_magnitude = G * particle.mass * other_particle.mass / float(r_mag_sq_val)  # Use float value of norm_sq
            r_hat_ga = ga_vector_normalize(r_vec_ga)  # Use kingdon GA normalize

            pairwise_force_ga = ga_scalar_mul(force_magnitude, r_hat_ga)  # Use scalar_mul
            total_force_ga = ga_vector_add(total_force_ga, pairwise_force_ga)  # Use vector_add

    return total_force_ga


if __name__ == '__main__':
    from src.particles import Star, BlackHole
    from src.shell_potential import SpheroidalShell
    from src.galactic_potential import SpheroidalParams

    example_spheroid_params = SpheroidalParams(a=20.0, b=20.0, c=5.0, M=100.0)
    shells_example = [
        SpheroidalShell(1e11, 5.0, 3.0, np.array([0.0, 0.0, 0.0])),  # Corrected SpheroidalShell init
        SpheroidalShell(1e11, 10.0, 6.0, np.array([0.0, 0.0, 0.0])),
        SpheroidalShell(1e11, 15.0, 9.0, np.array([0.0, 0.0, 0.0])),
        SpheroidalShell(1e11, 20.0, 12.0, np.array([0.0, 0.0, 0.0]))
    ]

    particle1 = Star(position=np.array([10.0, 0.0, 0.0]), velocity=np.array([0.0, 0.0, 0.0]), mass=1.0)
    particle2 = BlackHole(position=np.array([11.0, 0.0, 0.0]), velocity=np.array([0.0, 0.0, 0.0]), mass=100.0)
    particles_example = [particle1, particle2]

    interaction_radius = 2.0  # kpc

    force_on_p1_ga = localized_gravity_force(particle1, particles_example, shells_example, interaction_radius)
    print(f"Force on particle 1: {from_ga_vector(force_on_p1_ga)}")

    avg_dist = compute_average_interstellar_distance(particles_example)
    print(f"Average Interstellar Distance: {avg_dist}")

# --- END OF FILE forces.py ---