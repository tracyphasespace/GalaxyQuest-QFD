# run_simulations.py
import importlib
import src.plotting
importlib.reload(src.plotting)

import numba
print(f"Numba version being used by script: {numba.__version__}")
import numpy as np
import random
import os
import time
import logging
import sys

# --- Add src directory to Python path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.isdir(src_dir):
    sys.path.insert(0, src_dir)
else:
    print(f"Error: 'src' directory not found at {src_dir}")
    sys.exit(1)

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Import modules from src directory ---
from src.particles import Star, BlackHole
from src.galactic_potential import SpheroidalParams, DiskParams, SpiralParams
from src.initialization import initialize_particles, form_disk
from src.simulation_params import SimulationParams  # Corrected import for SimulationParams
from src.simulation import run_n_body_simulation_ga   # Keep this import for run_n_body_simulation_ga
from src import plotting
from src.shell_potential import total_spheroidal_force_approximation, SpheroidalShell # Corrected import
from src.ga_utils import to_ga_point # Import to_ga_point

def create_default_shells(spheroidal_params, num_shells=20, total_mass=100.0):
    """Creates a list of SpheroidalShell objects to approximate a spheroid."""
    shell_radii = np.linspace(0.0, max(spheroidal_params.a, spheroidal_params.b, spheroidal_params.c) * 1.1, num_shells + 1)
    shell_masses = np.diff(np.linspace(0.0, total_mass, num_shells + 1)) # Equal mass shells for simplicity
    shells = []
    for i in range(num_shells):
        center_radius = (shell_radii[i+1] + shell_radii[i]) / 2.0 # Approximate center radius for shell
        shells.append(SpheroidalShell(shell_masses[i], center_radius, center_radius * (spheroidal_params.c / spheroidal_params.a) , np.array([0.0, 0.0, 0.0]))) # More accurate shell semi-minor axis calc
    return shells

def run_simulation_with_params_ga():
    """Runs the GA-based N-body simulation."""

    # --- Simulation Parameters (REDUCED SCALE FOR TESTING) ---
    n_steps = 100
    num_stars = 50
    num_bhs = 3
    velocity_dispersion = 50.0
    disk_formation_step = 40

    # --- Spheroid Parameters ---
    spheroid_a = 15.0
    spheroid_b = 15.0
    spheroid_c = 4.0
    spheroid_mass = 80.0
    spheroidal_params = SpheroidalParams(spheroid_a, spheroid_b, spheroid_c, spheroid_mass)
    shells = create_default_shells(spheroidal_params, total_mass=spheroid_mass) # Create shells for GA potential

    # --- Disk Parameters ---
    disk_params = DiskParams(M=40.0, a=4.0, b=0.2, disk_radius=12.0, disk_thickness=0.8, v_circ_factor=0.9, velocity_dispersion=15.0)

    # --- Spiral Arm Parameters ---
    spiral_params = SpiralParams(num_arms=2, pitch_angle=0.2, pattern_speed=0.8, amplitude_pos=0.05, amplitude_vel=5.0, scale_length=4.0)

    # --- Simulation Parameters Struct ---
    sim_params = SimulationParams(
        dt_min=0.01, dt_max=0.5, CFL=0.1, softening_length=0.08, interaction_radius_kpc=2.0,
        verbosity=1, output_interval=10, log_level="INFO"
    )

    ln_Lambda = np.log(spheroid_a / sim_params.softening_length)
    rng_seed = 1234

    # --- Create Output Directory ---
    timestamp = time.strftime("%Y-%m-%dT%H-%M-%S")
    output_dir = f"simulation_data_ga_run_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    # --- Initialize Particles ---
    initial_stars, initial_bhs = initialize_particles(
        num_stars, num_bhs, spheroid_a, spheroid_b, spheroid_c, velocity_dispersion,
        bh_mass_min=40.0, bh_mass_max=150.0, bh_mass_alpha=2.35,
        bh_a_scale=0.4, bh_b_scale=0.4, bh_c_scale=0.4, rng=random.Random(rng_seed)
    )
    initial_particles = initial_stars + initial_bhs

    # --- Run GA-based Simulation ---
    logging.info("Starting GA-based N-body simulation...")
    final_particles, diagnostics = run_n_body_simulation_ga(
        n_steps, initial_particles, shells, sim_params,
        disk_formation_step, disk_params, spiral_params, ln_Lambda, spheroidal_params, rng_seed
    )
    logging.info("GA-based Simulation complete!")

    # --- Generate Plots (COMMENTED OUT FOR FASTER TESTING) ---
    # plotting.plot_star_positions_animation(diagnostics, output_dir=output_dir)
    # plotting.plot_rotation_curve_evolution(diagnostics, output_dir=output_dir)
    # plotting.plot_bh_density_evolution(diagnostics, output_dir=output_dir)
    # # Pass sim_params to plot_summary_stats
    # plotting.plot_summary_stats(diagnostics, output_dir=output_dir, sim_params=sim_params)
    # plotting.plot_max_bh_mass_evolution(diagnostics, output_dir=output_dir, sim_params=sim_params)
    # plotting.plot_particle_distribution(final_particles, output_dir=output_dir, step=n_steps)

    return output_dir

if __name__ == "__main__":
    output_directory = run_simulation_with_params_ga()
    print(f"GA-based simulation completed. Output files are in: {output_directory}")
