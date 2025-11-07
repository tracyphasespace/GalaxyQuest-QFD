# Physics Architecture: Cl(3,3) Phase Space for QFD Galactic Dynamics

**Technical Design Document**
**Status**: Architecture Design / Pre-Implementation
**Date**: 2025-11-07

---

## Executive Summary

This document describes the physics architecture for the GalaxyQuest-QFD simulator, transitioning from a traditional N-body approach to a **collisionless Boltzmann + phase space geometric algebra** framework using Cl(3,3).

**Key Insight**: Galaxies with 10¹² particles are NOT like solar systems with deterministic orbits. They are **statistical mechanical systems** described by phase space distributions evolving under self-consistent mean fields.

---

## I. The Problem with Traditional N-body

### Solar System Paradigm (What We're NOT Doing)

```python
# Traditional N-body: O(N²) or O(N log N) with tree codes
for particle_i in particles:
    force = 0
    for particle_j in particles:
        if i != j:
            force += G * m_i * m_j / r_ij²
    acceleration = force / m_i
```

**Issues:**
- Scales poorly: 10¹² particles → computationally intractable
- Misses fundamental physics: Galaxies are collisionless, not collision-dominated
- Wrong conceptual model: Particles don't have "orbits" - they exist as probability distributions

### Galaxy Reality (What We ARE Doing)

```python
# Self-consistent field + Boltzmann distribution
f(Ψ, t)  # Phase space distribution in Cl(3,3)

# Evolution: ∂f/∂t + {f, H} = 0
# where H = p²/2m + Φ[f](x,t)  (self-consistent!)
```

**Advantages:**
- Scales naturally: Distribution represented by macro-particles
- Correct physics: Collisionless Boltzmann equation
- Natural framework: Phase space is Cl(3,3) with symplectic structure

---

## II. Why Cl(3,3) Phase Space?

### Traditional Split Representation

```
Configuration space: q = (x, y, z) ∈ ℝ³
Momentum space:      p = (pₓ, pᵧ, pᵤ) ∈ ℝ³
Phase space:         (q, p) ∈ ℝ³ × ℝ³ = ℝ⁶
```

**Problems:**
- Position and momentum treated separately
- Symplectic structure imposed externally
- Poisson brackets defined ad-hoc
- Hamilton's equations require separate update logic

### Unified Cl(3,3) Representation

```
Phase space point: Ψ = x e₁ + y e₂ + z e₃ + pₓ e₄ + pᵧ e₅ + pᵤ e₆

Metric signature: (+++---) = (+,+,+,-,-,-)

Basis vectors:
    e₁² = e₂² = e₃² = +1  (position: spacelike)
    e₄² = e₅² = e₆² = -1  (momentum: timelike)
```

**Advantages:**
1. **Symplectic structure is intrinsic**: Encoded in the (+++---) metric
2. **Liouville's theorem automatic**: Phase space volume = |det(metric)| preserved
3. **Poisson brackets = geometric products**: `{A, B} = (∂A/∂Ψ) * (∂B/∂Ψ)`
4. **Hamilton's equations unified**: `dΨ/dt = ∇_Ψ H * Ω` where Ω is symplectic form

### Geometric Objects in Cl(3,3)

#### Vectors (Grade 1): Phase Space Points
```
Ψ = x e₁ + y e₂ + z e₃ + pₓ e₄ + pᵧ e₅ + pᵤ e₆
```

#### Bivectors (Grade 2): Planes and Angular Momentum
```
Orbital plane:      L = L_xy e₁∧e₂ + L_xz e₁∧e₃ + L_yz e₂∧e₃
Ecliptic plane E₁:  E₁ = e₁∧e₂ (xy-plane)
Rotated plane E₂:   E₂ = cos(θ) e₁∧e₂ + sin(θ) e₁∧e₃
```

#### Motors (Grade 0,2,4,6): Transformations
```
M = exp(θ/2 (e₁∧e₂)) = rotor in position space
Orbital motion = motor combining rotation + translation
```

#### Symplectic 2-form (Grade 2): Canonical Structure
```
ω = e₁∧e₄ + e₂∧e₅ + e₃∧e₆
Preserves phase space volume: dΨ₁ ∧ dΨ₂ ∧ ... ∧ dΨₙ
```

---

## III. Multi-Scale Architecture

The QFD simulation requires **three computational scales**:

### Level 1: SMBH Binary (2 particles, explicit)

**Physics**: Two supermassive black holes forming binary after galaxy collision

**Representation**:
```python
class SMBHBinary:
    smbh1: PhaseSpacePoint_Cl33  # Ψ₁ ∈ Cl(3,3)
    smbh2: PhaseSpacePoint_Cl33  # Ψ₂ ∈ Cl(3,3)

    def orbital_plane(self) -> Bivector_Cl33:
        """Current orbital plane as bivector"""
        L = (Ψ₁.position × Ψ₁.momentum) + (Ψ₂.position × Ψ₂.momentum)
        return L  # Bivector e₁∧e₂ + ...

    def barycenter(self) -> PhaseSpacePoint_Cl33:
        """Center of mass in phase space"""
        M = smbh1.mass + smbh2.mass
        return (smbh1.mass * Ψ₁ + smbh2.mass * Ψ₂) / M

    def at_periastron(self) -> bool:
        """Check for saddle-point ejection condition"""
        r = |Ψ₁.position - Ψ₂.position|
        return r < r_min + tolerance

    def eject_plasma(self) -> PlasmaEjecta:
        """Saddle-point triggered mass ejection"""
        direction = self.orbital_plane().dual()  # Perpendicular
        mass = calculate_ejection_mass(...)
        velocity = escape_velocity(...)
        return PlasmaEjecta(direction, mass, velocity)
```

**Integration**: High-fidelity symplectic integrator (e.g., 4th-order Yoshida)

**Timestep**: Adaptive, fine-grained (dt ~ 0.01 orbital period)

**Why explicit?**: Only 2 bodies, critically important for defining central potential and triggering disk formation

### Level 2: IMBH/Star Distribution (10⁹-10¹² particles, statistical)

**Physics**: Phase space distribution f(Ψ,t) evolving under collisionless Boltzmann equation

**Representation**:
```python
class PhaseSpaceDistribution:
    macro_particles: Array[N_macro, 6]  # Each samples f(Ψ,t)
    weights: Array[N_macro]              # Each represents ~10⁶ real particles

    def evolve_boltzmann(self, Φ_total, dt):
        """
        Solve: ∂f/∂t + {f, H} = 0
        where H = p²/2m + Φ_total(x,t)
        """
        # Hamilton's equations in Cl(3,3):
        # dq/dt = ∂H/∂p
        # dp/dt = -∂H/∂q

        for i in range(N_macro):
            Ψ = self.macro_particles[i]

            # Extract position/momentum (grade projection)
            q = Ψ.position_part()  # e₁,e₂,e₃ components
            p = Ψ.momentum_part()  # e₄,e₅,e₆ components

            # Hamiltonian derivatives
            dH_dp = p / mass  # Kinetic part
            dH_dq = -gradient(Φ_total, q)  # Potential part

            # Update in phase space
            q_new = q + dH_dp * dt
            p_new = p + dH_dq * dt

            self.macro_particles[i] = PhaseSpacePoint(q_new, p_new)
```

**Integration**: Symplectic (Velocity Verlet or Leap-Frog in phase space)

**Timestep**: Larger than SMBH binary (dt ~ 0.1-1.0 Myr)

**Why statistical?**: 10¹² particles can't be tracked individually; distribution captures all relevant physics

### Level 3: Mean Field (Self-Consistent Potential)

**Physics**: The phase space distribution creates gravitational potential that influences itself

**Representation**:
```python
class MeanFieldCalculator:
    grid: Grid3D  # Spatial grid for Φ(x)

    def calculate_potential(self, distribution: PhaseSpaceDistribution):
        """
        Solve: ∇²Φ = 4πG ρ(x)
        where ρ(x) = ∫ f(x,p) d³p
        """
        # 1. Deposit mass from macro-particles onto grid (CIC/NGP)
        density = self.deposit_density(distribution)

        # 2. Solve Poisson equation
        potential = self.solve_poisson(density)  # FFT or SOR

        # 3. Calculate force = -∇Φ
        force_grid = -self.gradient(potential)

        return potential, force_grid

    def total_potential(self, smbh_binary, distribution):
        """
        Φ_total = Φ_binary + Φ_mean
        """
        Φ_binary = self.binary_potential(smbh_binary)
        Φ_mean = self.calculate_potential(distribution)
        return Φ_binary + Φ_mean
```

**Self-Consistency Loop**:
```python
# At each timestep:
f(t) → ρ(x) → Φ_mean[f](x) → H(x,p,t) → ∂f/∂t → f(t+dt)
                ↑                           ↓
                └───────── self-consistent ──┘
```

---

## IV. Collisionless Boltzmann Dynamics

### The Vlasov Equation in Cl(3,3)

**Traditional form** (in 6D phase space):
```
∂f/∂t + v·∇_x f - ∇_x Φ·∇_v f = 0
```

**Geometric form** (in Cl(3,3)):
```
∂f/∂t + {f, H} = 0

where Poisson bracket: {f, H} = (∇_Ψ f) · (Ω · ∇_Ψ H)
and symplectic form: Ω = e₁∧e₄ + e₂∧e₅ + e₃∧e₆
```

**Interpretation**: Distribution flows along Hamiltonian vector field in phase space, preserving volume (Liouville)

### Phase Mixing and Violent Relaxation

**Violent Relaxation** (Lynden-Bell mechanism):
```
Time-varying potential Φ(x,t) → phase mixing in phase space
Fast timescale: t_relax ~ t_crossing ~ few 100 Myr
Drives toward maximum entropy: f → f_Boltzmann
```

**Implementation**:
```python
def track_phase_mixing(distribution, time):
    """
    Measure entropy: S = -∫ f log f d³x d³p
    Boltzmann distribution: maximum S for given E, L
    """
    entropy = calculate_entropy(distribution)

    # Check for equilibration
    if dS/dt < threshold:
        print("Violent relaxation complete")
        print("System reached Boltzmann distribution")
```

### Two-Body Relaxation (Slow)

**Two-body encounters** (rare in collisionless regime):
```
Relaxation time: t_2body ~ N × t_crossing ~ 100 Gyr

where N ~ 10¹² (number of particles)
```

**QFD Lifecycle**:
- 0-10 Gyr: Violent relaxation (collisionless) dominates
- 10-100 Gyr: Slow two-body relaxation → thermal equilibrium
- t > 100 Gyr: Zombie state (Boltzmann distribution)

---

## V. Ecliptic Plane Collision Mechanics

### Representation as Bivectors

**Galaxy 1** ecliptic plane:
```
E₁ = e₁∧e₂  (xy-plane)
```

**Galaxy 2** ecliptic plane (rotated by angle θ about z-axis, tilted by φ about x-axis):
```
E₂ = cos(θ)cos(φ) e₁∧e₂ + sin(θ)cos(φ) e₁∧e₃ + sin(φ) e₂∧e₃
```

### Collision Dynamics

**Geometric product of planes**:
```
E₁ * E₂ = (e₁∧e₂) * (cos(θ)cos(φ) e₁∧e₂ + sin(θ)cos(φ) e₁∧e₃ + sin(φ) e₂∧e₃)

Result contains:
- Scalar part: measure of alignment (E₁ · E₂)
- Bivector part: new emergent plane
- Higher grades: measure of chaos/turbulence
```

**Physical interpretation**:
- Scalar → 0: Orthogonal planes → maximum chaos
- Scalar → 1: Aligned planes → smooth merger
- Bivector: Defines new SMBH binary orbital plane

### IMBH Halo Chaos

When two planar distributions collide:

```python
def collide_planes(galaxy1, galaxy2):
    """
    Plane collision → chaos → redistribution
    """
    E₁ = galaxy1.ecliptic_plane  # Bivector
    E₂ = galaxy2.ecliptic_plane  # Bivector

    # Geometric product
    collision_result = E₁ * E₂

    # Extract components
    alignment = collision_result.scalar_part()
    new_plane = collision_result.bivector_part()
    chaos_measure = collision_result.higher_grades()

    if alignment < 0.5:  # Highly inclined
        # Maximum chaos → spheroidal redistribution
        redistribute_to_spheroid(galaxy1.imbhs, galaxy2.imbhs)
    else:
        # Partial alignment → disk with thickening
        redistribute_to_thick_disk(new_plane, chaos_measure)

    # New SMBH binary defines ultimate plane
    smbh_binary_plane = form_binary(galaxy1.smbh, galaxy2.smbh)

    return smbh_binary_plane, chaos_measure
```

---

## VI. Binary Black Hole Dynamics

### Detection of BH Pairs

```python
def detect_bh_binaries(imbh_distribution, threshold_separation, threshold_velocity):
    """
    Use KD-tree on GPU to find gravitationally bound pairs
    """
    # Spatial KD-tree
    positions = imbh_distribution.positions()
    tree = build_kdtree_gpu(positions)

    # Find pairs within threshold separation
    pairs = tree.query_pairs(threshold_separation)

    binaries = []
    for (i, j) in pairs:
        Ψᵢ = imbh_distribution[i]
        Ψⱼ = imbh_distribution[j]

        # Check if bound (E < 0)
        r = |Ψᵢ.position - Ψⱼ.position|
        v_rel = |Ψᵢ.velocity - Ψⱼ.velocity|

        E_tot = 0.5 * μ * v_rel² - G * M_tot / r

        if E_tot < 0:  # Bound
            binary = BinaryPair_Cl33(Ψᵢ, Ψⱼ)
            binaries.append(binary)

    return binaries
```

### Binary Tracking in Phase Space

```python
class BinaryPair_Cl33:
    """Two BHs represented as single phase space entity"""

    # Center of mass (single phase space point)
    com: PhaseSpacePoint_Cl33

    # Relative orbit (motor: rotation + translation)
    orbit: Motor_Cl33

    # Orbital elements (computed from motor)
    semimajor_axis: float
    eccentricity: float
    orbital_plane: Bivector_Cl33

    def evolve(self, dt):
        """
        Binary evolution in phase space
        """
        # COM motion in external potential
        self.com = hamiltonian_flow(self.com, Φ_external, dt)

        # Relative orbit (Kepler problem in Cl(3,3))
        self.orbit = kepler_step_motor(self.orbit, dt)

    def at_periastron(self) -> bool:
        """Saddle-point condition for ejection"""
        r = self.orbit.separation()
        r_min = self.semimajor_axis * (1 - self.eccentricity)
        return abs(r - r_min) < tolerance

    def eject_mass(self) -> Ejecta:
        """
        Periastron passage → gravitational tidal torque
        → saddle-point mass ejection
        """
        # Direction perpendicular to orbital plane
        direction = self.orbital_plane.dual()

        # Ejection velocity (escape velocity scale)
        v_eject = sqrt(2 * G * M_total / r_periastron)

        # Mass loss (tidal disruption of accretion disk)
        mass_ejected = calculate_tidal_mass_loss(...)

        return Ejecta(direction, v_eject, mass_ejected)
```

---

## VII. Star Formation from Ejecta

### SMBH Binary → Disk Stars

```python
def form_disk_stars(smbh_binary, plasma_ejecta):
    """
    Plasma ejecta from SMBH binary cools → fragments → stars
    Occurs in SMBH binary orbital plane
    """
    E_binary = smbh_binary.orbital_plane()  # Bivector

    # Ejecta cooling time
    t_cool = cooling_time(plasma_ejecta.temperature)

    # Fragmentation → Jeans mass
    M_jeans = jeans_mass(plasma_ejecta.density, plasma_ejecta.temperature)
    N_stars = plasma_ejecta.mass / M_jeans

    # Create star particles in phase space
    stars = []
    for i in range(N_stars):
        # Position: Sample disk in plane E_binary
        r, θ = sample_disk_distribution(E_binary)
        q = to_cartesian(r, θ, E_binary)

        # Velocity: Circular orbit + dispersion
        v_circ = sqrt(G * M_enclosed(r) / r)
        v = circular_velocity(v_circ, E_binary) + random_dispersion()
        p = mass_star * v

        # Create phase space point
        Ψ_star = PhaseSpacePoint_Cl33(q, p)
        stars.append(Ψ_star)

    return stars
```

### BH Binaries → Halo Stars

```python
def form_halo_stars(bh_binaries):
    """
    Smaller BH binary ejecta → brown dwarfs, Pop II stars
    Isotropic distribution (no preferred plane)
    """
    halo_stars = []

    for binary in bh_binaries:
        if binary.at_periastron():
            ejecta = binary.eject_mass()

            # Lower mass ejecta → lower mass stars
            M_star = ejecta.mass / 100  # Fragmentation

            # Isotropic velocity distribution
            v_eject = ejecta.velocity
            v_random = random_unit_vector() * v_eject

            # Phase space point
            Ψ_star = PhaseSpacePoint_Cl33(
                binary.com.position,
                M_star * v_random
            )

            halo_stars.append(Ψ_star)

    return halo_stars
```

---

## VIII. Long-Timescale Evolution

### Differential Timestepping

**Multi-rate integration**:
```
SMBH binary:        dt_fast  = 0.01 Myr   (high fidelity)
Distribution bulk:  dt_medium = 1.0 Myr    (statistical)
Zombie relaxation:  dt_slow  = 100 Myr     (thermal equilibrium)
```

**Implementation**:
```python
class MultiRateIntegrator:
    def step(self, t, dt_coarse):
        """
        Subcycle fast components within coarse step
        """
        # Subcycle SMBH binary
        n_sub = dt_coarse / dt_fast
        for i in range(n_sub):
            smbh_binary.evolve(dt_fast)

        # Update mean field once per coarse step
        Φ_total = calculate_mean_field(smbh_binary, distribution)

        # Evolve distribution with coarse step
        distribution.evolve_boltzmann(Φ_total, dt_coarse)
```

### Zombie State Detection

**Criteria for thermal equilibrium**:
```python
def check_zombie_state(distribution, history):
    """
    Zombie = Boltzmann distribution (thermal equilibrium)
    """
    # 1. Entropy approaches maximum
    S = calculate_entropy(distribution)
    dS_dt = (S - history[-1].entropy) / dt

    if dS_dt < 1e-6:
        equilibrium_criterion_1 = True

    # 2. Velocity distribution is Maxwellian
    v_dist = distribution.velocity_histogram()
    maxwell = fit_maxwellian(v_dist)
    chi_squared = goodness_of_fit(v_dist, maxwell)

    if chi_squared < threshold:
        equilibrium_criterion_2 = True

    # 3. Star formation ceased (no recent plasma ejections)
    ejection_rate = count_recent_ejections(history, time_window=1e9)

    if ejection_rate < 1e-3:  # < 1 per Gyr
        equilibrium_criterion_3 = True

    if all criteria:
        return ZombieState(
            temperature=maxwell.temperature,
            entropy=S,
            relaxation_complete=True
        )
```

---

## IX. Implementation Priorities

### Phase 1: PSGA Cl(3,3) Foundation ⭐ **CRITICAL**

**Dependencies**: All other phases depend on this

**Tasks**:
1. Integrate PSGA module from PSBoneyard
2. `PhaseSpacePoint_Cl33` class
3. `Bivector_Cl33` for planes
4. `Motor_Cl33` for binary orbits
5. Geometric product, grade projections
6. GPU backend (CuPy or JAX)

**Deliverable**: Working Cl(3,3) library with test suite

### Phase 2: Collisionless Boltzmann Integrator

**Dependencies**: Phase 1

**Tasks**:
1. `PhaseSpaceDistribution` class
2. Hamiltonian flow integrator (symplectic)
3. Macro-particle sampling
4. Mean field calculator (Poisson solver)
5. Self-consistency loop

**Deliverable**: Single galaxy evolving under self-gravity

### Phase 3: SMBH Binary System

**Dependencies**: Phase 1

**Tasks**:
1. `SMBHBinary` class
2. Explicit 2-body integrator in Cl(3,3)
3. Barycenter tracking
4. Saddle-point detection
5. Plasma ejection physics

**Deliverable**: Binary orbital evolution with ejections

### Phase 4: Two-Galaxy Collision

**Dependencies**: Phases 2 & 3

**Tasks**:
1. `ZombieGalaxy` initialization
2. Ecliptic plane collision (bivector product)
3. SMBH binary formation
4. Phase mixing and violent relaxation

**Deliverable**: Galaxy collision → SMBH binary → new plane

### Phase 5: Star Formation

**Dependencies**: Phase 3

**Tasks**:
1. Disk star formation from SMBH ejecta
2. Halo star formation from BH binaries
3. BH binary detection (KD-tree)
4. Star particle tracking in distribution

**Deliverable**: Luminous galaxy with disk + halo

### Phase 6: Long-Timescale Evolution

**Dependencies**: Phases 2-5

**Tasks**:
1. Differential timestepping
2. Checkpoint/restart
3. Zombie state detection
4. 100 Gyr simulation capability

**Deliverable**: Full lifecycle: zombie → active → zombie

---

## X. Performance Considerations

### GPU Acceleration Strategy

**SMBH binary** (2 particles):
- CPU is fine (negligible cost)

**Distribution** (10⁶ macro-particles):
- **GPU essential** for:
  - Hamiltonian flow (10⁶ phase space updates)
  - KD-tree BH binary search
  - Force interpolation from grid
  - Mean field calculation

**Recommendation**: JAX
- Auto-differentiation (useful for gradients ∇Φ)
- GPU/TPU support
- Vectorization (vmap)
- JIT compilation

### Memory Layout

**Structure of Arrays (SoA)** for GPU efficiency:
```python
class PhaseSpaceDistribution_GPU:
    # Separate arrays for each component (coalesced access)
    x:  DeviceArray[N]  # All x-coordinates
    y:  DeviceArray[N]
    z:  DeviceArray[N]
    px: DeviceArray[N]
    py: DeviceArray[N]
    pz: DeviceArray[N]
    weights: DeviceArray[N]
```

Not Array of Structures (AoS):
```python
# ❌ BAD for GPU (strided access)
particles: DeviceArray[N, 6]  # [(x,y,z,px,py,pz), ...]
```

### Computational Cost Estimates

**Current toy model** (50 stars, 100 steps):
- Runtime: ~10 seconds
- Total operations: ~5 × 10⁴ force calculations

**Target QFD simulation** (10⁹ particles, 10⁶ steps):
- Naive N-body: 10²⁷ operations → impossible
- Our approach:
  - SMBH: 2 particles × 10⁶ steps = 10⁶ ops (negligible)
  - Distribution: 10⁶ macro × 10⁶ steps = 10¹² ops
  - Mean field: 10⁶ grid points × 10⁶ steps = 10¹² ops
  - Total: ~10¹² ops → **feasible on GPU**

**Estimated runtime** (on single A100 GPU):
- 10¹² ops / 10¹² FLOPS = 1000 seconds ~ 15 minutes per Gyr
- 100 Gyr simulation: ~1 day

---

## XI. Validation Metrics

### Physics Checks

1. **Energy conservation** (Hamiltonian systems):
   ```
   H(t) = constant ± ε_numerical
   ```

2. **Phase space volume** (Liouville's theorem):
   ```
   ∫ d³x d³p = constant
   ```

3. **Entropy increase** (2nd law):
   ```
   dS/dt ≥ 0 (until equilibrium)
   ```

4. **Violent relaxation timescale**:
   ```
   t_relax ~ 5-10 × t_crossing ~ 0.5-1 Gyr
   ```

### Astrophysical Observables

1. **Rotation curve**:
   ```
   v_circ(r) should be flat at large r
   Compare to SPARC database
   ```

2. **Surface brightness profile**:
   ```
   I(r) ~ r^(-1) (exponential disk)
   ```

3. **BH mass function**:
   ```
   dN/dM ~ M^(-2.35) → evolves to IMBH peak
   ```

4. **Halo density profile**:
   ```
   ρ(r) ~ r^(-2) (isothermal) or r^(-3) (NFW-like)?
   ```

---

## XII. Next Steps

**Immediate** (Week 1):
- [ ] Copy PSGA from PSBoneyard or describe API
- [ ] Create `PhaseSpacePoint_Cl33` test implementation
- [ ] Verify geometric product operations

**Short-term** (Month 1):
- [ ] Complete PSGA Cl(3,3) module with GPU backend
- [ ] Implement single-galaxy collisionless Boltzmann
- [ ] Test mean field self-consistency

**Medium-term** (Months 2-3):
- [ ] SMBH binary with ejections
- [ ] Two-galaxy collision mechanics
- [ ] Star formation from ejecta

**Long-term** (Month 4+):
- [ ] Full lifecycle simulation (zombie → active → zombie)
- [ ] Validation against observations
- [ ] Publication-quality results

---

## XIII. Open Questions

1. **PSGA implementation details**:
   - Exact API for phase space points?
   - GPU backend (CuPy vs JAX vs PyTorch)?
   - Performance vs. correctness tradeoffs?

2. **Stellar evolution**:
   - Do we need explicit stellar evolution? Or just mass loss rates?
   - Metallicity tracking for Pop II vs Pop III?

3. **BH growth**:
   - Accretion rates onto IMBHs?
   - GW emission from BH mergers (removes energy)?

4. **Disk stability**:
   - Toomre Q parameter tracking?
   - Spiral arm formation (self-gravity)?

5. **Zombie state**:
   - What fraction of BHs merge vs remain in halo?
   - Final dark matter halo profile shape?

---

## References

**Collisionless Dynamics**:
- Binney & Tremaine, "Galactic Dynamics" (2008)
- Lynden-Bell, "Statistical Mechanics of Violent Relaxation" (1967)

**Geometric Algebra**:
- Doran & Lasenby, "Geometric Algebra for Physicists" (2003)
- Hestenes, "New Foundations for Classical Mechanics" (1986)

**Phase Space Methods**:
- Arnold, "Mathematical Methods of Classical Mechanics" (1989)
- Marsden & Ratiu, "Introduction to Mechanics and Symmetry" (1999)

**QFD Framework**:
- McSheery, "Quantum Field Dynamics" Book 7.0 (2025)

---

**Document Status**: Living document, updated as implementation progresses

**Last Updated**: 2025-11-07

**Authors**: Tracy McSheery, Claude (AI Assistant)
