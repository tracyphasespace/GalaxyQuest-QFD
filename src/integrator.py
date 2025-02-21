# src/integrator.py
#--- START OF FILE integrator.py ---
# src/integrator.py
import numpy as np
from src.ga_utils import from_ga_vector, to_ga_vector, ga_vector_add, ga_vector_norm_sq, to_ga_point # Added to_ga_point


def velocity_verlet_step(particles, forces_ga, dt):
    """
    Performs one step of Velocity Verlet integration (first half-kick and drift).
    Args:
        particles (list): List of particles to integrate.
        forces_ga (list): List of forces on each particle in GA vector form.
        dt (float): Time step.
        Returns:
        list: Updated list of particles (particles are updated in-place).
    """
    num_particles = len(particles)
    accelerations_ga = [to_ga_vector([0.0, 0.0, 0.0])] * num_particles

    # First half-kick of velocities
    for i in range(num_particles):
        force_cart = from_ga_vector(forces_ga[i])
        # Corrected line: Convert force_cart to NumPy array before division
        accel_cart = np.array(force_cart) / particles[i].mass # a = F/m (Cartesian for now)
        particles[i].velocity += 0.5 * dt * np.array(accel_cart)

    # Full drift of positions
    for i in range(num_particles):
        particles[i].position += dt * particles[i].velocity
        particles[i].position_ga = to_ga_point(particles[i].position) # Update GA position using kingdon
    return particles

def velocity_verlet_second_half_kick(particles, forces_ga, dt):
    """
    Performs the second half-kick of velocities in Velocity Verlet.
    Args:
        particles (list): List of particles.
        forces_ga (list): List of forces on each particle in GA vector form (at the *new* positions).
        dt (float): Time step.
        Returns:
        list: Updated list of particles (particles are updated in-place).
    """
    num_particles = len(particles)
    for i in range(num_particles):
        force_cart = from_ga_vector(forces_ga[i])
        # Corrected line: Convert force_cart to NumPy array before division
        accel_cart = np.array(force_cart) / particles[i].mass
        particles[i].velocity += 0.5 * dt * np.array(accel_cart)
    return particles


def adaptive_timestep(particles, sim_params, forces_ga):
    """
    Calculates an adaptive time step based on particle accelerations and velocities.
    Args:
        particles (list): List of particles.
        sim_params (SimulationParams): Simulation parameters object.
        forces_ga (list): List of forces on each particle in GA vector form.
        Returns:
        float: Adaptive time step.
    """
    max_acc_sq = 0.0
    max_vel_sq = 0.0

    for i, p in enumerate(particles):
        force_cart = from_ga_vector(forces_ga[i])
        # Corrected line: Convert force_cart to NumPy array before division
        accel_cart = np.array(force_cart) / p.mass
        accel_sq = np.sum(accel_cart**2) # Use numpy for squared sum of cartesian accel
        vel_sq = np.sum(p.velocity**2)   # Use numpy for squared sum of cartesian velocity

        max_acc_sq = max(max_acc_sq, accel_sq)
        max_vel_sq = max(max_vel_sq, vel_sq)

    max_acc = np.sqrt(max_acc_sq) if max_acc_sq > 0 else 1e-9
    max_vel = np.sqrt(max_vel_sq) if max_vel_sq > 0 else 1e-9

    dt_acc = np.sqrt(sim_params.CFL * sim_params.softening_length / max_acc)
    dt_vel = sim_params.CFL * sim_params.softening_length / max_vel
    dt_estimate = min(dt_vel, dt_acc)
    dt_estimate = max(sim_params.dt_min, dt_estimate)
    dt_estimate = min(sim_params.dt_max, dt_estimate)

    return dt_estimate
# --- END OF FILE integrator.py ---