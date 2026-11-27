"""Dimensionless 2D periodic Taylor--Green field and fixed-step RK4.

Velocity is (A cos(x) sin(y), -A sin(x) cos(y)); A=exp(-2 nu t).
Pressure uses unit density, zero spatial mean, and u_t+(u.grad)u=-grad(p)+nu Lap(u).
Coordinates stay unwrapped so segment lengths are not corrupted at the seam.
"""

import math


def _parameters(t, nu):
    if not math.isfinite(t) or not math.isfinite(nu) or t < 0 or nu < 0:
        raise ValueError("t and nu must be finite and nonnegative")


def amplitude(t, nu):
    _parameters(t, nu)
    return math.exp(-2 * nu * t)


def effective_time(t, nu):
    _parameters(t, nu)
    return t if nu == 0 else -math.expm1(-2 * nu * t) / (2 * nu)


def velocity(x, y, t, nu):
    a = amplitude(t, nu)
    return a * math.cos(x) * math.sin(y), -a * math.sin(x) * math.cos(y)


def pressure(x, y, t, nu):
    a = amplitude(t, nu)
    return -(a * a / 4) * (math.cos(2 * x) + math.cos(2 * y))


def gradient(x, y, t, nu):
    a = amplitude(t, nu)
    d = a * math.sin(x) * math.sin(y)
    r = a * math.cos(x) * math.cos(y)
    return ((-d, r), (-r, d))


def vorticity(x, y, t, nu):
    return -2 * amplitude(t, nu) * math.cos(x) * math.cos(y)


def energy(t, nu):
    """Domain mean of |u|^2/2, not domain integral."""
    return amplitude(t, nu) ** 2 / 4


def enstrophy(t, nu):
    """Domain mean of omega^2/2, not domain integral."""
    return amplitude(t, nu) ** 2 / 2


def segment_width(delta0, t, nu, expanding=False):
    """Exact full width on y=-pi/2 (expanding) or y=+pi/2.

    Endpoints start at x=pi/2 +/- delta0. 0 < delta0 < pi ensures
    both endpoints stay in the same open separatrix interval.
    """
    if not math.isfinite(delta0) or not 0 < delta0 < math.pi:
        raise ValueError("initial half-width must lie strictly between 0 and pi")
    s = effective_time(t, nu)
    log_tangent = math.log(math.tan(delta0 / 2)) + (s if expanding else -s)
    # Equivalent stable forms avoid overflow for long inviscid trajectories.
    return (2 * math.pi - 4 * math.atan(math.exp(-log_tangent))
            if log_tangent > 0 else 4 * math.atan(math.exp(log_tangent)))


def _rk4(rhs, state, end_time, steps):
    if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
        raise ValueError("steps must be a positive integer")
    if not math.isfinite(end_time) or end_time < 0:
        raise ValueError("end_time must be finite and nonnegative")
    h = end_time / steps
    q = tuple(float(v) for v in state)
    for i in range(steps):
        t = i * h
        k1 = rhs(q, t)
        k2 = rhs(tuple(v + h * k / 2 for v, k in zip(q, k1)), t + h / 2)
        k3 = rhs(tuple(v + h * k / 2 for v, k in zip(q, k2)), t + h / 2)
        k4 = rhs(tuple(v + h * k for v, k in zip(q, k3)), t + h)
        q = tuple(v + h * (a + 2*b + 2*c + d) / 6
                  for v, a, b, c, d in zip(q, k1, k2, k3, k4))
    return q


def integrate(x, y, end_time, nu, steps):
    _parameters(end_time, nu)
    return _rk4(lambda q, t: velocity(q[0], q[1], t, nu), (x, y), end_time, steps)


def integrate_deformation(x, y, end_time, nu, steps):
    """Integrate position and material deformation F with F'=grad(u) F, F(0)=I."""
    _parameters(end_time, nu)

    def rhs(q, t):
        vx, vy = velocity(q[0], q[1], t, nu)
        g = gradient(q[0], q[1], t, nu)
        f00, f01, f10, f11 = q[2:]
        return (vx, vy, g[0][0]*f00 + g[0][1]*f10,
                g[0][0]*f01 + g[0][1]*f11,
                g[1][0]*f00 + g[1][1]*f10,
                g[1][0]*f01 + g[1][1]*f11)

    q = _rk4(rhs, (x, y, 1, 0, 0, 1), end_time, steps)
    return q[:2], ((q[2], q[3]), (q[4], q[5]))
