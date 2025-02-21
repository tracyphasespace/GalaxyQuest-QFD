# src/ga_utils.py
#--- START OF FILE ga_utils.py ---
# src/ga_utils.py
import kingdon as kg
import numpy as np

alg = kg.Algebra(p=3, q=0, r=0) # Create Algebra instance here

# Assuming kingdon uses a similar layout concept, or if it's implicit, adjust accordingly.
# For PGA(3D), we might be using PGA or CGA in Kingdon. Let's assume PGA-like behavior for vectors/points.
# Kingdon might not have a 'layout' object in the same way as clifford. Adapt as needed.

def to_ga_point(cartesian_position):
    """
    Converts Cartesian coordinates to a GA point (homogeneous vector).
    Args:
        cartesian_position (list or np.array): Cartesian (x, y, z) position.
    Returns:
        kingdon.MultiVector: Kingdon MultiVector point representation.
    """
    x, y, z = cartesian_position
    # Assuming kingdon point representation is similar to PGA, might need adjustment
    return kg.MultiVector(alg, values=[x, y, z], grades=(1,)) # Use alg.vector() with individual components for point creation

def from_ga_point(ga_point):
    """
    Converts a GA point back to Cartesian coordinates.
    Args:
        ga_point (kingdon.MultiVector): Kingdon MultiVector point.
    Returns:
        list: Cartesian (x, y, z) coordinates.
    """
    return from_ga_vector(ga_point) # Re-using from_ga_vector as points are now vectors

def to_ga_vector(cartesian_velocity):
    """
    Converts Cartesian velocity to a GA vector (direction).
    Args:
        cartesian_velocity (list or np.array): Cartesian (vx, vy, vz) velocity.
    Returns:
        kingdon.MultiVector: Kingdon MultiVector vector representation.
    """
    vx, vy, vz = cartesian_velocity
    return alg.multivector(values=[vx, vy, vz], grades=(1,)) # Use alg.vector() with individual components for vector creation

def from_ga_vector(ga_vector):
    """
    Converts a GA vector back to Cartesian velocity.
    Args:
        ga_vector (kingdon.MultiVector): Kingdon MultiVector vector.
    Returns:
        list: Cartesian (vx, vy, vz) velocity components.
    """
    # Corrected to use attribute access for vector components (.e1, .e2, .e3)
    return [float(ga_vector.e1), float(ga_vector.e2), float(ga_vector.e3)] # Access vector components using .e1, .e2, .e3

def ga_vector_add(ga_vec1, ga_vec2):
    """Adds two GA vectors.
    Args:
        ga_vec1 (kingdon.MultiVector): First GA vector.
        ga_vec2 (kingdon.MultiVector): Second GA vector.
    Returns:
        kingdon.MultiVector: Sum of the two vectors.
    """
    return ga_vec1 + ga_vec2 # Assuming '+' operator works for vector addition

def ga_vector_subtract(ga_vec1, ga_vec2):
    """Subtracts the second GA vector from the first.
    Args:
        ga_vec1 (kingdon.MultiVector): First GA vector.
        ga_vec2 (kingdon.MultiVector): Second GA vector.
    Returns:
        kingdon.MultiVector: Difference of the two vectors.
    """
    return ga_vec1 - ga_vec2 # Assuming '-' operator works for vector subtraction

def ga_dot_product(ga_vec1, ga_vec2):
    """Calculates the dot product of two GA vectors (scalar product).
    Args:
        ga_vec1 (kingdon.MultiVector): First GA vector.
        ga_vec2 (kingdon.MultiVector): Second GA vector.
    Returns:
        kingdon.MultiVector: Dot product (scalar). # Kingdon might return scalar directly, or still a MultiVector
    """
    return ga_vec1 | ga_vec2 # Placeholder - adjust if kingdon uses a different operator/function for dot product. Using inner product '|'

def ga_cross_product(ga_vec1, ga_vec2):
    """Calculates the cross product of two GA vectors (using the pseudoscalar).
    Args:
        ga_vec1 (kingdon.MultiVector): First GA vector.
        ga_vec2 (kingdon.MultiVector): Second GA vector.
    Returns:
        kingdon.MultiVector: Cross product (bivector). # Kingdon might return bivector, or still a MultiVector
    """
    return ga_vec1 ^ ga_vec2 # Placeholder - adjust if kingdon uses a different operator/function for cross product. Using outer product '^'

def ga_scalar_mul(scalar, v):
    return scalar * v

def ga_vector_norm_sq(v):
    return v * v # Placeholder - adjust if kingdon uses a different method for squared norm. Using geometric product for squared norm

def ga_vector_normalize(v):
    norm_sq_mv = ga_vector_norm_sq(v) # Get norm squared as MultiVector
    norm_sq_val = norm_sq_mv.e # Extract scalar value of norm squared
    norm_mv = kg.MultiVector(alg, values=[norm_sq_val**0.5], grades=(0,)) if norm_sq_val is not None else kg.MultiVector(0) # Take square root and wrap in MultiVector
    norm_val = norm_mv.e # Extract scalar value *after* sqrt (now from MultiVector again)
    return v / norm_val if float(norm_val) != 0 else kg.MultiVector(0) # Avoid division by zero, return zero vector, adjust kingdon zero vector if needed

if __name__ == '__main__':
    cart_pos = [1.0, 2.0, 3.0]
    ga_p = to_ga_point(cart_pos)
    cart_pos_back = from_ga_point(ga_p)
    print(f"Cartesian Position: {cart_pos}, GA Point: {ga_p}, Back to Cartesian: {cart_pos_back}")

    cart_vel = [0.1, -0.2, 0.5]
    ga_v = to_ga_vector(cart_vel)
    cart_vel_back = from_ga_vector(ga_v)
    print(f"Cartesian Velocity: {cart_vel}, GA Vector: {ga_v}, Back to Cartesian: {cart_vel_back}")

    ga_v2 = to_ga_vector([0.3, 0.4, -0.1])
    ga_sum = ga_vector_add(ga_v, ga_v2)
    print(f"Vector Sum: {ga_sum}, Cartesian Sum: {from_ga_vector(ga_sum)}")
# --- END OF FILE ga_utils.py ---