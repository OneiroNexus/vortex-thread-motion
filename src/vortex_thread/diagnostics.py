"""Deterministic numerical diagnostics using only Python's standard library."""

import math
from .model import (amplitude, effective_time, energy, enstrophy, gradient,
                    integrate, integrate_deformation, pressure, segment_width,
                    velocity, vorticity)

POINTS = ((0.23, 0.71), (1.03, 2.19), (2.61, 4.17), (5.31, 1.47))


def _order(previous, current):
    return math.log(previous / current, 2) if current > 0 and previous > 0 else None


def finite_difference_convergence():
    """Centered spatial/time derivatives; h and dt halve together for residuals.

    Samples are fixed off-grid points to avoid cancellations from symmetry.
    This differentiates the exact field; no discrete PDE is evolved.
    """
    rows = []
    t, nu = 0.7, 0.25
    for h in (0.2, 0.1, 0.05, 0.025):
        errors = dict(gradient=0.0, laplacian=0.0, time_derivative=0.0,
                      divergence=0.0, momentum_residual=0.0)
        for x, y in POINTS:
            u = velocity(x, y, t, nu)
            xp, xm = velocity(x+h, y, t, nu), velocity(x-h, y, t, nu)
            yp, ym = velocity(x, y+h, t, nu), velocity(x, y-h, t, nu)
            tp, tm = velocity(x, y, t+h, nu), velocity(x, y, t-h, nu)
            dx = [(xp[i]-xm[i])/(2*h) for i in range(2)]
            dy = [(yp[i]-ym[i])/(2*h) for i in range(2)]
            dt = [(tp[i]-tm[i])/(2*h) for i in range(2)]
            lap = [(xp[i]+xm[i]+yp[i]+ym[i]-4*u[i])/h**2 for i in range(2)]
            dp = ((pressure(x+h,y,t,nu)-pressure(x-h,y,t,nu))/(2*h),
                  (pressure(x,y+h,t,nu)-pressure(x,y-h,t,nu))/(2*h))
            exact_grad = gradient(x,y,t,nu)
            errors["divergence"] = max(errors["divergence"], abs(dx[0]+dy[1]))
            for i in range(2):
                errors["gradient"] = max(errors["gradient"], abs(dx[i]-exact_grad[i][0]),
                                          abs(dy[i]-exact_grad[i][1]))
                errors["laplacian"] = max(errors["laplacian"], abs(lap[i]+2*u[i]))
                errors["time_derivative"] = max(errors["time_derivative"], abs(dt[i]+2*nu*u[i]))
                residual = dt[i]+u[0]*dx[i]+u[1]*dy[i]+dp[i]-nu*lap[i]
                errors["momentum_residual"] = max(errors["momentum_residual"],abs(residual))
        row = {"h":h,"dt":h,"max_absolute_errors":errors}
        if rows:
            row["observed_orders"] = {k:_order(rows[-1]["max_absolute_errors"][k], errors[k])
                                      for k in errors if k != "divergence"}
        rows.append(row)
    return rows


def trajectory_convergence():
    t, nu, delta = 2*math.log(2), 0.25, 0.10
    reference_steps = 8192
    reference = [integrate(x,y,t,nu,reference_steps) for x,y in POINTS]
    rows = []
    for steps in (8,16,32,64):
        generic_error, integral_drift, determinant_error = 0.0, 0.0, 0.0
        for (x,y), ref in zip(POINTS,reference):
            q = integrate(x,y,t,nu,steps)
            generic_error = max(generic_error, math.dist(q,ref))
            integral_drift = max(integral_drift, abs(math.cos(q[0])*math.cos(q[1])-math.cos(x)*math.cos(y)))
            _, f = integrate_deformation(x,y,t,nu,steps)
            determinant_error = max(determinant_error,abs(f[0][0]*f[1][1]-f[0][1]*f[1][0]-1))
        widths = {}
        for expanding in (False,True):
            y = -math.pi/2 if expanding else math.pi/2
            left = integrate(math.pi/2-delta,y,t,nu,steps)
            right = integrate(math.pi/2+delta,y,t,nu,steps)
            numerical = right[0]-left[0]
            exact = segment_width(delta,t,nu,expanding)
            widths["expanding" if expanding else "contracting"] = {
                "numerical":numerical,"exact":exact,"absolute_error":abs(numerical-exact),
                "max_transverse_drift":max(abs(left[1]-y),abs(right[1]-y))}
        row = {"steps":steps,"dt":t/steps,"generic_error_against_refined_rk4":generic_error,
               "first_integral_max_absolute_drift":integral_drift,
               "deformation_max_absolute_determinant_error":determinant_error,"segments":widths}
        if rows:
            row["observed_orders"] = {
                "generic_trajectory":_order(rows[-1]["generic_error_against_refined_rk4"],generic_error),
                **{k:_order(rows[-1]["segments"][k]["absolute_error"],widths[k]["absolute_error"])
                   for k in widths}}
        rows.append(row)
    return {"end_time":t,"viscosity":nu,"initial_half_width":delta,
            "generic_initial_points":POINTS,
            "segment_initial_geometry":"x=pi/2 +/- 0.10; contracting y=+pi/2; expanding y=-pi/2",
            "effective_time":effective_time(t,nu),"amplitude":amplitude(t,nu),
            "reference_steps":reference_steps,"reference_kind":"refined RK4, not an exact generic trajectory",
            "rows":rows}


def decay_samples():
    n, nu = 32, 0.25
    rows = []
    for t in (0,0.5,1,2*math.log(2),2,4):
        e, z = 0.0, 0.0
        for i in range(n):
            for j in range(n):
                x,y = 2*math.pi*i/n, 2*math.pi*j/n
                u = velocity(x,y,t,nu)
                e += (u[0]**2+u[1]**2)/2
                z += vorticity(x,y,t,nu)**2/2
        rows.append({"t":t,"amplitude":amplitude(t,nu),"energy_exact_mean":energy(t,nu),
                     "energy_sampled_mean":e/n**2,"enstrophy_exact_mean":enstrophy(t,nu),
                     "enstrophy_sampled_mean":z/n**2})
    return {"viscosity":nu,"periodic_grid_points_per_axis":n,"rows":rows}


def build_report():
    fd = finite_difference_convergence()
    paths = trajectory_convergence()
    decay = decay_samples()
    last = paths["rows"][-1]
    checks = {
        "centered_derivative_and_residual_second_order":all(
            1.95 < value < 2.05 for row in fd[1:] for value in row["observed_orders"].values()),
        "finite_difference_divergence_below_1e-12":max(r["max_absolute_errors"]["divergence"] for r in fd)<1e-12,
        "rk4_generic_and_exact_segment_orders_above_3_7":all(
            value > 3.7 for row in paths["rows"][1:] for value in row["observed_orders"].values()),
        "rk4_generic_error_below_1e-8":last["generic_error_against_refined_rk4"]<1e-8,
        "rk4_segment_errors_below_1e-8":all(r["absolute_error"]<1e-8 for r in last["segments"].values()),
        "first_integral_drift_below_1e-8":last["first_integral_max_absolute_drift"]<1e-8,
        "material_area_determinant_error_below_1e-8":last["deformation_max_absolute_determinant_error"]<1e-8,
        "energy_enstrophy_quadrature_error_below_1e-13":all(
            abs(r[k+"_exact_mean"]-r[k+"_sampled_mean"])<1e-13 for r in decay["rows"] for k in ("energy","enstrophy")),
    }
    return {"schema_version":1,"scope":"Fresh independent analytic-field and passive-trajectory verification; no PDE evolution, historical replay, 3D cloud simulation, or compression benchmark.",
            "field":"u=exp(-2*nu*t)*(cos(x)*sin(y),-sin(x)*cos(y))",
            "pressure":"p=-exp(-4*nu*t)*(cos(2*x)+cos(2*y))/4",
            "domain":"[0,2*pi)^2, dimensionless, unit density, no forcing",
            "finite_difference_parameters":{"time":0.7,"viscosity":0.25,"sample_points":POINTS,
                                             "scheme":"second-order centered differences; dt=h"},
            "finite_difference_convergence":fd,"trajectory_convergence":paths,"decay":decay,
            "numerical_acceptance_checks":checks,"all_numerical_checks_passed":all(checks.values())}
