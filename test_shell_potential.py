# src/test_shell_potential.py
#--- START OF FILE test_shell_potential.py ---
# src/test_shell_potential.py
import numpy as np
import sys
import os

# --- Add src directory to Python path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if os.path.isdir(src_dir):
    sys.path.insert(0, src_dir)
else:
    print(f"Error: 'src' directory not found at {src_dir}")
    sys.exit(1)

from src.shell_potential import total_spheroidal_force_approximation, SpheroidalShell # Corrected import
from src.galactic_potential import SpheroidalParams
from src.ga_utils import to_ga_point, from_ga_vector # Import to_ga_point, from_ga_vector
import kingdon as kg # Import kingdon


if __name__ == '__main__':
    # --- Example Spheroidal Parameters ---
    example_spheroid_params = SpheroidalParams(a=20.0, b=20.0, c=5.0, M=100.0)

    # --- Example Shells ---
    shells_example = [
        SpheroidalShell(1e11, 5.0, 3.0, np.array([0.0, 0.0, 0.0])), # Corrected SpheroidalShell init
        SpheroidalShell(1e11, 10.0, 6.0, np.array([0.0, 0.0, 0.0])),
        SpheroidalShell(1e11, 15.0, 9.0, np.array([0.0, 0.0, 0.0])),
        SpheroidalShell(1e11, 20.0, 12.0, np.array([0.0, 0.0, 0.0]))
    ]

    # --- Test Position (Cartesian) ---
    test_position_cart = [12.0, 0.0, 0.0]
    test_position_ga = to_ga_point(test_position_cart) # Use to_ga_point

    # --- Calculate Total Spheroidal Force ---
    total_force = total_spheroidal_force_approximation(test_position_ga, shells_example)

    # --- Print Results ---
    print(f"Testing total_spheroidal_force_approximation in isolation:")
    print(f"Test Position (Cartesian): {test_position_cart}")
    print(f"Total Spheroidal Force (Cartesian): {from_ga_vector(total_force)}")

    # --- You can add more test positions or modify shell parameters here to test further ---
# --- END OF FILE test_shell_potential.py ---