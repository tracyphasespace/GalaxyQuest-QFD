# src/plotting.py
#--- START OF FILE plotting.py ---
# src/plotting.py (For Geometric Algebra N-body Simulation)

import matplotlib.pyplot as plt
import numpy as np
import imageio
import os
from src.particles import Star, BlackHole

def configure_matplotlib():
    """Sets up matplotlib parameters for consistent plot style."""
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.75
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['font.size'] = 12

configure_matplotlib()

def plot_star_positions_animation(diagnostics, output_dir="simulation_data"):
    """Creates animation of star positions."""
    star_positions_over_time = diagnostics["star_positions_over_time"]
    filenames = []
    for step_index, positions in enumerate(star_positions_over_time):
        x = [pos[0] for pos in positions]
        y = [pos[1] for pos in positions]
        fig, ax = plt.subplots()
        ax.scatter(x, y, s=1)
        ax.set_xlim(-30, 30)
        ax.set_ylim(-30, 30)
        ax.set_xlabel("x (kpc)")
        ax.set_ylabel("y (kpc)")
        ax.set_title(f"Star Positions - Step {step_index * 10}")
        ax.set_aspect('equal')

        filename = os.path.join(output_dir, f"star_positions_step_{step_index * 10}.png")
        filenames.append(filename)
        plt.savefig(filename)
        plt.close(fig)

    with imageio.get_writer(os.path.join(output_dir, 'star_positions_animation.gif'), mode='I', fps=5) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
        for filename in set(filenames):
             os.remove(filename)

def plot_rotation_curve_evolution(diagnostics, output_dir="simulation_data"):
    """Generates animation of rotation curve evolution."""
    rotation_curves = diagnostics["rotation_curves"]
    filenames = []

    for i, (radii, velocities) in enumerate(rotation_curves):
        fig, ax = plt.subplots()
        ax.plot(radii, velocities, label="Rotation Curve")
        ax.set_xlabel("Radius (kpc)")
        ax.set_ylabel("Velocity (km/s)")
        ax.set_xlim(0, 25)
        ax.set_ylim(0, 250)
        ax.set_title(f"Rotation Curve Evolution - Step {i*10}")
        ax.legend()

        filename = os.path.join(output_dir, f"rotation_curve_step_{i*10}.png")
        filenames.append(filename)
        plt.savefig(filename)
        plt.close(fig)

    with imageio.get_writer(os.path.join(output_dir, 'rotation_curve_evolution.gif'), mode='I', fps=5) as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
        for filename in set(filenames):
            os.remove(filename)

def plot_bh_density_evolution(diagnostics, output_dir="simulation_data"):
    """Generates animation of black hole density evolution."""
    bh_density_profiles = diagnostics["bh_density_profiles"]
    filenames = []
    for step_index, (radii, density) in enumerate(bh_density_profiles):
        step = step_index * 10

        if len(radii) == 0 or len(density) == 0:
            fig, ax = plt.subplots()
            ax.set_title(f"BH Density Evolution - Step {step} (No Data)")
            ax.set_xlabel("Radius (kpc)")
            ax.set_ylabel("Density (10^9 M⊙ / kpc^3)")
            ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', transform=ax.transAxes)
            filename = os.path.join(output_dir, f"bh_density_step_{step}.png")
            filenames.append(filename)
            plt.savefig(filename)
            plt.close(fig)
            continue

        radii = np.array(radii)
        density = np.array(density)

        max_density = np.max(density)
        max_density_index = np.argmax(density)
        max_density_radius = radii[max_density_index]

        core_radius = 0.0
        for i, den in enumerate(density):
            if den < max_density / np.exp(1):
                core_radius = radii[i]
                break

        fig, ax = plt.subplots()
        ax.plot(radii, density, label=f"BH Density at Step {step}")
        ax.set_xlabel("Radius (kpc)")
        ax.set_ylabel("Density (10^9 M⊙ / kpc^3)")
        ax.set_xlim(0, radii[-1] if radii.size > 0 else 1)
        ax.set_ylim(0, max(1.0, max_density * 1.1))
        ax.set_title(f"BH Density Evolution - Step {step}")

        ax.annotate(f"Max Density: {max_density:.3f} at r={max_density_radius:.2f} kpc",
                    xy=(max_density_radius, max_density), xytext=(max_density_radius + 1, max_density * 0.8),
                    arrowprops=dict(arrowstyle="->"))
        if core_radius > 0.0:
          ax.vlines(x=core_radius, ymin=0, ymax=max_density, colors='r', linestyles='dashed', label=f"Core Radius: {core_radius:.2f} kpc")
          ax.annotate(f"Core Radius: {core_radius:.2f} kpc", xy=(core_radius, max_density / np.exp(1)),
                       xytext=(core_radius + 1, max_density / np.exp(1) * 0.8), arrowprops=dict(arrowstyle="->"))

        if "max_bh_mass" in diagnostics and step_index < len(diagnostics["max_bh_mass"]):
            max_bh_mass_val = diagnostics["max_bh_mass"][step_index]
            ax.annotate(f"Max BH Mass: {max_bh_mass_val:.2f} (10^9 M⊙)", xy=(0.7, 0.9), xycoords='axes fraction')

        ax.legend()

        filename = os.path.join(output_dir, f"bh_density_step_{step}.png")
        filenames.append(filename)
        plt.savefig(filename)
        plt.close(fig)

def plot_summary_stats(diagnostics, output_dir="simulation_data", sim_params=None):
    """Creates plots of summary statistics."""
    # Corrected time_steps calculation to match diagnostic data length
    # Check if diagnostics contain valid data
    if not diagnostics["star_counts"] or not diagnostics["velocity_dispersions"] or not diagnostics["bh_halo_masses"]:
        print("Warning: No diagnostic data available for plotting summary statistics.")
        return  # Avoid plotting if there is no data

    min_length = min(len(diagnostics["star_counts"]), len(diagnostics["velocity_dispersions"]), len(diagnostics["bh_halo_masses"]))
    time_steps = np.arange(0, min_length * sim_params.output_interval, sim_params.output_interval)

    fig1, ax1 = plt.subplots()
    ax1.plot(time_steps, diagnostics["star_counts"][:min_length], marker='o', linestyle='-')
    ax1.set_title("Star Count Evolution")
    ax1.set_xlabel("Time Step")
    ax1.set_ylabel("Number of Stars")
    fig1.savefig(os.path.join(output_dir, "star_count_evolution.png"))
    plt.close(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(time_steps, diagnostics["velocity_dispersions"][:min_length], marker='o', linestyle='-')
    ax2.set_title("Stellar Velocity Dispersion Evolution")
    ax2.set_xlabel("Time Step")
    ax2.set_ylabel("Velocity Dispersion (km/s)")
    fig2.savefig(os.path.join(output_dir, "velocity_dispersion_evolution.png"))
    plt.close(fig2)

    fig3, ax3 = plt.subplots()
    ax3.plot(time_steps, diagnostics["bh_halo_masses"][:min_length], marker='o', linestyle='-')
    ax3.set_title("Total Black Hole Halo Mass Evolution")
    ax3.set_xlabel("Time Step")
    ax3.set_ylabel("Total Mass (10^9 M⊙)")
    fig3.savefig(os.path.join(output_dir, "bh_halo_mass_evolution.png"))
    plt.close(fig3)

    fig5, ax5 = plt.subplots()
    ax5.plot(time_steps, diagnostics["star_counts"][:min_length], label="Number of Stars")
    ax5.plot(time_steps, diagnostics["velocity_dispersions"][:min_length], label="Velocity Dispersion (scaled)")
    ax5.plot(time_steps, diagnostics["bh_halo_masses"][:min_length], label="BH Halo Mass")
    ax5.set_xlabel("Time Step")
    ax5.set_ylabel("Stars/Dispersion/Mass")
    ax5.set_title("Combined Summary Statistics")
    ax5.legend()
    fig5.savefig(os.path.join(output_dir, "combined_plot.png"))
    plt.close(fig5)

def plot_max_bh_mass_evolution(diagnostics, output_dir="simulation_data", sim_params=None): # Corrected function signature - added sim_params=None
    """Plots max BH mass evolution."""
    # Corrected time_steps calculation to use sim_params
    # Check if diagnostics contain valid data
    if not diagnostics["max_bh_mass"]:
        print("Warning: No max_bh_mass data available for plotting max BH mass evolution.")
        return # Exit if no data

    time_steps = np.arange(0, len(diagnostics["max_bh_mass"]) * sim_params.output_interval, sim_params.output_interval)
    fig, ax = plt.subplots()
    ax.plot(time_steps, diagnostics["max_bh_mass"], marker='o', linestyle='-')
    ax.set_title("Maximum Black Hole Mass Evolution")
    ax.set_xlabel("Time Step (x10)")
    ax.set_ylabel("Mass (10^9 M⊙)")
    plt.savefig(os.path.join(output_dir, "max_bh_mass_evolution.png"))
    plt.close(fig)

def plot_particle_distribution(final_particles, output_dir="simulation_data", step=None):
    """Generates 3D and 2D particle distribution plots."""
    stars = [p for p in final_particles if isinstance(p, Star)]
    bhs = [p for p in final_particles if isinstance(p, BlackHole)]

    star_positions = np.array([p.position for p in stars]) if stars else np.empty((0,3))
    bh_positions = np.array([p.position for p in bhs]) if bhs else np.empty((0,3))

    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(projection='3d')
    if star_positions.size > 0:
        ax_3d.scatter(star_positions[:, 0], star_positions[:, 1], star_positions[:, 2], label="Stars", s=10, alpha=0.5, color='blue')
    if bh_positions.size > 0:
        ax_3d.scatter(bh_positions[:, 0], bh_positions[:, 1], bh_positions[:, 2], label="Black Holes", s=30, alpha=0.8, color='red')
    ax_3d.set_xlabel("x (kpc)")
    ax_3d.set_ylabel("y (kpc)")
    ax_3d.set_zlabel("z (kpc)")
    # Initialize title_step to a default value *before* the conditional
    title_step = "Unknown Step" # ADDED: Initialize title_step here

    title_step = f"Step {step}" if step is not None else "Final Step"

    ax_3d.set_title(f"Particle Distribution 3D - {title_step}")
    ax_3d.legend()
    fig_3d.savefig(os.path.join(output_dir, "particle_distribution_3d.png"))
    plt.close(fig_3d)

    fig_2d = plt.figure()
    ax_2d = fig_2d.add_subplot()
    if star_positions.size > 0:
        ax_2d.scatter(star_positions[:, 0], star_positions[:, 1], label="Stars", s=10, alpha=0.5, color='blue')
    if bh_positions.size > 0:
        ax_2d.scatter(bh_positions[:, 0], bh_positions[:, 1], label="Black Holes", s=30, alpha=0.8, color='red')

    ax_2d.set_xlabel("x (kpc)")
    ax_2d.set_ylabel("y (kpc)")
    ax_2d.set_aspect('equal')
    ax_2d.set_title(f"Particle Distribution (X-Y Projection) - {title_step}")
    ax_2d.legend()
    fig_2d.savefig(os.path.join(output_dir, "particle_distribution_2d.png"))
    plt.close(fig_2d)
# --- END OF FILE plotting.py ---