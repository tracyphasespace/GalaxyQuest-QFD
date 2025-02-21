# src/simulation_params.py
#--- START OF FILE simulation_params.py ---
# src/simulation_params.py
class SimulationParams:
    """
    Parameters for the N-body simulation.
    Attributes:
        dt_min (float): Minimum time step.
        dt_max (float): Maximum time step.
        CFL (float): CFL condition coefficient for adaptive time step.
        softening_length (float): Softening length for gravitational forces.
        interaction_radius_kpc (float): Interaction radius for localized N-body force calculation (kpc).
        verbosity (int): Verbosity level (0: None, 1: Basic, 2: Detailed).
        output_interval (int): Interval (in steps) for outputting diagnostics.
        log_level (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
    """
    def __init__(self, dt_min, dt_max, CFL, softening_length, interaction_radius_kpc,
                 verbosity, output_interval, log_level):
        """
        Initializes SimulationParams.
        Args:
            dt_min (float): Minimum time step.
            dt_max (float): Maximum time step.
            CFL (float): CFL condition coefficient.
            softening_length (float): Softening length.
            interaction_radius_kpc (float): Interaction radius (kpc).
            verbosity (int): Verbosity level.
            output_interval (int): Output interval.
            log_level (str): Logging level.
        """
        if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [dt_min, dt_max, CFL, softening_length, interaction_radius_kpc]):
            raise ValueError("All numeric parameters must be positive.")

        if not isinstance(verbosity, int) or verbosity not in [0, 1, 2]:
            raise ValueError("Verbosity level must be 0, 1, or 2.")

        if not isinstance(output_interval, int) or output_interval <= 0:
            raise ValueError("Output interval must be a positive integer.")

        if not isinstance(log_level, str) or log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Invalid log level.")

        self.dt_min = float(dt_min)
        self.dt_max = float(dt_max)
        self.CFL = float(CFL)
        self.softening_length = float(softening_length)
        self.interaction_radius_kpc = float(interaction_radius_kpc)
        self.verbosity = verbosity
        self.output_interval = output_interval
        self.log_level = log_level
# --- END OF FILE simulation_params.py ---