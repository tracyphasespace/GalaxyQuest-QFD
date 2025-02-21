# src/particles.py
#--- START OF FILE particles.py ---
# src/particles.py
import numpy as np
from src.ga_utils import to_ga_point, to_ga_vector # Import to_ga_point, to_ga_vector
import kingdon as kg # Import kingdon

class AbstractParticle:
    """
    Abstract base class for particles.
    Attributes:
        position (np.array): Cartesian position (3D).
        velocity (np.array): Cartesian velocity (3D).
        mass (float): Mass of the particle.
        position_ga (kingdon.MultiVector): Position in GA representation.
        velocity_ga (kingdon.MultiVector): Velocity in GA representation.
    """
    def __init__(self, position, velocity, mass):
        """
        Initializes an AbstractParticle.
        Args:
            position (np.array): Initial Cartesian position.
            velocity (np.array): Initial Cartesian velocity.
            mass (float): Mass of the particle.
        """
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.mass = float(mass)
        self.position_ga = to_ga_point(self.position) # Use kingdon version
        self.velocity_ga = to_ga_vector(self.velocity) # Use kingdon version

class Star(AbstractParticle):
    """Represents a star particle."""
    pass

class BlackHole(AbstractParticle):
    """Represents a black hole particle."""
    pass
# --- END OF FILE particles.py ---