# src/simulation.py
#--- START OF FILE simulation.py ---
# src/simulation.py
import numpy as np
import random
import logging
import time
import os
from src.particles import Star, BlackHole
from src.forces import localized_gravity_force
from src.integrator import velocity_verlet_step, velocity_verlet_second_half_kick, adaptive_timestep
from src.initialization import initialize_particles, form_disk
from src.shell_potential import total_spheroidal_force_approximation, SpheroidalShell # Import shell class and corrected potential function name
from src.galactic_potential import SpheroidalParams, DiskParams, SpiralParams # Parameter classes
from src.ga_utils import from_ga_point, to_ga_point # Import from_ga_point, to_ga_point
import kingdon as kg # Import kingdon
import sys # Import sys if not already present

alg = kg.Algebra(p=3, q=0, r=0) # Create Algebra instance here


# --- Module-level diagnostic data ---
star_positions_over_time = []
rotation_curves = []
bh_density_profiles = []
star_counts = []
velocity_dispersions = []
bh_halo_masses = []
max_bh_mass = []

def log_message(sim_params, level, message):
    """Logs messages based on verbosity level."""
    if sim_params.verbosity >= level:
        numeric_log_level = {
            0: logging.CRITICAL,
            1: logging.INFO,
            2: logging.DEBUG,
        }.get(level, logging.INFO)
        logging.log(numeric_log_level, message)

def calculate_rotation_curve(particles):
    """Calculates the rotation curve (placeholder - adapt for GA if needed)."""
    # ... (Rotation curve calculation - Placeholder, needs adaptation if you want GA-aware rotation curve) ...
    return [], [] # Placeholder - adapt

def calculate_bh_radial_density(particles):
    """Calculates BH radial density (placeholder - adapt for GA if needed)."""
    # ... (BH density profile calculation - Placeholder, needs adaptation if you want GA-aware density) ...
    return [], [] # Placeholder - adapt

def calculate_bh_halo_mass(particles):
    """Calculates total BH halo mass (placeholder - adapt if needed)."""
    # ... (BH halo mass calculation - Placeholder, adapt if needed) ...
    return 0.0 # Placeholder - adapt

def calculate_max_bh_mass(particles):
    """Calculates max BH mass (placeholder - adapt if needed)."""
    max_mass = 0.0
    for p in particles:
        if isinstance(p, BlackHole) and p.mass > max_mass:
            max_mass = p.mass
    return max_mass

def collect_diagnostics(particles, stars, step, dt, sim_params):
    """Collects simulation diagnostics at specified intervals."""
    global star_positions_over_time, rotation_curves, bh_density_profiles, star_counts, velocity_dispersions, bh_halo_masses, max_bh_mass

    if step % sim_params.output_interval == 0:
        if particles:
            star_positions_over_time.append([from_ga_point(star.position_ga).copy() for star in stars]) # Convert GA to Cartesian for diagnostics
            rotation_curves.append(calculate_rotation_curve(particles))
            bh_density_profiles.append(calculate_bh_radial_density(particles))
            star_counts.append(len(stars))
            velocity_disp = [np.linalg.norm(p.velocity) for p in particles if isinstance(p, Star)]

            # --- Debug Prints ---
            print(f"Debug - Step {step}: Number of stars = {len(stars)}") # Check star count
            print(f"Debug - Step {step}: velocity_disp before std = {velocity_disp}") # Check velocity_disp list

            velocity_dispersions_val = np.std(velocity_disp) if velocity_disp else 0.0
            velocity_dispersions.append(velocity_dispersions_val)

            print(f"Debug - Step {step}: velocity_dispersions = {velocity_dispersions}") # Check velocity_dispersions list after append
            # --- End Debug Prints ---

            bh_halo_masses.append(calculate_bh_halo_mass(particles))
            max_bh_mass.append(calculate_max_bh_mass(particles))

            log_message(sim_params, 2, f"Step: {step}, Stars: {len(stars)}, BHs: {len([p for p in particles if isinstance(p, BlackHole)])}, "
                                        f"Max BH Mass: {max_bh_mass[-1] if max_bh_mass else 0.0:.2f}, Time: {step * dt:.2f}")
        else:
            log_message(sim_params, 1, f"Warning: No particles remaining at step {step}")

def run_one_step_ga(particles, shells, dt, sim_params, disk_params, spiral_params, step, disk_formation_step, ln_Lambda, rng):
    """Performs one step of the GA-based simulation."""
    logging.info(f"Starting run_one_step_ga for step: {step}")

    stars = [p for p in particles if isinstance(p, Star)]
    bhs = [p for p in particles if isinstance(p, BlackHole)]

    forces_ga = [localized_gravity_force(p, particles, shells, sim_params.interaction_radius_kpc) for p in particles]
    dt = adaptive_timestep(particles, sim_params, forces_ga) # Adaptive time step

    particles = velocity_verlet_step(particles, forces_ga, dt) # Velocity Verlet - first half & drift

    if step == disk_formation_step: # Disk formation
        form_disk(particles, disk_params, spiral_params)
        stars = [p for p in particles if isinstance(p, Star)]
        bhs = [p for p in particles if isinstance(p, BlackHole)]

    # --- Placeholder for Encounters and Mergers (Adapt if needed) ---
    # particles_to_remove_indices = handle_encounters(stars, bhs, sim_params, spheroidal_params, rng, step)
    # bhs_to_remove_indices = merge_black_holes(bhs, sim_params.merger_radius)
    # particles[:] = [star for i, star in enumerate(stars) if i not in particles_to_remove_indices] + [bh for i, bh in enumerate(bhs) if i not in bhs_to_remove_indices]

    forces_ga_next_step = [localized_gravity_force(p, particles, shells, sim_params.interaction_radius_kpc) for p in particles] # Recalculate forces
    velocity_verlet_second_half_kick(particles, forces_ga_next_step, dt) # Velocity Verlet - second half kick

    logging.info(f"Finished run_one_step_ga for step: {step}, dt = {dt}")
    return particles, forces_ga_next_step, dt # Return forces for next step and dt for diagnostics

def run_n_body_simulation_ga(n_steps, initial_particles, shells, sim_params,
                               disk_formation_step, disk_params, spiral_params,
                               ln_Lambda, spheroidal_params, rng_seed):
    """Runs the GA-based N-body simulation."""
    rng = random.Random(rng_seed)
    particles = [ # Deepcopy initial particles and use GA representation
        Star(particle_init.position.copy(), particle_init.velocity.copy(), particle_init.mass) if isinstance(particle_init, Star)
        else BlackHole(particle_init.position.copy(), particle_init.velocity.copy(), particle_init.mass)
        for particle_init in initial_particles # Changed loop variable name here to particle_init
    ]
    zero_force_ga = kg.MultiVector(algebra=alg, values=None) # Initialize zero force using kingdon, adjust if needed - keyword values


    # Clear module-level lists (important for multiple simulations)
    star_positions_over_time.clear()
    rotation_curves.clear()
    bh_density_profiles.clear()
    star_counts = []
    velocity_dispersions.clear()
    bh_halo_masses = []
    max_bh_mass = []

    dt = sim_params.dt_max # Initial time step
    log_message(sim_params, 1, "Starting GA-based N-body simulation...")

    forces_ga_current_step = [localized_gravity_force(p, particles, shells, sim_params.interaction_radius_kpc) for p in particles] # Initial forces

    for step in range(1, n_steps + 1):
        particles, forces_ga_next_step, dt = run_one_step_ga(particles, shells, dt, sim_params, disk_params, spiral_params, step, disk_formation_step, ln_Lambda, rng)
        stars = [p for p in particles if isinstance(p, Star)]
        collect_diagnostics(particles, stars, step, dt, sim_params) # Collect diagnostics
        forces_ga_current_step = forces_ga_next_step # Update forces for next step

    log_message(sim_params, 1, "GA-based Simulation complete!")

    diagnostics = { # Return collected diagnostics
        "star_positions_over_time": star_positions_over_time,
        "rotation_curves": rotation_curves,
        "bh_density_profiles": bh_density_profiles,
        "star_counts": star_counts,
        "velocity_dispersions": velocity_dispersions,
        "bh_halo_masses": bh_halo_masses,
        "max_bh_mass": max_bh_mass
    }
    return particles, diagnostics
# --- END OF FILE simulation.py ---