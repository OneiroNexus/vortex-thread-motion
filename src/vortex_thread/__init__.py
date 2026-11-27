"""Independent Taylor--Green verification utilities by Aaron Michael Weis.

This package evaluates an exact field and integrates passive trajectories. It is
not a Navier--Stokes PDE solver or a replay of the missing historical archive.
"""

from .model import (amplitude, effective_time, energy, enstrophy, gradient,
                    integrate, integrate_deformation, pressure, segment_width,
                    velocity, vorticity)

__all__ = ["amplitude", "effective_time", "energy", "enstrophy", "gradient",
           "integrate", "integrate_deformation", "pressure", "segment_width",
           "velocity", "vorticity"]
