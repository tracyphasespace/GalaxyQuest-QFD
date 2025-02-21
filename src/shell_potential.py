# src/shell_potential.py
#--- START OF FILE shell_potential.py ---
# src/shell_potential.py
import numpy as np
from numba import njit # Corrected import: removed 'overload'
import kingdon as kg # Import kingdon
from typing import TYPE_CHECKING

alg = kg.Algebra(p=3, q=0, r=0) # Create Algebra instance here

if TYPE_CHECKING:
    from typing import Tuple, Any

# Assume ga_utils.py provides these (define placeholders here if not available for demonstration)
from src.ga_utils import ga_vector_add, ga_vector_subtract, ga_scalar_mul, ga_vector_norm_sq, ga_vector_normalize, to_ga_point, from_ga_vector # Corrected import - using ga_vector_subtract, removed typo

def ga_vector_add(v1, v2):
    return v1 + v2

def ga_vector_sub(v1, v2): # No longer used, can be removed if desired, or kept for potential future use.
    return v1 - v2

def ga_scalar_mul(scalar, v):
    return scalar * v

def ga_vector_norm_sq(v):
    return v * v  # Assuming squaring a PGA vector gives its squared norm as a scalar

def ga_vector_normalize(v):
    norm_sq_mv = ga_vector_norm_sq(v) # Get norm squared as MultiVector
    norm_sq_val = norm_sq_mv.e # Extract scalar value of norm squared
    norm = norm_sq_val**0.5 if norm_sq_val is not None else 0.0 # Take square root, handle None case
    return v / norm if float(norm) != 0 else kg.MultiVector(0)  # Avoid division by zero, return zero vector, adjust kingdon zero vector if needed

def to_ga_point(np_array):
    # Corrected to use keyword 'values' to pass components
    return alg.multivector(values=[np_array[0], np_array[1], np_array[2]], grades=(1,)) # Explicitly pass values and grades

def from_ga_vector(ga_vector):
    return np.array([float(ga_vector[0]), float(ga_vector[1]), float(ga_vector[2])]) # Assuming vector parts are indices 0, 1, 2


class SpheroidalShell:
    def __init__(self, mass: float, semimajor_axis: float, semiminor_axis: float, center_np: np.ndarray):
        self.mass = mass
        self.semimajor_axis = semimajor_axis
        self.semiminor_axis = semiminor_axis
        self.center_ga = to_ga_point(center_np) # Center as kingdon GA point


# ---  Implementation of spheroidal_shell_force_approximation without overload ---

def spheroidal_shell_force_approximation(position_ga, shells): # Changed shell to shells to match forces.py
    """
    Approximates the gravitational force exerted by a spheroidal shell on a given position.

    This function uses type-based specialization via @overload to handle different input types efficiently.
    Currently specialized for:
        - position_ga: kingdon.MultiVector (GA point representing position)
        - shell: SpheroidalShell object

    Args:
        position_ga (MultiVector): The position at which to calculate the force (GA point).
        shells (list of SpheroidalShell): A list of SpheroidalShell objects defining the shells. # Changed shell to shells

    Returns:
        kingdon.MultiVector: The gravitational force vector (GA vector).
    """

    # --- Specialized implementation for kingdon MultiVector and list of SpheroidalShell ---
    if isinstance(position_ga, kg.MultiVector) and isinstance(shells, list): # Specialize for list of shells and kingdon MultiVector
        total_force_ga = kg.MultiVector(alg, values=None) # Initialize zero force using kingdon zero vector
        for shell in shells: # Iterate over shells
            if not isinstance(shell, SpheroidalShell): # Basic type check inside loop for robustness
                continue # Skip if not a SpheroidalShell, or raise error if strict type enforcement is needed

            G = 1.0  # Gravitational constant (adjust as needed)
            softening_radius_sq = 1e-9 # Small softening to avoid singularities

            relative_pos_ga = ga_vector_sub(position_ga, shell.center_ga) # Vector from shell center to position
            r_vec_ga = ga_vector_subtract(shell.center_ga, position_ga) # Use ga_vector_subtract
            r_sq_ga = ga_vector_norm_sq(r_vec_ga) # Kingdon GA norm_sq
            # Corrected line to access scalar part using .e attribute
            r_sq_val = r_sq_ga.e
            r_sq = float(r_sq_val) if r_sq_val is not None else 0.0 # Extract scalar value and convert to float, handle None case
            # --- End of corrected line ---

            if r_sq <= softening_radius_sq:
                continue # Inside softening radius, force from this shell is zero, move to next shell

            r = r_sq**0.5

            if r > shell.semimajor_axis: # Outside shell - Shell Theorem applies
                force_magnitude = -G * shell.mass / (r_sq + softening_radius_sq) # Softened force magnitude
                force_direction = ga_vector_normalize(r_vec_ga) # Kingdon GA normalize
                force_ga = ga_scalar_mul(force_magnitude, force_direction) # Scalar multiply
                total_force_ga = ga_vector_add(total_force_ga, force_ga) # Accumulate force
            else: # Inside shell - Linearized approximation
                normalized_r = r / shell.semimajor_axis # Distance as fraction of semi-major axis
                force_magnitude_inner = -G * shell.mass / (shell.semimajor_axis**2 + softening_radius_sq) # Force at outer "radius"
                force_magnitude = force_magnitude_inner * normalized_r # Linearly reduce force inwards
                force_direction = ga_vector_normalize(r_vec_ga) # Kingdon GA normalize
                force_ga = ga_scalar_mul(force_magnitude, force_direction) # Scalar multiply
                total_force_ga = ga_vector_add(total_force_ga, force_ga) # Accumulate force

        return total_force_ga # Return total force from all shells

    # --- Fallback implementation or error for unsupported types ---
    else:
        raise TypeError(f"Unsupported input types for spheroidal_shell_force_approximation. "
                        f"Expected position_ga to be kingdon.MultiVector and shells to be list of SpheroidalShell. " # Changed shell to shells
                        f"Got position_ga type: {type(position_ga)}, shells type: {type(shells)}") # Changed shell to shells


def total_spheroidal_force_approximation(position_ga, shells): # Renamed to total_spheroidal_force_approximation, and expects list of shells
    """
    Public facing function that calls the overloaded implementation.
    This function now expects a list of shells.
    """
    return spheroidal_shell_force_approximation(position_ga, shells)


# --- Example usage and testing ---
if __name__ == '__main__':
    # Example usage
    shell_params_list = [{ # List of shell parameter dictionaries
        'mass': 1e11,  # Solar masses
        'semimajor_axis': 5.0, # kpc
        'semiminor_axis': 3.0, # kpc
        'center_np': np.array([0.0, 0.0, 0.0]) # kpc
    }, {
        'mass': 0.5e11,  # Solar masses
        'semimajor_axis': 10.0, # kpc
        'semiminor_axis': 6.0, # kpc
        'center_np': np.array([0.0, 0.0, 0.0]) # kpc
    }]
    shells = [SpheroidalShell(**shell_params) for shell_params in shell_params_list] # Create list of SpheroidalShell objects

    positions_np = [
        np.array([10.0, 0.0, 0.0]),  # Outside the inner shell, inside outer
        np.array([2.0, 0.0, 0.0]),   # Inside both shells
        np.array([0.0, 0.0, 0.0]),   # At the center
        np.array([15.0, 0.0, 0.0])   # Outside both shells
    ]

    for pos_np in positions_np:
        position_ga = to_ga_point(pos_np)
        force_ga = total_spheroidal_force_approximation(position_ga, shells) # Call total_spheroidal_force_approximation
        force_np = from_ga_vector(force_ga)

        print(f"Position: {pos_np} kpc")
        print(f"Total Force (GA): {force_ga}")
        print(f"Total Force (NumPy vector): {force_np}")
        print("-" * 30)
# --- END OF FILE shell_potential.py ---